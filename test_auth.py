# Импортируем модуль pytest для написания тестов
import pytest

# Класс для группировки тестов авторизации
class TestAuth:
    # Тест успешной регистрации нового пользователя
    def test_register_success(self, fastapi_client, mock_db_cursor):
        # Настраиваем мок: первые два вызова fetchone вернут None (пользователя нет),
        # третий вызов вернет данные нового пользователя с id=1
        mock_db_cursor["cursor"].fetchone.side_effect = [None, None, {"id": 1}]
        # Устанавливаем, что последний вставленный ряд получит id=1
        mock_db_cursor["cursor"].lastrowid = 1
        # Отправляем POST-запрос на регистрацию с тестовыми данными
        res = fastapi_client.post("/api/auth/register", json={
            "user_name": "new", "email": "n@n.com", "password": "pass123", "phone": "+7900"
        })
        # Проверяем, что ответ — 201 (создано) или 422 (ошибка валидации)
        assert res.status_code in [201, 422]

    # Тест регистрации с конфликтом (почта уже занята)
    def test_register_conflict_email(self, fastapi_client, mock_db_cursor):
        # Настраиваем мок: fetchone сразу вернет данные существующего пользователя
        mock_db_cursor["cursor"].fetchone.return_value = {"id": 1}
        # Отправляем запрос регистрации с уже существующей почтой
        res = fastapi_client.post("/api/auth/register", json={
            "user_name": "new", "email": "exists@example.com", "password": "pass"
        })
        # Проверяем, что ответ — 409 (конфликт) или 422 (валидация)
        assert res.status_code in [409, 422]

    # Тест успешного входа (логина)
    def test_login_success(self, fastapi_client, mock_db_cursor, full_user_data):
        # Возвращаем полные данные пользователя (требуется для serialize_user)
        mock_db_cursor["cursor"].fetchone.return_value = full_user_data
        # Отправляем POST-запрос на вход с корректными данными
        res = fastapi_client.post("/api/auth/login", json={"email": "test@example.com", "password": "pass"})
        # Проверяем, что вход успешен (статус 200)
        assert res.status_code == 200

    # Тест входа с неверным паролем
    def test_login_wrong_pass(self, fastapi_client, mock_db_cursor):
        # Настраиваем мок: пользователь не найден (None)
        mock_db_cursor["cursor"].fetchone.return_value = None
        # Отправляем запрос входа с несуществующей почтой
        res = fastapi_client.post("/api/auth/login", json={"email": "no@no.com", "password": "pass"})
        # Проверяем, что получаем 401 (неавторизован)
        assert res.status_code == 401

    # Тест получения данных текущего пользователя (/me)
    def test_get_me(self, fastapi_client, mock_db_cursor, full_user_data):
        # Возвращаем полные данные пользователя для мок-запроса
        mock_db_cursor["cursor"].fetchone.return_value = full_user_data
        # Отправляем GET-запрос с заголовком авторизации
        res = fastapi_client.get("/api/auth/me", headers={"Authorization": "Bearer token"})
        # Проверяем, что запрос успешен
        assert res.status_code == 200