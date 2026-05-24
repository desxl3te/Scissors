SELECT m1.name AS item1, m2.name AS item2
FROM menu_items m1, menu_items m2
WHERE m1.id != m2.id;