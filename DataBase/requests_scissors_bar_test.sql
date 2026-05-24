USE scissors_bar;

-- обычное меню 
SELECT * FROM menu_items WHERE is_secret = FALSE;

-- секретное меню 
SELECT * FROM menu_items WHERE is_secret = TRUE;

-- все столики
SELECT * FROM tables;

-- свободные столики на 19:00
SELECT * FROM tables 
WHERE id NOT IN (
    SELECT table_id FROM reservations 
    WHERE reservation_time = '2025-04-15 19:00:00'
      AND status = 'confirmed'
);

-- бронирования пользователя с id = 1
SELECT * FROM reservations WHERE user_id = 1;

-- проверка столика 3 на 20:00
SELECT * FROM reservations 
WHERE table_id = 3 AND reservation_time = '2025-04-15 20:00:00';








-- ===== ТЕСТ: Свободные столики на 19:00 =====
-- 1. Подготовка
INSERT INTO tables (id, table_number, seats_count) VALUES
  (301, 301, 2), (302, 302, 4), (303, 303, 6);
INSERT INTO reservations (table_id, user_id, reservation_time, guests_count, status) VALUES
  (302, 1, '2025-04-15 19:00:00', 3, 'confirmed');

-- 2. Запрос
SELECT * FROM tables 
WHERE id NOT IN (
    SELECT table_id FROM reservations 
    WHERE reservation_time = '2025-04-15 19:00:00' AND status = 'confirmed'
);

-- 3. Проверка: в результате должны быть 301 и 303, но НЕ 302

-- 4. Очистка
DELETE FROM reservations WHERE table_id IN (301,302,303);
DELETE FROM tables WHERE id IN (301,302,303);