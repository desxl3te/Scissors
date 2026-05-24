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
        pytest.fail(f"  Ошибка подключения: {e}")
    finally:
        if conn:
            conn.close()

def test_sql_injection_login_bypass(db_connection):
    """
    Проверка: параметризованный запрос защищает от обхода авторизации
    Атака: ' OR '1'='1
    """
    cursor = db_connection.cursor()
    
    # Опасная строка, которая в не параметризованном запросе вернула бы ВСЕХ пользователей
    malicious_input = "' OR '1'='1"
    
    #  БЕЗОПАСНО: параметризованный запрос (знак %s)
    cursor.execute("SELECT * FROM users WHERE email = %s", (malicious_input,))
    result = cursor.fetchall()
    
    # Ожидаемо: 0 записей (такого email не существует)
    #   Если бы запрос был строковым: f"SELECT ... WHERE email = '{malicious_input}'", 
    #    то вернулись бы ВСЕ пользователи базы!
    assert len(result) == 0, "  Запрос уязвим: вернул данные при инъекции!"
    
    # Дополнительно: убедимся, что таблица не была повреждена
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    assert total > 0, " Таблица users пуста или была удалена!"


def test_sql_injection_union_attack(db_connection):
    """
    Проверка: защита от UNION-атаки (попытка вытянуть данные из других таблиц)
    Атака: ' UNION SELECT password_hash, user_name, email FROM users --
    """
    cursor = db_connection.cursor()
    
    malicious_input = "' UNION SELECT password_hash, user_name, email FROM users --"
    
    # Параметризованный запрос ищет буквальное совпадение строки
    cursor.execute("SELECT name FROM menu_items WHERE name = %s", (malicious_input,))
    result = cursor.fetchall()
    
    assert len(result) == 0, "  UNION-атака прошла: получены данные из других таблиц!"


def test_sql_injection_drop_table(db_connection):
    """
    Проверка: защита от разрушительных команд (DROP, DELETE, UPDATE)
    Атака: '; DROP TABLE users; --
    """
    cursor = db_connection.cursor()
    
    # Запоминаем, сколько пользователей было ДО теста
    cursor.execute("SELECT COUNT(*) FROM users")
    count_before = cursor.fetchone()[0]
    
    malicious_input = "'; DROP TABLE users; --"
    
    try:
        # Пытаемся "выполнить" вредоносный код через параметр
        cursor.execute("SELECT * FROM users WHERE email = %s", (malicious_input,))
        db_connection.commit()
    except Exception:
        db_connection.rollback()
    
    # Проверяем, что таблица на месте и данные не потеряны
    cursor.execute("SELECT COUNT(*) FROM users")
    count_after = cursor.fetchone()[0]
    
    assert count_before == count_after, "  Таблица users была повреждена или удалена!"
    assert count_after > 0, "  Таблица users пуста!"


def test_stored_procedure_injection(db_connection):
    """
    Проверка: процедура безопасно обрабатывает вредоносные данные,
    сохраняет их как текст и не выполняет SQL-код.
    """
    cursor = db_connection.cursor()
    malicious_email = "test'; DROP TABLE reservations; --"
    
    # 1. Подготовка: пользователь с "опасным" email и тестовый столик
    cursor.execute("""
        INSERT IGNORE INTO users (id, user_name, password_hash, email) 
        VALUES (8001, 'InjectTest', 'hash', %s)
    """, (malicious_email,))
    cursor.execute("""
        INSERT IGNORE INTO tables (id, table_number, seats_count) 
        VALUES (8888, 8888, 4)
    """)
    db_connection.commit()
    
    # 2. Фиксируем состояние ДО
    cursor.execute("SELECT COUNT(*) FROM reservations")
    count_before = cursor.fetchone()[0]
    
    # 3. Вызываем процедуру (она создаст бронь, это нормально)
    try:
        cursor.callproc('BookTable', [8888, 8001, '2025-12-01 19:00:00', 2])
        db_connection.commit()
    except Exception:
        db_connection.rollback()
        pytest.fail("  Процедура упала при вызове с вредоносными данными!")
        
    # 4. Проверки безопасности
    cursor.execute("SELECT COUNT(*) FROM reservations")
    count_after = cursor.fetchone()[0]
    
    # Таблица НЕ должна была удалиться (DROP не сработал)
    assert count_after >= count_before, " Таблица reservations была повреждена или удалена!"
    
    # Вредоносная строка должна сохраниться как ОБЫЧНЫЙ ТЕКСТ
    cursor.execute("SELECT email FROM users WHERE id = 8001")
    saved_email = cursor.fetchone()[0]
    assert saved_email == malicious_email, " Email изменился или не сохранился как текст!"
    
    # 5. Очистка
    cursor.execute("DELETE FROM reservations WHERE table_id = 8888")
    cursor.execute("DELETE FROM tables WHERE id = 8888")
    cursor.execute("DELETE FROM users WHERE id = 8001")
    db_connection.commit()