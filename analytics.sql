USE scissors_bar;

-- количество броней по каждому столику
SELECT table_id, COUNT(*) AS total_reservations
FROM reservations
GROUP BY table_id
ORDER BY total_reservations DESC;

-- самый популярный день недели для броней
SELECT 
    DAYNAME(reservation_time) AS weekday,
    COUNT(*) AS bookings
FROM reservations
GROUP BY weekday
ORDER BY bookings DESC;

-- среднее количество гостей за одну бронь
SELECT AVG(guests_count) AS avg_guests_per_booking
FROM reservations;

-- бронь с максимальным количеством гостей
SELECT * FROM reservations
ORDER BY guests_count DESC
LIMIT 1;

-- количество броней по статусам
SELECT status, COUNT(*) AS count
FROM reservations
GROUP BY status;

-- самый популярный столик
SELECT table_id, COUNT(*) AS bookings
FROM reservations
GROUP BY table_id
ORDER BY bookings DESC
LIMIT 1;