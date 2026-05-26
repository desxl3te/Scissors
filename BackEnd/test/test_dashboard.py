import pytest

def test_root(flask_client):
        # запрос на корень
        res = flask_client.get("/")
        # Проверка статус и фреймворк в ответе
        assert res.status_code == 200 and res.json["framework"] == "Flask"

def test_dashboard_data(flask_client, mock_db_cursor):
        # Настройка последовательности вызовов
        mock_db_cursor["cursor"].fetchone.side_effect = [
            {"total": 10},  # users
            {"total": 20},  # reservations
            {"total": 15},  # confirmed
            {"total": 5},   # active tables
            None,           # конец status_rows
            None,           # конец weekday_rows
            None,           # конец popular_tables
        ]
        # fetchall для списков
        mock_db_cursor["cursor"].fetchall.side_effect = [
            [],  # reservation_statuses
            [],  # weekday_load
            [],  # popular_tables
        ]
        # запрос на получение данных дашборда
        res = flask_client.get("/api/dashboard")
        # Проверка, что запрос успешен
        assert res.status_code == 200
        # данные ответа
        data = res.json
        # Проверка на наличие ожидаемых секций
        assert "cards" in data and "charts" in data
