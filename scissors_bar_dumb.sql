DROP DATABASE IF EXISTS scissors_bar;
CREATE DATABASE scissors_bar;
USE scissors_bar;

-- категории меню
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO categories (name) VALUES
('Коктейль'), ('Шот'), ('Закуска'), ('Основное блюдо');

-- столики (6 столиков)
CREATE TABLE tables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_number INT UNIQUE NOT NULL,
    seats_count INT NOT NULL CHECK (seats_count BETWEEN 1 AND 12),
    is_active BOOLEAN DEFAULT TRUE
);

INSERT INTO tables (table_number, seats_count) VALUES
(1, 2), (2, 2), (3, 4), (4, 4), (5, 6), (6, 8);

-- меню + секретное меню
CREATE TABLE menu_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id INT NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    is_secret BOOLEAN DEFAULT FALSE,
    description TEXT,
    available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- коктейли (category_id = 1)
INSERT INTO menu_items (name, category_id, price, is_secret, description) VALUES
('Blessing wife', 1, 550.00, FALSE, 'Водка, ягодный ликёр, сок лайма, сахарный сироп, шоколадная крошка, бузина'),
('Third Wheel', 1, 590.00, FALSE, 'Джин, ликёр апельсин, спрайт, лёд, кондитерская вишня, цедра апельсина'),
('Send nudes', 1, 620.00, FALSE, 'Джин, водка, сок персика, сахарный сироп, долька персика, фигурка из белого шоколада'),
('Pussy boy', 1, 580.00, FALSE, 'Текила, клубничный ликер, ванильный сироп, листья мяты'),
('One Night Stand', 1, 650.00, FALSE, 'Джин, водка, спрайт, ежевичный сироп, лёд, ежевика');

-- шоты (category_id = 2)
INSERT INTO menu_items (name, category_id, price, is_secret, description) VALUES
('Future Ex', 2, 250.00, FALSE, 'Водка, ликёр вишня, сок лайма, сахарный сироп, вишня'),
('Broken Vows', 2, 270.00, FALSE, 'Бурбон, Ангостура, ликёр амаро, карамельная сетка'),
('Bad Decision', 2, 290.00, FALSE, 'Джин, водка, лайм, сахарный сироп, черная Роза, кондитерская вишня'),
('Licked her', 2, 260.00, FALSE, 'Водка, амаретто, Бейлис, цедра апельсина');

-- закуски (category_id = 3)
INSERT INTO menu_items (name, category_id, price, is_secret, description) VALUES
('Сырная тарелка', 3, 890.00, FALSE, 'Ассорти из выдержанных сыров с виноградом, орехами, мёдом и гриссини'),
('Карпаччо из говядины', 3, 750.00, FALSE, 'Тонко нарезанная говядина с рукколой, пармезаном, каперсами и трюфельным маслом'),
('Креветки в темпуре', 3, 690.00, FALSE, 'Хрустящие креветки в темпуре с острым соусом чили и лаймом'),
('Брускетты с лососем', 3, 590.00, FALSE, 'Хрустящие брускетты с слабосолёным лососем, сливочным сыром, огурцом и микрозеленью'),
('Острые крылышки', 3, 550.00, FALSE, 'Куриные крылышки в остром соусе барбекю с кунжутом и зелёным луком. Подаются с соусом блю чиз');

-- основные блюда (category_id = 4)
INSERT INTO menu_items (name, category_id, price, is_secret, description) VALUES
('Бургер "Scissors"', 4, 850.00, FALSE, 'Сочная говяжья котлета, сыр чеддер, бекон, томаты, маринованные огурцы, листья салата и фирменный соус'),
('Стейк Рибай', 4, 1890.00, FALSE, 'Премиальный стейк Рибай из мраморной говядины с розмарином, чесноком и морской солью'),
('Паста Карбонара', 4, 690.00, FALSE, 'Классическая паста с беконом, яичным желтком, пармезаном и чёрным перцем'),
('Ризотто с грибами', 4, 720.00, FALSE, 'Нежное ризотто с белыми грибами, пармезаном и трюфельным маслом'),
('Салат с ростбифом', 4, 650.00, FALSE, 'Ростбиф из говядины с миксом салатов, вялеными томатами, пармезаном и медово-горчичной заправкой');

