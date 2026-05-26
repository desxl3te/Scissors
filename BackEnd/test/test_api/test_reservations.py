import pytest

from datetime import datetime, timedelta

def test_tables_list(fastapi_client, mock_db_cursor):
        # мок-данные одного столика
        mock_db_cursor["cursor"].fetchall.return_value = [{
            "id": 1, "table_number": 1, "seats_count": 4, "is_active": 1
        }]
        # GET-запрос на получение списка столиков
        res = fastapi_client.get("/api/tables")
        # Проверка, что запрос успешен
        assert res.status_code == 200

def test_create_reservation(fastapi_client, mock_db_cursor, full_user_data):
        # последовательность вызовов fetchone:
        mock_db_cursor["cursor"].fetchone.side_effect = [
            # авторизация: данные пользователя
            full_user_data,
            # Проверка столика: данные столика
            {"id": 1, "table_number": 1, "seats_count": 4, "is_active": 1},
            # Проверка точного слота: слот свободен (None)
            None,
            # Получение созданного бронирования
            {"id": 10, "table_id": 1, "table_number": 1, "reservation_time": datetime.now(),
             "duration_hours": 2, "guests_count": 2, "status": "confirmed", "special_request": None},
        ]
        # fetchall для проверки пересекающихся интервалов
        mock_db_cursor["cursor"].fetchall.return_value = []
        # новая запись получит id=10
        mock_db_cursor["cursor"].lastrowid = 10
        # будущее время для бронирования
        future = (datetime.now() + timedelta(days=1)).isoformat()
        # POST-запрос на создание бронирования
        res = fastapi_client.post("/api/reservations", headers={"Authorization": "Bearer token"}, json={
            "table_id": 1, "reservation_time": future, "duration_hours": 2, "guests_count": 2
        })
        # Проверка, что бронирование создано (статус 201)
        assert res.status_code == 201

def test_create_reservation_past(fastapi_client, mock_db_cursor, full_user_data):
        # последовательность: авторизация → проверка столика
        mock_db_cursor["cursor"].fetchone.side_effect = [
            full_user_data,  # auth
            {"id": 1, "table_number": 1, "seats_count": 4, "is_active": 1},  # table
        ]
        # прошедшее время
        past = (datetime.now() - timedelta(days=1)).isoformat()
        # запрос на создание бронирования в прошлом
        res = fastapi_client.post("/api/reservations", headers={"Authorization": "Bearer token"}, json={
            "table_id": 1, "reservation_time": past, "duration_hours": 2, "guests_count": 2
        })
        # Проверка, что получаем ошибку валидации (400)
        assert res.status_code == 400

def test_cancel_reservation(fastapi_client, mock_db_cursor, full_user_data):
        # последовательность: авторизация → получение бронирования
        mock_db_cursor["cursor"].fetchone.side_effect = [
            full_user_data,  # auth
            {"id": 1, "user_id": 1, "status": "confirmed", "table_id": 1, "reservation_time": datetime.now(),
             "duration_hours": 2, "guests_count": 2, "special_request": None, "table_number": 1},  # reservation
        ]
        # PATCH-запрос на отмену бронирования
        res = fastapi_client.patch("/api/reservations/1/cancel", headers={"Authorization": "Bearer token"})
        # Проверка, что отмена успешна
        assert res.status_code == 200
