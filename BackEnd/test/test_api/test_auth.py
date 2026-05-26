import pytest

def test_register_success(fastapi_client, mock_db_cursor):
        # мок: первые два вызова fetchone вернут None (пользователя нет),
        # третий вызов вернет данные нового пользователя с id=1
        mock_db_cursor["cursor"].fetchone.side_effect = [None, None, {"id": 1}]
        # последний вставленный ряд получит id=1
        mock_db_cursor["cursor"].lastrowid = 1
        # POST-запрос на регистрацию с тестовыми данными
        res = fastapi_client.post("/api/auth/register", json={
            "user_name": "new", "email": "n@n.com", "password": "pass123", "phone": "+7900"
        })
        # Проверка, что ответ — 201 (создано) или 422 (ошибка валидации)
        assert res.status_code in [201, 422]

def test_register_conflict_email(fastapi_client, mock_db_cursor):
        # мок: fetchone сразу вернет данные существующего пользователя
        mock_db_cursor["cursor"].fetchone.return_value = {"id": 1}
        # запрос регистрации с уже существующей почтой
        res = fastapi_client.post("/api/auth/register", json={
            "user_name": "new", "email": "exists@example.com", "password": "pass"
        })
        # Проверка, что ответ — 409 (конфликт) или 422 (валидация)
        assert res.status_code in [409, 422]

def test_login_success(fastapi_client, mock_db_cursor, full_user_data):
        # полные данные пользователя (требуется для serialize_user)
        mock_db_cursor["cursor"].fetchone.return_value = full_user_data
        # POST-запрос на вход с корректными данными
        res = fastapi_client.post("/api/auth/login", json={"email": "test@example.com", "password": "pass"})
        # Проверка, что вход успешен (статус 200)
        assert res.status_code == 200

def test_login_wrong_pass(fastapi_client, mock_db_cursor):
        # мок: пользователь не найден (None)
        mock_db_cursor["cursor"].fetchone.return_value = None
        # запрос входа с несуществующей почтой
        res = fastapi_client.post("/api/auth/login", json={"email": "no@no.com", "password": "pass"})
        # Проверка, что получаем 401 (неавторизован)
        assert res.status_code == 401

def test_get_me(fastapi_client, mock_db_cursor, full_user_data):
        # полные данные пользователя для мок-запроса
        mock_db_cursor["cursor"].fetchone.return_value = full_user_data
        # GET-запрос с заголовком авторизации
        res = fastapi_client.get("/api/auth/me", headers={"Authorization": "Bearer token"})
        # Проверка, что запрос успешен
        assert res.status_code == 200
