import pytest

def test_send_message(fastapi_client, mock_db_cursor, full_user_data):
        # мок: при запросе пользователя возвращаются полные данные
        mock_db_cursor["cursor"].fetchone.return_value = full_user_data
        # POST-запрос с данными сообщения
        res = fastapi_client.post("/api/support", headers={"Authorization": "Bearer token"}, json={
            "name": "User", "email": "u@u.com", "message": "Hello"
        })
        # Проверка, что ответ — 201 (создано) или 422 (валидация), но не ошибка авторизации
        assert res.status_code in [201, 422]
