# Импортируем pytest и datetime для работы с датами
import pytest
from datetime import datetime

# Класс для тестов эндпоинтов событий
class TestEvents:
    # Тест получения списка событий
    def test_list_events(self, fastapi_client, mock_db_cursor):
        # Возвращаем мок-данные события (event_date — datetime, т.к. в коде вызывается .isoformat())
        mock_db_cursor["cursor"].fetchall.return_value = [{
            "id": 1, 
            "event_date": datetime(2025, 6, 1), 
            "title": "Concert", 
            "event_type": "music",
            "description": "Live", 
            "start_time": "20:00:00", 
            "price": 100, 
            "is_active": 1, 
            "image_url": None, 
            "created_at": None
        }]
        # Отправляем GET-запрос на получение списка событий
        res = fastapi_client.get("/api/events")
        # Проверяем, что в ответе ровно 1 событие
        assert res.json()["count"] == 1

    # Тест получения списка типов событий
    def test_get_event_types(self, fastapi_client, mock_db_cursor):
        # Возвращаем мок-данные: два типа событий
        mock_db_cursor["cursor"].fetchall.return_value = [
            {"event_type": "music"}, {"event_type": "dj"}
        ]
        # Отправляем GET-запрос на получение типов
        res = fastapi_client.get("/api/events/types/list")
        # Проверяем, что в ответе есть оба типа (как множество)
        assert set(res.json()["types"]) == {"music", "dj"}