from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token
import app.db.repository as repository

# зависимости для маршрутов
security = HTTPBearer(auto_error=False)

# преобразование пользователя в JSON
def _serialize_datetime(value: Any) -> Optional[str]:
    """преобразует datetime в строку формата 'YYYY-MM-DD HH:MM:SS' без микросекунд"""
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.replace(microsecond=0).isoformat(sep=" ")

    return str(value)


def serialize_user(row: dict[str, Any]) -> dict[str, Any]:
    """преобразует словарь пользователя из БД в API формат"""
    return {
        "id": row["id"],
        "user_name": row["user_name"],
        "email": row["email"],
        "phone": row["phone"],
        "total_visits": row["total_visits"],
        "created_at": _serialize_datetime(row["created_at"]),
        "role": row.get("role", "customer"),
        "avatar": row.get("avatar"),
    }
def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict[str, Any]]:
    if credentials is None:
        return None

    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен недействителен или просрочен.",
        )

    user = repository.get_user_by_id(int(payload["sub"]))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден.",
        )

    return serialize_user(user)


def get_current_user(
    current_user: Optional[dict[str, Any]] = Depends(get_optional_current_user),
) -> dict[str, Any]:
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Для этого действия нужна авторизация.",
        )

    return current_user
