import pytest
import pymysql
from datetime import datetime

# ФИКСТУРА ПОДКЛЮЧЕНИЯ
@pytest.fixture(scope="module")
def db_connection():
    conn = None
    try:
        conn = pymysql.connect(
            host='localhost', port=5432, user='root',
            password='2020Polina', database='scissors_bar'
        )
        yield conn
    except Exception as e:
        pytest.fail(f" Ошибка подключения: {e}")
    finally:
        if conn:
            conn.close()


#  ТЕСТЫ

# 1. Обычное меню
def test_ordinary_menu(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM menu_items WHERE name LIKE 'Тест_%'")
    db_connection.commit()

    cursor.execute("""
        INSERT INTO menu_items (name, category_id, price, is_secret)
        VALUES ('Тест_Обычный1', 1, 350.00, 0),
               ('Тест_Обычный2', 1, 200.00, 0),
               ('Тест_Секретный', 1, 500.00, 1)
    """)
    db_connection.commit()

    cursor.execute("SELECT name, is_secret FROM menu_items WHERE is_secret = FALSE")
    names = [row[0] for row in cursor.fetchall()]

    assert 'Тест_Обычный1' in names, "Обычное блюдо 1 не найдено"
    assert 'Тест_Обычный2' in names, "Обычное блюдо 2 не найдено"
    assert 'Тест_Секретный' not in names, "Секретное блюдо ошибочно попало в выдачу!"

    cursor.execute("DELETE FROM menu_items WHERE name LIKE 'Тест_%'")
    db_connection.commit()

# 2. Секретное меню
def test_secret_menu(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM menu_items WHERE name LIKE 'Тест_%'")
    db_connection.commit()

    cursor.execute("""
        INSERT INTO menu_items (name, category_id, price, is_secret)
        VALUES ('Тест_Секрет1', 1, 5000.00, 1),
               ('Тест_Секрет2', 1, 1500.00, 1),
               ('Тест_Обычный', 1, 200.00, 0)
    """)
    db_connection.commit()

    cursor.execute("SELECT name, is_secret FROM menu_items WHERE is_secret = TRUE")
    names = [row[0] for row in cursor.fetchall()]

    assert 'Тест_Секрет1' in names, "Секретное блюдо 1 не найдено"
    assert 'Тест_Секрет2' in names, "Секретное блюдо 2 не найдено"
    assert 'Тест_Обычный' not in names, "Обычное блюдо ошибочно попало в секретную выдачу!"

    cursor.execute("DELETE FROM menu_items WHERE name LIKE 'Тест_%'")
    db_connection.commit()

# 3. Все столики
def test_all_tables(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("INSERT IGNORE INTO tables (table_number, seats_count, is_active) VALUES (901, 4, 1), (902, 2, 0)")
    db_connection.commit()

    cursor.execute("SELECT table_number FROM tables WHERE table_number IN (901, 902)")
    found = [row[0] for row in cursor.fetchall()]
    assert 901 in found and 902 in found, "Тестовые столики не найдены"

    cursor.execute("DELETE FROM tables WHERE table_number IN (901, 902)")
    db_connection.commit()

# 4. Свободные столики на 19:00
def test_free_tables_at_time(db_connection):
    cursor = db_connection.cursor()
    target_time = '2025-04-15 19:00:00'
    
    cursor.execute("INSERT IGNORE INTO users (id, user_name, password_hash, email) VALUES (9998, 'Test', 'h', 't@m')")
    cursor.execute("INSERT INTO tables (id, table_number, seats_count) VALUES (801, 801, 2), (802, 802, 4), (803, 803, 6)")
    
    # Вставляем брони одной командой (без переносов строки внутри скобок)
    cursor.execute(f"INSERT INTO reservations (table_id, user_id, reservation_time, guests_count, status) VALUES (802, 9998, '{target_time}', 2, 'confirmed')")
    cursor.execute("INSERT INTO reservations (table_id, user_id, reservation_time, guests_count, status) VALUES (803, 9998, '2025-04-15 20:00:00', 2, 'confirmed')")
    db_connection.commit()

    cursor.execute(f"""SELECT table_number FROM tables WHERE id NOT IN (
        SELECT table_id FROM reservations WHERE reservation_time = '{target_time}' AND status = 'confirmed')""")
    free = [row[0] for row in cursor.fetchall()]

    assert 801 in free and 803 in free, "Свободные столики должны быть в списке"
    assert 802 not in free, "Занятый столик не должен быть в списке"

    cursor.execute("DELETE FROM reservations WHERE table_id IN (801, 802, 803)")
    cursor.execute("DELETE FROM tables WHERE id IN (801, 802, 803)")
    cursor.execute("DELETE FROM users WHERE id = 9998")
    db_connection.commit()

# 5. Брони пользователя id=1
def test_user_reservations(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("INSERT IGNORE INTO users (id, user_name, password_hash, email) VALUES (1, 'Admin', 'h', 'a@b.c')")
    cursor.execute("INSERT INTO tables (id, table_number, seats_count) VALUES (701, 701, 4), (702, 702, 2)")
    
    # Исправлена длинная строка (убраны переносы внутри строки)
    cursor.execute("""INSERT INTO reservations (table_id, user_id, reservation_time, guests_count, status) VALUES (701, 1, '2025-04-15 19:00:00', 2, 'confirmed'), (702, 1, '2025-04-16 20:00:00', 4, 'confirmed')""")
    db_connection.commit()

    cursor.execute("SELECT user_id FROM reservations WHERE table_id IN (701, 702)")
    users = [row[0] for row in cursor.fetchall()]
    assert all(u == 1 for u in users), "Все брони должны принадлежать user_id=1"

    cursor.execute("DELETE FROM reservations WHERE table_id IN (701, 702)")
    cursor.execute("DELETE FROM tables WHERE id IN (701, 702)")
    db_connection.commit()

# 6. Проверка столика 3 и времени 20:00
def test_specific_table_time_check(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("INSERT IGNORE INTO users (id, user_name, password_hash, email) VALUES (9997, 'U2', 'h', 'u@m')")
    
    # Исправлена длинная строка
    cursor.execute("""INSERT INTO reservations (table_id, user_id, reservation_time, guests_count, status) VALUES (3, 9997, '2025-04-15 20:00:00', 3, 'confirmed'), (3, 9997, '2025-04-15 19:00:00', 2, 'confirmed'), (4, 9997, '2025-04-15 20:00:00', 1, 'confirmed')""")
    db_connection.commit()

    cursor.execute("SELECT table_id FROM reservations WHERE table_id = 3 AND reservation_time = '2025-04-15 20:00:00'")
    res = cursor.fetchall()
    assert len(res) == 1 and res[0][0] == 3, "Должна быть ровно 1 запись для столика 3 в 20:00"

    cursor.execute("DELETE FROM reservations WHERE (table_id=3 AND reservation_time='2025-04-15 20:00:00') OR (table_id=3 AND reservation_time='2025-04-15 19:00:00') OR (table_id=4 AND reservation_time='2025-04-15 20:00:00')")
    cursor.execute("DELETE FROM users WHERE id = 9997")
    db_connection.commit()