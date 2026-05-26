# Импортируем необходимые модули
import pytest
from datetime import datetime
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
# Импортируем тестируемые функции
from app.api.dependencies import _serialize_datetime, serialize_user, get_optional_current_user, get_current_user

# Класс для тестов сериализации datetime
class TestSerializeDatetime:
    # Тест обработки None
    def test_none(self): assert _serialize_datetime(None) is None
    # Тест обработки datetime-объекта
    def test_dt(self): assert _serialize_datetime(datetime(2025, 1, 1, 12, 0)) == "2025-01-01 12:00:00"
    # Тест обработки строки
    def test_str(self): assert _serialize_datetime("2025-01-01") == "2025-01-01"

# Класс для тестов сериализации пользователя
class TestSerializeUser:
    # Тест сериализации полных данных пользователя
    def test_full(self, full_user_data):
        # Вызываем функцию сериализации
        res = serialize_user(full_user_data)
        # Проверяем ключевые поля
        assert res["id"] == 1 and res["role"] == "customer"

# Класс для тестов зависимостей авторизации
class TestAuthDeps:
    # Тест отсутствия учётных данных
    def test_no_creds(self):
        # Проверяем, что функция возвращает None при отсутствии credentials
        assert get_optional_current_user(credentials=None) is None

    # Тест валидного токена
    def test_valid_token(self, mock_db_cursor, full_user_data):
        # Настраиваем мок: возвращаем данные пользователя
        mock_db_cursor["cursor"].fetchone.return_value = full_user_data
        # Создаём объект учётных данных с токеном
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
        # Вызываем функцию получения пользователя
        res = get_optional_current_user(credentials=creds)
        # Проверяем, что пользователь найден и id совпадает
        assert res is not None and res["id"] == 1

    # Тест отсутствия пользователя в БД при валидном токене
    def test_user_not_found(self, mock_db_cursor):
        # Настраиваем мок: пользователь не найден
        mock_db_cursor["cursor"].fetchone.return_value = None
        # Создаём объект учётных данных
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
        # Проверяем, что функция выбрасывает ожидаемое исключение
        with pytest.raises(HTTPException, match="Пользователь не найден"):
            get_optional_current_user(credentials=creds)

    # Тест отсутствия авторизации для обязательной зависимости
    def test_no_auth(self):
        # Проверяем, что функция выбрасывает исключение при отсутствии пользователя
        with pytest.raises(HTTPException, match="авторизация"):
            get_current_user(current_user=None)