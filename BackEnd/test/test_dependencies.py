import pytest

from datetime import datetime

from fastapi import HTTPException

from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies import _serialize_datetime, serialize_user, get_optional_current_user, get_current_user

def test_none(): assert _serialize_datetime(None) is None

def test_dt(): assert _serialize_datetime(datetime(2025, 1, 1, 12, 0)) == "2025-01-01 12:00:00"

def test_str(): assert _serialize_datetime("2025-01-01") == "2025-01-01"

def test_full(full_user_data):
        res = serialize_user(full_user_data)
        # Проверка ключевых полей
        assert res["id"] == 1 and res["role"] == "customer"

def test_no_creds():
        # Проверка, что функция возвращает None при отсутствии credentials
        assert get_optional_current_user(credentials=None) is None

def test_valid_token(mock_db_cursor, full_user_data):
        # мок: возвращаем данные пользователя
        mock_db_cursor["cursor"].fetchone.return_value = full_user_data
        # Создание объект учётных данных с токеном
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
        # функция получения пользователя
        res = get_optional_current_user(credentials=creds)
        # Проверка, что пользователь найден и id совпадает
        assert res is not None and res["id"] == 1

def test_user_not_found(mock_db_cursor):
        # мок: пользователь не найден
        mock_db_cursor["cursor"].fetchone.return_value = None
        # Создание объект учётных данных
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
        # Проверка, что функция выбрасывает ожидаемое исключение
        with pytest.raises(HTTPException, match="Пользователь не найден"):
            get_optional_current_user(credentials=creds)

def test_no_auth():
        # Проверка, что функция выбрасывает исключение при отсутствии пользователя
        with pytest.raises(HTTPException, match="авторизация"):
            get_current_user(current_user=None)
