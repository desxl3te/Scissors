# Импортируем pytest
import pytest

# Класс для тестов эндпоинтов пользователей
class TestUser:
    # Тест получения профиля существующего пользователя
    def test_get_profile(self, fastapi_client, mock_db_cursor):
        # Настраиваем мок: возвращаем данные пользователя
        mock_db_cursor["cursor"].fetchone.return_value = {
            "user_name": "testuser", "email": "t@t.com", "phone": None, 
            "total_visits": 5, "created_at": None, "role": "customer"
        }
        # Отправляем GET-запрос на получение профиля
        res = fastapi_client.get("/api/users/testuser")
        # Проверяем, что запрос успешен
        assert res.status_code == 200
        # Проверяем, что имя пользователя совпадает
        assert res.json()["user_name"] == "testuser"

    # Тест получения профиля несуществующего пользователя
    def test_get_profile_not_found(self, fastapi_client, mock_db_cursor):
        # Настраиваем мок: пользователь не найден
        mock_db_cursor["cursor"].fetchone.return_value = None
        # Отправляем запрос на несуществующего пользователя
        res = fastapi_client.get("/api/users/unknown")
        # Проверяем, что получаем 404 (не найдено)
        assert res.status_code == 404