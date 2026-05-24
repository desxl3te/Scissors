-- master
INSERT INTO users (user_name, email) VALUES ('Boris', 'boris@mail.com');
-- slave
SELECT * FROM users WHERE name = 'Boris';