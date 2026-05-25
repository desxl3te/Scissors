from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

# определяем корневую директорию проекта
BASE_DIR = Path(__file__).resolve().parents[2]
APP_DIR = BASE_DIR / "app"

# загружаем .env из папки backend — настройки БД, CORS, путей, файлов, почты.
# обеспечивает единую конфигурацию при любом запуске (bat, PowerShell, терминал).
load_dotenv(BASE_DIR / ".env")


def _bool_env(name: str, default: bool = False) -> bool:
    """преобразует строку из .env в булево значение"""
    return os.getenv(name, str(default)).strip().lower() == "true"


def _path_env(name: str, default_value: str) -> Path:
    """преобразует строку пути в объект Path с абсолютным путем"""
    raw_value = os.getenv(name, default_value).strip()
    path = Path(raw_value).expanduser()
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


def _origins_env() -> list[str]:
    """парсит список разрешенных CORS доменов из строки"""
    raw_value = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://127.0.0.1:8080,http://localhost:8080",
    )
    return [item.strip() for item in raw_value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_title: str
    dashboard_title: str
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
    cors_allow_origins: list[str]
    about_path: Path
    dashboard_config_path: Path
    support_messages_path: Path
    fastapi_host: str
    fastapi_port: int
    dashboard_host: str
    dashboard_port: int
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_use_tls: bool
    smtp_from: str
    support_inbox: str
    uploads_dir: Path

# создаем глобальный объект настроек
settings = Settings(
    app_title=os.getenv("APP_TITLE", "Scissors Bar API"),
    dashboard_title=os.getenv("DASHBOARD_TITLE", "Scissors Bar Dashboard"),
    debug=_bool_env("DEBUG"),
    db_host=os.getenv("DB_HOST", "127.0.0.1"),
    db_port=int(os.getenv("DB_PORT", "3306")),
    db_user=os.getenv("DB_USER", "root"),
    db_password=os.getenv("DB_PASSWORD", ""),
    db_name=os.getenv("DB_NAME", "scissors_bar"),
    db_dump_path=_path_env("DB_DUMP_PATH", "app/data/scissors_bar_dumb.sql"),
    jwt_secret=os.getenv("JWT_SECRET", "scissors_bar_super_secret_key_2026"),
    jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
    access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
    cors_allow_origins=_origins_env(),
    about_path=_path_env("ABOUT_JSON_PATH", "app/data/about.json"),
    dashboard_config_path=_path_env("DASHBOARD_JSON_PATH", "app/data/dashboard.json"),
    support_messages_path=_path_env("SUPPORT_MESSAGES_PATH", "app/storage/support_messages.json"),
    fastapi_host=os.getenv("FASTAPI_HOST", "127.0.0.1"),
    fastapi_port=int(os.getenv("FASTAPI_PORT", "8000")),
    dashboard_host=os.getenv("DASHBOARD_HOST", "127.0.0.1"),
    dashboard_port=int(os.getenv("DASHBOARD_PORT", "5000")),
    smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
    smtp_port=int(os.getenv("SMTP_PORT", "587")),
    smtp_user=os.getenv("SMTP_USER", "").strip(),
    smtp_password=os.getenv("SMTP_PASSWORD", ""),
    smtp_use_tls=_bool_env("SMTP_USE_TLS", True),
    smtp_from=os.getenv("SMTP_FROM", "").strip(),
    support_inbox=os.getenv("SUPPORT_INBOX", "").strip(),
    uploads_dir=_path_env("UPLOADS_DIR", "uploads"),
)
