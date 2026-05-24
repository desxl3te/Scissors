"""Pydantic-схемы запросов и ответов.

Схемы здесь привязаны именно к тем данным, которые реально поддерживаются
исходной схемой БД проекта.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """Тело запроса на регистрацию пользователя."""

    user_name: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    phone: Optional[str] = Field(default=None, max_length=20)


class LoginRequest(BaseModel):
    """Тело запроса на вход."""

    email: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=1, max_length=128)


class UpdateProfileRequest(BaseModel):
    """Тело запроса на обновление профиля.

    Обновляем только те поля, которые действительно есть в таблице `users`.
    """

    user_name: Optional[str] = Field(default=None, min_length=2, max_length=50)
    email: Optional[str] = Field(default=None, min_length=5, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)


class ReservationCreateRequest(BaseModel):
    """Тело запроса на создание брони.

    Ограничение по длительности синхронизировано с CHECK-ограничением
    исходной таблицы `reservations`: от 1 до 4 часов.
    """

    table_id: int = Field(..., ge=1)
    reservation_time: datetime
    duration_hours: int = Field(default=2, ge=1, le=4)
    guests_count: int = Field(..., ge=1, le=12)
    special_request: Optional[str] = Field(default=None, max_length=500)
