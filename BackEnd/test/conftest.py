import os  # Для работы с переменными окружения
import sys  # Для управления путями импорта модулей
import pytest  # Фреймворк для написания и запуска тестов
from pathlib import Path  # Для кроссплатформенной работы с путями файлов
from datetime import datetime  # Для создания тестовых дат
from unittest.mock import MagicMock, patch  # Для создания мок-объектов и патчинга функций
from fastapi.testclient import TestClient  # Для отправки запросов к приложению в тестах

# директорий проекта: родительская папка от папки test
BACKEND_DIR = Path(__file__).resolve().parents[1]
# backend в sys.path для корректной работы импортов
sys.path.insert(0, str(BACKEND_DIR))

# autouse=True - применяется автоматически ко всем тестам
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    # сохранение чтобы восстановить все после тестов
    original = {k: os.environ.get(k) for k in ["APP_TITLE", "DEBUG", "DB_HOST", "JWT_SECRET"]}
    # тестовые значения
    os.environ.update({
        "APP_TITLE": "Test API",  
        "DEBUG": "True",  
        "DB_HOST": "127.0.0.1",  
        "DB_PORT": "3306",  
        "DB_USER": "test",  
        "DB_PASSWORD": "test",  
        "DB_NAME": "test_db",  
        "JWT_SECRET": "test_secret",  
        "JWT_ALGORITHM": "HS256",  
        "CORS_ALLOW_ORIGINS": "http://test.local",  
    })
    # yield: код до yield выполняется до тестов, после — после всех тестов
    yield
    # восстановление оригинальных значений переменных окружения после завершения тестов
    for k, v in original.items():
        if v is None: 
            os.environ.pop(k, None)
        else: 
            os.environ[k] = v

@pytest.fixture(autouse=True)
def reset_all_mocks():
    # мок-объект для курсора БД (эмитирует выполнение запросов)
    mock_cursor = MagicMock()
    # мок по умолчанию возвращает None
    mock_cursor.fetchone.return_value = None
    # fetchall() по умолчанию возвращает пустой список
    mock_cursor.fetchall.return_value = []
    # id последней вставленной строки
    mock_cursor.lastrowid = 1
    
    # мок-объект для соединения с БД
    mock_conn = MagicMock()
    # Настраиваем метод cursor() соединения возвращать наш мок-курсор
    mock_conn.cursor.return_value = mock_cursor
    # Настраиваем контекстный менеджер __enter__ для конструкции with connection:
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    # Настраиваем контекстный менеджер __exit__
    mock_conn.__exit__ = MagicMock(return_value=False)
    
    # patch для подмены реальных функций на моки
    with patch("mysql.connector.connect", return_value=mock_conn), \
         patch("passlib.context.CryptContext.verify", return_value=True), \
         patch("jose.jwt.decode", return_value={"sub": "1", "email": "t@t.com", "user_name": "test"}):
        yield {"cursor": mock_cursor, "conn": mock_conn}
    # после выхода из with-блока все патчи автоматически отменяются

# создание тестового клиента FastAPI
@pytest.fixture
def fastapi_client(reset_all_mocks):
    # очистка кэша
    for mod in list(sys.modules.keys()):
        if mod.startswith("app"): 
            del sys.modules[mod]  
    # initialize_database, чтобы не создавать реальную БД при старте
    with patch("app.api.main.initialize_database"):
        from app.api.main import app
        with TestClient(app) as client:
            yield client  # тест получает клиент, после завершения теста клиент закрывается

# создание тестового клиента Flask (дашборд)
@pytest.fixture
def flask_client(reset_all_mocks):
    with patch("app.core.files.read_json", return_value={}):
        from dashboard_service.app import create_app
        app = create_app()
        app.config["TESTING"] = True
        # создание тестового клиента Flask и передача управления тесту
        with app.test_client() as client:
            yield client

# фикстура-обёртка для удобного доступа к мок-курсорам в тестах
@pytest.fixture
def mock_db_cursor(reset_all_mocks):
    # словарь с ключом "cursor" для удобного обращения в тестах
    return {"cursor": reset_all_mocks["cursor"]}

# фикстура с полными данными пользователя для использования в моках
@pytest.fixture
def full_user_data():
    """Полные данные пользователя для моков БД"""
    # словарь со всеми полями, которые требует serialize_user
    return {
        "id": 1, 
        "user_name": "testuser", 
        "email": "test@example.com", 
        "phone": "+1234567890",  
        "total_visits": 0, 
        "created_at": datetime(2025, 1, 1), 
        "role": "customer",  
        "avatar": None, 
        "password_hash": "mock" 
    }