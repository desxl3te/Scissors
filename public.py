from __future__ import annotations

import hashlib
from fastapi import APIRouter

from app.core.config import settings
from app.core.files import read_json

# публичные эндпоинты (без авторизации)
router = APIRouter(tags=["public"])

# информация о сервисе
@router.get("/")
def root() -> dict[str, str]:
    return {
        "service": "Scissors Bar API",
        "framework": "FastAPI",
        "status": "running",
        "docs": "/docs",
    }

# проверка здоровья
@router.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "service": settings.app_title,
        "database_host": settings.db_host,
        "database_port": settings.db_port,
        "database_name": settings.db_name,
    }

# информация о проекте
@router.get("/api/about")
def about() -> dict:
    return read_json(
        settings.about_path,
        {
            "project_name": "Scissors Bar",
            "description": "Бар с острыми впечатлениями.",
            "technologies": ["FastAPI", "Flask", "MySQL", "HTML/CSS/JS"],
        },
    )

# хеширование текста (утилита для тестов)
@router.get("/api/hash/{text}")
def get_text_hash(text: str) -> dict:
    return {
        "request": text,
        "result": hashlib.sha256(text.encode()).hexdigest()
    }
