"""Общие FastAPI-зависимости для backend-сервиса."""

from datetime import datetime
from typing import Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth import decode_access_token
from database import get_connection


# Этот security-объект нужен для чтения Bearer-токена из заголовка Authorization.
security = HTTPBearer(auto_error=False)


def _serialize_datetime(value) -> Optional[str]:
    """Преобразует datetime в строку, удобную для JSON."""

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.replace(microsecond=0).isoformat(sep=" ")

    return str(value)


def serialize_user(row: Dict[str, object]) -> Dict[str, object]:
    """Приводит строку пользователя из MySQL к API-формату.

    В исходной схеме проекта у пользователя нет поля аватара,
    поэтому backend не придумывает его и не пытается вернуть псевдоданные.
    """

    return {
        "id": row["id"],
        "user_name": row["user_name"],
        "email": row["email"],
        "phone": row["phone"],
        "total_visits": row["total_visits"],
        "created_at": _serialize_datetime(row["created_at"]),
    }


def _load_user_by_id(user_id: int) -> Optional[Dict[str, object]]:
    """Загружает пользователя по идентификатору."""

    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, user_name, email, phone, total_visits, created_at
            FROM users
            WHERE id = %s
            """,
            (user_id,),
        )
        row = cursor.fetchone()
        cursor.close()

    return serialize_user(row) if row else None


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, object]]:
    """Возвращает текущего пользователя или None, если токен не передан."""

    if credentials is None:
        return None

    payload = decode_access_token(credentials.credentials)

    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен недействителен или просрочен.",
        )

    user = _load_user_by_id(int(payload["sub"]))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь из токена не найден.",
        )

    return user


def get_current_user(
    current_user: Optional[Dict[str, object]] = Depends(get_optional_current_user),
) -> Dict[str, object]:
    """Требует обязательную авторизацию и возвращает пользователя."""

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Для этого действия нужна авторизация.",
        )

    return current_user
