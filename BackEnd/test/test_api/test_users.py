import pytest

def test_get_profile(fastapi_client, mock_db_cursor):
        # мок: данные пользователя
        mock_db_cursor["cursor"].fetchone.return_value = {
            "user_name": "testuser", "email": "t@t.com", "phone": None, 
            "total_visits": 5, "created_at": None, "role": "customer"
        }
        # GET-запрос на получение профиля
        res = fastapi_client.get("/api/users/testuser")
        # Проверка, что запрос успешен
        assert res.status_code == 200
        # Проверка, что имя пользователя совпадает
        assert res.json()["user_name"] == "testuser"

def test_get_profile_not_found(fastapi_client, mock_db_cursor):
        # мок: пользователь не найден
        mock_db_cursor["cursor"].fetchone.return_value = None
        # запрос на несуществующего пользователя
        res = fastapi_client.get("/api/users/unknown")
        # Проверка, что получено 404 (не найдено)
        assert res.status_code == 404
