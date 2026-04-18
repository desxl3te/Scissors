USE scissors_bar;

-- обычное меню 
SELECT * FROM menu_items;

-- секретное меню
SELECT * FROM secret_menu;

-- столики
SELECT * FROM tables 
WHERE id NOT IN (
    SELECT table_id FROM reservations 
    WHERE reservation_time = '2025-04-15 19:00:00'
      AND status = 'confirmed'
);

-- просмотр бронирований
SELECT * FROM reservations 
WHERE user_id = 1 
   OR (table_id = 3 AND reservation_time = '2025-04-15 20:00:00');

-- тестовый пользователь
INSERT INTO users (user_name, password_hash, email, phone) 
VALUES ('test_user', '123123', 'test123@scissors.bar', '+79123456789');
  
-- тестовая бронь
INSERT INTO reservations (table_id, user_id, reservation_time, guests_count) 
VALUES (1, 1, '2025-04-15 19:00:00', 2);