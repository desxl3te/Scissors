import pytest

from datetime import datetime

def test_list_events(fastapi_client, mock_db_cursor):
        # мок-данные события (event_date — datetime, т.к. в коде вызывается .isoformat())
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
        # GET-запрос на получение списка событий
        res = fastapi_client.get("/api/events")
        # Проверка, что в ответе ровно 1 событие
        assert res.json()["count"] == 1

def test_get_event_types(fastapi_client, mock_db_cursor):
        # мок-данные: два типа событий
        mock_db_cursor["cursor"].fetchall.return_value = [
            {"event_type": "music"}, {"event_type": "dj"}
        ]
        # GET-запрос на получение типов
        res = fastapi_client.get("/api/events/types/list")
        # Проверка, что в ответе есть оба типа (как множество)
        assert set(res.json()["types"]) == {"music", "dj"}
