USE scissors_bar;

-- Количество броней по каждому столику
SELECT table_id, COUNT(*) AS total_reservations
FROM reservations
GROUP BY table_id
ORDER BY total_reservations DESC;

-- Самый популярный день недели для броней
SELECT 
    DAYNAME(reservation_time) AS weekday,
    COUNT(*) AS bookings
FROM reservations
GROUP BY weekday
ORDER BY bookings DESC;

-- Среднее количество гостей за одну бронь
SELECT AVG(guests_count) AS avg_guests_per_booking
FROM reservations;

-- Бронь с максимальным количеством гостей
SELECT * FROM reservations
ORDER BY guests_count DESC
LIMIT 1;

-- Количество броней по статусам
SELECT status, COUNT(*) AS count
FROM reservations
GROUP BY status;

-- Самый популярный столик (по количеству броней)
SELECT table_id, COUNT(*) AS bookings
FROM reservations
GROUP BY table_id
ORDER BY bookings DESC
LIMIT 1;

-- Есть ли пользователь с id = 1
INSERT IGNORE INTO users (id, user_name, password_hash, email, phone) 
VALUES (1, 'test_user', 'dummy_hash', 'test@scissors.bar', '+79991234567');

-- Очистка старых тестовых броней, чтобы не было дубль-броней
DELETE FROM reservations WHERE user_id = 1 AND reservation_time < NOW();

-- Добавление тестовых броней на разные дни и столики
INSERT INTO reservations (table_id, user_id, reservation_time, guests_count, status) VALUES
(1, 1, '2025-04-10 18:00:00', 2, 'confirmed'),
(1, 1, '2025-04-15 19:00:00', 2, 'confirmed'),
(1, 1, '2025-04-20 20:00:00', 3, 'confirmed'),
(2, 1, '2025-04-11 19:00:00', 4, 'confirmed'),
(2, 1, '2025-04-18 18:30:00', 2, 'confirmed'),
(3, 1, '2025-04-12 20:00:00', 6, 'confirmed'),
(3, 1, '2025-04-19 19:00:00', 4, 'confirmed'),
(3, 1, '2025-04-25 21:00:00', 5, 'confirmed'),
(4, 1, '2025-04-13 18:00:00', 2, 'confirmed'),
(5, 1, '2025-04-14 19:30:00', 8, 'confirmed'),
(5, 1, '2025-04-21 20:00:00', 6, 'cancelled');
