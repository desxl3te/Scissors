# Импортируем pytest и datetime для работы с датами
import pytest
from datetime import datetime, timedelta

# Класс для тестов эндпоинтов бронирования
class TestReservations:
    # Тест получения списка столиков
    def test_tables_list(self, fastapi_client, mock_db_cursor):
        # Возвращаем мок-данные одного столика
        mock_db_cursor["cursor"].fetchall.return_value = [{
            "id": 1, "table_number": 1, "seats_count": 4, "is_active": 1
        }]
        # Отправляем GET-запрос на получение списка столиков
        res = fastapi_client.get("/api/tables")
        # Проверяем, что запрос успешен
        assert res.status_code == 200

    # Тест создания нового бронирования
    def test_create_reservation(self, fastapi_client, mock_db_cursor, full_user_data):
        # Настраиваем последовательность вызовов fetchone:
        mock_db_cursor["cursor"].fetchone.side_effect = [
            # 1. Авторизация: получаем данные пользователя
            full_user_data,
            # 2. Проверка столика: получаем данные столика
            {"id": 1, "table_number": 1, "seats_count": 4, "is_active": 1},
            # 3. Проверка точного слота: слот свободен (None)
            None,
            # 4. Получение созданного бронирования
            {"id": 10, "table_id": 1, "table_number": 1, "reservation_time": datetime.now(),
             "duration_hours": 2, "guests_count": 2, "status": "confirmed", "special_request": None},
        ]
        # Настраиваем fetchall для проверки пересекающихся интервалов
        mock_db_cursor["cursor"].fetchall.return_value = []
        # Устанавливаем, что новая запись получит id=10
        mock_db_cursor["cursor"].lastrowid = 10
        # Формируем будущее время для бронирования
        future = (datetime.now() + timedelta(days=1)).isoformat()
        # Отправляем POST-запрос на создание бронирования
        res = fastapi_client.post("/api/reservations", headers={"Authorization": "Bearer token"}, json={
            "table_id": 1, "reservation_time": future, "duration_hours": 2, "guests_count": 2
        })
        # Проверяем, что бронирование создано (статус 201)
        assert res.status_code == 201

    # Тест создания бронирования на прошедшее время (должно вернуть 400)
    def test_create_reservation_past(self, fastapi_client, mock_db_cursor, full_user_data):
        # Настраиваем последовательность: авторизация → проверка столика
        mock_db_cursor["cursor"].fetchone.side_effect = [
            full_user_data,  # auth
            {"id": 1, "table_number": 1, "seats_count": 4, "is_active": 1},  # table
        ]
        # Формируем прошедшее время
        past = (datetime.now() - timedelta(days=1)).isoformat()
        # Отправляем запрос на создание бронирования в прошлом
        res = fastapi_client.post("/api/reservations", headers={"Authorization": "Bearer token"}, json={
            "table_id": 1, "reservation_time": past, "duration_hours": 2, "guests_count": 2
        })
        # Проверяем, что получаем ошибку валидации (400)
        assert res.status_code == 400

    # Тест отмены бронирования
    def test_cancel_reservation(self, fastapi_client, mock_db_cursor, full_user_data):
        # Настраиваем последовательность: авторизация → получение бронирования
        mock_db_cursor["cursor"].fetchone.side_effect = [
            full_user_data,  # auth
            {"id": 1, "user_id": 1, "status": "confirmed", "table_id": 1, "reservation_time": datetime.now(),
             "duration_hours": 2, "guests_count": 2, "special_request": None, "table_number": 1},  # reservation
        ]
        # Отправляем PATCH-запрос на отмену бронирования
        res = fastapi_client.patch("/api/reservations/1/cancel", headers={"Authorization": "Bearer token"})
        # Проверяем, что отмена успешна
        assert res.status_code == 200