# Импортируем pytest
import pytest

# Класс для тестов инициализации БД
class TestBootstrap:
    # Тест пропуска инициализации, если БД уже существует
    def test_initialize_database_skip_if_exists(self, mock_db_cursor):
        # Импортируем функцию инициализации внутри теста
        from app.db.bootstrap import initialize_database
        # Настраиваем мок: БД уже существует (возвращаем имя БД)
        mock_db_cursor["cursor"].fetchone.return_value = ("test_db",)
        # Вызываем функцию инициализации
        initialize_database()
        # Проверяем, что execute был вызван (проверка существования БД)
        assert mock_db_cursor["cursor"].execute.called

    # Тест ошибки при отсутствии обязательных таблиц
    def test_ensure_tables_missing(self, mock_db_cursor):
        # Импортируем функцию проверки таблиц
        from app.db.bootstrap import _ensure_tables
        # Настраиваем мок: все 5 таблиц отсутствуют (возвращаем None 5 раз)
        mock_db_cursor["cursor"].fetchone.side_effect = [None] * 5
        # Проверяем, что функция выбрасывает RuntimeError с ожидаемым сообщением
        with pytest.raises(RuntimeError, match="отсутствуют обязательные таблицы"):
            _ensure_tables()