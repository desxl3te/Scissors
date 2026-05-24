"""Роуты для пользователей и авторизации."""

import re
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status

from auth import create_access_token, get_password_hash, verify_password
from database import get_connection
from dependencies import get_current_user, serialize_user
from schemas import LoginRequest, RegisterRequest, UpdateProfileRequest


router = APIRouter(prefix="/api", tags=["accounts"])

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _normalize_email(email: str) -> str:
    """Приводит email к единому виду."""

    return email.strip().lower()


def _normalize_user_name(user_name: str) -> str:
    """Очищает имя от лишних пробелов."""

    return user_name.strip()


def _validate_email(email: str) -> None:
    """Проверяет базовую корректность email."""

    if not EMAIL_REGEX.match(email):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Некорректный email.",
        )


def _load_user_by_email(connection, email: str):
    """Загружает пользователя по email в рамках текущего соединения."""

    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, user_name, email, phone, total_visits, created_at, password_hash
        FROM users
        WHERE email = %s
        """,
        (email,),
    )
    row = cursor.fetchone()
    cursor.close()
    return row


def _build_auth_response(user_row: Dict[str, object]) -> Dict[str, object]:
    """Собирает стандартный ответ после логина или регистрации."""

    token = create_access_token(
        {
            "sub": str(user_row["id"]),
            "email": user_row["email"],
            "user_name": user_row["user_name"],
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(user_row),
    }


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest) -> Dict[str, object]:
    """Регистрирует нового пользователя и сразу выдаёт токен."""

    normalized_email = _normalize_email(payload.email)
    normalized_user_name = _normalize_user_name(payload.user_name)
    _validate_email(normalized_email)

    if len(normalized_user_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Имя пользователя должно содержать минимум 2 символа.",
        )

    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT id FROM users WHERE email = %s", (normalized_email,))
        if cursor.fetchone():
            cursor.close()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email уже существует.",
            )

        cursor.execute("SELECT id FROM users WHERE user_name = %s", (normalized_user_name,))
        if cursor.fetchone():
            cursor.close()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким именем уже существует.",
            )

        insert_cursor = connection.cursor()
        insert_cursor.execute(
            """
            INSERT INTO users (user_name, email, password_hash, phone, total_visits)
            VALUES (%s, %s, %s, %s, 0)
            """,
            (
                normalized_user_name,
                normalized_email,
                get_password_hash(payload.password),
                payload.phone.strip() if payload.phone else None,
            ),
        )
        user_id = insert_cursor.lastrowid
        insert_cursor.close()

        cursor.execute(
            """
            SELECT id, user_name, email, phone, total_visits, created_at
            FROM users
            WHERE id = %s
            """,
            (user_id,),
        )
        user_row = cursor.fetchone()
        cursor.close()

    return _build_auth_response(user_row)


@router.post("/auth/login")
def login(payload: LoginRequest) -> Dict[str, object]:
    """Проверяет логин/пароль и возвращает JWT-токен."""

    normalized_email = _normalize_email(payload.email)
    _validate_email(normalized_email)

    with get_connection() as connection:
        user_row = _load_user_by_email(connection, normalized_email)

    if not user_row or not verify_password(payload.password, user_row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль.",
        )

    return _build_auth_response(user_row)


@router.get("/auth/me")
def get_me(current_user: Dict[str, object] = Depends(get_current_user)) -> Dict[str, object]:
    """Возвращает профиль текущего пользователя."""

    return {
        "request": "me",
        "result": current_user,
    }


@router.patch("/auth/me")
def update_me(
    payload: UpdateProfileRequest,
    current_user: Dict[str, object] = Depends(get_current_user),
) -> Dict[str, object]:
    """Обновляет профиль текущего пользователя.

    Обновляем только те поля, которые действительно существуют в `users`.
    """

    data = payload.model_dump(exclude_unset=True)

    if not data:
        return {
            "request": "update_profile",
            "result": current_user,
            "message": "Изменений не передано.",
        }

    updates = []
    params = []

    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)

        if "user_name" in data:
            normalized_user_name = _normalize_user_name(data["user_name"] or "")

            if len(normalized_user_name) < 2:
                cursor.close()
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Имя пользователя должно содержать минимум 2 символа.",
                )

            cursor.execute(
                "SELECT id FROM users WHERE user_name = %s AND id != %s",
                (normalized_user_name, current_user["id"]),
            )
            if cursor.fetchone():
                cursor.close()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Пользователь с таким именем уже существует.",
                )

            updates.append("user_name = %s")
            params.append(normalized_user_name)

        if "email" in data:
            normalized_email = _normalize_email(data["email"] or "")
            _validate_email(normalized_email)

            cursor.execute(
                "SELECT id FROM users WHERE email = %s AND id != %s",
                (normalized_email, current_user["id"]),
            )
            if cursor.fetchone():
                cursor.close()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Пользователь с таким email уже существует.",
                )

            updates.append("email = %s")
            params.append(normalized_email)

        if "phone" in data:
            phone_value = data["phone"].strip() if isinstance(data["phone"], str) else data["phone"]
            updates.append("phone = %s")
            params.append(phone_value or None)

        if updates:
            update_cursor = connection.cursor()
            update_cursor.execute(
                f"""
                UPDATE users
                SET {", ".join(updates)}
                WHERE id = %s
                """,
                (*params, current_user["id"]),
            )
            update_cursor.close()

        cursor.execute(
            """
            SELECT id, user_name, email, phone, total_visits, created_at
            FROM users
            WHERE id = %s
            """,
            (current_user["id"],),
        )
        updated_row = cursor.fetchone()
        cursor.close()

    return {
        "request": "update_profile",
        "result": serialize_user(updated_row),
    }
