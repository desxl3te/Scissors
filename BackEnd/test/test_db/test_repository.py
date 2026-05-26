import pytest

from datetime import datetime, timedelta

from mysql.connector.errors import IntegrityError

def test_get_user_by_id(mock_db_cursor):
        # импорт модуль репозитория*
        from app.db import repository
        # мок: данные пользователя
        mock_db_cursor["cursor"].fetchone.return_value = {"id": 1, "user_name": "test"}
        # функция получения пользователя
        res = repository.get_user_by_id(1)
        # Проверка, что id совпадает
        assert res["id"] == 1

def test_create_reservation_conflict(mock_db_cursor):
        # *
        from app.db import repository
        # мок: execute выбрасывает ошибку дубликата
        mock_db_cursor["cursor"].execute.side_effect = IntegrityError("1062: Duplicate entry", errno=1062)
        # Проверка, что функция выбрасывает ожидаемое исключение
        with pytest.raises(repository.ReservationConflictError):
            repository.create_reservation(1, 1, datetime.now(), 2, 2, None)

def test_cancel_reservation_missing(mock_db_cursor):
        # *
        from app.db import repository
        # мок: бронирование не найдено
        mock_db_cursor["cursor"].fetchone.return_value = None
        # функция отмены
        status = repository.cancel_reservation(999, 1)
        # Проверка, что статус — "missing"
        assert status == "missing"

def test_is_table_available_overlap(mock_db_cursor):
        # *
        from app.db import repository
        # базовое время для теста
        base_time = datetime(2025, 5, 25, 18, 0)
        # мок: точный слот свободен (None)
        mock_db_cursor["cursor"].fetchone.return_value = None
        # мок: есть пересекающееся бронирование
        mock_db_cursor["cursor"].fetchall.return_value = [
            {"reservation_time": base_time, "duration_hours": 2}
        ]
        # Проверка, что столик недоступен в пересекающийся интервал
        assert repository.is_table_available(1, base_time + timedelta(hours=1), 2) is False
