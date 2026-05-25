from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

# Pydantic модели для аутентификации
class RegisterRequest(BaseModel):
    user_name: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    phone: Optional[str] = Field(default=None, max_length=20)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=1, max_length=128)


class UpdateProfileRequest(BaseModel):
    user_name: Optional[str] = Field(default=None, min_length=2, max_length=50)
    email: Optional[str] = Field(default=None, min_length=5, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
