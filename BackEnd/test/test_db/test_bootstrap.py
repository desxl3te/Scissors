import pytest

def test_initialize_database_skip_if_exists(mock_db_cursor):
        # функция инициализации внутри теста
        from app.db.bootstrap import initialize_database
        # мок: БД уже существует
        mock_db_cursor["cursor"].fetchone.return_value = ("test_db",)
        # функция инициализации
        initialize_database()
        # Проверка, что execute был вызван (проверка существования БД)
        assert mock_db_cursor["cursor"].execute.called

def test_ensure_tables_missing(mock_db_cursor):
        # функция проверки таблиц
        from app.db.bootstrap import _ensure_tables
        # мок: все 5 таблиц отсутствуют
        mock_db_cursor["cursor"].fetchone.side_effect = [None] * 5
        # Проверка, что функция выбрасывает RuntimeError с ожидаемым сообщением
        with pytest.raises(RuntimeError, match="отсутствуют обязательные таблицы"):
            _ensure_tables()
