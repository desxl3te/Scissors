from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.auth import router as auth_router
from app.api.routes.public import router as public_router
from app.api.routes.reservations import router as reservations_router
from app.api.routes.support import router as support_router
from app.api.routes.user import router as users_router
from app.api.routes.events import router as events_router
from app.core.config import settings
from app.db.bootstrap import initialize_database

# главный файл FastAPI приложения
@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title=settings.app_title,
    version="3.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)
# настраивает CORS(middleware), монтирует статические файлы, подключает все роутеры
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public_router)
app.include_router(auth_router)
app.include_router(reservations_router)
app.include_router(support_router)
app.include_router(users_router)
app.include_router(events_router)

# раздача загруженных файлов (аватары пользователей).
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount(
    "/uploads",
    StaticFiles(directory=settings.uploads_dir),
    name="uploads",
)