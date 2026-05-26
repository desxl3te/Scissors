# Импорт стандартных модулей для работы с окружением и путями
import os  # Для работы с переменными окружения
import sys  # Для управления путями импорта модулей
import pytest  # Фреймворк для написания и запуска тестов
# Импорт модулей для работы с путями, датами и моками
from pathlib import Path  # Для кроссплатформенной работы с путями файлов
from datetime import datetime  # Для создания тестовых дат
from unittest.mock import MagicMock, patch  # Для создания мок-объектов и патчинга функций
# Импорт тестового клиента для FastAPI
from fastapi.testclient import TestClient  # Для отправки запросов к приложению в тестах

# Определяем базовую директорию проекта: родительская папка от папки test
BACKEND_DIR = Path(__file__).resolve().parents[1]
# Добавляем backend в sys.path, чтобы импорты работали корректно
sys.path.insert(0, str(BACKEND_DIR))

# Фикстура с областью видимости "сессия" (выполняется один раз на все тесты)
# autouse=True означает, что фикстура применяется автоматически ко всем тестам
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    # Сохраняем оригинальные значения переменных окружения, чтобы восстановить их после тестов
    original = {k: os.environ.get(k) for k in ["APP_TITLE", "DEBUG", "DB_HOST", "JWT_SECRET"]}
    # Устанавливаем тестовые значения переменных окружения
    os.environ.update({
        "APP_TITLE": "Test API",  # Тестовое название приложения
        "DEBUG": "True",  # Включаем режим отладки для тестов
        "DB_HOST": "127.0.0.1",  # Хост тестовой БД (локальный)
        "DB_PORT": "3306",  # Порт тестовой БД
        "DB_USER": "test",  # Пользователь тестовой БД
        "DB_PASSWORD": "test",  # Пароль тестовой БД
        "DB_NAME": "test_db",  # Имя тестовой БД
        "JWT_SECRET": "test_secret",  # Секретный ключ для тестовых JWT-токенов
        "JWT_ALGORITHM": "HS256",  # Алгоритм подписи токенов
        "CORS_ALLOW_ORIGINS": "http://test.local",  # Разрешённые CORS-источники для тестов
    })
    # Ключевое слово yield: код до yield выполняется до тестов, после — после всех тестов
    yield
    # Восстанавливаем оригинальные значения переменных окружения после завершения тестов
    for k, v in original.items():
        if v is None:  # Если переменной не было, удаляем её
            os.environ.pop(k, None)
        else:  # Если была, восстанавливаем значение
            os.environ[k] = v

# Фикстура с областью видимости "функция" (выполняется перед каждым тестом)
# autouse=True — применяется автоматически ко всем тестам
@pytest.fixture(autouse=True)
def reset_all_mocks():
    # Создаём мок-объект для курсора БД (эмулирует выполнение запросов)
    mock_cursor = MagicMock()
    # Настраиваем поведение мока: fetchone() по умолчанию возвращает None
    mock_cursor.fetchone.return_value = None
    # fetchall() по умолчанию возвращает пустой список
    mock_cursor.fetchall.return_value = []
    # lastrowid — id последней вставленной строки (для тестов создания)
    mock_cursor.lastrowid = 1
    
    # Создаём мок-объект для соединения с БД
    mock_conn = MagicMock()
    # Настраиваем метод cursor() соединения возвращать наш мок-курсор
    mock_conn.cursor.return_value = mock_cursor
    # Настраиваем контекстный менеджер __enter__ для конструкции with connection:
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    # Настраиваем контекстный менеджер __exit__
    mock_conn.__exit__ = MagicMock(return_value=False)
    
    # Используем контекстный менеджер patch для подмены реальных функций на моки
    # Патчим mysql.connector.connect — все подключения к БД будут возвращать mock_conn
    # Патчим passlib.context.CryptContext.verify — проверка пароля всегда возвращает True
    # Патчим jose.jwt.decode — декодирование токена всегда возвращает тестовый payload
    with patch("mysql.connector.connect", return_value=mock_conn), \
         patch("passlib.context.CryptContext.verify", return_value=True), \
         patch("jose.jwt.decode", return_value={"sub": "1", "email": "t@t.com", "user_name": "test"}):
        # Ключевое слово yield: возвращаем словарь с моками для использования в тестах
        yield {"cursor": mock_cursor, "conn": mock_conn}
    # После выхода из with-блока все патчи автоматически отменяются

# Фикстура для создания тестового клиента FastAPI
@pytest.fixture
def fastapi_client(reset_all_mocks):
    # Очищаем кеш импортов модулей app*, чтобы они подхватили моки заново
    for mod in list(sys.modules.keys()):
        if mod.startswith("app"):  # Если модуль из нашего проекта
            del sys.modules[mod]  # Удаляем из кеша для повторного импорта
    # Патчим функцию initialize_database, чтобы не создавать реальную БД при старте
    with patch("app.api.main.initialize_database"):
        # Импортируем приложение FastAPI (теперь с применёнными моками)
        from app.api.main import app
        # Создаём тестовый клиент и передаём управление тесту
        with TestClient(app) as client:
            yield client  # Тест получает клиент, после завершения теста клиент закрывается

# Фикстура для создания тестового клиента Flask (дашборд)
@pytest.fixture
def flask_client(reset_all_mocks):
    # Патчим функцию read_json, чтобы не читать реальные файлы конфигурации
    with patch("app.core.files.read_json", return_value={}):
        # Импортируем функцию создания Flask-приложения
        from dashboard_service.app import create_app
        # Создаём приложение
        app = create_app()
        # Включаем тестовый режим Flask
        app.config["TESTING"] = True
        # Создаём тестовый клиент Flask и передаём управление тесту
        with app.test_client() as client:
            yield client

# Фикстура-обёртка для удобного доступа к мок-курсорам в тестах
@pytest.fixture
def mock_db_cursor(reset_all_mocks):
    # Возвращаем словарь с ключом "cursor" для удобного обращения в тестах
    return {"cursor": reset_all_mocks["cursor"]}

# Фикстура с полными данными пользователя для использования в моках
@pytest.fixture
def full_user_data():
    """Полные данные пользователя для моков БД"""
    # Возвращаем словарь со всеми полями, которые требует serialize_user
    return {
        "id": 1,  # Уникальный идентификатор пользователя
        "user_name": "testuser",  # Имя пользователя
        "email": "test@example.com",  # Email пользователя
        "phone": "+1234567890",  # Телефон пользователя
        "total_visits": 0,  # Количество посещений
        "created_at": datetime(2025, 1, 1),  # Дата создания аккаунта
        "role": "customer",  # Роль пользователя
        "avatar": None,  # Ссылка на аватар (отсутствует)
        "password_hash": "mock"  # Хеш пароля (тестовый)
    }