import mysql.connector
from mysql.connector import Error
from datetime import datetime
from typing import List, Dict, Any, Optional

class ScissorsBarDB:
    """Класс для работы с БД бара Scissors"""
    
    def __init__(self, host: str, user: str, password: str, database: str):
        """Подключение к БД"""
        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            print("Подключение к БД успешно")
        except Error as e:
            print(f"Ошибка подключения к БД: {e}")
    
    def close(self):
        """Закрыть соединение"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 Соединение закрыто")
    
    # меню
    
    def get_all_menu(self) -> List[Dict]:
        """Получить всё меню (обычное + секретное)"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT mi.id, mi.name, c.name AS category, mi.price, mi.is_secret, mi.description
            FROM menu_items mi
            JOIN categories c ON mi.category_id = c.id
            WHERE mi.available = TRUE
        """)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_regular_menu(self) -> List[Dict]:
        """Получить обычное меню"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT mi.id, mi.name, c.name AS category, mi.price, mi.description
            FROM menu_items mi
            JOIN categories c ON mi.category_id = c.id
            WHERE mi.is_secret = FALSE AND mi.available = TRUE
        """)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_secret_menu(self) -> List[Dict]:
        """Получить секретное меню"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT mi.id, mi.name, c.name AS category, mi.price, mi.description
            FROM menu_items mi
            JOIN categories c ON mi.category_id = c.id
            WHERE mi.is_secret = TRUE AND mi.available = TRUE
        """)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_menu_by_category(self, category_name: str) -> List[Dict]:
        """Получить меню по категории (Коктейль, Шот, Закуска, Основное блюдо)"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT mi.id, mi.name, mi.price, mi.description
            FROM menu_items mi
            JOIN categories c ON mi.category_id = c.id
            WHERE c.name = %s AND mi.is_secret = FALSE AND mi.available = TRUE
        """, (category_name,))
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_menu_item_by_id(self, item_id: int) -> Optional[Dict]:
        """Получить блюдо по ID"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT mi.id, mi.name, c.name AS category, mi.price, mi.is_secret, mi.description
            FROM menu_items mi
            JOIN categories c ON mi.category_id = c.id
            WHERE mi.id = %s
        """, (item_id,))
        result = cursor.fetchone()
        cursor.close()
        return result
    
    # столики
    
    def get_all_tables(self) -> List[Dict]:
        """Получить все столики"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT id, table_number, seats_count, is_active FROM tables WHERE is_active = TRUE")
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_table_by_id(self, table_id: int) -> Optional[Dict]:
        """Получить столик по ID"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT id, table_number, seats_count FROM tables WHERE id = %s", (table_id,))
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def get_free_tables(self, reservation_time: datetime, guests_count: int = None) -> List[Dict]:
        """Получить свободные столики на конкретное время"""
        cursor = self.connection.cursor(dictionary=True)
        query = """
            SELECT t.id, t.table_number, t.seats_count
            FROM tables t
            WHERE t.is_active = TRUE
              AND t.id NOT IN (
                  SELECT table_id FROM reservations 
                  WHERE reservation_time = %s AND status = 'confirmed'
              )
        """
        params = [reservation_time]
        
        if guests_count:
            query += " AND t.seats_count >= %s"
            params.append(guests_count)
        
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    # пользователи
    
    def register_user(self, user_name: str, password: str, email: str, phone: str) -> Optional[int]:
        """Регистрация нового пользователя"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (user_name, password_hash, email, phone, role)
                VALUES (%s, SHA2(%s, 256), %s, %s, 'customer')
            """, (user_name, password, email, phone))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Ошибка регистрации: {e}")
            return None
        finally:
            cursor.close()
    
    def login_user(self, user_name: str, password: str) -> Optional[Dict]:
        """Авторизация пользователя"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, user_name, email, phone, role, total_visits
            FROM users
            WHERE user_name = %s AND password_hash = SHA2(%s, 256) AND is_active = TRUE
        """, (user_name, password))
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Получить пользователя по ID"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, user_name, email, phone, role, total_visits, created_at
            FROM users WHERE id = %s
        """, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def update_user_visits(self, user_id: int):
        """Увеличить счётчик визитов пользователя"""
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET total_visits = total_visits + 1 WHERE id = %s", (user_id,))
        self.connection.commit()
        cursor.close()
    
    # бронивароавние
    
    def book_table(self, table_id: int, user_id: int, reservation_time: datetime, guests_count: int) -> Dict:
        """Забронировать столик (броьн через хранимую процедуру)"""
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.callproc('BookTable', (table_id, user_id, reservation_time, guests_count))
            for result in cursor.stored_results():
                new_id = result.fetchone()
                self.connection.commit()
                return {"success": True, "reservation_id": new_id['new_reservation_id']}
        except Error as e:
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
    
    def get_user_reservations(self, user_id: int) -> List[Dict]:
        """Получить все брони пользователя"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.id, r.table_id, t.table_number, r.reservation_time, 
                   r.guests_count, r.status, r.special_request
            FROM reservations r
            JOIN tables t ON r.table_id = t.id
            WHERE r.user_id = %s
            ORDER BY r.reservation_time DESC
        """, (user_id,))
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def cancel_reservation(self, reservation_id: int, user_id: int) -> bool:
        """Отменить бронь (только свою)"""
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE reservations 
            SET status = 'cancelled'
            WHERE id = %s AND user_id = %s AND status = 'confirmed'
        """, (reservation_id, user_id))
        self.connection.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected > 0
    
    def get_reservations_by_table(self, table_id: int) -> List[Dict]:
        """Получить все брони столика"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.id, u.user_name, r.reservation_time, r.guests_count, r.status
            FROM reservations r
            JOIN users u ON r.user_id = u.id
            WHERE r.table_id = %s
            ORDER BY r.reservation_time DESC
        """, (table_id,))
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def check_table_available(self, table_id: int, reservation_time: datetime) -> bool:
        """Проверить, свободен ли столик в указанное время"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM reservations
            WHERE table_id = %s AND reservation_time = %s AND status = 'confirmed'
        """, (table_id, reservation_time))
        count = cursor.fetchone()[0]
        cursor.close()
        return count == 0
    
    # аналитика
    
    def get_popular_tables(self) -> List[Dict]:
        """Самые популярные столики"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.table_number, COUNT(r.id) AS total_bookings
            FROM tables t
            LEFT JOIN reservations r ON t.id = r.table_id
            GROUP BY t.id, t.table_number
            ORDER BY total_bookings DESC
        """)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_popular_weekday(self) -> List[Dict]:
        """Самый популярный день недели для броней"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT DAYNAME(reservation_time) AS weekday, COUNT(*) AS bookings
            FROM reservations
            GROUP BY weekday
            ORDER BY bookings DESC
        """)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_avg_guests(self) -> float:
        """Среднее количество гостей на бронь"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT ROUND(AVG(guests_count)) FROM reservations")
        result = cursor.fetchone()[0]
        cursor.close()
        return result if result else 0
    
    def get_reservations_stats(self) -> Dict:
        """Статистика по броням (общее количество, по статусам)"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed
            FROM reservations
        """)
        result = cursor.fetchone()
        cursor.close()
        return result
    
    # смена аватарки и ника у пользователя

    def update_username(self, user_id: int, new_username: str) -> Dict:
        """Изменить имя пользователя (ник)"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("UPDATE users SET user_name = %s WHERE id = %s", (new_username, user_id))
            self.connection.commit()
            return {"success": True, "message": "Имя успешно изменено"}
        except Error as e:
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
    
    def update_avatar(self, user_id: int, avatar_url: str) -> Dict:
        """Обновить аватарку пользователя (сохраняем URL или путь к файлу)"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("UPDATE users SET avatar = %s WHERE id = %s", (avatar_url, user_id))
            self.connection.commit()
            return {"success": True, "message": "Аватарка успешно обновлена", "avatar": avatar_url}
        except Error as e:
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
    
    # доп
    
    def get_menu_categories(self) -> List[Dict]:
        """Получить все категории меню"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories")
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def search_menu_items(self, search_term: str) -> List[Dict]:
        """Поиск блюд по названию или описанию"""
        cursor = self.connection.cursor(dictionary=True)
        query = "%{}%".format(search_term)
        cursor.execute("""
            SELECT mi.id, mi.name, c.name AS category, mi.price, mi.description
            FROM menu_items mi
            JOIN categories c ON mi.category_id = c.id
            WHERE mi.name LIKE %s OR mi.description LIKE %s
        """, (query, query))
        result = cursor.fetchall()
        cursor.close()
        return result