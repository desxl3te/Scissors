CREATE DATABASE  IF NOT EXISTS `scissors_bar` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `scissors_bar`;
-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: scissors_bar
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `menu_items`
--

DROP TABLE IF EXISTS `menu_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `category` enum('Коктейль','Шот','Закуска','Основное блюдо') NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `description` text,
  `available` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  CONSTRAINT `menu_items_chk_1` CHECK ((`price` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_items`
--

LOCK TABLES `menu_items` WRITE;
/*!40000 ALTER TABLE `menu_items` DISABLE KEYS */;
INSERT INTO `menu_items` VALUES (1,'Blessing wife','Коктейль',550.00,'Водка, ягодный ликёр, сок лайма, сахарный сироп, шоколадная крошка, бузина',1),(2,'Third Wheel','Коктейль',590.00,'Джин, ликёр апельсин, спрайт, лёд, кондитерская вишня, цедра апельсина',1),(3,'Send nudes','Коктейль',620.00,'Джин, водка, сок персика, сахарный сироп, долька персика, фигурка из белого шоколада',1),(4,'Pussy boy','Коктейль',580.00,'Текила, клубничный ликер, ванильный сироп, листья мяты',1),(5,'One Night Stand','Коктейль',650.00,'Джин, водка, спрайт, ежевичный сироп, лёд, ежевика',1),(6,'Future Ex','Шот',250.00,'Водка, ликёр вишня, сок лайма, сахарный сироп, вишня',1),(7,'Broken Vows','Шот',270.00,'Бурбон, Ангостура, ликёр амаро, карамельная сетка',1),(8,'Bad Decision','Шот',290.00,'Джин, водка, лайм, сахарный сироп, черная Роза, кондитерская вишня',1),(9,'Licked her','Шот',260.00,'Водка, амаретто, Бейлис, цедра апельсина',1),(10,'Сырная тарелка','Закуска',890.00,'3 сорта сыра, орехи, мёд, виноград',1),(11,'Карпаччо из говядины','Закуска',750.00,'Пармезан, руккола, трюфельное масло',1),(12,'Креветки в темпуре','Закуска',690.00,'Сладкий чили, кунжут, лайм',1),(13,'Брускетты с лососем','Закуска',590.00,'Творожный сыр, красная икра, укроп',1),(14,'Острые крылышки','Закуска',550.00,'Соус барбекю, сельдерей, блю чиз',1),(15,'Бургер \"Scissors\"','Основное блюдо',850.00,'Двойная говядина, бекон, сыр чеддер, соус \"Ножницы\"',1),(16,'Стейк Рибай','Основное блюдо',1890.00,'Мраморная говядина, картофель гратен, розмарин',1),(17,'Паста Карбонара','Основное блюдо',690.00,'Панчетта, пармезан, желток, чёрный перец',1),(18,'Ризотто с грибами','Основное блюдо',720.00,'Белые грибы, трюфельное масло, пармезан',1),(19,'Салат с ростбифом','Основное блюдо',650.00,'Ростбиф, микс салата, перечный соус, пармезан',1);
/*!40000 ALTER TABLE `menu_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservations`
--

DROP TABLE IF EXISTS `reservations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `table_id` int NOT NULL,
  `user_id` int NOT NULL,
  `reservation_time` datetime NOT NULL,
  `duration_hours` int DEFAULT '2',
  `guests_count` int NOT NULL,
  `status` enum('confirmed','cancelled','completed') DEFAULT 'confirmed',
  `special_request` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_reservation` (`table_id`,`reservation_time`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `reservations_ibfk_1` FOREIGN KEY (`table_id`) REFERENCES `tables` (`id`) ON DELETE CASCADE,
  CONSTRAINT `reservations_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `reservations_chk_1` CHECK ((`duration_hours` between 1 and 4)),
  CONSTRAINT `reservations_chk_2` CHECK ((`guests_count` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservations`
--

LOCK TABLES `reservations` WRITE;
/*!40000 ALTER TABLE `reservations` DISABLE KEYS */;
/*!40000 ALTER TABLE `reservations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `secret_menu`
--

DROP TABLE IF EXISTS `secret_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `secret_menu` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `category` enum('Коктейль','Шот','Закуска','Основное блюдо') NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `description` text,
  `unlock_trigger` varchar(50) DEFAULT 'scissors_click',
  PRIMARY KEY (`id`),
  CONSTRAINT `secret_menu_chk_1` CHECK ((`price` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `secret_menu`
--

LOCK TABLES `secret_menu` WRITE;
/*!40000 ALTER TABLE `secret_menu` DISABLE KEYS */;
INSERT INTO `secret_menu` VALUES (1,'The Deer Penis','Шот',350.00,'Секретный шот. Открывается только по нажатию на ножницы ✂️  Джин, настойка чили, ягермейстер','scissors_click');
/*!40000 ALTER TABLE `secret_menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tables`
--

DROP TABLE IF EXISTS `tables`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tables` (
  `id` int NOT NULL AUTO_INCREMENT,
  `table_number` int NOT NULL,
  `seats_count` int NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `table_number` (`table_number`),
  CONSTRAINT `tables_chk_1` CHECK ((`seats_count` between 1 and 12))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tables`
--

LOCK TABLES `tables` WRITE;
/*!40000 ALTER TABLE `tables` DISABLE KEYS */;
INSERT INTO `tables` VALUES (1,1,2,1),(2,2,2,1),(3,3,4,1),(4,4,4,1),(5,5,6,1);
/*!40000 ALTER TABLE `tables` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_name` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `total_visits` int DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_name` (`user_name`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','dummy_hash_will_be_replaced_by_backend','admin@scissors.bar','+1234567890',0,'2026-04-03 19:34:10');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-03 22:34:39
