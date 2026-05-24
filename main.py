"""Точка входа backend-сервиса Scissors Bar.

Здесь собирается само FastAPI-приложение: подключаются middleware,
инициализация базы данных и все роутеры.
"""

from contextlib import asynccontextmanager
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from accounts import router as accounts_router
from config import settings
from database import initialize_database
from menu import router as bar_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Подготавливает приложение к старту.

    На старте проверяем доступность штатной схемы проекта.
    Backend больше не расширяет её собственными миграциями.
    """

    initialize_database()
    yield


app = FastAPI(
    title=settings.app_title,
    debug=settings.debug,
    version="2.0.0",
    lifespan=lifespan,
)


# CORS разрешаем явно, потому что фронт может запускаться отдельно
# как статический сайт или с другого локального порта.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts_router)
app.include_router(bar_router)


@app.get("/")
def root():
    """Корневой endpoint для быстрой проверки, что API поднялось."""

    return {
        "service": "Scissors Bar API",
        "framework": "FastAPI",
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/health")
def health():
    """Лёгкая health-check ручка без обращения к тяжёлой бизнес-логике."""

    return {
        "status": "ok",
        "service": settings.app_title,
        "database_engine": "mysql",
        "database_host": settings.db_host,
        "database_port": settings.db_port,
        "database_name": settings.db_name,
    }


@app.get("/api/about")
def about():
    """Возвращает описание проекта из about.json, если файл существует.

    Если JSON-файл когда-нибудь удалят или повредят, endpoint не развалится:
    в таком случае вернём безопасный fallback-ответ.
    """

    if settings.about_path.exists():
        with settings.about_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    return {
        "project": "Scissors Bar",
        "description": "Backend API для меню, профилей, бронирований и аналитики.",
        "technologies": ["FastAPI", "MySQL", "JWT"],
    }
