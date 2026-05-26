# Импортируем pytest
import pytest

# Класс для тестов эндпоинта поддержки
class TestSupport:
    # Тест отправки сообщения в поддержку
    def test_send_message(self, fastapi_client, mock_db_cursor, full_user_data):
        # Настраиваем мок: при запросе пользователя возвращаем полные данные
        mock_db_cursor["cursor"].fetchone.return_value = full_user_data
        # Отправляем POST-запрос с данными сообщения
        res = fastapi_client.post("/api/support", headers={"Authorization": "Bearer token"}, json={
            "name": "User", "email": "u@u.com", "message": "Hello"
        })
        # Проверяем, что ответ — 201 (создано) или 422 (валидация), но не ошибка авторизации
        assert res.status_code in [201, 422]