-- секретный шот (is_secret = TRUE)
INSERT INTO menu_items (name, category_id, price, is_secret, description) VALUES
('The Deer Penis', 2, 350.00, TRUE, 'Секретный шот. Джин, настойка чили, ягермейстер.');

-- пользователи
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    avatar VARCHAR(255) DEFAULT NULL,
    role ENUM('admin', 'manager', 'customer') DEFAULT 'customer',
    is_active BOOLEAN DEFAULT TRUE,
    total_visits INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (user_name, password_hash, email, phone, role) VALUES
('admin', SHA2('admin', 256), 'admin@scissors.bar', '+1234567890', 'admin');

-- афиша мероприятий
CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_date DATE NOT NULL,
    title VARCHAR(200) NOT NULL,
    event_type ENUM('Вечеринка', 'Мастер-класс', 'Стендап', 'Концерт', 'Закрытая вечеринка', 'Финал месяца') NOT NULL,
    description TEXT NOT NULL,
    start_time TIME NOT NULL,
    price DECIMAL(10,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    image_url VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- брони
CREATE TABLE reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_id INT NOT NULL,
    user_id INT NOT NULL,
    event_id INT NULL,
    reservation_time DATETIME NOT NULL,
    duration_hours INT DEFAULT 2 CHECK (duration_hours BETWEEN 1 AND 4),
    guests_count INT NOT NULL CHECK (guests_count > 0),
    status ENUM('confirmed', 'cancelled', 'completed') DEFAULT 'confirmed',
    special_request TEXT,
    
    FOREIGN KEY (table_id) REFERENCES tables(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE SET NULL,
    
    UNIQUE KEY unique_reservation (table_id, reservation_time)
);

-- добавление мероприятий из афиши
INSERT INTO events (event_date, title, event_type, description, start_time, price) VALUES
('2025-05-28', 'Ladies Night: Розовая Пятница', 'Вечеринка', 'Специальная программа для девушек: скидки на коктейли, живая музыка и розыгрыш призов от бара.', '20:00:00', 0),
('2025-05-30', 'Cocktail Masterclass', 'Мастер-класс', 'Научись готовить фирменные коктейли Scissors Bar под руководством шеф-бармена.', '19:00:00', 1500),
('2025-06-05', 'Start of Summer Party', 'Вечеринка', 'Открываем летний сезон громко! Dg set танцы до утра и летние коктейли по сниженной цене.', '22:00:00', 0),
('2025-06-12', 'Stand Up Night: Женский взгляд', 'Стендап', 'Вечер юмора с лучшими девушками-комиксами города. Смех, шутки и отличное настроение.', '20:00:00', 0),
('2025-06-19', 'Rock Covers Live', 'Концерт', 'Кавер-группа "Pink Noise" исполнит хиты рок-сцены в женском вокале.', '21:00:00', 0),
('2025-06-26', 'Scissors Secret Party', 'Закрытая вечеринка', 'Закрытое мероприятие для своих. Вход только по спискам или брони столика.', '23:00:00', 0),
('2025-06-30', 'Hello July: Прощай, Июнь!', 'Финал месяца', 'Грандиозная вечеринка в честь конца месяца. Подводим итоги и встречаем июль ярко!', '20:00:00', 0);
-- аля проверка 
SELECT * FROM categories;
SELECT * FROM events;
SELECT id, name, category_id, is_secret, price FROM menu_items LIMIT 5;
SELECT id, name, price FROM menu_items WHERE is_secret = TRUE;
SELECT * FROM tables;
SELECT id, user_name, role FROM users;
-- ===== тестовые данные =====
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