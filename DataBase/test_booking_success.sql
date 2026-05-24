USE scissors_bar;

-- 1. Подготовить данные
INSERT IGNORE INTO users (id, user_name, password_hash, email) 
VALUES (7001, 'TestWB', 'hash', 'wb@test.com');

INSERT IGNORE INTO tables (id, table_number, seats_count) 
VALUES (7001, 7001, 4);

-- использовать title вместо name
INSERT IGNORE INTO events (id, event_date, title, event_type, start_time, price, is_active)
VALUES (999, '2025-12-01', 'Тестовое событие', 'Тест', '19:00:00', 0.00, 1);

-- 2. Вызвать процедуру (5 параметров!)
CALL BookTable(7001, 7001, 999, '2025-12-01 19:00:00', 3);

-- 3. Проверить результат
SELECT id, table_id, user_id, event_id, reservation_time, guests_count, status 
FROM reservations 
WHERE table_id = 7001;
-- Ожидаемо: 1 запись с event_id = 999

-- 4. Очистить
DELETE FROM reservations WHERE table_id = 7001;