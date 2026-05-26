# Импортируем pytest и patch для мокирования функций
import pytest
from unittest.mock import patch

# Класс для тестов публичных эндпоинтов
class TestPublic:
    # Тест корневого эндпоинта (/)
    def test_root(self, fastapi_client):
        # Проверяем, что статус приложения — "running"
        assert fastapi_client.get("/").json()["status"] == "running"

    # Тест эндпоинта здоровья (/health)
    def test_health(self, fastapi_client):
        # Отправляем запрос на health check
        res = fastapi_client.get("/health")
        # Проверяем, что статус — "ok"
        assert res.json()["status"] == "ok"

    # Тест эндпоинта /api/about (информация о проекте)
    def test_about(self, fastapi_client):
        # Мокируем функцию read_json, чтобы вернуть тестовые данные
        with patch("app.core.files.read_json", return_value={"project_name": "Bar", "description": "Test"}):
            # Отправляем запрос на /api/about
            res = fastapi_client.get("/api/about")
            # Проверяем, что запрос успешен
            assert res.status_code == 200
            # Получаем данные ответа
            data = res.json()
        # Проверяем, что в ответе есть хотя бы один из ожидаемых ключей
        assert "project_name" in data or "description" in data

    # Тест эндпоинта хеширования (/api/hash/test)
    def test_hash(self, fastapi_client):
        # Отправляем запрос на хеширование тестовой строки
        res = fastapi_client.get("/api/hash/test")
        # Проверяем, что в ответе есть поле "result"
        assert "result" in res.json()
        # Проверяем, что хеш имеет длину 64 символа (SHA-256)
        assert len(res.json()["result"]) == 64