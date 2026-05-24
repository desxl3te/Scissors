-- 1. Очистка
DELETE FROM reservations WHERE table_id = 7001;
DELETE FROM tables WHERE id = 7001;
DELETE FROM users WHERE id = 7001;

-- 2. Вставка (без ошибок)
INSERT INTO users (id, user_name, password_hash, email) 
VALUES (7001, 'User1', 'hash', 'u1@test.com');

INSERT INTO tables (id, table_number, seats_count) 
VALUES (7001, 7001, 4);

-- 3. Первая бронь
INSERT INTO reservations (table_id, user_id, event_id, reservation_time, guests_count, status)
VALUES (7001, 7001, 1, '2025-12-01 19:00:00', 2, 'confirmed');

-- 4. Попытка второй брони (должна упасть с ошибкой 1644)
CALL BookTable(7001, 7002, 1, '2025-12-01 19:00:00', 3);

-- 5. Финальная очистка
DELETE FROM reservations WHERE table_id = 7001;