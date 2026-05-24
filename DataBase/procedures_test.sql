USE scissors_bar;

DROP PROCEDURE IF EXISTS BookTable;

DELIMITER //

CREATE PROCEDURE BookTable(
    IN p_table_id INT,
    IN p_user_id INT,
    IN p_reservation_time DATETIME,
    IN p_guests_count INT
)
BEGIN
    -- существует ли пользователь
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = p_user_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ошибка: пользователь не найден';
    END IF;

    -- существует ли столик
    IF NOT EXISTS (SELECT 1 FROM tables WHERE id = p_table_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ошибка: столик не найден';
    END IF;

    -- свободен ли столик
    IF EXISTS (
        SELECT 1 FROM reservations 
        WHERE table_id = p_table_id 
          AND reservation_time = p_reservation_time
          AND status = 'confirmed'
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ошибка: столик уже забронирован на это время';
    END IF;

    -- добавление брони
    INSERT INTO reservations (table_id, user_id, reservation_time, guests_count, status)
    VALUES (p_table_id, p_user_id, p_reservation_time, p_guests_count, 'confirmed');
    
    -- возврат ID созданной брони
    SELECT LAST_INSERT_ID() AS new_reservation_id;
END //

DELIMITER ;


-- Тест 1: Успешная бронь

-- 1. Подготовить данные
INSERT INTO users (id, user_name, password_hash, email) VALUES (999, 'TestUser', 'hash', 'test@mail.com');
INSERT INTO tables (id, table_number, seats_count) VALUES (99, 99, 4);

-- 2. Вызвать процедуру
CALL BookTable(99, 999, '2026-06-01 19:00:00', 3);

-- 3. Проверить результат
-- 3.1. Вернулся ли ID? (должно быть число > 0)
-- 3.2. Появилась ли запись в reservations?
SELECT * FROM reservations WHERE user_id = 999 AND table_id = 99;
-- Ожидаемо: 1 строка, status='confirmed', guests_count=3

-- 4. Очистить тестовые данные
DELETE FROM reservations WHERE user_id = 999;
DELETE FROM users WHERE id = 999;
DELETE FROM tables WHERE id = 99;

-- Тест 2: Пользователь не найден

CALL BookTable(1, 99999, '2026-06-01 19:00:00', 2);
-- Ожидаемо: ОШИБКА 1644 (45000): "Ошибка: пользователь не найден"
-- В Workbench: красная надпись в нижней панели

-- Тест 3: Столик не найден

CALL BookTable(99999, 1, '2026-06-01 19:00:00', 2);
-- Ожидаемо: ОШИБКА 1644 (45000): "Ошибка: столик не найден"


-- Тест 4: Столик уже занят

-- 1. Создать конфликтующую бронь (user_id=1 существует)
INSERT INTO reservations (table_id, user_id, reservation_time, guests_count, status)
VALUES (1, 1, '2026-06-01 19:00:00', 2, 'confirmed');

-- 2. Попробовать забронировать то же время ДРУГИМ пользователем
-- Создать этого пользователя!
INSERT INTO users (id, user_name, password_hash, email) 
VALUES (2, 'TestUser2', 'hash2', 'test2@mail.com');

CALL BookTable(1, 2, '2026-06-01 19:00:00', 3);
-- Должно быть: ОШИБКА 1644: "Ошибка: столик уже забронирован на это время"

-- 3. Очистить
DELETE FROM reservations WHERE table_id = 1 AND reservation_time = '2026-06-01 19:00:00';
DELETE FROM users WHERE id = 2;



-- Тест 5: Граничные значения

-- NULL в параметрах
CALL BookTable(NULL, 1, '2026-06-01 19:00:00', 2); -- Ошибка или обработка?

-- Отрицательное количество гостей
CALL BookTable(1, 1, '2026-06-01 19:00:00', -1); -- Должна быть валидация

-- Будущее время
CALL BookTable(1, 1, '2020-01-01 19:00:00', 2); -- Разрешено или нет по бизнес-логике?
