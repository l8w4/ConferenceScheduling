-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: localhost    Database: conference_scheduling
-- ------------------------------------------------------
-- Server version	8.0.37

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
-- Table structure for table `attendees`
--

DROP TABLE IF EXISTS `attendees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendees` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `conf_title` varchar(255) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `abstract` text,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `optimal_order` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `conf_title` (`conf_title`),
  CONSTRAINT `attendees_ibfk_1` FOREIGN KEY (`conf_title`) REFERENCES `conferences` (`conf_title`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendees`
--

LOCK TABLES `attendees` WRITE;
/*!40000 ALTER TABLE `attendees` DISABLE KEYS */;
INSERT INTO `attendees` VALUES (1,'Sajedah Ghizawi','gsajedah@gmail.com','Interior Design','Nature-Inspired Interiors','Biophilic design is an innovative approach in interior design that seeks to incorporate natural elements into built environments to enhance human well-being. This design philosophy integrates features such as natural lighting, indoor plants, water elements, and natural materials to create spaces that foster a connection with nature. Research indicates that biophilic design can improve mental health, boost productivity, and reduce stress. By bringing elements of the outdoors inside, biophilic design not only enhances aesthetic appeal but also promotes a healthier and more sustainable living and working environment. This approach is gaining popularity in residential, commercial, and public spaces alike.','10:00:00','11:00:00',1),(2,'Abdulla Elkahlout','abdulla.elkahlout@gmail.com','Software Engineering ','Modular Software Arhitectures','Microservices architecture is a modular approach in software engineering that structures an application as a collection of loosely coupled services. Each service is independently deployable, scalable, and able to communicate through well-defined APIs. This architecture enhances flexibility, allowing development teams to work on different services concurrently and deploy them without affecting the entire system. It also improves fault isolation and simplifies maintenance and updates. Despite challenges like increased complexity in management and inter-service communication, microservices are widely adopted for their ability to enhance agility, scalability, and resilience in modern software applications.','15:00:00','16:00:00',6),(4,'Iman Assi','iman.assi@gmail.com','Software Engineering ','Continuous Integration: Agile Code','Continuous Integration (CI) is a software development practice where team members integrate their code frequently into a shared repository. Each integration triggers an automated build and test process, enabling early detection of integration errors. CI promotes collaboration, reduces integration problems, and provides rapid feedback to developers. It enhances software quality, accelerates delivery, and fosters a culture of transparency and accountability within development teams. By automating repetitive tasks and ensuring code reliability, CI is a fundamental practice in modern software engineering methodologies like Agile and DevOps.','16:00:00','17:00:00',7),(5,'Baraah','baraah@gmail.com','Software Engineering ','Hello from the other side','Hi my name is baraah and i love coding so much','13:00:00','14:00:00',4),(6,'Mohammad','mohammad@gmail.com','Industrial Engineering','Number 1','Hello my name is mohammad and i am number 1','10:00:00','11:00:00',1),(7,'Stacy','stacy@gmail.com','Software Engineering ','Number 2','hello my name is stacy','14:00:00','15:00:00',5),(8,'Rama','rama@gmail.com','Industrial Engineering','Number 3','Hi my name is rama','11:00:00','12:00:00',2),(9,'hello5','hello@gmail.com','Software Engineering ','Number 5','hello i am hello number 5','10:00:00','11:00:00',1),(10,'hello6','hello6@gmail.com','Software Engineering ','Number 6','hello i am hello number 6','11:00:00','12:00:00',2),(11,'hello7','hello7@gmail.com','Software Engineering ','Number 7','hello i am hello number 7','12:00:00','13:00:00',3),(12,'Number 3','helloooo@gmail.com','Industrial Engineering','Number333','hiiiiiiiii','14:00:00','15:00:00',5),(13,'Yasser Shoshaa','yasser@gmail.com','Mechatronics Engineering','Big brain yasser','hi my name is yasser and i am big brain','10:00:00','11:00:00',1),(14,'Obadah Ghizawi','obadah.ghizawi@gmail.com','Mechatronics Engineering','I am stupid i am not smart','yasser is smarter than obadah','11:00:00','12:00:00',2),(15,'Serena Williams','serena.williams@gmail.com','Industrial Engineering','Test-Driven Development','Test-Driven Development (TDD) is a software development approach where tests are written before code implementation. This abstract explores TDD\'s benefits, including improved code quality, faster development cycles, and enhanced design clarity through incremental development.','12:00:00','13:00:00',3),(16,'Jamba Juice','jamba@gmail.com','Industrial Engineering','Continuous Integration','Continuous Integration (CI) automates the integration process in software development, ensuring frequent code integration and early bug detection. This abstract discusses CI\'s role in enhancing team productivity, reducing integration issues, and maintaining code quality.','13:00:00','14:00:00',4);
/*!40000 ALTER TABLE `attendees` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-05-27 19:22:52
