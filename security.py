from __future__ import annotations

from datetime import datetime, timedelta
from hashlib import sha256
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# безопасность и криптография
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# проверка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    if len(hashed_password) == 64: 
        # Если хеш - это 64 hex символа (старый формат SHA256)
        return sha256(plain_password.encode()).hexdigest() == hashed_password
    return pwd_context.verify(plain_password, hashed_password)

# хеширование пароля
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# создание JWT токена
def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    payload = data.copy()
    now = datetime.utcnow()
    lifetime = expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    # Issued At - время создания, xpiration - время истечения
    payload.update({"iat": now, "exp": now + lifetime})
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

# decode_access_token() - декодирование токена
def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
