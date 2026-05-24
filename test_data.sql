USE scissors_bar;

-- добавление тестового пользователя
INSERT IGNORE INTO users (id, user_name, password_hash, email, phone, avatar, role) 
VALUES (1, 'test_user', SHA2('123456', 256), 'test@scissors.bar', '+79991234567', 'https://example.com/avatar.jpg', 'customer');

-- очистка старых тестовых броней
SET SQL_SAFE_UPDATES = 0;
DELETE FROM reservations WHERE user_id = 1 AND reservation_time < NOW();
SET SQL_SAFE_UPDATES = 1;

-- добавление тестовых броней
INSERT INTO reservations (table_id, user_id, event_id, reservation_time, duration_hours, guests_count, status) VALUES
(1, 1, NULL, '2026-04-10 18:00:00', 2, 2, 'confirmed'),
(1, 1, NULL, '2026-04-15 19:00:00', 1,  2, 'confirmed'),
(1, 1, NULL, '2026-04-20 20:00:00', 3, 2, 'confirmed'),
(2, 1, NULL, '2026-04-11 19:00:00', 2, 4, 'confirmed'),
(2, 1, NULL, '2026-04-18 18:30:00', 2, 2, 'confirmed'),
(3, 1, NULL, '2026-04-12 20:00:00', 3, 4, 'confirmed'),
(3, 1, NULL, '2026-04-19 19:00:00', 4, 4, 'confirmed'),
(3, 1, NULL, '2026-04-25 21:00:00', 1, 3, 'confirmed'),
(4, 1, NULL, '2026-04-13 18:00:00', 1, 2, 'confirmed'),
(5, 1, NULL, '2026-04-14 19:30:00', 3, 5, 'confirmed'),
(6, 1, NULL, '2026-04-21 20:30:00', 4, 6, 'cancelled');