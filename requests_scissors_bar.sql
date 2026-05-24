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
    WHERE reservation_time = '2026-04-15 19:00:00'
      AND status = 'confirmed'
);

-- бронирования пользователя с id = 1
SELECT * FROM reservations WHERE user_id = 1;

-- проверка столика 3 на 20:00
SELECT * FROM reservations 
WHERE table_id = 3 AND reservation_time = '2026-04-15 20:00:00';