USE scissors_bar;

-- Удаление процедуры, потому что может в будущем быть баг
DROP PROCEDURE IF EXISTS BookTable;

-- Разделитель, иначе код не будет нормально работать
DELIMITER //

CREATE PROCEDURE BookTable(
    IN p_table_id INT,
    IN p_user_id INT,
    IN p_reservation_time DATETIME,
    IN p_guests_count INT
)
BEGIN
    -- Проверяка, существует ли пользователь
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = p_user_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ошибка: пользователь не найден';
    END IF;

    -- Проверка, существует ли столик
    IF NOT EXISTS (SELECT 1 FROM tables WHERE id = p_table_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ошибка: столик не найден';
    END IF;

    -- Проверка, свободен ли столик в указанное время
    IF EXISTS (
        SELECT 1 FROM reservations 
        WHERE table_id = p_table_id 
          AND reservation_time = p_reservation_time
          AND status IN ('confirmed', 'pending')
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ошибка: столик уже забронирован на это время';
    END IF;

    -- Всё нормально = добавление брони
    INSERT INTO reservations (table_id, user_id, reservation_time, guests_count, status)
    VALUES (p_table_id, p_user_id, p_reservation_time, p_guests_count, 'confirmed');
    
    -- Возврат ID созданной брони
    SELECT LAST_INSERT_ID() AS new_reservation_id;
END //

DELIMITER ;

-- Вызов процедуры
CALL BookTable(1, 1, '2025-05-01 19:00:00', 4);