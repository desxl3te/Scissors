"""Конфигурация backend-сервиса Scissors Bar.

Теперь backend работает не с локальной SQLite-базой, а с существующей
MySQL-схемой проекта. Поэтому здесь собраны настройки подключения к MySQL
и пути к файлам, которые относятся к backend-части.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List
import os

from dotenv import load_dotenv


# Подгружаем настройки из .env, если пользователь решит их создать.
load_dotenv()

# Базовая директория backend-проекта нужна для корректных путей к файлам.
BASE_DIR = Path(__file__).resolve().parent


def _resolve_path(value: str, default_name: str) -> Path:
    """Преобразует строковый путь в абсолютный Path."""

    raw_value = value.strip() if value else default_name
    path = Path(raw_value).expanduser()

    if not path.is_absolute():
        path = BASE_DIR / path

    return path


def _parse_cors_origins(value: str) -> List[str]:
    """Разбирает список origins для CORS."""

    if not value or not value.strip():
        return ["*"]

    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    """Единый объект настроек приложения."""

    app_title: str
    debug: bool
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str
    db_dump_path: Path
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    cors_allow_origins: List[str]
    about_path: Path


settings = Settings(
    app_title=os.getenv("APP_TITLE", "Scissors Bar API"),
    debug=os.getenv("DEBUG", "false").strip().lower() == "true",
    db_host=os.getenv("DB_HOST", "127.0.0.1"),
    db_port=int(os.getenv("DB_PORT", "3306")),
    db_user=os.getenv("DB_USER", "root"),
    db_password=os.getenv("DB_PASSWORD", ""),
    db_name=os.getenv("DB_NAME", "scissors_bar"),
    db_dump_path=_resolve_path(os.getenv("DB_DUMP_PATH", ""), "scissors_bar_dumb.sql"),
    jwt_secret=os.getenv("JWT_SECRET", "scissors_bar_super_secret_key_2026"),
    jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
    access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
    cors_allow_origins=_parse_cors_origins(os.getenv("CORS_ALLOW_ORIGINS", "*")),
    about_path=_resolve_path(os.getenv("ABOUT_JSON_PATH", ""), "about.json"),
)
