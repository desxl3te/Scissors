"""Функции для работы с паролями и JWT-токенами.

Этот модуль не знает ничего о FastAPI-роутах и базе данных.
Его задача узкая: безопасно хешировать пароли и выдавать/читать токены доступа.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from config import settings


# Используем pbkdf2_sha256 через passlib.
# Для этого проекта это практичнее, чем bcrypt, потому что схема не зависит
# от проблем совместимости конкретных бинарных сборок bcrypt в окружении.
# При этом пароль всё равно хранится безопасно в виде вычисленного хеша.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, совпадает ли введённый пароль с хешем из базы."""

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Создаёт безопасный хеш пароля для сохранения в базе."""

    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Создаёт JWT-токен доступа.

    В payload обязательно добавляем срок жизни токена.
    Дополнительно сохраняем момент выдачи токена, чтобы его было проще
    отлаживать и анализировать при необходимости.
    """

    payload = data.copy()
    lifetime = expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    now = datetime.utcnow()

    payload.update(
        {
            "iat": now,
            "exp": now + lifetime,
        }
    )

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Декодирует токен и возвращает payload.

    Если токен испорчен, просрочен или подписан не тем секретом,
    возвращаем None вместо падения приложения.
    """

    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        return None
