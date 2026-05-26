import pytest

from unittest.mock import patch

def test_root(fastapi_client):
        # Проверка, что статус приложения — "running"
        assert fastapi_client.get("/").json()["status"] == "running"

def test_health(fastapi_client):
        # запрос на health check
        res = fastapi_client.get("/health")
        # Проверка, что статус — "ok"
        assert res.json()["status"] == "ok"

def test_about(fastapi_client):
        # мок функцию read_json, чтобы вернуть тестовые данные
        with patch("app.core.files.read_json", return_value={"project_name": "Bar", "description": "Test"}):
            # запрос на /api/about
            res = fastapi_client.get("/api/about")
            # Проверка, что запрос успешен
            assert res.status_code == 200
            # данные ответа
            data = res.json()
        # Проверка, что в ответе есть хотя бы один из ожидаемых ключей
        assert "project_name" in data or "description" in data

def test_hash(fastapi_client):
        # запрос на хеширование тестовой строки
        res = fastapi_client.get("/api/hash/test")
        # Проверка, что в ответе есть поле "result"
        assert "result" in res.json()
        # Проверка, что хеш имеет длину 64 символа (SHA-256)
        assert len(res.json()["result"]) == 64
