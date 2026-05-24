import pytest
import pymysql

@pytest.fixture(scope="module")
def db_connection():
    """Общее подключение к БД для всех тестов в папке"""
    conn = None
    try:
        conn = pymysql.connect(
            host='localhost', port=5432, user='root',
            password='2020Polina', database='scissors_bar'
        )
        yield conn
    except Exception as e:
        pytest.fail(f"Ошибка подключения: {e}")
    finally:
        if conn:
            conn.close()

def test_sql_injection_login_bypass(db_connection):
    """Проверка: параметризованный запрос защищает от обхода авторизации"""
    cursor = db_connection.cursor()
    malicious_input = "' OR '1'='1"
    
    cursor.execute("SELECT * FROM users WHERE email = %s", (malicious_input,))
    result = cursor.fetchall()
    
    assert len(result) == 0, "Запрос уязвим!"
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    assert total > 0, "Таблица users пуста!"

def test_sql_injection_union_attack(db_connection):
    """Проверка: защита от UNION-атаки"""
    cursor = db_connection.cursor()
    malicious_input = "' UNION SELECT password_hash, user_name, email FROM users --"
    
    cursor.execute("SELECT name FROM menu_items WHERE name = %s", (malicious_input,))
    result = cursor.fetchall()
    
    assert len(result) == 0, "UNION-атака прошла!"

def test_sql_injection_drop_table(db_connection):
    """Проверка: защита от разрушительных команд"""
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count_before = cursor.fetchone()[0]
    
    malicious_input = "'; DROP TABLE users; --"
    
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (malicious_input,))
        db_connection.commit()
    except Exception:
        db_connection.rollback()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    count_after = cursor.fetchone()[0]
    
    assert count_before == count_after, "Таблица users повреждена!"
    assert count_after > 0, "Таблица users пуста!"

def test_stored_procedure_injection(db_connection):
    """Проверка: процедура безопасно обрабатывает вредоносные данные"""
    cursor = db_connection.cursor()
    malicious_email = "test'; DROP TABLE reservations; --"
    
    cursor.execute("""
        INSERT IGNORE INTO users (id, user_name, password_hash, email) 
        VALUES (8001, 'InjectTest', 'hash', %s)
    """, (malicious_email,))
    cursor.execute("""
        INSERT IGNORE INTO tables (id, table_number, seats_count) 
        VALUES (8888, 8888, 4)
    """)
    db_connection.commit()
    
    cursor.execute("SELECT COUNT(*) FROM reservations")
    count_before = cursor.fetchone()[0]
    
    try:
        cursor.callproc('BookTable', [8888, 8001, 1, '2025-12-01 19:00:00', 2])
        db_connection.commit()
    except Exception:
        db_connection.rollback()
        pytest.fail("Процедура упала!")
    
    cursor.execute("SELECT COUNT(*) FROM reservations")
    count_after = cursor.fetchone()[0]
    
    assert count_after >= count_before, "Таблица reservations повреждена!"
    
    cursor.execute("SELECT email FROM users WHERE id = 8001")
    saved_email = cursor.fetchone()[0]
    assert saved_email == malicious_email, "Email не сохранился!"
    
    cursor.execute("DELETE FROM reservations WHERE table_id = 8888")
    cursor.execute("DELETE FROM tables WHERE id = 8888")
    cursor.execute("DELETE FROM users WHERE id = 8001")
    db_connection.commit()