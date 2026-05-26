# Импортируем pytest
import pytest

# Класс для тестов основного приложения FastAPI
class TestFastAPIMain:
    # Тест наличия заголовка приложения
    def test_title(self, fastapi_client):
        # Проверяем, что title — строка
        assert isinstance(fastapi_client.app.title, str)
    # Тест версии приложения
    def test_version(self, fastapi_client):
        # Проверяем, что версия — "3.0.0"
        assert fastapi_client.app.version == "3.0.0"
    # Тест эндпоинта здоровья
    def test_health(self, fastapi_client):
        # Проверяем, что health check возвращает 200
        assert fastapi_client.get("/health").status_code == 200
    # Тест корневого эндпоинта
    def test_root(self, fastapi_client):
        # Проверяем, что корень возвращает 200
        assert fastapi_client.get("/").status_code == 200
    # Тест доступности Swagger-документации
    def test_docs(self, fastapi_client):
        # Проверяем, что /docs доступен
        assert fastapi_client.get("/docs").status_code == 200