SELECT * FROM scissors_bar.categories;
INSERT INTO scissors_bar.categories (name) VALUES ('Демо-репликация');
SELECT * FROM scissors_bar.categories;
-- должны быть видны изменения в slave (добавляться строка)