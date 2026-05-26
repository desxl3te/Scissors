# Импортируем pytest и функции из config.py
import pytest
from app.core.config import _bool_env, _path_env, _origins_env

# Класс для тестов хелпер-функций конфигурации
class TestBoolEnv:
    # Тест истинных значений для _bool_env
    def test_true_values(self, monkeypatch):
        # Перебираем допустимые истинные значения
        for val in ["true", "True", "TRUE"]:
            # Устанавливаем переменную окружения через monkeypatch
            monkeypatch.setenv("TEST_VAR", val)
            # Проверяем, что функция возвращает True
            assert _bool_env("TEST_VAR", False) is True

    # Тест ложных значений для _bool_env
    def test_false_values(self, monkeypatch):
        # Перебираем допустимые ложные значения (включая "1")
        for val in ["false", "False", "0", "no", "", "1"]:
            monkeypatch.setenv("TEST_VAR", val)
            assert _bool_env("TEST_VAR", True) is False

    # Тест значения по умолчанию для _bool_env
    def test_default_value(self, monkeypatch):
        # Удаляем переменную окружения, если она существует
        monkeypatch.delenv("NON_EXISTENT", raising=False)
        # Проверяем, что при отсутствии переменной возвращается default=True
        assert _bool_env("NON_EXISTENT", True) is True
        # Проверяем, что при отсутствии переменной возвращается default=False
        assert _bool_env("NON_EXISTENT", False) is False

# Класс для тестов _path_env
class TestPathEnv:
    # Тест абсолютного пути
    def test_absolute_path(self, monkeypatch):
        # Устанавливаем абсолютный путь
        monkeypatch.setenv("TEST_PATH", "C:/absolute/path")
        # Вызываем функцию
        result = _path_env("TEST_PATH", "default")
        # Проверяем, что путь абсолютный
        assert result.is_absolute()

    # Тест относительного пути
    def test_relative_path(self, monkeypatch):
        # Устанавливаем относительный путь
        monkeypatch.setenv("TEST_PATH", "relative/path")
        result = _path_env("TEST_PATH", "default")
        # Проверяем, что путь стал абсолютным (дополнен BASE_DIR)
        assert result.is_absolute()

    # Тест значения по умолчанию для пути
    def test_default_value(self, monkeypatch):
        # Удаляем переменную окружения
        monkeypatch.delenv("NON_EXISTENT", raising=False)
        result = _path_env("NON_EXISTENT", "default/path")
        # Проверяем, что путь абсолютный
        assert result.is_absolute()

# Класс для тестов _origins_env
class TestOriginsEnv:
    # Тест множественных origin
    def test_multiple_origins(self, monkeypatch):
        # Устанавливаем список origin через запятую
        monkeypatch.setenv("CORS_ALLOW_ORIGINS", "http://a.com,http://b.com")
        # Проверяем, что функция возвращает список
        assert _origins_env() == ["http://a.com", "http://b.com"]

    # Тест origin с пробелами
    def test_with_spaces(self, monkeypatch):
        # Устанавливаем origin с пробелами
        monkeypatch.setenv("CORS_ALLOW_ORIGINS", "http://a.com, http://b.com ")
        # Проверяем, что пробелы обрезаны
        assert _origins_env() == ["http://a.com", "http://b.com"]

    # Тест значения по умолчанию для origin
    def test_default_value(self, monkeypatch):
        # Удаляем переменную окружения
        monkeypatch.delenv("CORS_ALLOW_ORIGINS", raising=False)
        # Получаем список origin
        origins = _origins_env()
        # Проверяем, что дефолтные значения присутствуют
        assert "http://127.0.0.1:8080" in origins