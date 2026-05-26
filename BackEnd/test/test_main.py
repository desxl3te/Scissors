import pytest

def test_title(fastapi_client):
        # Проверка, что title — строка
        assert isinstance(fastapi_client.app.title, str)

def test_version(fastapi_client):
        # Проверка, что версия — "3.0.0"
        assert fastapi_client.app.version == "3.0.0"

def test_health(fastapi_client):
        # Проверка, что health check возвращает 200
        assert fastapi_client.get("/health").status_code == 200

def test_root(fastapi_client):
        # Проверка, что корень возвращает 200
        assert fastapi_client.get("/").status_code == 200

def test_docs(fastapi_client):
        # Проверка, что /docs доступен
        assert fastapi_client.get("/docs").status_code == 200
