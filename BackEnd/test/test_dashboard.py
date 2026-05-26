# Импортируем pytest
import pytest

# Класс для тестов Flask-дашборда
class TestDashboard:
    # Тест корневого эндпоинта дашборда
    def test_root(self, flask_client):
        # Отправляем запрос на корень
        res = flask_client.get("/")
        # Проверяем статус и фреймворк в ответе
        assert res.status_code == 200 and res.json["framework"] == "Flask"

    # Тест получения данных дашборда
    def test_dashboard_data(self, flask_client, mock_db_cursor):
        # Настраиваем последовательность вызовов fetchone для dashboard_snapshot
        mock_db_cursor["cursor"].fetchone.side_effect = [
            {"total": 10},  # users
            {"total": 20},  # reservations
            {"total": 15},  # confirmed
            {"total": 5},   # active tables
            None,           # конец status_rows
            None,           # конец weekday_rows
            None,           # конец popular_tables
        ]
        # Настраиваем fetchall для списков
        mock_db_cursor["cursor"].fetchall.side_effect = [
            [],  # reservation_statuses
            [],  # weekday_load
            [],  # popular_tables
        ]
        # Отправляем запрос на получение данных дашборда
        res = flask_client.get("/api/dashboard")
        # Проверяем, что запрос успешен
        assert res.status_code == 200
        # Получаем данные ответа
        data = res.json
        # Проверяем наличие ожидаемых секций
        assert "cards" in data and "charts" in data