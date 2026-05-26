# Импортируем pytest, datetime и класс ошибки IntegrityError
import pytest
from datetime import datetime, timedelta
from mysql.connector.errors import IntegrityError

# Класс для тестов репозитория (работа с БД)
class TestRepository:
    # Тест получения пользователя по id
    def test_get_user_by_id(self, mock_db_cursor):
        # Импортируем модуль репозитория
        from app.db import repository
        # Настраиваем мок: возвращаем данные пользователя
        mock_db_cursor["cursor"].fetchone.return_value = {"id": 1, "user_name": "test"}
        # Вызываем функцию получения пользователя
        res = repository.get_user_by_id(1)
        # Проверяем, что id совпадает
        assert res["id"] == 1

    # Тест обработки конфликта при создании бронирования (дубликат)
    def test_create_reservation_conflict(self, mock_db_cursor):
        # Импортируем модуль репозитория
        from app.db import repository
        # Настраиваем мок: execute выбрасывает ошибку дубликата
        mock_db_cursor["cursor"].execute.side_effect = IntegrityError("1062: Duplicate entry", errno=1062)
        # Проверяем, что функция выбрасывает ожидаемое исключение
        with pytest.raises(repository.ReservationConflictError):
            repository.create_reservation(1, 1, datetime.now(), 2, 2, None)

    # Тест отмены несуществующего бронирования
    def test_cancel_reservation_missing(self, mock_db_cursor):
        # Импортируем модуль репозитория
        from app.db import repository
        # Настраиваем мок: бронирование не найдено
        mock_db_cursor["cursor"].fetchone.return_value = None
        # Вызываем функцию отмены
        status = repository.cancel_reservation(999, 1)
        # Проверяем, что статус — "missing"
        assert status == "missing"

    # Тест проверки доступности столика при пересекающемся бронировании
    def test_is_table_available_overlap(self, mock_db_cursor):
        # Импортируем модуль репозитория
        from app.db import repository
        # Формируем базовое время для теста
        base_time = datetime(2025, 5, 25, 18, 0)
        # Настраиваем мок: точный слот свободен (None)
        mock_db_cursor["cursor"].fetchone.return_value = None
        # Настраиваем мок: есть пересекающееся бронирование
        mock_db_cursor["cursor"].fetchall.return_value = [
            {"reservation_time": base_time, "duration_hours": 2}
        ]
        # Проверяем, что столик недоступен в пересекающийся интервал
        assert repository.is_table_available(1, base_time + timedelta(hours=1), 2) is False