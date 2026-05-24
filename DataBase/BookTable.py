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

def test_book_table_success(db_connection):
    """
    Успешный сценарий: все данные валидны → бронь создана
    """
    cursor = db_connection.cursor()
    
    # Подготовка: создаём тестовых пользователя и столик
    cursor.execute("""
        INSERT IGNORE INTO users (id, user_name, password_hash, email) 
        VALUES (9001, 'BookSuccess', 'hash', 'success@test.com')
    """)
    cursor.execute("""
        INSERT IGNORE INTO tables (id, table_number, seats_count) 
        VALUES (9001, 9001, 4)
    """)
    db_connection.commit()
    
    # Вызов процедуры
    cursor.callproc('BookTable', [9001, 9001, '2025-11-01 19:00:00', 3])
    db_connection.commit()
    
    # Проверка: бронь появилась
    cursor.execute("""
        SELECT id, table_id, user_id, guests_count, status 
        FROM reservations 
        WHERE table_id = 9001 AND user_id = 9001
    """)
    booking = cursor.fetchone()
    
    assert booking is not None, "  Бронь не создана!"
    assert booking[1] == 9001, f"  table_id={booking[1]}, ожидалось 9001"
    assert booking[2] == 9001, f"  user_id={booking[2]}, ожидалось 9001"
    assert booking[3] == 3, f"  guests_count={booking[3]}, ожидалось 3"
    assert booking[4] == 'confirmed', f"  status={booking[4]}, ожидалось 'confirmed'"
    
    # Очистка
    cursor.execute("DELETE FROM reservations WHERE table_id = 9001")
    cursor.execute("DELETE FROM tables WHERE id = 9001")
    cursor.execute("DELETE FROM users WHERE id = 9001")
    db_connection.commit()


def test_book_table_user_not_found(db_connection):
    """
    Ошибка: пользователь не найден → сигнал 45000
    """
    cursor = db_connection.cursor()
    
    # Столик существует, пользователя с id=99999 — нет
    cursor.execute("INSERT IGNORE INTO tables (id, table_number, seats_count) VALUES (9002, 9002, 4)")
    db_connection.commit()
    
    try:
        cursor.callproc('BookTable', [9002, 99999, '2025-11-01 19:00:00', 2])
        db_connection.commit()
        pytest.fail("  Процедура не выбросила ошибку для несуществующего пользователя!")
    except pymysql.err.OperationalError as e:
        # Ошибка 1644 = SIGNAL SQLSTATE '45000'
        assert e.args[0] == 1644, f"  Ожидалась ошибка 1644, получена {e.args[0]}"
        assert 'пользователь не найден' in str(e).lower(), f"  Текст ошибки не совпадает: {e}"
        db_connection.rollback()
    finally:
        cursor.execute("DELETE FROM tables WHERE id = 9002")
        db_connection.commit()


def test_book_table_table_not_found(db_connection):
    """
    Ошибка: столик не найден → сигнал 45000
    """
    cursor = db_connection.cursor()
    
    # Пользователь существует, столика с id=99999 — нет
    cursor.execute("""
        INSERT IGNORE INTO users (id, user_name, password_hash, email) 
        VALUES (9003, 'BookFail', 'hash', 'fail@test.com')
    """)
    db_connection.commit()
    
    try:
        cursor.callproc('BookTable', [99999, 9003, '2025-11-01 19:00:00', 2])
        db_connection.commit()
        pytest.fail("  Процедура не выбросила ошибку для несуществующего столика!")
    except pymysql.err.OperationalError as e:
        assert e.args[0] == 1644, f"  Ожидалась ошибка 1644, получена {e.args[0]}"
        assert 'столик не найден' in str(e).lower(), f"  Текст ошибки не совпадает: {e}"
        db_connection.rollback()
    finally:
        cursor.execute("DELETE FROM users WHERE id = 9003")
        db_connection.commit()


def test_book_table_already_booked(db_connection):
    """
    Ошибка: столик уже занят на это время → сигнал 45000
    """
    cursor = db_connection.cursor()
    
    # Подготовка: пользователь, столик, первая бронь
    cursor.execute("""
        INSERT IGNORE INTO users (id, user_name, password_hash, email) 
        VALUES (9004, 'UserA', 'hash', 'a@test.com'),
               (9005, 'UserB', 'hash', 'b@test.com')
    """)
    cursor.execute("""
        INSERT IGNORE INTO tables (id, table_number, seats_count) 
        VALUES (9004, 9004, 4)
    """)
    # Первая бронь (успешная)
    cursor.execute("""
        INSERT INTO reservations (table_id, user_id, reservation_time, guests_count, status)
        VALUES (9004, 9004, '2025-11-01 19:00:00', 2, 'confirmed')
    """)
    db_connection.commit()
    
    # Пытаемся забронировать тот же столик на то же время другим пользователем
    try:
        cursor.callproc('BookTable', [9004, 9005, '2025-11-01 19:00:00', 3])
        db_connection.commit()
        pytest.fail("  Процедура не выбросила ошибку для занятого времени!")
    except pymysql.err.OperationalError as e:
        assert e.args[0] == 1644, f"  Ожидалась ошибка 1644, получена {e.args[0]}"
        assert 'уже забронирован' in str(e).lower(), f"  Текст ошибки не совпадает: {e}"
        db_connection.rollback()
    finally:
        # Очистка
        cursor.execute("DELETE FROM reservations WHERE table_id = 9004")
        cursor.execute("DELETE FROM tables WHERE id = 9004")
        cursor.execute("DELETE FROM users WHERE id IN (9004, 9005)")
        db_connection.commit()


def test_book_table_invalid_guests_count(db_connection):
    """
    Проверка: отрицательное guests_count блокируется на уровне БД (CHECK constraint)
    """
    cursor = db_connection.cursor()
    
    cursor.execute("""
        INSERT IGNORE INTO users (id, user_name, password_hash, email) 
        VALUES (9006, 'GuestsTest', 'hash', 'guests@test.com')
    """)
    cursor.execute("""
        INSERT IGNORE INTO tables (id, table_number, seats_count) 
        VALUES (9006, 9006, 4)
    """)
    db_connection.commit()
    
    # Пытаемся забронировать для -5 гостей
    try:
        cursor.callproc('BookTable', [9006, 9006, '2025-11-01 19:00:00', -5])
        db_connection.commit()
        # Если код дошёл сюда — значит ограничение НЕ сработало (это баг!)
        pytest.fail("  CHECK constraint не сработал: отрицательное guests_count прошло!")
        
    except (pymysql.err.OperationalError, pymysql.err.IntegrityError) as e:
        #   Ожидаемо: либо OperationalError (код 3819), либо IntegrityError
        assert 'guests_count' in str(e).lower() or 'chk' in str(e).lower() or 'check' in str(e).lower(), \
            f"  Ошибка не связана с guests_count: {e}"
        db_connection.rollback()
        
    finally:
        # Гарантированная очистка (на случай, если запись всё же создалась)
        cursor.execute("DELETE FROM reservations WHERE table_id = 9006 AND guests_count < 0")
        cursor.execute("DELETE FROM tables WHERE id = 9006")
        cursor.execute("DELETE FROM users WHERE id = 9006")
        db_connection.commit()