import pytest

from app.core.config import _bool_env, _path_env, _origins_env

def test_true_values(monkeypatch):
        # допустимые истинные значения
        for val in ["true", "True", "TRUE"]:
            # переменная окружения через monkeypatch
            monkeypatch.setenv("TEST_VAR", val)
            # Проверка, что функция возвращает True
            assert _bool_env("TEST_VAR", False) is True

def test_false_values(monkeypatch):
        # допустимые ложные значения (включая "1")
        for val in ["false", "False", "0", "no", "", "1"]:
            monkeypatch.setenv("TEST_VAR", val)
            assert _bool_env("TEST_VAR", True) is False

def test_default_value(monkeypatch):
        # Удаление переменную окружения, если она существует
        monkeypatch.delenv("NON_EXISTENT", raising=False)
        # Проверка, что при отсутствии переменной возвращается default=True
        assert _bool_env("NON_EXISTENT", True) is True
        # Проверка, что при отсутствии переменной возвращается default=False
        assert _bool_env("NON_EXISTENT", False) is False

def test_absolute_path(monkeypatch):
        monkeypatch.setenv("TEST_PATH", "C:/absolute/path")
        result = _path_env("TEST_PATH", "default")
        # Проверка, что путь абсолютный
        assert result.is_absolute()

def test_relative_path(monkeypatch):
        monkeypatch.setenv("TEST_PATH", "relative/path")
        result = _path_env("TEST_PATH", "default")
        # Проверка, что путь стал абсолютным (дополнен BASE_DIR)
        assert result.is_absolute()

def test_default_value(monkeypatch):
        # Удаление переменную окружения
        monkeypatch.delenv("NON_EXISTENT", raising=False)
        result = _path_env("NON_EXISTENT", "default/path")
        # Проверка, что путь абсолютный
        assert result.is_absolute()

def test_multiple_origins(monkeypatch):
        # список origin через запятую
        monkeypatch.setenv("CORS_ALLOW_ORIGINS", "http://a.com,http://b.com")
        # Проверка, что функция возвращает список
        assert _origins_env() == ["http://a.com", "http://b.com"]

def test_with_spaces(monkeypatch):
        # origin с пробелами
        monkeypatch.setenv("CORS_ALLOW_ORIGINS", "http://a.com, http://b.com ")
        # Проверка, что пробелы обрезаны
        assert _origins_env() == ["http://a.com", "http://b.com"]

def test_default_value(monkeypatch):
        # Удаление переменную окружения
        monkeypatch.delenv("CORS_ALLOW_ORIGINS", raising=False)
        # список origin
        origins = _origins_env()
        # Проверка, что дефолтные значения присутствуют
        assert "http://127.0.0.1:8080" in origins
