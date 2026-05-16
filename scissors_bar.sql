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
    role ENUM('admin', 'manager', 'customer') DEFAULT 'customer',
    is_active BOOLEAN DEFAULT TRUE,
    total_visits INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (user_name, password_hash, email, phone, role) VALUES
('admin', SHA2('admin', 256), 'admin@scissors.bar', '+1234567890', 'admin');

-- брони
CREATE TABLE reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_id INT NOT NULL,
    user_id INT NOT NULL,
    reservation_time DATETIME NOT NULL,
    duration_hours INT DEFAULT 2 CHECK (duration_hours BETWEEN 1 AND 4),
    guests_count INT NOT NULL CHECK (guests_count > 0),
    status ENUM('confirmed', 'cancelled', 'completed') DEFAULT 'confirmed',
    special_request TEXT,
    
    FOREIGN KEY (table_id) REFERENCES tables(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_reservation (table_id, reservation_time)
);

-- аля проверка 
SELECT * FROM categories;
SELECT id, name, category_id, is_secret, price FROM menu_items LIMIT 5;
SELECT id, name, price FROM menu_items WHERE is_secret = TRUE;
SELECT * FROM tables;
SELECT id, user_name, role FROM users;