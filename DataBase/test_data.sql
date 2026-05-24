USE scissors_bar;

-- добавление тестового пользователя
INSERT IGNORE INTO users (id, user_name, password_hash, email, phone, avatar, role) 
VALUES (1, 'test_user', SHA2('123456', 256), 'test@scissors.bar', '+79991234567', 'https://example.com/avatar.jpg', 'customer');

-- очистка старых тестовых броней
SET SQL_SAFE_UPDATES = 0;
DELETE FROM reservations WHERE user_id = 1 AND reservation_time < NOW();
SET SQL_SAFE_UPDATES = 1;

-- добавление тестовых броней
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
(6, 1, '2025-04-21 20:30:00', 6, 'cancelled');