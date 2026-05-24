import pytest
import pymysql
from pymysql import Error

#  КОНФИГУРАЦИЯ
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,          
    'user': 'root',
    'password': '2020Polina',
    'database': 'scissors_bar'
}

@pytest.fixture(scope="module")
def db_connection():
    """Подключение к БД"""
    conn = None
    try:
        # Используем pymysql вместо mysql.connector
        conn = pymysql.connect(**DB_CONFIG)
        yield conn
    except Error as e:
        pytest.fail(f" Ошибка подключения: {e}")
    finally:
        if conn:
            conn.close()

# --- ТЕСТЫ ---

def test_connection_active(db_connection):
    assert db_connection.open, " База недоступна"

def test_tables_exist(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    required = ['users', 'tables', 'reservations', 'menu_items', 'categories']
    for t in required:
        assert t in tables, f" Таблица {t} отсутствует!"

def test_unique_email(db_connection):
    cursor = db_connection.cursor()
    test_email = f"unique_test_{id(db_connection)}@mail.com"
    try:
        cursor.execute("INSERT INTO users (user_name, password_hash, email) VALUES ('User1', 'hash', %s)", (test_email,))
        db_connection.commit()
        cursor.execute("INSERT INTO users (user_name, password_hash, email) VALUES ('User2', 'hash', %s)", (test_email,))
        db_connection.commit()
        pytest.fail(" UNIQUE constraint для email не сработал!")
    except Error:
        db_connection.rollback()
        assert True
    finally:
        cursor.execute("DELETE FROM users WHERE email = %s", (test_email,))
        db_connection.commit()

def test_check_price(db_connection):
    cursor = db_connection.cursor()
    try:
        cursor.execute("INSERT INTO menu_items (name, category, price) VALUES ('BadItem', 'Коктейль', -50.00)")
        db_connection.commit()
        pytest.fail(" CHECK (price >= 0) не сработал!")
    except Error:
        assert True
    finally:
        cursor.execute("DELETE FROM menu_items WHERE name = 'BadItem' AND price < 0")
        db_connection.commit()

def test_foreign_key_orders(db_connection):
    cursor = db_connection.cursor()
    try:
        cursor.execute("INSERT INTO orders (reservation_id, status) VALUES (99999, 'open')")
        db_connection.commit()
        pytest.fail(" Foreign Key для orders не сработал!")
    except Error:
        assert True
    except Error as e:
        pytest.skip("️ Таблица orders ещё не создана")

def test_default_role(db_connection):
    cursor = db_connection.cursor()
    test_email = "default_role_test@mail.com"
    cursor.execute("INSERT INTO users (user_name, password_hash, email) VALUES ('RoleTest', 'hash', %s)", (test_email,))
    db_connection.commit()
    cursor.execute("SELECT role FROM users WHERE email = %s", (test_email,))
    role = cursor.fetchone()[0]
    assert role == 'customer', f" Роль по умолчанию '{role}', ожидалось 'customer'"
    cursor.execute("DELETE FROM users WHERE email = %s", (test_email,))
    db_connection.commit()

def test_transaction_rollback(db_connection):
    cursor = db_connection.cursor()
    test_email = "rollback_test@mail.com"
    cursor.execute("START TRANSACTION")
    cursor.execute("INSERT INTO users (user_name, password_hash, email) VALUES ('Rollback', 'hash', %s)", (test_email,))
    cursor.execute("ROLLBACK")
    cursor.execute("SELECT * FROM users WHERE email = %s", (test_email,))
    result = cursor.fetchone()
    assert result is None, " Транзакция не откатилась!"
    # pytest autho_test.py -v