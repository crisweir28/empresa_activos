-- MySQL dump 10.13  Distrib 9.4.0, for Win64 (x86_64)
--
-- Host: localhost    Database: empresa_activos
-- ------------------------------------------------------
-- Server version	9.4.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activos`
--

DROP TABLE IF EXISTS `activos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(120) NOT NULL,
  `descripcion` text,
  `numero_serie` varchar(100) DEFAULT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `estado` varchar(20) NOT NULL DEFAULT 'activo',
  `valor` float NOT NULL DEFAULT '0',
  `fecha_adquisicion` date DEFAULT NULL,
  `creado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `actualizado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `departamento_id` int DEFAULT NULL,
  `usuario_id` int DEFAULT NULL,
  `estatus` varchar(20) DEFAULT 'comprado',
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero_serie` (`numero_serie`),
  KEY `fk_activo_depto` (`departamento_id`),
  KEY `fk_activo_usuario` (`usuario_id`),
  CONSTRAINT `fk_activo_depto` FOREIGN KEY (`departamento_id`) REFERENCES `departamentos` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_activo_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`IdUsuario`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `adjuntosticket`
--

DROP TABLE IF EXISTS `adjuntosticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `adjuntosticket` (
  `IdAdjunto` int NOT NULL AUTO_INCREMENT,
  `IdTicket` int NOT NULL,
  `IdUsuario` int NOT NULL,
  `NombreArchivo` varchar(255) NOT NULL,
  `NombreOriginal` varchar(255) NOT NULL,
  `RutaArchivo` varchar(500) NOT NULL,
  `TipoMIME` varchar(100) DEFAULT NULL,
  `TamanoKB` decimal(10,2) DEFAULT NULL,
  `FechaSubida` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdAdjunto`),
  KEY `idx_ticket` (`IdTicket`),
  KEY `fk_adjuntos_usuario` (`IdUsuario`),
  CONSTRAINT `fk_adjuntos_ticket` FOREIGN KEY (`IdTicket`) REFERENCES `tickets` (`IdTicket`) ON DELETE CASCADE,
  CONSTRAINT `fk_adjuntos_usuario` FOREIGN KEY (`IdUsuario`) REFERENCES `usuario` (`IdUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `asignacion_equipo`
--

DROP TABLE IF EXISTS `asignacion_equipo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `asignacion_equipo` (
  `IdAsignacion` int NOT NULL AUTO_INCREMENT,
  `IdEquipo` int NOT NULL,
  `IdUsuario` int NOT NULL,
  `FechaAsignacion` datetime DEFAULT CURRENT_TIMESTAMP,
  `FechaLiberacion` datetime DEFAULT NULL,
  `AsignadoPor` int DEFAULT NULL,
  PRIMARY KEY (`IdAsignacion`),
  KEY `AsignadoPor` (`AsignadoPor`),
  KEY `idx_equipo` (`IdEquipo`),
  KEY `idx_usuario` (`IdUsuario`),
  CONSTRAINT `asignacion_equipo_ibfk_1` FOREIGN KEY (`IdEquipo`) REFERENCES `electronico` (`IdElectronico`),
  CONSTRAINT `asignacion_equipo_ibfk_2` FOREIGN KEY (`IdUsuario`) REFERENCES `usuario` (`IdUsuario`),
  CONSTRAINT `asignacion_equipo_ibfk_3` FOREIGN KEY (`AsignadoPor`) REFERENCES `usuario` (`IdUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `asignacionherramienta`
--

DROP TABLE IF EXISTS `asignacionherramienta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `asignacionherramienta` (
  `IdAsignacion` int NOT NULL AUTO_INCREMENT,
  `IdHerramienta` int NOT NULL,
  `IdUsuario` int NOT NULL,
  `FechaAsignacion` date NOT NULL,
  `FechaDevolucion` date DEFAULT NULL,
  `AsignadoPor` int DEFAULT NULL,
  `RecibidoPor` int DEFAULT NULL,
  `Observaciones` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdAsignacion`),
  KEY `FK_AsignHerr_AsignadoPor` (`AsignadoPor`),
  KEY `FK_AsignHerr_RecibidoPor` (`RecibidoPor`),
  KEY `idx_asign_herramienta` (`IdHerramienta`),
  KEY `idx_asign_usuario` (`IdUsuario`),
  CONSTRAINT `FK_AsignHerr_AsignadoPor` FOREIGN KEY (`AsignadoPor`) REFERENCES `usuario` (`IdUsuario`) ON DELETE SET NULL,
  CONSTRAINT `FK_AsignHerr_Herramienta` FOREIGN KEY (`IdHerramienta`) REFERENCES `herramienta` (`IdHerramienta`) ON DELETE CASCADE,
  CONSTRAINT `FK_AsignHerr_RecibidoPor` FOREIGN KEY (`RecibidoPor`) REFERENCES `usuario` (`IdUsuario`) ON DELETE SET NULL,
  CONSTRAINT `FK_AsignHerr_Usuario` FOREIGN KEY (`IdUsuario`) REFERENCES `usuario` (`IdUsuario`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bajaactivo`
--

DROP TABLE IF EXISTS `bajaactivo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bajaactivo` (
  `IdBaja` int NOT NULL AUTO_INCREMENT,
  `TipoActivo` enum('herramienta','electronico','vehiculo') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `IdActivo` int NOT NULL,
  `NombreActivo` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `DadoDeBajaPor` int DEFAULT NULL,
  `FechaBaja` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdBaja`),
  KEY `DadoDeBajaPor` (`DadoDeBajaPor`),
  CONSTRAINT `bajaactivo_ibfk_1` FOREIGN KEY (`DadoDeBajaPor`) REFERENCES `usuario` (`IdUsuario`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bajaactivoretiro`
--

DROP TABLE IF EXISTS `bajaactivoretiro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bajaactivoretiro` (
  `IdRetiro` int NOT NULL AUTO_INCREMENT,
  `IdBaja` int NOT NULL,
  `TipoActivo` enum('electronico','herramienta','vehiculo','general') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `IdActivo` int NOT NULL,
  `NombreActivo` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Condicion` enum('bueno','regular','dañado','perdido') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'bueno',
  `Observaciones` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `RetiroPor` int DEFAULT NULL,
  `FechaRetiro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdRetiro`),
  KEY `idx_retiro_baja` (`IdBaja`),
  KEY `FK_Retiro_Retiro` (`RetiroPor`),
  CONSTRAINT `FK_Retiro_Baja` FOREIGN KEY (`IdBaja`) REFERENCES `procesobaja` (`IdBaja`) ON DELETE CASCADE,
  CONSTRAINT `FK_Retiro_Retiro` FOREIGN KEY (`RetiroPor`) REFERENCES `usuario` (`IdUsuario`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `categoria`
--

DROP TABLE IF EXISTS `categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categoria` (
  `IdCategoria` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`IdCategoria`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `categoriasticket`
--

DROP TABLE IF EXISTS `categoriasticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categoriasticket` (
  `IdCategoria` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) NOT NULL,
  `Descripcion` text,
  `Icono` varchar(50) DEFAULT NULL,
  `Color` varchar(20) DEFAULT NULL,
  `Activo` tinyint(1) DEFAULT '1',
  `FechaCreacion` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdCategoria`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comentariosticket`
--

DROP TABLE IF EXISTS `comentariosticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comentariosticket` (
  `IdComentario` int NOT NULL AUTO_INCREMENT,
  `IdTicket` int NOT NULL,
  `IdUsuario` int NOT NULL,
  `Comentario` text NOT NULL,
  `EsInterno` tinyint(1) DEFAULT '0',
  `EsRespuestaOficial` tinyint(1) DEFAULT '0',
  `FechaCreacion` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdComentario`),
  KEY `idx_ticket` (`IdTicket`),
  KEY `idx_fecha` (`FechaCreacion`),
  KEY `fk_comentarios_usuario` (`IdUsuario`),
  CONSTRAINT `fk_comentarios_ticket` FOREIGN KEY (`IdTicket`) REFERENCES `tickets` (`IdTicket`) ON DELETE CASCADE,
  CONSTRAINT `fk_comentarios_usuario` FOREIGN KEY (`IdUsuario`) REFERENCES `usuario` (`IdUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `condicion`
--

DROP TABLE IF EXISTS `condicion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `condicion` (
  `IdCondicion` int NOT NULL AUTO_INCREMENT,
  `NombreCondicion` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`IdCondicion`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `conductorvehiculo`
--

DROP TABLE IF EXISTS `conductorvehiculo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `conductorvehiculo` (
  `IdConductorVehiculo` int NOT NULL AUTO_INCREMENT,
  `IdPersonal` int NOT NULL,
  `IdVehiculo` int NOT NULL,
  `FechaInicio` date NOT NULL,
  `FechaFin` date DEFAULT NULL,
  PRIMARY KEY (`IdConductorVehiculo`),
  KEY `FK_ConductorVehiculo_Personal` (`IdPersonal`),
  KEY `FK_ConductorVehiculo_Vehiculo` (`IdVehiculo`),
  CONSTRAINT `FK_ConductorVehiculo_Personal` FOREIGN KEY (`IdPersonal`) REFERENCES `personal` (`IdPersonal`) ON DELETE CASCADE,
  CONSTRAINT `FK_ConductorVehiculo_Vehiculo` FOREIGN KEY (`IdVehiculo`) REFERENCES `vehiculo` (`IdVehiculo`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `departamentos`
--

DROP TABLE IF EXISTS `departamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `departamentos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `creado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `documentousuario`
--

DROP TABLE IF EXISTS `documentousuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documentousuario` (
  `IdDocumento` int NOT NULL AUTO_INCREMENT,
  `IdUsuario` int NOT NULL,
  `TipoDocumento` enum('licencia_conducir','ine','examen_medico','comprobante_domicilio','curp','rfc','nss','carta_antecedentes','otro') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `NombreArchivo` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ArchivoUrl` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `TipoArchivo` enum('imagen','documento','pdf') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'documento',
  `MimeType` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `FechaEmision` date DEFAULT NULL,
  `FechaVencimiento` date DEFAULT NULL,
  `Vigente` tinyint(1) DEFAULT '1',
  `NumeroDocumento` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `Observaciones` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `CreadoPor` int DEFAULT NULL,
  `CreadoEn` datetime DEFAULT CURRENT_TIMESTAMP,
  `ActualizadoEn` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdDocumento`),
  KEY `CreadoPor` (`CreadoPor`),
  KEY `idx_usuario` (`IdUsuario`),
  KEY `idx_tipo` (`TipoDocumento`),
  KEY `idx_vencimiento` (`FechaVencimiento`),
  CONSTRAINT `documentousuario_ibfk_1` FOREIGN KEY (`IdUsuario`) REFERENCES `usuario` (`IdUsuario`) ON DELETE CASCADE,
  CONSTRAINT `documentousuario_ibfk_2` FOREIGN KEY (`CreadoPor`) REFERENCES `usuario` (`IdUsuario`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Documentos personales de empleados (licencia, INE, examen médico, etc.)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `electronico`
--

DROP TABLE IF EXISTS `electronico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `electronico` (
  `IdElectronico` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Marca` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Modelo` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `NumeroSerie` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `IMEI` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `SerieCargador` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Procesador` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `MemoriaRAM` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Almacenamiento` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `SistemaOperativo` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Garantia` date DEFAULT NULL,
  `Accesorios` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Comentarios` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `Arrendamiento` tinyint(1) NOT NULL DEFAULT '0',
  `FechaRenovacion` date DEFAULT NULL,
  `ProveedorArrendamiento` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `TipoEquipo` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'otro',
  `Gama` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Estado` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'almacen',
  `Condicion` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'bueno',
  `IdUsuario` int DEFAULT NULL,
  `IdUbicacion` int DEFAULT NULL,
  `FechaAdquisicion` date DEFAULT NULL,
  `Costo` float DEFAULT '0',
  `Descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ActualizadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdElectronico`),
  UNIQUE KEY `NumeroSerie` (`NumeroSerie`),
  UNIQUE KEY `UQ_Electronicos_NumeroSerie` (`NumeroSerie`),
  KEY `FK_Electronico_Ubicacion` (`IdUbicacion`),
  KEY `idx_elec_estado` (`Estado`),
  KEY `idx_elec_tipo` (`TipoEquipo`),
  KEY `idx_elec_usuario` (`IdUsuario`),
  KEY `idx_elec_serie` (`NumeroSerie`),
  CONSTRAINT `FK_Electronico_Ubicacion` FOREIGN KEY (`IdUbicacion`) REFERENCES `ubicacion` (`IdUbicacion`) ON DELETE SET NULL,
  CONSTRAINT `FK_Electronico_Usuario` FOREIGN KEY (`IdUsuario`) REFERENCES `usuario` (`IdUsuario`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `estadosticket`
--

DROP TABLE IF EXISTS `estadosticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estadosticket` (
  `IdEstado` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) NOT NULL,
  `Descripcion` text,
  `Color` varchar(20) DEFAULT NULL,
  `EsEstadoFinal` tinyint(1) DEFAULT '0',
  `Orden` int DEFAULT NULL,
  `Activo` tinyint(1) DEFAULT '1',
  `FechaCreacion` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdEstado`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `evidenciaequipo`
--

DROP TABLE IF EXISTS `evidenciaequipo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evidenciaequipo` (
  `IdEvidencia` int NOT NULL AUTO_INCREMENT,
  `IdElectronico` int NOT NULL,
  `IdAsignacion` int DEFAULT NULL COMMENT 'FK a asignacion si aplica',
  `ArchivoUrl` varchar(500) NOT NULL,
  `NombreArchivo` varchar(255) DEFAULT NULL,
  `Tipo` varchar(20) NOT NULL DEFAULT 'entrega' COMMENT 'entrega, devolucion, daño, otro',
  `TipoArchivo` enum('imagen','documento') NOT NULL DEFAULT 'imagen',
  `MimeType` varchar(100) DEFAULT NULL,
  `Descripcion` varchar(255) DEFAULT NULL,
  `CreadoPor` int DEFAULT NULL,
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdEvidencia`),
  KEY `FK_EvidenciaEquipo_Electronico` (`IdElectronico`),
  KEY `FK_EvidenciaEquipo_Usuario` (`CreadoPor`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `evidenciaherramienta`
--

DROP TABLE IF EXISTS `evidenciaherramienta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evidenciaherramienta` (
  `IdEvidencia` int NOT NULL AUTO_INCREMENT,
  `IdHerramienta` int NOT NULL,
  `ArchivoUrl` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `NombreArchivo` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Tipo` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'daño',
  `TipoArchivo` enum('imagen','documento') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'imagen',
  `MimeType` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Descripcion` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CreadoPor` int DEFAULT NULL,
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdEvidencia`),
  KEY `FK_Evidencia_CreadoPor` (`CreadoPor`),
  KEY `idx_evid_herramienta` (`IdHerramienta`),
  CONSTRAINT `FK_Evidencia_CreadoPor` FOREIGN KEY (`CreadoPor`) REFERENCES `usuario` (`IdUsuario`) ON DELETE SET NULL,
  CONSTRAINT `FK_Evidencia_Herramienta` FOREIGN KEY (`IdHerramienta`) REFERENCES `herramienta` (`IdHerramienta`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `evidenciavehiculo`
--

DROP TABLE IF EXISTS `evidenciavehiculo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evidenciavehiculo` (
  `IdEvidencia` int NOT NULL AUTO_INCREMENT,
  `IdVehiculo` int NOT NULL,
  `Tipo` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ArchivoUrl` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CreadoEn` datetime DEFAULT NULL,
  PRIMARY KEY (`IdEvidencia`),
  KEY `IdVehiculo` (`IdVehiculo`),
  CONSTRAINT `evidenciavehiculo_ibfk_1` FOREIGN KEY (`IdVehiculo`) REFERENCES `vehiculo` (`IdVehiculo`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `herramienta`
--

DROP TABLE IF EXISTS `herramienta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `herramienta` (
  `IdHerramienta` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Marca` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Modelo` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `NumeroSerie` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Estado` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'disponible',
  `Costo` float DEFAULT '0',
  `FechaAlta` date NOT NULL DEFAULT (curdate()),
  `Descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `IdCategoria` int DEFAULT NULL,
  `TipoHerramienta` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `IdUbicacion` int DEFAULT NULL,
  `IdDepartamento` int DEFAULT NULL,
  `Subarea` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ActualizadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdHerramienta`),
  UNIQUE KEY `NumeroSerie` (`NumeroSerie`),
  KEY `idx_herr_estado` (`Estado`),
  KEY `idx_herr_serie` (`NumeroSerie`),
  KEY `FK_Herramienta_Categoria` (`IdCategoria`),
  KEY `FK_Herramienta_Ubicacion` (`IdUbicacion`),
  KEY `FK_Herramienta_Departamento` (`IdDepartamento`),
  CONSTRAINT `FK_Herramienta_Categoria` FOREIGN KEY (`IdCategoria`) REFERENCES `categoria` (`IdCategoria`) ON DELETE SET NULL,
  CONSTRAINT `FK_Herramienta_Departamento` FOREIGN KEY (`IdDepartamento`) REFERENCES `departamentos` (`id`) ON DELETE SET NULL,
  CONSTRAINT `FK_Herramienta_Ubicacion` FOREIGN KEY (`IdUbicacion`) REFERENCES `ubicacion` (`IdUbicacion`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `historialticket`
--

DROP TABLE IF EXISTS `historialticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historialticket` (
  `IdHistorial` int NOT NULL AUTO_INCREMENT,
  `IdTicket` int NOT NULL,
  `IdUsuario` int DEFAULT NULL,
  `TipoCambio` varchar(50) NOT NULL,
  `ValorAnterior` varchar(255) DEFAULT NULL,
  `ValorNuevo` varchar(255) DEFAULT NULL,
  `Descripcion` text,
  `FechaCambio` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdHistorial`),
  KEY `idx_ticket` (`IdTicket`),
  KEY `idx_fecha` (`FechaCambio`),
  KEY `fk_historial_usuario` (`IdUsuario`),
  CONSTRAINT `fk_historial_ticket` FOREIGN KEY (`IdTicket`) REFERENCES `tickets` (`IdTicket`) ON DELETE CASCADE,
  CONSTRAINT `fk_historial_usuario` FOREIGN KEY (`IdUsuario`) REFERENCES `usuario` (`IdUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mantenimientoelectronico`
--

DROP TABLE IF EXISTS `mantenimientoelectronico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mantenimientoelectronico` (
  `IdMantenimiento` int NOT NULL AUTO_INCREMENT,
  `IdElectronico` int NOT NULL,
  `Tipo` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Diagnostico` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `Descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `FechaInicio` date NOT NULL,
  `FechaTermino` date DEFAULT NULL,
  `Costo` float DEFAULT '0',
  `Tecnico` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Estatus` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'en_proceso',
  `CreadoPor` int DEFAULT NULL,
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdMantenimiento`),
  KEY `FK_MantElec_CreadoPor` (`CreadoPor`),
  KEY `idx_me_electronico` (`IdElectronico`),
  KEY `idx_me_tipo` (`Tipo`),
  KEY `idx_me_estatus` (`Estatus`),
  CONSTRAINT `FK_MantElec_CreadoPor` FOREIGN KEY (`CreadoPor`) REFERENCES `usuario` (`IdUsuario`) ON DELETE SET NULL,
  CONSTRAINT `FK_MantElec_Electronico` FOREIGN KEY (`IdElectronico`) REFERENCES `electronico` (`IdElectronico`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mantenimientovehiculo`
--

DROP TABLE IF EXISTS `mantenimientovehiculo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mantenimientovehiculo` (
  `IdMantenimiento` int NOT NULL AUTO_INCREMENT,
  `IdVehiculo` int NOT NULL,
  `IdPersonal` int DEFAULT NULL,
  `IdTipoServicio` int NOT NULL,
  `Descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `FechaInicio` date NOT NULL,
  `FechaEntrega` date DEFAULT NULL,
  `Kilometraje` int DEFAULT NULL,
  `Costo` float DEFAULT '0',
  `Proveedor` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Estatus` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'en_proceso',
  `CreadoPor` int DEFAULT NULL,
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdMantenimiento`),
  KEY `FK_MantVehiculo_Personal` (`IdPersonal`),
  KEY `FK_MantVehiculo_TipoServicio` (`IdTipoServicio`),
  KEY `FK_MantVehiculo_Usuario` (`CreadoPor`),
  KEY `idx_mv_vehiculo` (`IdVehiculo`),
  KEY `idx_mv_estatus` (`Estatus`),
  CONSTRAINT `FK_MantVehiculo_Personal` FOREIGN KEY (`IdPersonal`) REFERENCES `personal` (`IdPersonal`) ON DELETE SET NULL,
  CONSTRAINT `FK_MantVehiculo_TipoServicio` FOREIGN KEY (`IdTipoServicio`) REFERENCES `tiposervicio` (`IdTipoServicio`),
  CONSTRAINT `FK_MantVehiculo_Usuario` FOREIGN KEY (`CreadoPor`) REFERENCES `usuario` (`IdUsuario`),
  CONSTRAINT `FK_MantVehiculo_Vehiculo` FOREIGN KEY (`IdVehiculo`) REFERENCES `vehiculo` (`IdVehiculo`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `modulo`
--

DROP TABLE IF EXISTS `modulo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modulo` (
  `IdModulo` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Descripcion` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Icono` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Orden` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`IdModulo`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `password_reset_tokens`
--

DROP TABLE IF EXISTS `password_reset_tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `password_reset_tokens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `token` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `expira_en` datetime NOT NULL,
  `usado` tinyint(1) NOT NULL DEFAULT '0',
  `creado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `IdUsuario` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `idx_token` (`token`),
  KEY `fk_reset_usuario` (`usuario_id`),
  CONSTRAINT `fk_reset_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`IdUsuario`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `permisorol`
--

DROP TABLE IF EXISTS `permisorol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permisorol` (
  `IdPermiso` int NOT NULL AUTO_INCREMENT,
  `IdRol` int NOT NULL,
  `IdModulo` int NOT NULL,
  `PuedeVer` tinyint(1) NOT NULL DEFAULT '0',
  `PuedeCrear` tinyint(1) NOT NULL DEFAULT '0',
  `PuedeEditar` tinyint(1) NOT NULL DEFAULT '0',
  `PuedeEliminar` tinyint(1) NOT NULL DEFAULT '0',
  `ActualizadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdPermiso`),
  UNIQUE KEY `UQ_PermisoRol` (`IdRol`,`IdModulo`),
  KEY `FK_PermisoRol_Modulo` (`IdModulo`),
  CONSTRAINT `FK_PermisoRol_Modulo` FOREIGN KEY (`IdModulo`) REFERENCES `modulo` (`IdModulo`) ON DELETE CASCADE,
  CONSTRAINT `FK_PermisoRol_Rol` FOREIGN KEY (`IdRol`) REFERENCES `rol` (`IdRol`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=272 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `permisosvehiculo`
--

DROP TABLE IF EXISTS `permisosvehiculo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permisosvehiculo` (
  `IdPermiso` int NOT NULL AUTO_INCREMENT,
  `IdVehiculo` int NOT NULL,
  `IdTipoServicio` int NOT NULL,
  `Descripcion` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Numero` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `FechaInicio` date DEFAULT NULL,
  `FechaVencimiento` date NOT NULL,
  `ArchivoUrl` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdPermiso`),
  KEY `FK_PermisosVehiculo_Tipo` (`IdTipoServicio`),
  KEY `idx_pv_vencimiento` (`FechaVencimiento`),
  KEY `idx_pv_vehiculo` (`IdVehiculo`),
  CONSTRAINT `FK_PermisosVehiculo_Tipo` FOREIGN KEY (`IdTipoServicio`) REFERENCES `tiposervicio` (`IdTipoServicio`),
  CONSTRAINT `FK_PermisosVehiculo_Vehiculo` FOREIGN KEY (`IdVehiculo`) REFERENCES `vehiculo` (`IdVehiculo`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `permisousuario`
--

DROP TABLE IF EXISTS `permisousuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permisousuario` (
  `IdPermiso` int NOT NULL AUTO_INCREMENT,
  `IdUsuario` int NOT NULL,
  `IdModulo` int NOT NULL,
  `PuedeVer` tinyint(1) NOT NULL,
  `PuedeCrear` tinyint(1) NOT NULL,
  `PuedeEditar` tinyint(1) NOT NULL,
  `PuedeEliminar` tinyint(1) NOT NULL,
  `ActualizadoEn` datetime DEFAULT (now()),
  PRIMARY KEY (`IdPermiso`),
  UNIQUE KEY `UQ_PermisoUsuario` (`IdUsuario`,`IdModulo`),
  KEY `IdModulo` (`IdModulo`),
  CONSTRAINT `permisousuario_ibfk_1` FOREIGN KEY (`IdUsuario`) REFERENCES `usuario` (`IdUsuario`),
  CONSTRAINT `permisousuario_ibfk_2` FOREIGN KEY (`IdModulo`) REFERENCES `modulo` (`IdModulo`)
) ENGINE=InnoDB AUTO_INCREMENT=3818 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `permisovehiculo`
--

DROP TABLE IF EXISTS `permisovehiculo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permisovehiculo` (
  `IdPermiso` int NOT NULL AUTO_INCREMENT,
  `IdVehiculo` int NOT NULL,
  `IdTipoServicio` int NOT NULL,
  `Descripcion` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Numero` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `FechaInicio` date DEFAULT NULL,
  `FechaVencimiento` date NOT NULL,
  `ArchivoUrl` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdPermiso`),
  KEY `idx_vehiculo` (`IdVehiculo`),
  KEY `idx_tipo_servicio` (`IdTipoServicio`),
  KEY `idx_vencimiento` (`FechaVencimiento`),
  CONSTRAINT `permisovehiculo_ibfk_1` FOREIGN KEY (`IdVehiculo`) REFERENCES `vehiculo` (`IdVehiculo`) ON DELETE CASCADE,
  CONSTRAINT `permisovehiculo_ibfk_2` FOREIGN KEY (`IdTipoServicio`) REFERENCES `tiposervicio` (`IdTipoServicio`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Permisos y documentos de vehículos (póliza, tarjeta circulación, verificación, tenencia)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `personal`
--

DROP TABLE IF EXISTS `personal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `personal` (
  `IdPersonal` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Apellido` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Telefono` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Area` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Correo` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `JefeInmediato` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `LicenciaNumero` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `LicenciaVigencia` date DEFAULT NULL,
  `SeguroMedico` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `SeguroVigencia` date DEFAULT NULL,
  `IdCondicion` int DEFAULT NULL,
  `Activo` tinyint(1) NOT NULL DEFAULT '1',
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdPersonal`),
  KEY `FK_Personal_Condicion` (`IdCondicion`),
  CONSTRAINT `FK_Personal_Condicion` FOREIGN KEY (`IdCondicion`) REFERENCES `condicion` (`IdCondicion`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `prioridadesticket`
--

DROP TABLE IF EXISTS `prioridadesticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prioridadesticket` (
  `IdPrioridad` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) NOT NULL,
  `Descripcion` text,
  `Color` varchar(20) DEFAULT NULL,
  `Nivel` int DEFAULT NULL,
  `TiempoRespuestaHoras` int DEFAULT NULL,
  `Activo` tinyint(1) DEFAULT '1',
  `FechaCreacion` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdPrioridad`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `procesobaja`
--

DROP TABLE IF EXISTS `procesobaja`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `procesobaja` (
  `IdBaja` int NOT NULL AUTO_INCREMENT,
  `IdUsuario` int NOT NULL,
  `FechaAviso` date NOT NULL,
  `FechaBaja` date DEFAULT NULL,
  `Motivo` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `SolicitadoPor` int DEFAULT NULL,
  `Estatus` enum('aviso','proceso','autorizado','completado','cancelado') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'aviso',
  `AutorizadoPor` int DEFAULT NULL,
  `FechaAutorizacion` datetime DEFAULT NULL,
  `Observaciones` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `CreadoEn` datetime DEFAULT CURRENT_TIMESTAMP,
  `ActualizadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdBaja`),
  KEY `IdUsuario` (`IdUsuario`),
  KEY `AutorizadoPor` (`AutorizadoPor`),
  KEY `FK_Baja_Solicitado` (`SolicitadoPor`),
  CONSTRAINT `FK_Baja_Solicitado` FOREIGN KEY (`SolicitadoPor`) REFERENCES `usuario` (`IdUsuario`) ON DELETE SET NULL,
  CONSTRAINT `procesobaja_ibfk_1` FOREIGN KEY (`IdUsuario`) REFERENCES `usuario` (`IdUsuario`),
  CONSTRAINT `procesobaja_ibfk_2` FOREIGN KEY (`AutorizadoPor`) REFERENCES `usuario` (`IdUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proyecto`
--

DROP TABLE IF EXISTS `proyecto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyecto` (
  `IdProyecto` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `FechaInicio` date NOT NULL,
  `FechaTermino` date NOT NULL,
  `Estatus` enum('Activo','En progreso','Pausado','Completado','Cancelado') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Activo',
  `CreadoPor` int NOT NULL,
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ActualizadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdProyecto`),
  KEY `FK_Proyecto_Usuario` (`CreadoPor`),
  CONSTRAINT `FK_Proyecto_Usuario` FOREIGN KEY (`CreadoPor`) REFERENCES `usuario` (`IdUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proyectoactivo`
--

DROP TABLE IF EXISTS `proyectoactivo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyectoactivo` (
  `IdAsignacion` int NOT NULL AUTO_INCREMENT,
  `IdProyecto` int NOT NULL,
  `TipoActivo` enum('electronico','vehiculo','herramienta') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `IdActivo` int NOT NULL COMMENT 'ID según el tipo',
  `EstadoInicial` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `EstadoFinal` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `AsignadoPor` int NOT NULL,
  `FechaAsignacion` date NOT NULL,
  `FechaDevolucion` date DEFAULT NULL,
  `Observaciones` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdAsignacion`),
  KEY `FK_ProjActivo_Proyecto` (`IdProyecto`),
  KEY `FK_ProjActivo_AsignadoPor` (`AsignadoPor`),
  CONSTRAINT `FK_ProjActivo_AsignadoPor` FOREIGN KEY (`AsignadoPor`) REFERENCES `usuario` (`IdUsuario`),
  CONSTRAINT `FK_ProjActivo_Proyecto` FOREIGN KEY (`IdProyecto`) REFERENCES `proyecto` (`IdProyecto`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proyectoauditoria`
--

DROP TABLE IF EXISTS `proyectoauditoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyectoauditoria` (
  `IdAuditoria` int NOT NULL AUTO_INCREMENT,
  `IdProyecto` int NOT NULL,
  `Accion` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'crear, editar, cambio_estatus, asignar_personal, asignar_activo',
  `Detalle` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT 'Descripción del cambio',
  `RazonCambio` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `RealizadoPor` int NOT NULL,
  `RealizadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdAuditoria`),
  KEY `FK_Auditoria_Proyecto` (`IdProyecto`),
  KEY `FK_Auditoria_RealizadoPor` (`RealizadoPor`),
  CONSTRAINT `FK_Auditoria_Proyecto` FOREIGN KEY (`IdProyecto`) REFERENCES `proyecto` (`IdProyecto`) ON DELETE CASCADE,
  CONSTRAINT `FK_Auditoria_RealizadoPor` FOREIGN KEY (`RealizadoPor`) REFERENCES `usuario` (`IdUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proyectopersonal`
--

DROP TABLE IF EXISTS `proyectopersonal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyectopersonal` (
  `IdAsignacion` int NOT NULL AUTO_INCREMENT,
  `IdProyecto` int NOT NULL,
  `IdUsuario` int NOT NULL,
  `Rol` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Rol dentro del proyecto',
  `FechaAsignacion` date NOT NULL,
  `AsignadoPor` int NOT NULL,
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdAsignacion`),
  UNIQUE KEY `UQ_ProyectoPersonal` (`IdProyecto`,`IdUsuario`),
  KEY `FK_ProjPersonal_Usuario` (`IdUsuario`),
  KEY `FK_ProjPersonal_AsignadoPor` (`AsignadoPor`),
  CONSTRAINT `FK_ProjPersonal_AsignadoPor` FOREIGN KEY (`AsignadoPor`) REFERENCES `usuario` (`IdUsuario`),
  CONSTRAINT `FK_ProjPersonal_Proyecto` FOREIGN KEY (`IdProyecto`) REFERENCES `proyecto` (`IdProyecto`) ON DELETE CASCADE,
  CONSTRAINT `FK_ProjPersonal_Usuario` FOREIGN KEY (`IdUsuario`) REFERENCES `usuario` (`IdUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reportedanio`
--

DROP TABLE IF EXISTS `reportedanio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reportedanio` (
  `IdReporte` int NOT NULL AUTO_INCREMENT,
  `IdHerramienta` int NOT NULL,
  `NombreMaterial` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Caracteristica` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Razon` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Tipo` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'daño',
  `ArchivoUrl` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `NombreArchivo` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `TipoArchivo` enum('imagen','documento') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `MimeType` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `IdUsuarioResponsable` int DEFAULT NULL,
  `CreadoPor` int DEFAULT NULL,
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdReporte`),
  KEY `FK_ReporteDanio_Responsable` (`IdUsuarioResponsable`),
  KEY `FK_ReporteDanio_CreadoPor` (`CreadoPor`),
  KEY `idx_reporte_herramienta` (`IdHerramienta`),
  CONSTRAINT `FK_ReporteDanio_CreadoPor` FOREIGN KEY (`CreadoPor`) REFERENCES `usuario` (`IdUsuario`) ON DELETE SET NULL,
  CONSTRAINT `FK_ReporteDanio_Herramienta` FOREIGN KEY (`IdHerramienta`) REFERENCES `herramienta` (`IdHerramienta`) ON DELETE CASCADE,
  CONSTRAINT `FK_ReporteDanio_Responsable` FOREIGN KEY (`IdUsuarioResponsable`) REFERENCES `usuario` (`IdUsuario`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rol`
--

DROP TABLE IF EXISTS `rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol` (
  `IdRol` int NOT NULL AUTO_INCREMENT,
  `NombreRol` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`IdRol`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `slaticket`
--

DROP TABLE IF EXISTS `slaticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `slaticket` (
  `IdSLA` int NOT NULL AUTO_INCREMENT,
  `IdTicket` int NOT NULL,
  `TiempoRespuestaEsperadoHoras` int DEFAULT NULL,
  `TiempoResolucionEsperadoHoras` int DEFAULT NULL,
  `FechaLimiteRespuesta` datetime DEFAULT NULL,
  `FechaLimiteResolucion` datetime DEFAULT NULL,
  `CumplioRespuesta` tinyint(1) DEFAULT NULL,
  `CumplioResolucion` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`IdSLA`),
  UNIQUE KEY `IdTicket` (`IdTicket`),
  KEY `idx_fecha_limite_respuesta` (`FechaLimiteRespuesta`),
  KEY `idx_fecha_limite_resolucion` (`FechaLimiteResolucion`),
  CONSTRAINT `fk_sla_ticket` FOREIGN KEY (`IdTicket`) REFERENCES `tickets` (`IdTicket`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tickets`
--

DROP TABLE IF EXISTS `tickets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tickets` (
  `IdTicket` int NOT NULL AUTO_INCREMENT,
  `NumeroTicket` varchar(20) NOT NULL,
  `IdUsuarioCreador` int NOT NULL,
  `Titulo` varchar(200) NOT NULL,
  `Descripcion` text NOT NULL,
  `IdCategoria` int NOT NULL,
  `IdPrioridad` int NOT NULL DEFAULT '2',
  `IdEstado` int NOT NULL DEFAULT '1',
  `IdEquipo` int DEFAULT NULL,
  `IdAsignadoA` int DEFAULT NULL,
  `CanalCreacion` varchar(50) DEFAULT 'Portal de Usuario',
  `IdSede` int DEFAULT NULL,
  `IdDepartamento` int DEFAULT NULL,
  `FechaCreacion` datetime DEFAULT CURRENT_TIMESTAMP,
  `FechaUltimaActualizacion` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `FechaPrimeraRespuesta` datetime DEFAULT NULL,
  `FechaResolucion` datetime DEFAULT NULL,
  `FechaCierre` datetime DEFAULT NULL,
  `CalificacionServicio` tinyint DEFAULT NULL,
  `ComentarioSatisfaccion` text,
  PRIMARY KEY (`IdTicket`),
  UNIQUE KEY `NumeroTicket` (`NumeroTicket`),
  KEY `idx_numero` (`NumeroTicket`),
  KEY `idx_creador` (`IdUsuarioCreador`),
  KEY `idx_asignado` (`IdAsignadoA`),
  KEY `idx_estado` (`IdEstado`),
  KEY `idx_prioridad` (`IdPrioridad`),
  KEY `idx_fecha_creacion` (`FechaCreacion`),
  KEY `fk_tickets_categoria` (`IdCategoria`),
  CONSTRAINT `fk_tickets_asignado` FOREIGN KEY (`IdAsignadoA`) REFERENCES `usuario` (`IdUsuario`) ON DELETE SET NULL,
  CONSTRAINT `fk_tickets_categoria` FOREIGN KEY (`IdCategoria`) REFERENCES `categoriasticket` (`IdCategoria`),
  CONSTRAINT `fk_tickets_estado` FOREIGN KEY (`IdEstado`) REFERENCES `estadosticket` (`IdEstado`),
  CONSTRAINT `fk_tickets_prioridad` FOREIGN KEY (`IdPrioridad`) REFERENCES `prioridadesticket` (`IdPrioridad`),
  CONSTRAINT `fk_tickets_usuario_creador` FOREIGN KEY (`IdUsuarioCreador`) REFERENCES `usuario` (`IdUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=97 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_generar_numero_ticket` BEFORE INSERT ON `tickets` FOR EACH ROW BEGIN
    DECLARE contador INT;
    DECLARE prefijo VARCHAR(10);
    DECLARE fecha_actual VARCHAR(10);
    DECLARE dept_nombre VARCHAR(50);
    DECLARE fecha_ticket DATE;
    
    -- Fecha del ticket (puede ser NOW() o una fecha específica)
    SET fecha_ticket = DATE(COALESCE(NEW.FechaCreacion, NOW()));
    
    -- Obtener el departamento del usuario creador
    SELECT d.nombre COLLATE utf8mb4_unicode_ci INTO dept_nombre
    FROM usuarios u
    INNER JOIN departamentos d ON u.departamento_id = d.id
    WHERE u.id = NEW.IdUsuarioCreador;
    
    -- Definir prefijo según departamento
    SET prefijo = CASE 
        WHEN dept_nombre COLLATE utf8mb4_unicode_ci = 'RH' THEN 'TRH'
        WHEN dept_nombre COLLATE utf8mb4_unicode_ci = 'Recursos Humanos' THEN 'TRH'
        WHEN dept_nombre COLLATE utf8mb4_unicode_ci = 'Compras' THEN 'TCPR'
        WHEN dept_nombre COLLATE utf8mb4_unicode_ci = 'TI' THEN 'TTI'
        WHEN dept_nombre COLLATE utf8mb4_unicode_ci = 'Sistemas' THEN 'TTI'
        WHEN dept_nombre COLLATE utf8mb4_unicode_ci = 'Contabilidad' THEN 'TCONT'
        WHEN dept_nombre COLLATE utf8mb4_unicode_ci = 'Finanzas' THEN 'TFIN'
        WHEN dept_nombre COLLATE utf8mb4_unicode_ci = 'Administrativo' THEN 'TADM'
        WHEN dept_nombre COLLATE utf8mb4_unicode_ci = 'Ventas' THEN 'TVEN'
        WHEN dept_nombre COLLATE utf8mb4_unicode_ci = 'Marketing' THEN 'TMKT'
        WHEN dept_nombre COLLATE utf8mb4_unicode_ci = 'Logística' THEN 'TLOG'
        WHEN dept_nombre COLLATE utf8mb4_unicode_ci = 'Almacén' THEN 'TALM'
        WHEN dept_nombre COLLATE utf8mb4_unicode_ci = 'Producción' THEN 'TPROD'
        WHEN dept_nombre COLLATE utf8mb4_unicode_ci = 'Calidad' THEN 'TCAL'
        WHEN dept_nombre COLLATE utf8mb4_unicode_ci = 'Mantenimiento' THEN 'TMANT'
        ELSE 'T'
    END;
    
    -- Formato de fecha DD/MM/YYYY
    SET fecha_actual = DATE_FORMAT(fecha_ticket, '%d/%m/%Y');
    
    -- Contar tickets del MISMO DEPARTAMENTO y MISMA FECHA
    SELECT COUNT(*) + 1 INTO contador
    FROM Tickets t
    INNER JOIN usuarios u ON t.IdUsuarioCreador = u.id
    INNER JOIN departamentos d ON u.departamento_id = d.id
    WHERE d.nombre COLLATE utf8mb4_unicode_ci = dept_nombre COLLATE utf8mb4_unicode_ci
      AND DATE(t.FechaCreacion) = fecha_ticket;
    
    -- Generar número: PREFIJO-DD/MM/YYYY-XXX
    SET NEW.NumeroTicket = CONCAT(
        prefijo, '-',
        fecha_actual, '-',
        LPAD(contador, 3, '0')
    );
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_actualizar_fechas_ticket` BEFORE UPDATE ON `tickets` FOR EACH ROW BEGIN
    IF NEW.FechaPrimeraRespuesta IS NULL AND OLD.IdEstado = 1 AND NEW.IdEstado != 1 THEN
        SET NEW.FechaPrimeraRespuesta = NOW();
    END IF;
    
    IF NEW.FechaResolucion IS NULL AND NEW.IdEstado = 5 THEN
        SET NEW.FechaResolucion = NOW();
    END IF;
    
    IF NEW.FechaCierre IS NULL AND NEW.IdEstado IN (6, 7) THEN
        SET NEW.FechaCierre = NOW();
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_historial_ticket_update` AFTER UPDATE ON `tickets` FOR EACH ROW BEGIN
    IF OLD.IdEstado != NEW.IdEstado THEN
        INSERT INTO HistorialTicket (IdTicket, IdUsuario, TipoCambio, ValorAnterior, ValorNuevo, Descripcion)
        VALUES (
            NEW.IdTicket,
            NULL,
            'Estado',
            (SELECT Nombre FROM EstadosTicket WHERE IdEstado = OLD.IdEstado),
            (SELECT Nombre FROM EstadosTicket WHERE IdEstado = NEW.IdEstado),
            CONCAT('Estado cambiado de "', 
                   (SELECT Nombre FROM EstadosTicket WHERE IdEstado = OLD.IdEstado),
                   '" a "',
                   (SELECT Nombre FROM EstadosTicket WHERE IdEstado = NEW.IdEstado),
                   '"')
        );
    END IF;
    
    IF OLD.IdPrioridad != NEW.IdPrioridad THEN
        INSERT INTO HistorialTicket (IdTicket, IdUsuario, TipoCambio, ValorAnterior, ValorNuevo, Descripcion)
        VALUES (
            NEW.IdTicket,
            NULL,
            'Prioridad',
            (SELECT Nombre FROM PrioridadesTicket WHERE IdPrioridad = OLD.IdPrioridad),
            (SELECT Nombre FROM PrioridadesTicket WHERE IdPrioridad = NEW.IdPrioridad),
            CONCAT('Prioridad cambiada de "', 
                   (SELECT Nombre FROM PrioridadesTicket WHERE IdPrioridad = OLD.IdPrioridad),
                   '" a "',
                   (SELECT Nombre FROM PrioridadesTicket WHERE IdPrioridad = NEW.IdPrioridad),
                   '"')
        );
    END IF;
    
    IF COALESCE(OLD.IdAsignadoA, 0) != COALESCE(NEW.IdAsignadoA, 0) THEN
        INSERT INTO HistorialTicket (IdTicket, IdUsuario, TipoCambio, ValorAnterior, ValorNuevo, Descripcion)
        VALUES (
            NEW.IdTicket,
            NULL,
            'Asignacion',
            COALESCE((SELECT nombre FROM usuarios WHERE id = OLD.IdAsignadoA), 'Sin asignar'),
            COALESCE((SELECT nombre FROM usuarios WHERE id = NEW.IdAsignadoA), 'Sin asignar'),
            CONCAT('Ticket ',
                   CASE 
                       WHEN OLD.IdAsignadoA IS NULL THEN 'asignado a '
                       WHEN NEW.IdAsignadoA IS NULL THEN 'desasignado'
                       ELSE 'reasignado a '
                   END,
                   COALESCE((SELECT nombre FROM usuarios WHERE id = NEW.IdAsignadoA), ''))
        );
    END IF;
    
    IF OLD.IdCategoria != NEW.IdCategoria THEN
        INSERT INTO HistorialTicket (IdTicket, IdUsuario, TipoCambio, ValorAnterior, ValorNuevo, Descripcion)
        VALUES (
            NEW.IdTicket,
            NULL,
            'Categoria',
            (SELECT Nombre FROM CategoriasTicket WHERE IdCategoria = OLD.IdCategoria),
            (SELECT Nombre FROM CategoriasTicket WHERE IdCategoria = NEW.IdCategoria),
            CONCAT('Categoría cambiada de "', 
                   (SELECT Nombre FROM CategoriasTicket WHERE IdCategoria = OLD.IdCategoria),
                   '" a "',
                   (SELECT Nombre FROM CategoriasTicket WHERE IdCategoria = NEW.IdCategoria),
                   '"')
        );
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `tiposervicio`
--

DROP TABLE IF EXISTS `tiposervicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tiposervicio` (
  `IdTipoServicio` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `IdCategoria` int NOT NULL,
  PRIMARY KEY (`IdTipoServicio`),
  KEY `FK_TipoServicio_Categoria` (`IdCategoria`),
  CONSTRAINT `FK_TipoServicio_Categoria` FOREIGN KEY (`IdCategoria`) REFERENCES `categoria` (`IdCategoria`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ubicacion`
--

DROP TABLE IF EXISTS `ubicacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ubicacion` (
  `IdUbicacion` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`IdUbicacion`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `IdUsuario` int NOT NULL AUTO_INCREMENT,
  `NombreUsuario` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ApellidoPaterno` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ApellidoMaterno` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `NumeroTelefono` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Correo` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Contrasena` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Estatus` tinyint(1) NOT NULL DEFAULT '1',
  `PrimerLogin` tinyint(1) NOT NULL DEFAULT '1',
  `IdRol` int NOT NULL,
  `IdDepartamento` int DEFAULT NULL,
  `TipoUsuario` enum('administrador','empleado') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'empleado',
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `IntentosFallidos` int NOT NULL DEFAULT '0',
  `BloqueadoHasta` datetime DEFAULT NULL,
  `EstadoRegistro` tinyint DEFAULT '1' COMMENT '0=Inactivo, 1=Activo, 2=Eliminado',
  PRIMARY KEY (`IdUsuario`),
  UNIQUE KEY `NombreUsuario` (`NombreUsuario`),
  UNIQUE KEY `Correo` (`Correo`),
  KEY `FK_Usuario_Rol` (`IdRol`),
  KEY `idx_usuario_username` (`NombreUsuario`),
  KEY `idx_usuario_correo` (`Correo`),
  KEY `FK_Usuario_Departamento` (`IdDepartamento`),
  CONSTRAINT `FK_Usuario_Departamento` FOREIGN KEY (`IdDepartamento`) REFERENCES `departamentos` (`id`) ON DELETE SET NULL,
  CONSTRAINT `FK_Usuario_Rol` FOREIGN KEY (`IdRol`) REFERENCES `rol` (`IdRol`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(64) NOT NULL,
  `email` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `nombre` varchar(120) NOT NULL,
  `password_hash` varchar(256) DEFAULT NULL,
  `rol` varchar(30) NOT NULL DEFAULT 'viewer',
  `departamento_id` int DEFAULT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `primer_login` tinyint(1) NOT NULL DEFAULT '1',
  `creado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`),
  KEY `fk_usuario_depto` (`departamento_id`),
  CONSTRAINT `fk_usuario_depto` FOREIGN KEY (`departamento_id`) REFERENCES `departamentos` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usuarios_backup`
--

DROP TABLE IF EXISTS `usuarios_backup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios_backup` (
  `id` int NOT NULL DEFAULT '0',
  `username` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `email` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `nombre` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `password_hash` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `rol` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'viewer',
  `departamento_id` int DEFAULT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `primer_login` tinyint(1) NOT NULL DEFAULT '1',
  `creado_en` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `v_activos`
--

DROP TABLE IF EXISTS `v_activos`;
/*!50001 DROP VIEW IF EXISTS `v_activos`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_activos` AS SELECT 
 1 AS `id`,
 1 AS `nombre`,
 1 AS `descripcion`,
 1 AS `numero_serie`,
 1 AS `categoria`,
 1 AS `estado`,
 1 AS `valor`,
 1 AS `fecha_adquisicion`,
 1 AS `creado_en`,
 1 AS `actualizado_en`,
 1 AS `departamento_id`,
 1 AS `departamento_nombre`,
 1 AS `usuario_id`,
 1 AS `responsable_nombre`,
 1 AS `responsable_email`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_activos_por_area`
--

DROP TABLE IF EXISTS `v_activos_por_area`;
/*!50001 DROP VIEW IF EXISTS `v_activos_por_area`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_activos_por_area` AS SELECT 
 1 AS `IdDepartamento`,
 1 AS `Area`,
 1 AS `TipoActivo`,
 1 AS `IdActivo`,
 1 AS `NombreActivo`,
 1 AS `NumeroSerie`,
 1 AS `Estado`,
 1 AS `Condicion`,
 1 AS `Valor`,
 1 AS `AsignadoA`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_activos_por_departamento`
--

DROP TABLE IF EXISTS `v_activos_por_departamento`;
/*!50001 DROP VIEW IF EXISTS `v_activos_por_departamento`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_activos_por_departamento` AS SELECT 
 1 AS `departamento_id`,
 1 AS `departamento`,
 1 AS `total_activos`,
 1 AS `activos`,
 1 AS `bajas`,
 1 AS `en_mantenimiento`,
 1 AS `valor_total`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_activos_por_usuario`
--

DROP TABLE IF EXISTS `v_activos_por_usuario`;
/*!50001 DROP VIEW IF EXISTS `v_activos_por_usuario`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_activos_por_usuario` AS SELECT 
 1 AS `IdUsuario`,
 1 AS `NombreCompleto`,
 1 AS `Correo`,
 1 AS `Rol`,
 1 AS `TipoActivo`,
 1 AS `IdActivo`,
 1 AS `NombreActivo`,
 1 AS `NumeroSerie`,
 1 AS `Estado`,
 1 AS `Condicion`,
 1 AS `Valor`,
 1 AS `FechaAdquisicion`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_activos_unificado`
--

DROP TABLE IF EXISTS `v_activos_unificado`;
/*!50001 DROP VIEW IF EXISTS `v_activos_unificado`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_activos_unificado` AS SELECT 
 1 AS `id_unico`,
 1 AS `id_origen`,
 1 AS `origen`,
 1 AS `nombre`,
 1 AS `numero_serie`,
 1 AS `descripcion`,
 1 AS `categoria`,
 1 AS `estado`,
 1 AS `valor`,
 1 AS `fecha_adquisicion`,
 1 AS `departamento_id`,
 1 AS `departamento_nombre`,
 1 AS `usuario_id`,
 1 AS `creado_en`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_adjuntos_ticket`
--

DROP TABLE IF EXISTS `v_adjuntos_ticket`;
/*!50001 DROP VIEW IF EXISTS `v_adjuntos_ticket`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_adjuntos_ticket` AS SELECT 
 1 AS `IdAdjunto`,
 1 AS `IdTicket`,
 1 AS `IdUsuario`,
 1 AS `NombreUsuario`,
 1 AS `NombreArchivo`,
 1 AS `NombreOriginal`,
 1 AS `RutaArchivo`,
 1 AS `TipoMIME`,
 1 AS `TamanoKB`,
 1 AS `FechaSubida`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `v_alertas_mantenimiento`
--

DROP TABLE IF EXISTS `v_alertas_mantenimiento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `v_alertas_mantenimiento` (
  `IdMantenimiento` int NOT NULL AUTO_INCREMENT,
  `ProximoKilometraje` int DEFAULT NULL,
  `ProximaFecha` date DEFAULT NULL,
  `Estatus` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `TipoServicio` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `IdVehiculo` int DEFAULT NULL,
  `VehiculoNombre` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Matricula` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `KilometrajeActual` int DEFAULT NULL,
  `AlertaKilometraje` int DEFAULT NULL,
  `KmRestantes` int DEFAULT NULL,
  `AlertaFecha` int DEFAULT NULL,
  `DiasRestantes` int DEFAULT NULL,
  PRIMARY KEY (`IdMantenimiento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `v_auditoria_resguardo`
--

DROP TABLE IF EXISTS `v_auditoria_resguardo`;
/*!50001 DROP VIEW IF EXISTS `v_auditoria_resguardo`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_auditoria_resguardo` AS SELECT 
 1 AS `TipoActivo`,
 1 AS `IdActivo`,
 1 AS `Nombre`,
 1 AS `NombreActivo`,
 1 AS `NumeroSerie`,
 1 AS `Estado`,
 1 AS `Condicion`,
 1 AS `Valor`,
 1 AS `AsignadoA`,
 1 AS `Correo`,
 1 AS `Ubicacion`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_bajas_activos`
--

DROP TABLE IF EXISTS `v_bajas_activos`;
/*!50001 DROP VIEW IF EXISTS `v_bajas_activos`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_bajas_activos` AS SELECT 
 1 AS `IdBaja`,
 1 AS `TipoActivo`,
 1 AS `IdActivo`,
 1 AS `NombreActivo`,
 1 AS `DadoDeBajaPor`,
 1 AS `FechaBaja`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_comentarios_ticket`
--

DROP TABLE IF EXISTS `v_comentarios_ticket`;
/*!50001 DROP VIEW IF EXISTS `v_comentarios_ticket`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_comentarios_ticket` AS SELECT 
 1 AS `IdComentario`,
 1 AS `IdTicket`,
 1 AS `IdUsuario`,
 1 AS `NombreUsuario`,
 1 AS `EmailUsuario`,
 1 AS `Comentario`,
 1 AS `EsInterno`,
 1 AS `EsRespuestaOficial`,
 1 AS `FechaCreacion`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_dashboard_stats`
--

DROP TABLE IF EXISTS `v_dashboard_stats`;
/*!50001 DROP VIEW IF EXISTS `v_dashboard_stats`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_dashboard_stats` AS SELECT 
 1 AS `total_activos`,
 1 AS `activos`,
 1 AS `bajas`,
 1 AS `en_mantenimiento`,
 1 AS `valor_total`,
 1 AS `valor_promedio`,
 1 AS `departamentos_con_activos`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_departamentos`
--

DROP TABLE IF EXISTS `v_departamentos`;
/*!50001 DROP VIEW IF EXISTS `v_departamentos`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_departamentos` AS SELECT 
 1 AS `id`,
 1 AS `nombre`,
 1 AS `descripcion`,
 1 AS `creado_en`,
 1 AS `total_activos`,
 1 AS `valor_total`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_documentos_usuario`
--

DROP TABLE IF EXISTS `v_documentos_usuario`;
/*!50001 DROP VIEW IF EXISTS `v_documentos_usuario`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_documentos_usuario` AS SELECT 
 1 AS `IdDocumento`,
 1 AS `IdUsuario`,
 1 AS `TipoDocumento`,
 1 AS `NombreArchivo`,
 1 AS `ArchivoUrl`,
 1 AS `TipoArchivo`,
 1 AS `FechaEmision`,
 1 AS `FechaVencimiento`,
 1 AS `Vigente`,
 1 AS `NumeroDocumento`,
 1 AS `Descripcion`,
 1 AS `CreadoEn`,
 1 AS `UsuarioNombre`,
 1 AS `ApellidoPaterno`,
 1 AS `Correo`,
 1 AS `DiasParaVencer`,
 1 AS `EstadoDocumento`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_empleado_activos_completo`
--

DROP TABLE IF EXISTS `v_empleado_activos_completo`;
/*!50001 DROP VIEW IF EXISTS `v_empleado_activos_completo`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_empleado_activos_completo` AS SELECT 
 1 AS `IdUsuario`,
 1 AS `NombreCompleto`,
 1 AS `Correo`,
 1 AS `Rol`,
 1 AS `TipoActivo`,
 1 AS `IdActivo`,
 1 AS `NombreActivo`,
 1 AS `NumeroSerie`,
 1 AS `Estado`,
 1 AS `Condicion`,
 1 AS `Valor`,
 1 AS `FechaAdquisicion`,
 1 AS `IdProyecto`,
 1 AS `NombreProyecto`,
 1 AS `EstatusProyecto`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_equipos_consolidado`
--

DROP TABLE IF EXISTS `v_equipos_consolidado`;
/*!50001 DROP VIEW IF EXISTS `v_equipos_consolidado`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_equipos_consolidado` AS SELECT 
 1 AS `IdEquipo`,
 1 AS `NombreEquipo`,
 1 AS `TipoEquipo`,
 1 AS `Marca`,
 1 AS `Modelo`,
 1 AS `NumeroSerie`,
 1 AS `EstadoEquipo`,
 1 AS `Condicion`,
 1 AS `Costo`,
 1 AS `FechaAdquisicion`,
 1 AS `IdUsuario`,
 1 AS `NombreUsuario`,
 1 AS `CorreoUsuario`,
 1 AS `NumeroTelefono`,
 1 AS `NombreRol`,
 1 AS `IdDepartamento`,
 1 AS `NombreDepartamento`,
 1 AS `IdProyecto`,
 1 AS `NombreProyecto`,
 1 AS `EstatusProyecto`,
 1 AS `ProyectoFechaInicio`,
 1 AS `ProyectoFechaTermino`,
 1 AS `RolEnProyecto`,
 1 AS `IdProyectoEquipo`,
 1 AS `NombreProyectoEquipo`,
 1 AS `EstadoInicialEquipo`,
 1 AS `FechaAsignacionProyecto`,
 1 AS `FechaDevolucionProyecto`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_equipos_ti`
--

DROP TABLE IF EXISTS `v_equipos_ti`;
/*!50001 DROP VIEW IF EXISTS `v_equipos_ti`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_equipos_ti` AS SELECT 
 1 AS `IdElectronico`,
 1 AS `Nombre`,
 1 AS `Marca`,
 1 AS `Modelo`,
 1 AS `MarcaModelo`,
 1 AS `NumeroSerie`,
 1 AS `TipoEquipo`,
 1 AS `Estado`,
 1 AS `Condicion`,
 1 AS `Costo`,
 1 AS `Valor`,
 1 AS `FechaAdquisicion`,
 1 AS `Descripcion`,
 1 AS `UsuarioNombre`,
 1 AS `UsuarioCorreo`,
 1 AS `UsuarioRol`,
 1 AS `UbicacionNombre`,
 1 AS `MantenimientosActivos`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_equipos_usuario`
--

DROP TABLE IF EXISTS `v_equipos_usuario`;
/*!50001 DROP VIEW IF EXISTS `v_equipos_usuario`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_equipos_usuario` AS SELECT 
 1 AS `IdEquipo`,
 1 AS `IdUsuario`,
 1 AS `Nombre`,
 1 AS `Marca`,
 1 AS `Modelo`,
 1 AS `MarcaModelo`,
 1 AS `TipoEquipo`,
 1 AS `NumeroSerie`,
 1 AS `Estado`,
 1 AS `Condicion`,
 1 AS `Valor`,
 1 AS `FechaAdquisicion`,
 1 AS `UsuarioNombre`,
 1 AS `ApellidoPaterno`,
 1 AS `Correo`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_estadisticas_ti`
--

DROP TABLE IF EXISTS `v_estadisticas_ti`;
/*!50001 DROP VIEW IF EXISTS `v_estadisticas_ti`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_estadisticas_ti` AS SELECT 
 1 AS `TotalEquipos`,
 1 AS `EnAlmacen`,
 1 AS `Asignados`,
 1 AS `EnMantenimiento`,
 1 AS `Bajas`,
 1 AS `EnBuenEstado`,
 1 AS `EnMalEstado`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_estado_documentos_usuario`
--

DROP TABLE IF EXISTS `v_estado_documentos_usuario`;
/*!50001 DROP VIEW IF EXISTS `v_estado_documentos_usuario`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_estado_documentos_usuario` AS SELECT 
 1 AS `IdUsuario`,
 1 AS `Nombre`,
 1 AS `ApellidoPaterno`,
 1 AS `Correo`,
 1 AS `DocsVencidos`,
 1 AS `DocsPorVencer`,
 1 AS `DocsVigentes`,
 1 AS `TotalDocumentos`,
 1 AS `EstadoGeneral`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_expediente_empleado`
--

DROP TABLE IF EXISTS `v_expediente_empleado`;
/*!50001 DROP VIEW IF EXISTS `v_expediente_empleado`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_expediente_empleado` AS SELECT 
 1 AS `IdUsuario`,
 1 AS `NombreUsuario`,
 1 AS `Nombre`,
 1 AS `ApellidoPaterno`,
 1 AS `ApellidoMaterno`,
 1 AS `Correo`,
 1 AS `NumeroTelefono`,
 1 AS `IdRol`,
 1 AS `TipoUsuario`,
 1 AS `TotalEquipos`,
 1 AS `TotalVehiculos`,
 1 AS `TotalActivos`,
 1 AS `ValorTotal`,
 1 AS `DocsVencidos`,
 1 AS `DocsPorVencer`,
 1 AS `DocsVigentes`,
 1 AS `TotalDocumentos`,
 1 AS `EstadoDocumentos`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_herramientas_disponibles`
--

DROP TABLE IF EXISTS `v_herramientas_disponibles`;
/*!50001 DROP VIEW IF EXISTS `v_herramientas_disponibles`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_herramientas_disponibles` AS SELECT 
 1 AS `IdHerramienta`,
 1 AS `Nombre`,
 1 AS `Marca`,
 1 AS `Modelo`,
 1 AS `NumeroSerie`,
 1 AS `Costo`,
 1 AS `FechaAlta`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_historial_asignaciones`
--

DROP TABLE IF EXISTS `v_historial_asignaciones`;
/*!50001 DROP VIEW IF EXISTS `v_historial_asignaciones`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_historial_asignaciones` AS SELECT 
 1 AS `IdAsignacion`,
 1 AS `IdHerramienta`,
 1 AS `HerramientaNombre`,
 1 AS `NumeroSerie`,
 1 AS `UsuarioNombre`,
 1 AS `UsuarioCorreo`,
 1 AS `FechaAsignacion`,
 1 AS `FechaDevolucion`,
 1 AS `Observaciones`,
 1 AS `AsignadoPorNombre`,
 1 AS `RecibidoPorNombre`,
 1 AS `EstadoAsignacion`,
 1 AS `EstadoHerramienta`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_inventario`
--

DROP TABLE IF EXISTS `v_inventario`;
/*!50001 DROP VIEW IF EXISTS `v_inventario`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_inventario` AS SELECT 
 1 AS `IdHerramienta`,
 1 AS `Nombre`,
 1 AS `Marca`,
 1 AS `Modelo`,
 1 AS `NumeroSerie`,
 1 AS `Estado`,
 1 AS `Costo`,
 1 AS `FechaAlta`,
 1 AS `Descripcion`,
 1 AS `UsuarioAsignado`,
 1 AS `FechaAsignacion`,
 1 AS `TotalReportes`,
 1 AS `TotalEvidencias`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_mantenimiento_electronico`
--

DROP TABLE IF EXISTS `v_mantenimiento_electronico`;
/*!50001 DROP VIEW IF EXISTS `v_mantenimiento_electronico`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_mantenimiento_electronico` AS SELECT 
 1 AS `IdMantenimiento`,
 1 AS `Tipo`,
 1 AS `Diagnostico`,
 1 AS `Descripcion`,
 1 AS `FechaInicio`,
 1 AS `FechaTermino`,
 1 AS `Costo`,
 1 AS `Tecnico`,
 1 AS `Estatus`,
 1 AS `CreadoEn`,
 1 AS `IdElectronico`,
 1 AS `EquipoNombre`,
 1 AS `NumeroSerie`,
 1 AS `TipoEquipo`,
 1 AS `CreadoPorNombre`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_mantenimiento_vehiculo`
--

DROP TABLE IF EXISTS `v_mantenimiento_vehiculo`;
/*!50001 DROP VIEW IF EXISTS `v_mantenimiento_vehiculo`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_mantenimiento_vehiculo` AS SELECT 
 1 AS `id`,
 1 AS `tipo_servicio`,
 1 AS `descripcion`,
 1 AS `fecha_inicio`,
 1 AS `fecha_entrega`,
 1 AS `kilometraje`,
 1 AS `costo`,
 1 AS `proveedor`,
 1 AS `estatus`,
 1 AS `creado_en`,
 1 AS `vehiculo_id`,
 1 AS `vehiculo_nombre`,
 1 AS `matricula`,
 1 AS `personal_nombre`,
 1 AS `creado_por_nombre`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_metricas_ticketing`
--

DROP TABLE IF EXISTS `v_metricas_ticketing`;
/*!50001 DROP VIEW IF EXISTS `v_metricas_ticketing`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_metricas_ticketing` AS SELECT 
 1 AS `TotalTickets`,
 1 AS `TotalAbiertos`,
 1 AS `TotalEnProceso`,
 1 AS `TotalResueltos`,
 1 AS `TotalCerrados`,
 1 AS `CerradosHoy`,
 1 AS `TotalUrgentes`,
 1 AS `TotalAlta`,
 1 AS `TotalMedia`,
 1 AS `TotalBaja`,
 1 AS `SinAsignar`,
 1 AS `PromedioHorasCierre`,
 1 AS `PromedioHorasRespuesta`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_mis_tickets`
--

DROP TABLE IF EXISTS `v_mis_tickets`;
/*!50001 DROP VIEW IF EXISTS `v_mis_tickets`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_mis_tickets` AS SELECT 
 1 AS `IdTicket`,
 1 AS `NumeroTicket`,
 1 AS `Titulo`,
 1 AS `Categoria`,
 1 AS `CategoriaColor`,
 1 AS `Prioridad`,
 1 AS `PrioridadColor`,
 1 AS `Estado`,
 1 AS `EstadoColor`,
 1 AS `AsignadoA`,
 1 AS `FechaCreacion`,
 1 AS `FechaUltimaActualizacion`,
 1 AS `TotalComentarios`,
 1 AS `ComentariosPublicos`,
 1 AS `TotalAdjuntos`,
 1 AS `IdUsuarioCreador`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_permisos_rol`
--

DROP TABLE IF EXISTS `v_permisos_rol`;
/*!50001 DROP VIEW IF EXISTS `v_permisos_rol`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_permisos_rol` AS SELECT 
 1 AS `IdRol`,
 1 AS `NombreRol`,
 1 AS `IdModulo`,
 1 AS `Modulo`,
 1 AS `ModuloDesc`,
 1 AS `Icono`,
 1 AS `Orden`,
 1 AS `PuedeVer`,
 1 AS `PuedeCrear`,
 1 AS `PuedeEditar`,
 1 AS `PuedeEliminar`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_permisos_usuario`
--

DROP TABLE IF EXISTS `v_permisos_usuario`;
/*!50001 DROP VIEW IF EXISTS `v_permisos_usuario`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_permisos_usuario` AS SELECT 
 1 AS `IdUsuario`,
 1 AS `NombreUsuario`,
 1 AS `NombreCompleto`,
 1 AS `NombreRol`,
 1 AS `IdModulo`,
 1 AS `Modulo`,
 1 AS `ModuloDesc`,
 1 AS `Icono`,
 1 AS `Orden`,
 1 AS `PuedeVer`,
 1 AS `PuedeCrear`,
 1 AS `PuedeEditar`,
 1 AS `PuedeEliminar`,
 1 AS `EsPersonalizado`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_permisos_vehiculo`
--

DROP TABLE IF EXISTS `v_permisos_vehiculo`;
/*!50001 DROP VIEW IF EXISTS `v_permisos_vehiculo`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_permisos_vehiculo` AS SELECT 
 1 AS `IdPermiso`,
 1 AS `IdVehiculo`,
 1 AS `IdTipoServicio`,
 1 AS `TipoServicio`,
 1 AS `Descripcion`,
 1 AS `Numero`,
 1 AS `FechaInicio`,
 1 AS `FechaVencimiento`,
 1 AS `ArchivoUrl`,
 1 AS `CreadoEn`,
 1 AS `VehiculoNombre`,
 1 AS `Marca`,
 1 AS `Modelo`,
 1 AS `Matricula`,
 1 AS `DiasParaVencer`,
 1 AS `EstadoPermiso`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_permisos_vencer`
--

DROP TABLE IF EXISTS `v_permisos_vencer`;
/*!50001 DROP VIEW IF EXISTS `v_permisos_vencer`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_permisos_vencer` AS SELECT 
 1 AS `id`,
 1 AS `tipo`,
 1 AS `descripcion`,
 1 AS `numero`,
 1 AS `fecha_vencimiento`,
 1 AS `dias_restantes`,
 1 AS `vehiculo_id`,
 1 AS `vehiculo_nombre`,
 1 AS `matricula`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_procesos_baja`
--

DROP TABLE IF EXISTS `v_procesos_baja`;
/*!50001 DROP VIEW IF EXISTS `v_procesos_baja`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_procesos_baja` AS SELECT 
 1 AS `IdBaja`,
 1 AS `Estatus`,
 1 AS `FechaAviso`,
 1 AS `FechaBaja`,
 1 AS `Motivo`,
 1 AS `Observaciones`,
 1 AS `CreadoEn`,
 1 AS `Empleado`,
 1 AS `CorreoEmpleado`,
 1 AS `RolEmpleado`,
 1 AS `SolicitadoPorNombre`,
 1 AS `AutorizadoPorNombre`,
 1 AS `FechaAutorizacion`,
 1 AS `TotalActivosRetirados`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_proyecto_detalle_completo`
--

DROP TABLE IF EXISTS `v_proyecto_detalle_completo`;
/*!50001 DROP VIEW IF EXISTS `v_proyecto_detalle_completo`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_proyecto_detalle_completo` AS SELECT 
 1 AS `IdProyecto`,
 1 AS `NombreProyecto`,
 1 AS `EstatusProyecto`,
 1 AS `FechaInicio`,
 1 AS `FechaTermino`,
 1 AS `IdUsuario`,
 1 AS `NombrePersonal`,
 1 AS `Correo`,
 1 AS `NombreRol`,
 1 AS `RolEnProyecto`,
 1 AS `IdDepartamento`,
 1 AS `Departamento`,
 1 AS `IdAsignacionActivo`,
 1 AS `TipoActivo`,
 1 AS `IdActivo`,
 1 AS `EstadoInicial`,
 1 AS `FechaAsignacionActivo`,
 1 AS `FechaDevolucion`,
 1 AS `ObservacionesActivo`,
 1 AS `NombreActivo`,
 1 AS `SerieActivo`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_proyectos`
--

DROP TABLE IF EXISTS `v_proyectos`;
/*!50001 DROP VIEW IF EXISTS `v_proyectos`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_proyectos` AS SELECT 
 1 AS `IdProyecto`,
 1 AS `Nombre`,
 1 AS `Descripcion`,
 1 AS `FechaInicio`,
 1 AS `FechaTermino`,
 1 AS `Estatus`,
 1 AS `CreadoEn`,
 1 AS `CreadoPorNombre`,
 1 AS `DiasRestantes`,
 1 AS `TotalPersonal`,
 1 AS `TotalActivos`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_resumen_activos_usuario`
--

DROP TABLE IF EXISTS `v_resumen_activos_usuario`;
/*!50001 DROP VIEW IF EXISTS `v_resumen_activos_usuario`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_resumen_activos_usuario` AS SELECT 
 1 AS `IdUsuario`,
 1 AS `Nombre`,
 1 AS `ApellidoPaterno`,
 1 AS `Correo`,
 1 AS `IdRol`,
 1 AS `TotalEquipos`,
 1 AS `TotalVehiculos`,
 1 AS `TotalActivos`,
 1 AS `ValorTotal`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_tecnicos_ti`
--

DROP TABLE IF EXISTS `v_tecnicos_ti`;
/*!50001 DROP VIEW IF EXISTS `v_tecnicos_ti`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_tecnicos_ti` AS SELECT 
 1 AS `IdUsuario`,
 1 AS `NombreUsuario`,
 1 AS `NombreCompleto`,
 1 AS `Correo`,
 1 AS `NumeroTelefono`,
 1 AS `Estatus`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_tickets_abiertos`
--

DROP TABLE IF EXISTS `v_tickets_abiertos`;
/*!50001 DROP VIEW IF EXISTS `v_tickets_abiertos`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_tickets_abiertos` AS SELECT 
 1 AS `IdTicket`,
 1 AS `NumeroTicket`,
 1 AS `Titulo`,
 1 AS `UsuarioCreador`,
 1 AS `EmailCreador`,
 1 AS `Categoria`,
 1 AS `CategoriaColor`,
 1 AS `Prioridad`,
 1 AS `PrioridadColor`,
 1 AS `PrioridadNivel`,
 1 AS `Estado`,
 1 AS `EstadoColor`,
 1 AS `AsignadoA`,
 1 AS `FechaCreacion`,
 1 AS `FechaUltimaActualizacion`,
 1 AS `HorasHastaPrimeraRespuesta`,
 1 AS `TiempoRespuestaHoras`,
 1 AS `SLARespuestaCumplido`,
 1 AS `TotalComentarios`,
 1 AS `TotalAdjuntos`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_tickets_activos`
--

DROP TABLE IF EXISTS `v_tickets_activos`;
/*!50001 DROP VIEW IF EXISTS `v_tickets_activos`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_tickets_activos` AS SELECT 
 1 AS `IdTicket`,
 1 AS `NumeroTicket`,
 1 AS `Titulo`,
 1 AS `Descripcion`,
 1 AS `IdUsuarioCreador`,
 1 AS `UsuarioCreador`,
 1 AS `EmailCreador`,
 1 AS `IdCategoria`,
 1 AS `Categoria`,
 1 AS `CategoriaColor`,
 1 AS `CategoriaIcono`,
 1 AS `IdPrioridad`,
 1 AS `Prioridad`,
 1 AS `PrioridadColor`,
 1 AS `PrioridadNivel`,
 1 AS `TiempoRespuestaHoras`,
 1 AS `IdEstado`,
 1 AS `Estado`,
 1 AS `EstadoColor`,
 1 AS `EsEstadoFinal`,
 1 AS `IdAsignadoA`,
 1 AS `AsignadoA`,
 1 AS `EmailAsignado`,
 1 AS `FechaCreacion`,
 1 AS `FechaUltimaActualizacion`,
 1 AS `FechaPrimeraRespuesta`,
 1 AS `FechaResolucion`,
 1 AS `FechaCierre`,
 1 AS `SLARespuestaCumplido`,
 1 AS `IdDepartamento`,
 1 AS `IdSede`,
 1 AS `IdEquipo`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_tickets_asignados`
--

DROP TABLE IF EXISTS `v_tickets_asignados`;
/*!50001 DROP VIEW IF EXISTS `v_tickets_asignados`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_tickets_asignados` AS SELECT 
 1 AS `IdTicket`,
 1 AS `NumeroTicket`,
 1 AS `Titulo`,
 1 AS `UsuarioCreador`,
 1 AS `EmailCreador`,
 1 AS `Categoria`,
 1 AS `CategoriaColor`,
 1 AS `Prioridad`,
 1 AS `PrioridadColor`,
 1 AS `Estado`,
 1 AS `EstadoColor`,
 1 AS `FechaCreacion`,
 1 AS `HorasHastaPrimeraRespuesta`,
 1 AS `HorasHastaResolucion`,
 1 AS `TiempoRespuestaHoras`,
 1 AS `SLARespuestaCumplido`,
 1 AS `TotalComentarios`,
 1 AS `IdAsignadoA`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_tickets_completo`
--

DROP TABLE IF EXISTS `v_tickets_completo`;
/*!50001 DROP VIEW IF EXISTS `v_tickets_completo`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_tickets_completo` AS SELECT 
 1 AS `IdTicket`,
 1 AS `NumeroTicket`,
 1 AS `Titulo`,
 1 AS `Descripcion`,
 1 AS `IdUsuarioCreador`,
 1 AS `UsuarioCreador`,
 1 AS `EmailCreador`,
 1 AS `DepartamentoCreadorId`,
 1 AS `IdCategoria`,
 1 AS `Categoria`,
 1 AS `CategoriaIcono`,
 1 AS `CategoriaColor`,
 1 AS `IdPrioridad`,
 1 AS `Prioridad`,
 1 AS `PrioridadColor`,
 1 AS `PrioridadNivel`,
 1 AS `TiempoRespuestaHoras`,
 1 AS `IdEstado`,
 1 AS `Estado`,
 1 AS `EstadoColor`,
 1 AS `EsEstadoFinal`,
 1 AS `IdEquipo`,
 1 AS `IdAsignadoA`,
 1 AS `AsignadoA`,
 1 AS `EmailAsignado`,
 1 AS `IdSede`,
 1 AS `IdDepartamento`,
 1 AS `CanalCreacion`,
 1 AS `FechaCreacion`,
 1 AS `FechaUltimaActualizacion`,
 1 AS `FechaPrimeraRespuesta`,
 1 AS `FechaResolucion`,
 1 AS `FechaCierre`,
 1 AS `CalificacionServicio`,
 1 AS `ComentarioSatisfaccion`,
 1 AS `HorasHastaPrimeraRespuesta`,
 1 AS `HorasHastaResolucion`,
 1 AS `HorasHastaCierre`,
 1 AS `SLARespuestaCumplido`,
 1 AS `TotalComentarios`,
 1 AS `ComentariosPublicos`,
 1 AS `TotalAdjuntos`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_tickets_dashboard`
--

DROP TABLE IF EXISTS `v_tickets_dashboard`;
/*!50001 DROP VIEW IF EXISTS `v_tickets_dashboard`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_tickets_dashboard` AS SELECT 
 1 AS `IdTicket`,
 1 AS `NumeroTicket`,
 1 AS `Titulo`,
 1 AS `Descripcion`,
 1 AS `IdUsuarioCreador`,
 1 AS `UsuarioCreador`,
 1 AS `EmailCreador`,
 1 AS `IdCategoria`,
 1 AS `Categoria`,
 1 AS `CategoriaColor`,
 1 AS `CategoriaIcono`,
 1 AS `IdPrioridad`,
 1 AS `Prioridad`,
 1 AS `PrioridadColor`,
 1 AS `PrioridadNivel`,
 1 AS `TiempoRespuestaHoras`,
 1 AS `IdEstado`,
 1 AS `Estado`,
 1 AS `EstadoColor`,
 1 AS `EsEstadoFinal`,
 1 AS `IdAsignadoA`,
 1 AS `AsignadoA`,
 1 AS `EmailAsignado`,
 1 AS `FechaCreacion`,
 1 AS `FechaUltimaActualizacion`,
 1 AS `FechaPrimeraRespuesta`,
 1 AS `FechaResolucion`,
 1 AS `FechaCierre`,
 1 AS `SLARespuestaCumplido`,
 1 AS `IdDepartamento`,
 1 AS `IdSede`,
 1 AS `IdEquipo`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_tickets_dashboard_ti`
--

DROP TABLE IF EXISTS `v_tickets_dashboard_ti`;
/*!50001 DROP VIEW IF EXISTS `v_tickets_dashboard_ti`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_tickets_dashboard_ti` AS SELECT 
 1 AS `IdTicket`,
 1 AS `NumeroTicket`,
 1 AS `Titulo`,
 1 AS `Descripcion`,
 1 AS `IdUsuarioCreador`,
 1 AS `UsuarioCreador`,
 1 AS `EmailCreador`,
 1 AS `IdCategoria`,
 1 AS `Categoria`,
 1 AS `CategoriaColor`,
 1 AS `CategoriaIcono`,
 1 AS `IdPrioridad`,
 1 AS `Prioridad`,
 1 AS `PrioridadColor`,
 1 AS `PrioridadNivel`,
 1 AS `TiempoRespuestaHoras`,
 1 AS `IdEstado`,
 1 AS `Estado`,
 1 AS `EstadoColor`,
 1 AS `EsEstadoFinal`,
 1 AS `IdAsignadoA`,
 1 AS `AsignadoA`,
 1 AS `EmailAsignado`,
 1 AS `FechaCreacion`,
 1 AS `FechaUltimaActualizacion`,
 1 AS `FechaPrimeraRespuesta`,
 1 AS `FechaResolucion`,
 1 AS `FechaCierre`,
 1 AS `SLARespuestaCumplido`,
 1 AS `IdDepartamento`,
 1 AS `IdSede`,
 1 AS `IdEquipo`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_tickets_metricas`
--

DROP TABLE IF EXISTS `v_tickets_metricas`;
/*!50001 DROP VIEW IF EXISTS `v_tickets_metricas`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_tickets_metricas` AS SELECT 
 1 AS `TotalTickets`,
 1 AS `TotalAbiertos`,
 1 AS `TotalEnProceso`,
 1 AS `TotalEscalados`,
 1 AS `TotalPendientes`,
 1 AS `TotalResueltos`,
 1 AS `TotalCerrados`,
 1 AS `CerradosHoy`,
 1 AS `TotalUrgentes`,
 1 AS `TotalAlta`,
 1 AS `TotalMedia`,
 1 AS `TotalBaja`,
 1 AS `PromedioHorasRespuesta`,
 1 AS `PromedioHorasResolucion`,
 1 AS `PromedioSatisfaccion`,
 1 AS `TicketsSLACumplido`,
 1 AS `TicketsSLAIncumplido`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_tickets_por_usuario`
--

DROP TABLE IF EXISTS `v_tickets_por_usuario`;
/*!50001 DROP VIEW IF EXISTS `v_tickets_por_usuario`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_tickets_por_usuario` AS SELECT 
 1 AS `IdTicket`,
 1 AS `NumeroTicket`,
 1 AS `Titulo`,
 1 AS `Descripcion`,
 1 AS `IdUsuarioCreador`,
 1 AS `UsuarioCreador`,
 1 AS `EmailCreador`,
 1 AS `IdCategoria`,
 1 AS `Categoria`,
 1 AS `CategoriaColor`,
 1 AS `CategoriaIcono`,
 1 AS `IdPrioridad`,
 1 AS `Prioridad`,
 1 AS `PrioridadColor`,
 1 AS `PrioridadNivel`,
 1 AS `TiempoRespuestaHoras`,
 1 AS `IdEstado`,
 1 AS `Estado`,
 1 AS `EstadoColor`,
 1 AS `EsEstadoFinal`,
 1 AS `IdAsignadoA`,
 1 AS `AsignadoA`,
 1 AS `EmailAsignado`,
 1 AS `FechaCreacion`,
 1 AS `FechaUltimaActualizacion`,
 1 AS `FechaPrimeraRespuesta`,
 1 AS `FechaResolucion`,
 1 AS `FechaCierre`,
 1 AS `SLARespuestaCumplido`,
 1 AS `IdDepartamento`,
 1 AS `IdSede`,
 1 AS `IdEquipo`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_usuarios`
--

DROP TABLE IF EXISTS `v_usuarios`;
/*!50001 DROP VIEW IF EXISTS `v_usuarios`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_usuarios` AS SELECT 
 1 AS `id`,
 1 AS `username`,
 1 AS `email`,
 1 AS `nombre_completo`,
 1 AS `nombre`,
 1 AS `rol`,
 1 AS `activo`,
 1 AS `creado_en`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_usuarios_area`
--

DROP TABLE IF EXISTS `v_usuarios_area`;
/*!50001 DROP VIEW IF EXISTS `v_usuarios_area`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_usuarios_area` AS SELECT 
 1 AS `IdUsuario`,
 1 AS `NombreUsuario`,
 1 AS `NombreCompleto`,
 1 AS `Correo`,
 1 AS `NumeroTelefono`,
 1 AS `Estatus`,
 1 AS `PrimerLogin`,
 1 AS `TipoUsuario`,
 1 AS `IdDepartamento`,
 1 AS `NombreArea`,
 1 AS `IdRol`,
 1 AS `NombreRol`,
 1 AS `IntentosFallidos`,
 1 AS `BloqueadoHasta`,
 1 AS `TieneModulo`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_vehiculos`
--

DROP TABLE IF EXISTS `v_vehiculos`;
/*!50001 DROP VIEW IF EXISTS `v_vehiculos`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_vehiculos` AS SELECT 
 1 AS `id`,
 1 AS `nombre`,
 1 AS `marca`,
 1 AS `modelo`,
 1 AS `matricula`,
 1 AS `kilometraje`,
 1 AS `tipo_adquisicion`,
 1 AS `estado`,
 1 AS `valor`,
 1 AS `fecha_adquisicion`,
 1 AS `ubicacion_nombre`,
 1 AS `conductor_nombre`,
 1 AS `licencia_numero`,
 1 AS `licencia_vigencia`,
 1 AS `permisos_por_vencer`,
 1 AS `mantenimientos_activos`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_vehiculos_usuario`
--

DROP TABLE IF EXISTS `v_vehiculos_usuario`;
/*!50001 DROP VIEW IF EXISTS `v_vehiculos_usuario`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_vehiculos_usuario` AS SELECT 
 1 AS `IdVehiculo`,
 1 AS `IdUsuario`,
 1 AS `VehiculoNombre`,
 1 AS `Marca`,
 1 AS `Modelo`,
 1 AS `Anio`,
 1 AS `Matricula`,
 1 AS `VIN`,
 1 AS `Color`,
 1 AS `Estado`,
 1 AS `Valor`,
 1 AS `Kilometraje`,
 1 AS `FechaAsignacion`,
 1 AS `PolizaSeguro`,
 1 AS `Aseguradora`,
 1 AS `VigenciaSeguro`,
 1 AS `UsuarioNombre`,
 1 AS `ApellidoPaterno`,
 1 AS `Correo`,
 1 AS `EstadoSeguro`,
 1 AS `DiasVigenciaSeguro`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `vehiculo`
--

DROP TABLE IF EXISTS `vehiculo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vehiculo` (
  `IdVehiculo` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `TipoVehiculo` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Marca` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Modelo` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Anio` year DEFAULT NULL,
  `Matricula` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `VIN` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Color` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Kilometraje` int DEFAULT '0',
  `TipoAdquisicion` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `PolizaSeguro` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Aseguradora` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `VigenciaSeguro` date DEFAULT NULL,
  `UltimaVerificacion` date DEFAULT NULL,
  `Accesorios` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Comentarios` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `Arrendamiento` tinyint(1) NOT NULL DEFAULT '0',
  `FechaRenovacion` date DEFAULT NULL,
  `ProveedorArrendamiento` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Estado` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'activo',
  `IdUsuario` int DEFAULT NULL,
  `FechaAsignacion` date DEFAULT NULL,
  `Valor` float NOT NULL DEFAULT '0',
  `FechaAdquisicion` date DEFAULT NULL,
  `IdUbicacion` int DEFAULT NULL,
  `CreadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ActualizadoEn` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdVehiculo`),
  UNIQUE KEY `UQ_Vehiculo_Matricula` (`Matricula`),
  KEY `FK_Vehiculo_Ubicacion` (`IdUbicacion`),
  KEY `fk_vehiculo_usuario` (`IdUsuario`),
  CONSTRAINT `FK_Vehiculo_Ubicacion` FOREIGN KEY (`IdUbicacion`) REFERENCES `ubicacion` (`IdUbicacion`),
  CONSTRAINT `fk_vehiculo_usuario` FOREIGN KEY (`IdUsuario`) REFERENCES `usuario` (`IdUsuario`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vehiculoarchivo`
--

DROP TABLE IF EXISTS `vehiculoarchivo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vehiculoarchivo` (
  `IdArchivo` int NOT NULL AUTO_INCREMENT,
  `IdVehiculo` int NOT NULL,
  `TipoArchivo` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `NombreArchivo` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ArchivoUrl` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `MimeType` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `FechaSubida` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`IdArchivo`),
  KEY `IdVehiculo` (`IdVehiculo`),
  CONSTRAINT `vehiculoarchivo_ibfk_1` FOREIGN KEY (`IdVehiculo`) REFERENCES `vehiculo` (`IdVehiculo`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `v_activos`
--

/*!50001 DROP VIEW IF EXISTS `v_activos`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_activos` AS select `a`.`id` AS `id`,`a`.`nombre` AS `nombre`,`a`.`descripcion` AS `descripcion`,`a`.`numero_serie` AS `numero_serie`,`a`.`categoria` AS `categoria`,`a`.`estado` AS `estado`,`a`.`valor` AS `valor`,`a`.`fecha_adquisicion` AS `fecha_adquisicion`,`a`.`creado_en` AS `creado_en`,`a`.`actualizado_en` AS `actualizado_en`,`a`.`departamento_id` AS `departamento_id`,`d`.`nombre` AS `departamento_nombre`,`a`.`usuario_id` AS `usuario_id`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `responsable_nombre`,`u`.`Correo` AS `responsable_email` from ((`activos` `a` left join `departamentos` `d` on((`a`.`departamento_id` = `d`.`id`))) left join `usuario` `u` on((`a`.`usuario_id` = `u`.`IdUsuario`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_activos_por_area`
--

/*!50001 DROP VIEW IF EXISTS `v_activos_por_area`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_activos_por_area` AS select `d`.`id` AS `IdDepartamento`,convert(`d`.`nombre` using utf8mb4) AS `Area`,convert('electronico' using utf8mb4) AS `TipoActivo`,`e`.`IdElectronico` AS `IdActivo`,convert(`e`.`Nombre` using utf8mb4) AS `NombreActivo`,convert(`e`.`NumeroSerie` using utf8mb4) AS `NumeroSerie`,convert(`e`.`Estado` using utf8mb4) AS `Estado`,convert(`e`.`Condicion` using utf8mb4) AS `Condicion`,`e`.`Costo` AS `Valor`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `AsignadoA` from (((`departamentos` `d` join `activos` `a` on((`a`.`departamento_id` = `d`.`id`))) join `electronico` `e` on((`e`.`IdUsuario` = `a`.`usuario_id`))) left join `usuario` `u` on((`u`.`IdUsuario` = `e`.`IdUsuario`))) union all select `d`.`id` AS `id`,convert(`d`.`nombre` using utf8mb4) AS `CONVERT(d.nombre USING utf8mb4)`,convert('general' using utf8mb4) AS `CONVERT('general' USING utf8mb4)`,`a`.`id` AS `id`,convert(`a`.`nombre` using utf8mb4) AS `CONVERT(a.nombre USING utf8mb4)`,convert(`a`.`numero_serie` using utf8mb4) AS `CONVERT(a.numero_serie USING utf8mb4)`,convert(`a`.`estado` using utf8mb4) AS `CONVERT(a.estado USING utf8mb4)`,NULL AS `NULL`,`a`.`valor` AS `valor`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `CONCAT(u.Nombre,' ',u.ApellidoPaterno)` from ((`departamentos` `d` join `activos` `a` on((`a`.`departamento_id` = `d`.`id`))) left join `usuario` `u` on((`u`.`IdUsuario` = `a`.`usuario_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_activos_por_departamento`
--

/*!50001 DROP VIEW IF EXISTS `v_activos_por_departamento`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_activos_por_departamento` AS select `d`.`id` AS `departamento_id`,`d`.`nombre` AS `departamento`,count(`a`.`id`) AS `total_activos`,sum((case when (`a`.`estado` = 'activo') then 1 else 0 end)) AS `activos`,sum((case when (`a`.`estado` = 'baja') then 1 else 0 end)) AS `bajas`,sum((case when (`a`.`estado` = 'mantenimiento') then 1 else 0 end)) AS `en_mantenimiento`,coalesce(sum(`a`.`valor`),0) AS `valor_total` from (`departamentos` `d` left join `activos` `a` on((`a`.`departamento_id` = `d`.`id`))) group by `d`.`id`,`d`.`nombre` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_activos_por_usuario`
--

/*!50001 DROP VIEW IF EXISTS `v_activos_por_usuario`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_activos_por_usuario` AS select `u`.`IdUsuario` AS `IdUsuario`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `NombreCompleto`,`u`.`Correo` AS `Correo`,`r`.`NombreRol` AS `Rol`,convert('electronico' using utf8mb4) AS `TipoActivo`,`e`.`IdElectronico` AS `IdActivo`,convert(`e`.`Nombre` using utf8mb4) AS `NombreActivo`,convert(`e`.`NumeroSerie` using utf8mb4) AS `NumeroSerie`,convert(`e`.`Estado` using utf8mb4) AS `Estado`,convert(`e`.`Condicion` using utf8mb4) AS `Condicion`,`e`.`Costo` AS `Valor`,`e`.`FechaAdquisicion` AS `FechaAdquisicion` from ((`usuario` `u` join `rol` `r` on((`r`.`IdRol` = `u`.`IdRol`))) join `electronico` `e` on((`e`.`IdUsuario` = `u`.`IdUsuario`))) union all select `u`.`IdUsuario` AS `IdUsuario`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `CONCAT(u.Nombre,' ',u.ApellidoPaterno)`,`u`.`Correo` AS `Correo`,`r`.`NombreRol` AS `NombreRol`,convert('herramienta' using utf8mb4) AS `CONVERT('herramienta' USING utf8mb4)`,`ah`.`IdHerramienta` AS `IdHerramienta`,convert(`h`.`Nombre` using utf8mb4) AS `CONVERT(h.Nombre USING utf8mb4)`,convert(`h`.`NumeroSerie` using utf8mb4) AS `CONVERT(h.NumeroSerie USING utf8mb4)`,convert(`h`.`Estado` using utf8mb4) AS `CONVERT(h.Estado USING utf8mb4)`,NULL AS `NULL`,`h`.`Costo` AS `Costo`,`ah`.`FechaAsignacion` AS `FechaAsignacion` from (((`usuario` `u` join `rol` `r` on((`r`.`IdRol` = `u`.`IdRol`))) join `asignacionherramienta` `ah` on(((`ah`.`IdUsuario` = `u`.`IdUsuario`) and (`ah`.`FechaDevolucion` is null)))) join `herramienta` `h` on((`h`.`IdHerramienta` = `ah`.`IdHerramienta`))) union all select `u`.`IdUsuario` AS `IdUsuario`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `CONCAT(u.Nombre,' ',u.ApellidoPaterno)`,`u`.`Correo` AS `Correo`,`r`.`NombreRol` AS `NombreRol`,convert('general' using utf8mb4) AS `CONVERT('general' USING utf8mb4)`,`a`.`id` AS `id`,convert(`a`.`nombre` using utf8mb4) AS `CONVERT(a.nombre USING utf8mb4)`,convert(`a`.`numero_serie` using utf8mb4) AS `CONVERT(a.numero_serie USING utf8mb4)`,convert(`a`.`estado` using utf8mb4) AS `CONVERT(a.estado USING utf8mb4)`,NULL AS `NULL`,`a`.`valor` AS `valor`,`a`.`fecha_adquisicion` AS `fecha_adquisicion` from ((`usuario` `u` join `rol` `r` on((`r`.`IdRol` = `u`.`IdRol`))) join `activos` `a` on((`a`.`usuario_id` = `u`.`IdUsuario`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_activos_unificado`
--

/*!50001 DROP VIEW IF EXISTS `v_activos_unificado`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_activos_unificado` AS select concat('A-',`a`.`id`) AS `id_unico`,`a`.`id` AS `id_origen`,'activos' AS `origen`,`a`.`nombre` AS `nombre`,`a`.`numero_serie` AS `numero_serie`,`a`.`descripcion` AS `descripcion`,`a`.`categoria` AS `categoria`,`a`.`estado` AS `estado`,`a`.`valor` AS `valor`,`a`.`fecha_adquisicion` AS `fecha_adquisicion`,`a`.`departamento_id` AS `departamento_id`,`d`.`nombre` AS `departamento_nombre`,`a`.`usuario_id` AS `usuario_id`,`a`.`creado_en` AS `creado_en` from (`activos` `a` left join `departamentos` `d` on((`a`.`departamento_id` = `d`.`id`))) union all select concat('E-',`e`.`IdElectronico`) AS `id_unico`,`e`.`IdElectronico` AS `id_origen`,'electronico' AS `origen`,`e`.`Nombre` AS `nombre`,`e`.`NumeroSerie` AS `numero_serie`,concat_ws(' · ',`e`.`TipoEquipo`,nullif(concat_ws(' ',`e`.`Marca`,`e`.`Modelo`),' '),`e`.`Descripcion`) AS `descripcion`,'equipo' AS `categoria`,(case when (`e`.`Estado` = 'baja') then 'baja' when (`e`.`Estado` = 'mantenimiento') then 'mantenimiento' else 'activo' end) AS `estado`,`e`.`Costo` AS `valor`,`e`.`FechaAdquisicion` AS `fecha_adquisicion`,`u`.`IdDepartamento` AS `departamento_id`,`d`.`nombre` AS `departamento_nombre`,`e`.`IdUsuario` AS `usuario_id`,`e`.`CreadoEn` AS `creado_en` from ((`electronico` `e` left join `usuario` `u` on((`e`.`IdUsuario` = `u`.`IdUsuario`))) left join `departamentos` `d` on((`u`.`IdDepartamento` = `d`.`id`))) union all select concat('V-',`v`.`IdVehiculo`) AS `id_unico`,`v`.`IdVehiculo` AS `id_origen`,'vehiculo' AS `origen`,`v`.`Nombre` AS `nombre`,`v`.`Matricula` AS `numero_serie`,concat_ws(' · ',`v`.`TipoVehiculo`,nullif(concat_ws(' ',`v`.`Marca`,`v`.`Modelo`),' '),nullif(concat_ws(' ',`v`.`Anio`,`v`.`Color`),' ')) AS `descripcion`,'vehiculo' AS `categoria`,(case when (`v`.`Estado` = 'baja') then 'baja' when (`v`.`Estado` = 'mantenimiento') then 'mantenimiento' else 'activo' end) AS `estado`,`v`.`Valor` AS `valor`,`v`.`FechaAdquisicion` AS `fecha_adquisicion`,`u`.`IdDepartamento` AS `departamento_id`,`d`.`nombre` AS `departamento_nombre`,`v`.`IdUsuario` AS `usuario_id`,`v`.`CreadoEn` AS `creado_en` from ((`vehiculo` `v` left join `usuario` `u` on((`v`.`IdUsuario` = `u`.`IdUsuario`))) left join `departamentos` `d` on((`u`.`IdDepartamento` = `d`.`id`))) union all select concat('H-',`h`.`IdHerramienta`) AS `id_unico`,`h`.`IdHerramienta` AS `id_origen`,'herramienta' AS `origen`,`h`.`Nombre` AS `nombre`,`h`.`NumeroSerie` AS `numero_serie`,concat_ws(' · ',`h`.`TipoHerramienta`,nullif(concat_ws(' ',`h`.`Marca`,`h`.`Modelo`),' '),`h`.`Descripcion`) AS `descripcion`,'herramienta' AS `categoria`,(case when (`h`.`Estado` = 'baja') then 'baja' when (`h`.`Estado` = 'mantenimiento') then 'mantenimiento' when (`h`.`Estado` in ('disponible','asignada','en_uso')) then 'activo' else 'activo' end) AS `estado`,`h`.`Costo` AS `valor`,`h`.`FechaAlta` AS `fecha_adquisicion`,`h`.`IdDepartamento` AS `departamento_id`,`d`.`nombre` AS `departamento_nombre`,(select `ah`.`IdUsuario` from `asignacionherramienta` `ah` where ((`ah`.`IdHerramienta` = `h`.`IdHerramienta`) and (`ah`.`FechaDevolucion` is null)) order by `ah`.`FechaAsignacion` desc limit 1) AS `usuario_id`,`h`.`CreadoEn` AS `creado_en` from (`herramienta` `h` left join `departamentos` `d` on((`h`.`IdDepartamento` = `d`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_adjuntos_ticket`
--

/*!50001 DROP VIEW IF EXISTS `v_adjuntos_ticket`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_adjuntos_ticket` AS select `a`.`IdAdjunto` AS `IdAdjunto`,`a`.`IdTicket` AS `IdTicket`,`a`.`IdUsuario` AS `IdUsuario`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `NombreUsuario`,`a`.`NombreArchivo` AS `NombreArchivo`,`a`.`NombreOriginal` AS `NombreOriginal`,`a`.`RutaArchivo` AS `RutaArchivo`,`a`.`TipoMIME` AS `TipoMIME`,`a`.`TamanoKB` AS `TamanoKB`,`a`.`FechaSubida` AS `FechaSubida` from (`adjuntosticket` `a` left join `usuario` `u` on((`a`.`IdUsuario` = `u`.`IdUsuario`))) order by `a`.`FechaSubida` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_auditoria_resguardo`
--

/*!50001 DROP VIEW IF EXISTS `v_auditoria_resguardo`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_auditoria_resguardo` AS select convert('electronico' using utf8mb4) AS `TipoActivo`,`e`.`IdElectronico` AS `IdActivo`,convert(`e`.`Nombre` using utf8mb4) AS `Nombre`,convert(`e`.`Nombre` using utf8mb4) AS `NombreActivo`,convert(`e`.`NumeroSerie` using utf8mb4) AS `NumeroSerie`,convert(`e`.`Estado` using utf8mb4) AS `Estado`,convert(`e`.`Condicion` using utf8mb4) AS `Condicion`,`e`.`Costo` AS `Valor`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `AsignadoA`,`u`.`Correo` AS `Correo`,convert(`ub`.`Nombre` using utf8mb4) AS `Ubicacion` from ((`electronico` `e` left join `usuario` `u` on((`u`.`IdUsuario` = `e`.`IdUsuario`))) left join `ubicacion` `ub` on((`ub`.`IdUbicacion` = `e`.`IdUbicacion`))) where (`e`.`Estado` in ('asignado','almacen')) union all select convert('general' using utf8mb4) AS `CONVERT('general' USING utf8mb4)`,`a`.`id` AS `id`,convert(`a`.`nombre` using utf8mb4) AS `CONVERT(a.nombre USING utf8mb4)`,convert(`a`.`nombre` using utf8mb4) AS `CONVERT(a.nombre USING utf8mb4)`,convert(`a`.`numero_serie` using utf8mb4) AS `CONVERT(a.numero_serie USING utf8mb4)`,convert(`a`.`estado` using utf8mb4) AS `CONVERT(a.estado USING utf8mb4)`,NULL AS `NULL`,`a`.`valor` AS `valor`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `CONCAT(u.Nombre,' ',u.ApellidoPaterno)`,`u`.`Correo` AS `Correo`,convert(`d`.`nombre` using utf8mb4) AS `CONVERT(d.nombre USING utf8mb4)` from ((`activos` `a` left join `usuario` `u` on((`u`.`IdUsuario` = `a`.`usuario_id`))) left join `departamentos` `d` on((`d`.`id` = `a`.`departamento_id`))) where (`a`.`estado` in ('activo','mantenimiento')) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_bajas_activos`
--

/*!50001 DROP VIEW IF EXISTS `v_bajas_activos`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_bajas_activos` AS select `b`.`IdBaja` AS `IdBaja`,`b`.`TipoActivo` AS `TipoActivo`,`b`.`IdActivo` AS `IdActivo`,`b`.`NombreActivo` AS `NombreActivo`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `DadoDeBajaPor`,`b`.`FechaBaja` AS `FechaBaja` from (`bajaactivo` `b` left join `usuario` `u` on((`b`.`DadoDeBajaPor` = `u`.`IdUsuario`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_comentarios_ticket`
--

/*!50001 DROP VIEW IF EXISTS `v_comentarios_ticket`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_comentarios_ticket` AS select `c`.`IdComentario` AS `IdComentario`,`c`.`IdTicket` AS `IdTicket`,`c`.`IdUsuario` AS `IdUsuario`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `NombreUsuario`,`u`.`Correo` AS `EmailUsuario`,`c`.`Comentario` AS `Comentario`,`c`.`EsInterno` AS `EsInterno`,`c`.`EsRespuestaOficial` AS `EsRespuestaOficial`,`c`.`FechaCreacion` AS `FechaCreacion` from (`comentariosticket` `c` left join `usuario` `u` on((`c`.`IdUsuario` = `u`.`IdUsuario`))) order by `c`.`FechaCreacion` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_dashboard_stats`
--

/*!50001 DROP VIEW IF EXISTS `v_dashboard_stats`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_dashboard_stats` AS select count(0) AS `total_activos`,sum((case when (`activos`.`estado` = 'activo') then 1 else 0 end)) AS `activos`,sum((case when (`activos`.`estado` = 'baja') then 1 else 0 end)) AS `bajas`,sum((case when (`activos`.`estado` = 'mantenimiento') then 1 else 0 end)) AS `en_mantenimiento`,coalesce(sum(`activos`.`valor`),0) AS `valor_total`,coalesce(avg(`activos`.`valor`),0) AS `valor_promedio`,count(distinct `activos`.`departamento_id`) AS `departamentos_con_activos` from `activos` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_departamentos`
--

/*!50001 DROP VIEW IF EXISTS `v_departamentos`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_departamentos` AS select `d`.`id` AS `id`,`d`.`nombre` AS `nombre`,`d`.`descripcion` AS `descripcion`,`d`.`creado_en` AS `creado_en`,count(`a`.`id`) AS `total_activos`,coalesce(sum(`a`.`valor`),0) AS `valor_total` from (`departamentos` `d` left join `activos` `a` on((`a`.`departamento_id` = `d`.`id`))) group by `d`.`id`,`d`.`nombre`,`d`.`descripcion`,`d`.`creado_en` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_documentos_usuario`
--

/*!50001 DROP VIEW IF EXISTS `v_documentos_usuario`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_documentos_usuario` AS select `d`.`IdDocumento` AS `IdDocumento`,`d`.`IdUsuario` AS `IdUsuario`,`d`.`TipoDocumento` AS `TipoDocumento`,`d`.`NombreArchivo` AS `NombreArchivo`,`d`.`ArchivoUrl` AS `ArchivoUrl`,`d`.`TipoArchivo` AS `TipoArchivo`,`d`.`FechaEmision` AS `FechaEmision`,`d`.`FechaVencimiento` AS `FechaVencimiento`,`d`.`Vigente` AS `Vigente`,`d`.`NumeroDocumento` AS `NumeroDocumento`,`d`.`Descripcion` AS `Descripcion`,`d`.`CreadoEn` AS `CreadoEn`,`u`.`Nombre` AS `UsuarioNombre`,`u`.`ApellidoPaterno` AS `ApellidoPaterno`,`u`.`Correo` AS `Correo`,(case when (`d`.`FechaVencimiento` is null) then NULL when (`d`.`FechaVencimiento` < curdate()) then 0 else (to_days(`d`.`FechaVencimiento`) - to_days(curdate())) end) AS `DiasParaVencer`,(case when (`d`.`FechaVencimiento` is null) then 'sin_vencimiento' when (`d`.`FechaVencimiento` < curdate()) then 'vencido' when ((to_days(`d`.`FechaVencimiento`) - to_days(curdate())) <= 30) then 'por_vencer' else 'vigente' end) AS `EstadoDocumento` from (`documentousuario` `d` join `usuario` `u` on((`d`.`IdUsuario` = `u`.`IdUsuario`))) where (`u`.`Estatus` = true) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_empleado_activos_completo`
--

/*!50001 DROP VIEW IF EXISTS `v_empleado_activos_completo`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_empleado_activos_completo` AS select `u`.`IdUsuario` AS `IdUsuario`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `NombreCompleto`,`u`.`Correo` AS `Correo`,`r`.`NombreRol` AS `Rol`,convert('electronico' using utf8mb4) AS `TipoActivo`,`e`.`IdElectronico` AS `IdActivo`,convert(`e`.`Nombre` using utf8mb4) AS `NombreActivo`,convert(`e`.`NumeroSerie` using utf8mb4) AS `NumeroSerie`,convert(`e`.`Estado` using utf8mb4) AS `Estado`,convert(`e`.`Condicion` using utf8mb4) AS `Condicion`,`e`.`Costo` AS `Valor`,`e`.`FechaAdquisicion` AS `FechaAdquisicion`,`pa`.`IdProyecto` AS `IdProyecto`,convert(`p`.`Nombre` using utf8mb4) AS `NombreProyecto`,convert(`p`.`Estatus` using utf8mb4) AS `EstatusProyecto` from ((((`usuario` `u` join `rol` `r` on((`r`.`IdRol` = `u`.`IdRol`))) join `electronico` `e` on((`e`.`IdUsuario` = `u`.`IdUsuario`))) left join `proyectoactivo` `pa` on(((`pa`.`TipoActivo` = 'electronico') and (`pa`.`IdActivo` = `e`.`IdElectronico`) and (`pa`.`FechaDevolucion` is null)))) left join `proyecto` `p` on((`p`.`IdProyecto` = `pa`.`IdProyecto`))) union all select `u`.`IdUsuario` AS `IdUsuario`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `CONCAT(u.Nombre,' ',u.ApellidoPaterno)`,`u`.`Correo` AS `Correo`,`r`.`NombreRol` AS `NombreRol`,convert('herramienta' using utf8mb4) AS `CONVERT('herramienta' USING utf8mb4)`,`ah`.`IdHerramienta` AS `IdHerramienta`,convert(`h`.`Nombre` using utf8mb4) AS `CONVERT(h.Nombre      USING utf8mb4)`,convert(`h`.`NumeroSerie` using utf8mb4) AS `CONVERT(h.NumeroSerie USING utf8mb4)`,convert(`h`.`Estado` using utf8mb4) AS `CONVERT(h.Estado      USING utf8mb4)`,NULL AS `NULL`,`h`.`Costo` AS `Costo`,`ah`.`FechaAsignacion` AS `FechaAsignacion`,`pa`.`IdProyecto` AS `IdProyecto`,convert(`p`.`Nombre` using utf8mb4) AS `CONVERT(p.Nombre USING utf8mb4)`,convert(`p`.`Estatus` using utf8mb4) AS `CONVERT(p.Estatus USING utf8mb4)` from (((((`usuario` `u` join `rol` `r` on((`r`.`IdRol` = `u`.`IdRol`))) join `asignacionherramienta` `ah` on(((`ah`.`IdUsuario` = `u`.`IdUsuario`) and (`ah`.`FechaDevolucion` is null)))) join `herramienta` `h` on((`h`.`IdHerramienta` = `ah`.`IdHerramienta`))) left join `proyectoactivo` `pa` on(((`pa`.`TipoActivo` = 'herramienta') and (`pa`.`IdActivo` = `ah`.`IdHerramienta`) and (`pa`.`FechaDevolucion` is null)))) left join `proyecto` `p` on((`p`.`IdProyecto` = `pa`.`IdProyecto`))) union all select `u`.`IdUsuario` AS `IdUsuario`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `CONCAT(u.Nombre,' ',u.ApellidoPaterno)`,`u`.`Correo` AS `Correo`,`r`.`NombreRol` AS `NombreRol`,convert('general' using utf8mb4) AS `CONVERT('general' USING utf8mb4)`,`a`.`id` AS `id`,convert(`a`.`nombre` using utf8mb4) AS `CONVERT(a.nombre      USING utf8mb4)`,convert(`a`.`numero_serie` using utf8mb4) AS `CONVERT(a.numero_serie USING utf8mb4)`,convert(`a`.`estado` using utf8mb4) AS `CONVERT(a.estado      USING utf8mb4)`,NULL AS `NULL`,`a`.`valor` AS `valor`,`a`.`fecha_adquisicion` AS `fecha_adquisicion`,`pa`.`IdProyecto` AS `IdProyecto`,convert(`p`.`Nombre` using utf8mb4) AS `CONVERT(p.Nombre USING utf8mb4)`,convert(`p`.`Estatus` using utf8mb4) AS `CONVERT(p.Estatus USING utf8mb4)` from ((((`usuario` `u` join `rol` `r` on((`r`.`IdRol` = `u`.`IdRol`))) join `activos` `a` on((`a`.`usuario_id` = `u`.`IdUsuario`))) left join `proyectoactivo` `pa` on(((`pa`.`TipoActivo` = 'general') and (`pa`.`IdActivo` = `a`.`id`) and (`pa`.`FechaDevolucion` is null)))) left join `proyecto` `p` on((`p`.`IdProyecto` = `pa`.`IdProyecto`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_equipos_consolidado`
--

/*!50001 DROP VIEW IF EXISTS `v_equipos_consolidado`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_equipos_consolidado` AS select `e`.`IdElectronico` AS `IdEquipo`,convert(`e`.`Nombre` using utf8mb4) AS `NombreEquipo`,convert(`e`.`TipoEquipo` using utf8mb4) AS `TipoEquipo`,convert(`e`.`Marca` using utf8mb4) AS `Marca`,convert(`e`.`Modelo` using utf8mb4) AS `Modelo`,convert(`e`.`NumeroSerie` using utf8mb4) AS `NumeroSerie`,convert(`e`.`Estado` using utf8mb4) AS `EstadoEquipo`,convert(`e`.`Condicion` using utf8mb4) AS `Condicion`,`e`.`Costo` AS `Costo`,`e`.`FechaAdquisicion` AS `FechaAdquisicion`,`u`.`IdUsuario` AS `IdUsuario`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `NombreUsuario`,`u`.`Correo` AS `CorreoUsuario`,`u`.`NumeroTelefono` AS `NumeroTelefono`,`r`.`NombreRol` AS `NombreRol`,`d`.`id` AS `IdDepartamento`,convert(`d`.`nombre` using utf8mb4) AS `NombreDepartamento`,`p`.`IdProyecto` AS `IdProyecto`,convert(`p`.`Nombre` using utf8mb4) AS `NombreProyecto`,convert(`p`.`Estatus` using utf8mb4) AS `EstatusProyecto`,`p`.`FechaInicio` AS `ProyectoFechaInicio`,`p`.`FechaTermino` AS `ProyectoFechaTermino`,convert(`pp`.`Rol` using utf8mb4) AS `RolEnProyecto`,`pa`.`IdProyecto` AS `IdProyectoEquipo`,convert(`pe`.`Nombre` using utf8mb4) AS `NombreProyectoEquipo`,convert(`pa`.`EstadoInicial` using utf8mb4) AS `EstadoInicialEquipo`,`pa`.`FechaAsignacion` AS `FechaAsignacionProyecto`,`pa`.`FechaDevolucion` AS `FechaDevolucionProyecto` from ((((((((`electronico` `e` left join `usuario` `u` on((`u`.`IdUsuario` = `e`.`IdUsuario`))) left join `rol` `r` on((`r`.`IdRol` = `u`.`IdRol`))) left join `activos` `a` on((`a`.`usuario_id` = `u`.`IdUsuario`))) left join `departamentos` `d` on((`d`.`id` = `a`.`departamento_id`))) left join `proyectopersonal` `pp` on((`pp`.`IdUsuario` = `u`.`IdUsuario`))) left join `proyecto` `p` on(((`p`.`IdProyecto` = `pp`.`IdProyecto`) and (`p`.`Estatus` not in ('Completado','Cancelado'))))) left join `proyectoactivo` `pa` on(((`pa`.`TipoActivo` = 'electronico') and (`pa`.`IdActivo` = `e`.`IdElectronico`) and (`pa`.`FechaDevolucion` is null)))) left join `proyecto` `pe` on((`pe`.`IdProyecto` = `pa`.`IdProyecto`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_equipos_ti`
--

/*!50001 DROP VIEW IF EXISTS `v_equipos_ti`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_equipos_ti` AS select `e`.`IdElectronico` AS `IdElectronico`,`e`.`Nombre` AS `Nombre`,`e`.`Marca` AS `Marca`,`e`.`Modelo` AS `Modelo`,concat(coalesce(`e`.`Marca`,''),' ',coalesce(`e`.`Modelo`,'')) AS `MarcaModelo`,`e`.`NumeroSerie` AS `NumeroSerie`,`e`.`TipoEquipo` AS `TipoEquipo`,`e`.`Estado` AS `Estado`,`e`.`Condicion` AS `Condicion`,`e`.`Costo` AS `Costo`,`e`.`Costo` AS `Valor`,`e`.`FechaAdquisicion` AS `FechaAdquisicion`,`e`.`Descripcion` AS `Descripcion`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `UsuarioNombre`,`u`.`Correo` AS `UsuarioCorreo`,`r`.`NombreRol` AS `UsuarioRol`,`ub`.`Nombre` AS `UbicacionNombre`,(select count(0) from `mantenimientoelectronico` `me` where ((`me`.`IdElectronico` = `e`.`IdElectronico`) and (`me`.`Estatus` = 'en_proceso'))) AS `MantenimientosActivos` from (((`electronico` `e` left join `usuario` `u` on((`e`.`IdUsuario` = `u`.`IdUsuario`))) left join `rol` `r` on((`u`.`IdRol` = `r`.`IdRol`))) left join `ubicacion` `ub` on((`e`.`IdUbicacion` = `ub`.`IdUbicacion`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_equipos_usuario`
--

/*!50001 DROP VIEW IF EXISTS `v_equipos_usuario`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_equipos_usuario` AS select `e`.`IdElectronico` AS `IdEquipo`,`e`.`IdUsuario` AS `IdUsuario`,`e`.`Nombre` AS `Nombre`,`e`.`Marca` AS `Marca`,`e`.`Modelo` AS `Modelo`,concat(coalesce(`e`.`Marca`,''),' ',coalesce(`e`.`Modelo`,'')) AS `MarcaModelo`,`e`.`TipoEquipo` AS `TipoEquipo`,`e`.`NumeroSerie` AS `NumeroSerie`,`e`.`Estado` AS `Estado`,`e`.`Condicion` AS `Condicion`,`e`.`Costo` AS `Valor`,`e`.`FechaAdquisicion` AS `FechaAdquisicion`,`u`.`Nombre` AS `UsuarioNombre`,`u`.`ApellidoPaterno` AS `ApellidoPaterno`,`u`.`Correo` AS `Correo` from (`electronico` `e` join `usuario` `u` on((`e`.`IdUsuario` = `u`.`IdUsuario`))) where ((`e`.`Estado` <> 'baja') and (`u`.`Estatus` = true)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_estadisticas_ti`
--

/*!50001 DROP VIEW IF EXISTS `v_estadisticas_ti`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_estadisticas_ti` AS select count(0) AS `TotalEquipos`,sum((case when (`electronico`.`Estado` = 'almacen') then 1 else 0 end)) AS `EnAlmacen`,sum((case when (`electronico`.`Estado` = 'asignado') then 1 else 0 end)) AS `Asignados`,sum((case when (`electronico`.`Estado` = 'mantenimiento') then 1 else 0 end)) AS `EnMantenimiento`,sum((case when (`electronico`.`Estado` = 'baja') then 1 else 0 end)) AS `Bajas`,sum((case when (`electronico`.`Condicion` = 'bueno') then 1 else 0 end)) AS `EnBuenEstado`,sum((case when (`electronico`.`Condicion` in ('malo','dañado')) then 1 else 0 end)) AS `EnMalEstado` from `electronico` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_estado_documentos_usuario`
--

/*!50001 DROP VIEW IF EXISTS `v_estado_documentos_usuario`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_estado_documentos_usuario` AS select `u`.`IdUsuario` AS `IdUsuario`,`u`.`Nombre` AS `Nombre`,`u`.`ApellidoPaterno` AS `ApellidoPaterno`,`u`.`Correo` AS `Correo`,count(distinct (case when (`d`.`EstadoDocumento` = 'vencido') then `d`.`IdDocumento` end)) AS `DocsVencidos`,count(distinct (case when (`d`.`EstadoDocumento` = 'por_vencer') then `d`.`IdDocumento` end)) AS `DocsPorVencer`,count(distinct (case when (`d`.`EstadoDocumento` = 'vigente') then `d`.`IdDocumento` end)) AS `DocsVigentes`,count(distinct `d`.`IdDocumento`) AS `TotalDocumentos`,(case when (count(distinct (case when (`d`.`EstadoDocumento` = 'vencido') then `d`.`IdDocumento` end)) > 0) then 'vencido' when (count(distinct (case when (`d`.`EstadoDocumento` = 'por_vencer') then `d`.`IdDocumento` end)) > 0) then 'por_vencer' when (count(distinct `d`.`IdDocumento`) > 0) then 'vigente' else 'sin_documentos' end) AS `EstadoGeneral` from (`usuario` `u` left join `v_documentos_usuario` `d` on((`u`.`IdUsuario` = `d`.`IdUsuario`))) where (`u`.`Estatus` = true) group by `u`.`IdUsuario`,`u`.`Nombre`,`u`.`ApellidoPaterno`,`u`.`Correo` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_expediente_empleado`
--

/*!50001 DROP VIEW IF EXISTS `v_expediente_empleado`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_expediente_empleado` AS select `u`.`IdUsuario` AS `IdUsuario`,`u`.`NombreUsuario` AS `NombreUsuario`,`u`.`Nombre` AS `Nombre`,`u`.`ApellidoPaterno` AS `ApellidoPaterno`,`u`.`ApellidoMaterno` AS `ApellidoMaterno`,`u`.`Correo` AS `Correo`,`u`.`NumeroTelefono` AS `NumeroTelefono`,`u`.`IdRol` AS `IdRol`,`u`.`TipoUsuario` AS `TipoUsuario`,`r`.`TotalEquipos` AS `TotalEquipos`,`r`.`TotalVehiculos` AS `TotalVehiculos`,`r`.`TotalActivos` AS `TotalActivos`,`r`.`ValorTotal` AS `ValorTotal`,`e`.`DocsVencidos` AS `DocsVencidos`,`e`.`DocsPorVencer` AS `DocsPorVencer`,`e`.`DocsVigentes` AS `DocsVigentes`,`e`.`TotalDocumentos` AS `TotalDocumentos`,`e`.`EstadoGeneral` AS `EstadoDocumentos` from ((`usuario` `u` left join `v_resumen_activos_usuario` `r` on((`u`.`IdUsuario` = `r`.`IdUsuario`))) left join `v_estado_documentos_usuario` `e` on((`u`.`IdUsuario` = `e`.`IdUsuario`))) where (`u`.`Estatus` = true) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_herramientas_disponibles`
--

/*!50001 DROP VIEW IF EXISTS `v_herramientas_disponibles`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_herramientas_disponibles` AS select `herramienta`.`IdHerramienta` AS `IdHerramienta`,`herramienta`.`Nombre` AS `Nombre`,`herramienta`.`Marca` AS `Marca`,`herramienta`.`Modelo` AS `Modelo`,`herramienta`.`NumeroSerie` AS `NumeroSerie`,`herramienta`.`Costo` AS `Costo`,`herramienta`.`FechaAlta` AS `FechaAlta` from `herramienta` where (`herramienta`.`Estado` = 'disponible') order by `herramienta`.`Nombre` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_historial_asignaciones`
--

/*!50001 DROP VIEW IF EXISTS `v_historial_asignaciones`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_historial_asignaciones` AS select `a`.`IdAsignacion` AS `IdAsignacion`,`h`.`IdHerramienta` AS `IdHerramienta`,`h`.`Nombre` AS `HerramientaNombre`,`h`.`NumeroSerie` AS `NumeroSerie`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `UsuarioNombre`,`u`.`Correo` AS `UsuarioCorreo`,`a`.`FechaAsignacion` AS `FechaAsignacion`,`a`.`FechaDevolucion` AS `FechaDevolucion`,`a`.`Observaciones` AS `Observaciones`,concat(`ap`.`Nombre`,' ',`ap`.`ApellidoPaterno`) AS `AsignadoPorNombre`,concat(`rp`.`Nombre`,' ',`rp`.`ApellidoPaterno`) AS `RecibidoPorNombre`,(case when (`a`.`FechaDevolucion` is null) then 'activa' else 'devuelta' end) AS `EstadoAsignacion`,`h`.`Estado` AS `EstadoHerramienta` from ((((`asignacionherramienta` `a` join `herramienta` `h` on((`a`.`IdHerramienta` = `h`.`IdHerramienta`))) join `usuario` `u` on((`a`.`IdUsuario` = `u`.`IdUsuario`))) left join `usuario` `ap` on((`a`.`AsignadoPor` = `ap`.`IdUsuario`))) left join `usuario` `rp` on((`a`.`RecibidoPor` = `rp`.`IdUsuario`))) order by `a`.`FechaAsignacion` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_inventario`
--

/*!50001 DROP VIEW IF EXISTS `v_inventario`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_inventario` AS select `h`.`IdHerramienta` AS `IdHerramienta`,`h`.`Nombre` AS `Nombre`,`h`.`Marca` AS `Marca`,`h`.`Modelo` AS `Modelo`,`h`.`NumeroSerie` AS `NumeroSerie`,`h`.`Estado` AS `Estado`,`h`.`Costo` AS `Costo`,`h`.`FechaAlta` AS `FechaAlta`,`h`.`Descripcion` AS `Descripcion`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `UsuarioAsignado`,`a`.`FechaAsignacion` AS `FechaAsignacion`,(select count(0) from `reportedanio` `rd` where (`rd`.`IdHerramienta` = `h`.`IdHerramienta`)) AS `TotalReportes`,(select count(0) from `evidenciaherramienta` `ev` where (`ev`.`IdHerramienta` = `h`.`IdHerramienta`)) AS `TotalEvidencias` from ((`herramienta` `h` left join `asignacionherramienta` `a` on(((`a`.`IdHerramienta` = `h`.`IdHerramienta`) and (`a`.`FechaDevolucion` is null)))) left join `usuario` `u` on((`a`.`IdUsuario` = `u`.`IdUsuario`))) order by `h`.`Estado`,`h`.`Nombre` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_mantenimiento_electronico`
--

/*!50001 DROP VIEW IF EXISTS `v_mantenimiento_electronico`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_mantenimiento_electronico` AS select `me`.`IdMantenimiento` AS `IdMantenimiento`,`me`.`Tipo` AS `Tipo`,`me`.`Diagnostico` AS `Diagnostico`,`me`.`Descripcion` AS `Descripcion`,`me`.`FechaInicio` AS `FechaInicio`,`me`.`FechaTermino` AS `FechaTermino`,`me`.`Costo` AS `Costo`,`me`.`Tecnico` AS `Tecnico`,`me`.`Estatus` AS `Estatus`,`me`.`CreadoEn` AS `CreadoEn`,`e`.`IdElectronico` AS `IdElectronico`,`e`.`Nombre` AS `EquipoNombre`,`e`.`NumeroSerie` AS `NumeroSerie`,`e`.`TipoEquipo` AS `TipoEquipo`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `CreadoPorNombre` from ((`mantenimientoelectronico` `me` join `electronico` `e` on((`me`.`IdElectronico` = `e`.`IdElectronico`))) left join `usuario` `u` on((`me`.`CreadoPor` = `u`.`IdUsuario`))) order by `me`.`CreadoEn` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_mantenimiento_vehiculo`
--

/*!50001 DROP VIEW IF EXISTS `v_mantenimiento_vehiculo`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_mantenimiento_vehiculo` AS select `mv`.`IdMantenimiento` AS `id`,`ts`.`Nombre` AS `tipo_servicio`,`mv`.`Descripcion` AS `descripcion`,`mv`.`FechaInicio` AS `fecha_inicio`,`mv`.`FechaEntrega` AS `fecha_entrega`,`mv`.`Kilometraje` AS `kilometraje`,`mv`.`Costo` AS `costo`,`mv`.`Proveedor` AS `proveedor`,`mv`.`Estatus` AS `estatus`,`mv`.`CreadoEn` AS `creado_en`,`v`.`IdVehiculo` AS `vehiculo_id`,`v`.`Nombre` AS `vehiculo_nombre`,`v`.`Matricula` AS `matricula`,concat(`p`.`Nombre`,' ',`p`.`Apellido`) AS `personal_nombre`,`u`.`Nombre` AS `creado_por_nombre` from ((((`mantenimientovehiculo` `mv` join `vehiculo` `v` on((`mv`.`IdVehiculo` = `v`.`IdVehiculo`))) join `tiposervicio` `ts` on((`mv`.`IdTipoServicio` = `ts`.`IdTipoServicio`))) left join `personal` `p` on((`mv`.`IdPersonal` = `p`.`IdPersonal`))) left join `usuario` `u` on((`mv`.`CreadoPor` = `u`.`IdUsuario`))) order by `mv`.`CreadoEn` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_metricas_ticketing`
--

/*!50001 DROP VIEW IF EXISTS `v_metricas_ticketing`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_metricas_ticketing` AS select count(0) AS `TotalTickets`,sum((case when (`e`.`Nombre` = 'Abierto') then 1 else 0 end)) AS `TotalAbiertos`,sum((case when (`e`.`Nombre` in ('En Proceso','Escalado','Pendiente')) then 1 else 0 end)) AS `TotalEnProceso`,sum((case when (`e`.`Nombre` = 'Resuelto') then 1 else 0 end)) AS `TotalResueltos`,sum((case when (`e`.`Nombre` = 'Cerrado') then 1 else 0 end)) AS `TotalCerrados`,sum((case when ((`e`.`Nombre` in ('Resuelto','Cerrado')) and (cast(`t`.`FechaCierre` as date) = curdate())) then 1 else 0 end)) AS `CerradosHoy`,sum((case when ((`p`.`Nombre` = 'Urgente') and (`e`.`Nombre` not in ('Resuelto','Cerrado','Sin Solución'))) then 1 else 0 end)) AS `TotalUrgentes`,sum((case when ((`p`.`Nombre` = 'Alta') and (`e`.`Nombre` not in ('Resuelto','Cerrado','Sin Solución'))) then 1 else 0 end)) AS `TotalAlta`,sum((case when ((`p`.`Nombre` = 'Media') and (`e`.`Nombre` not in ('Resuelto','Cerrado','Sin Solución'))) then 1 else 0 end)) AS `TotalMedia`,sum((case when ((`p`.`Nombre` = 'Baja') and (`e`.`Nombre` not in ('Resuelto','Cerrado','Sin Solución'))) then 1 else 0 end)) AS `TotalBaja`,sum((case when ((`t`.`IdAsignadoA` is null) and (`e`.`Nombre` not in ('Resuelto','Cerrado','Sin Solución'))) then 1 else 0 end)) AS `SinAsignar`,avg((case when (`t`.`FechaCierre` is not null) then timestampdiff(HOUR,`t`.`FechaCreacion`,`t`.`FechaCierre`) else NULL end)) AS `PromedioHorasCierre`,avg((case when (`t`.`FechaPrimeraRespuesta` is not null) then timestampdiff(HOUR,`t`.`FechaCreacion`,`t`.`FechaPrimeraRespuesta`) else NULL end)) AS `PromedioHorasRespuesta` from ((`tickets` `t` join `estadosticket` `e` on((`t`.`IdEstado` = `e`.`IdEstado`))) join `prioridadesticket` `p` on((`t`.`IdPrioridad` = `p`.`IdPrioridad`))) where (`e`.`Nombre` not in ('Resuelto','Cerrado','Sin Solución')) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_mis_tickets`
--

/*!50001 DROP VIEW IF EXISTS `v_mis_tickets`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_mis_tickets` AS select `v_tickets_completo`.`IdTicket` AS `IdTicket`,`v_tickets_completo`.`NumeroTicket` AS `NumeroTicket`,`v_tickets_completo`.`Titulo` AS `Titulo`,`v_tickets_completo`.`Categoria` AS `Categoria`,`v_tickets_completo`.`CategoriaColor` AS `CategoriaColor`,`v_tickets_completo`.`Prioridad` AS `Prioridad`,`v_tickets_completo`.`PrioridadColor` AS `PrioridadColor`,`v_tickets_completo`.`Estado` AS `Estado`,`v_tickets_completo`.`EstadoColor` AS `EstadoColor`,`v_tickets_completo`.`AsignadoA` AS `AsignadoA`,`v_tickets_completo`.`FechaCreacion` AS `FechaCreacion`,`v_tickets_completo`.`FechaUltimaActualizacion` AS `FechaUltimaActualizacion`,`v_tickets_completo`.`TotalComentarios` AS `TotalComentarios`,`v_tickets_completo`.`ComentariosPublicos` AS `ComentariosPublicos`,`v_tickets_completo`.`TotalAdjuntos` AS `TotalAdjuntos`,`v_tickets_completo`.`IdUsuarioCreador` AS `IdUsuarioCreador` from `v_tickets_completo` order by `v_tickets_completo`.`FechaCreacion` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_permisos_rol`
--

/*!50001 DROP VIEW IF EXISTS `v_permisos_rol`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_permisos_rol` AS select `r`.`IdRol` AS `IdRol`,`r`.`NombreRol` AS `NombreRol`,`m`.`IdModulo` AS `IdModulo`,`m`.`Nombre` AS `Modulo`,`m`.`Descripcion` AS `ModuloDesc`,`m`.`Icono` AS `Icono`,`m`.`Orden` AS `Orden`,ifnull(`p`.`PuedeVer`,0) AS `PuedeVer`,ifnull(`p`.`PuedeCrear`,0) AS `PuedeCrear`,ifnull(`p`.`PuedeEditar`,0) AS `PuedeEditar`,ifnull(`p`.`PuedeEliminar`,0) AS `PuedeEliminar` from ((`rol` `r` join `modulo` `m`) left join `permisorol` `p` on(((`p`.`IdRol` = `r`.`IdRol`) and (`p`.`IdModulo` = `m`.`IdModulo`)))) order by `r`.`IdRol`,`m`.`Orden` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_permisos_usuario`
--

/*!50001 DROP VIEW IF EXISTS `v_permisos_usuario`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_permisos_usuario` AS select `u`.`IdUsuario` AS `IdUsuario`,`u`.`NombreUsuario` AS `NombreUsuario`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `NombreCompleto`,`r`.`NombreRol` AS `NombreRol`,`m`.`IdModulo` AS `IdModulo`,`m`.`Nombre` AS `Modulo`,`m`.`Descripcion` AS `ModuloDesc`,`m`.`Icono` AS `Icono`,`m`.`Orden` AS `Orden`,ifnull(`pu`.`PuedeVer`,ifnull(`pr`.`PuedeVer`,0)) AS `PuedeVer`,ifnull(`pu`.`PuedeCrear`,ifnull(`pr`.`PuedeCrear`,0)) AS `PuedeCrear`,ifnull(`pu`.`PuedeEditar`,ifnull(`pr`.`PuedeEditar`,0)) AS `PuedeEditar`,ifnull(`pu`.`PuedeEliminar`,ifnull(`pr`.`PuedeEliminar`,0)) AS `PuedeEliminar`,(case when (`pu`.`IdPermiso` is not null) then 1 else 0 end) AS `EsPersonalizado` from ((((`usuario` `u` join `rol` `r` on((`u`.`IdRol` = `r`.`IdRol`))) join `modulo` `m`) left join `permisousuario` `pu` on(((`pu`.`IdUsuario` = `u`.`IdUsuario`) and (`pu`.`IdModulo` = `m`.`IdModulo`)))) left join `permisorol` `pr` on(((`pr`.`IdRol` = `u`.`IdRol`) and (`pr`.`IdModulo` = `m`.`IdModulo`)))) order by `u`.`IdUsuario`,`m`.`Orden` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_permisos_vehiculo`
--

/*!50001 DROP VIEW IF EXISTS `v_permisos_vehiculo`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_permisos_vehiculo` AS select `p`.`IdPermiso` AS `IdPermiso`,`p`.`IdVehiculo` AS `IdVehiculo`,`p`.`IdTipoServicio` AS `IdTipoServicio`,`ts`.`Nombre` AS `TipoServicio`,`p`.`Descripcion` AS `Descripcion`,`p`.`Numero` AS `Numero`,`p`.`FechaInicio` AS `FechaInicio`,`p`.`FechaVencimiento` AS `FechaVencimiento`,`p`.`ArchivoUrl` AS `ArchivoUrl`,`p`.`CreadoEn` AS `CreadoEn`,`v`.`Nombre` AS `VehiculoNombre`,`v`.`Marca` AS `Marca`,`v`.`Modelo` AS `Modelo`,`v`.`Matricula` AS `Matricula`,(case when (`p`.`FechaVencimiento` < curdate()) then 0 else (to_days(`p`.`FechaVencimiento`) - to_days(curdate())) end) AS `DiasParaVencer`,(case when (`p`.`FechaVencimiento` < curdate()) then 'vencido' when ((to_days(`p`.`FechaVencimiento`) - to_days(curdate())) <= 30) then 'por_vencer' else 'vigente' end) AS `EstadoPermiso` from ((`permisovehiculo` `p` join `vehiculo` `v` on((`p`.`IdVehiculo` = `v`.`IdVehiculo`))) join `tiposervicio` `ts` on((`p`.`IdTipoServicio` = `ts`.`IdTipoServicio`))) where (`v`.`Estado` = 'activo') */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_permisos_vencer`
--

/*!50001 DROP VIEW IF EXISTS `v_permisos_vencer`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_permisos_vencer` AS select `pv`.`IdPermiso` AS `id`,`ts`.`Nombre` AS `tipo`,`pv`.`Descripcion` AS `descripcion`,`pv`.`Numero` AS `numero`,`pv`.`FechaVencimiento` AS `fecha_vencimiento`,(to_days(`pv`.`FechaVencimiento`) - to_days(curdate())) AS `dias_restantes`,`v`.`IdVehiculo` AS `vehiculo_id`,`v`.`Nombre` AS `vehiculo_nombre`,`v`.`Matricula` AS `matricula` from ((`permisosvehiculo` `pv` join `vehiculo` `v` on((`pv`.`IdVehiculo` = `v`.`IdVehiculo`))) join `tiposervicio` `ts` on((`pv`.`IdTipoServicio` = `ts`.`IdTipoServicio`))) where (`pv`.`FechaVencimiento` >= curdate()) order by `pv`.`FechaVencimiento` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_procesos_baja`
--

/*!50001 DROP VIEW IF EXISTS `v_procesos_baja`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_procesos_baja` AS select `pb`.`IdBaja` AS `IdBaja`,`pb`.`Estatus` AS `Estatus`,`pb`.`FechaAviso` AS `FechaAviso`,`pb`.`FechaBaja` AS `FechaBaja`,`pb`.`Motivo` AS `Motivo`,`pb`.`Observaciones` AS `Observaciones`,`pb`.`CreadoEn` AS `CreadoEn`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `Empleado`,`u`.`Correo` AS `CorreoEmpleado`,`r`.`NombreRol` AS `RolEmpleado`,concat(`s`.`Nombre`,' ',`s`.`ApellidoPaterno`) AS `SolicitadoPorNombre`,concat(`a`.`Nombre`,' ',`a`.`ApellidoPaterno`) AS `AutorizadoPorNombre`,`pb`.`FechaAutorizacion` AS `FechaAutorizacion`,(select count(0) from `bajaactivoretiro` `bar` where (`bar`.`IdBaja` = `pb`.`IdBaja`)) AS `TotalActivosRetirados` from ((((`procesobaja` `pb` join `usuario` `u` on((`u`.`IdUsuario` = `pb`.`IdUsuario`))) join `rol` `r` on((`r`.`IdRol` = `u`.`IdRol`))) left join `usuario` `s` on((`s`.`IdUsuario` = `pb`.`SolicitadoPor`))) left join `usuario` `a` on((`a`.`IdUsuario` = `pb`.`AutorizadoPor`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_proyecto_detalle_completo`
--

/*!50001 DROP VIEW IF EXISTS `v_proyecto_detalle_completo`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_proyecto_detalle_completo` AS select `p`.`IdProyecto` AS `IdProyecto`,convert(`p`.`Nombre` using utf8mb4) AS `NombreProyecto`,convert(`p`.`Estatus` using utf8mb4) AS `EstatusProyecto`,`p`.`FechaInicio` AS `FechaInicio`,`p`.`FechaTermino` AS `FechaTermino`,`u`.`IdUsuario` AS `IdUsuario`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `NombrePersonal`,`u`.`Correo` AS `Correo`,`r`.`NombreRol` AS `NombreRol`,convert(`pp`.`Rol` using utf8mb4) AS `RolEnProyecto`,`d`.`id` AS `IdDepartamento`,convert(`d`.`nombre` using utf8mb4) AS `Departamento`,`pa`.`IdAsignacion` AS `IdAsignacionActivo`,convert(`pa`.`TipoActivo` using utf8mb4) AS `TipoActivo`,`pa`.`IdActivo` AS `IdActivo`,convert(`pa`.`EstadoInicial` using utf8mb4) AS `EstadoInicial`,`pa`.`FechaAsignacion` AS `FechaAsignacionActivo`,`pa`.`FechaDevolucion` AS `FechaDevolucion`,convert(`pa`.`Observaciones` using utf8mb4) AS `ObservacionesActivo`,convert(coalesce(`e`.`Nombre`,`h`.`Nombre`,`v`.`Nombre`) using utf8mb4) AS `NombreActivo`,convert(coalesce(`e`.`NumeroSerie`,`h`.`NumeroSerie`,`v`.`Matricula`) using utf8mb4) AS `SerieActivo` from (((((((((`proyecto` `p` left join `proyectopersonal` `pp` on((`pp`.`IdProyecto` = `p`.`IdProyecto`))) left join `usuario` `u` on((`u`.`IdUsuario` = `pp`.`IdUsuario`))) left join `rol` `r` on((`r`.`IdRol` = `u`.`IdRol`))) left join `activos` `ag` on((`ag`.`usuario_id` = `u`.`IdUsuario`))) left join `departamentos` `d` on((`d`.`id` = `ag`.`departamento_id`))) left join `proyectoactivo` `pa` on((`pa`.`IdProyecto` = `p`.`IdProyecto`))) left join `electronico` `e` on(((`pa`.`TipoActivo` = 'electronico') and (`e`.`IdElectronico` = `pa`.`IdActivo`)))) left join `herramienta` `h` on(((`pa`.`TipoActivo` = 'herramienta') and (`h`.`IdHerramienta` = `pa`.`IdActivo`)))) left join `vehiculo` `v` on(((`pa`.`TipoActivo` = 'vehiculo') and (`v`.`IdVehiculo` = `pa`.`IdActivo`)))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_proyectos`
--

/*!50001 DROP VIEW IF EXISTS `v_proyectos`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_proyectos` AS select `p`.`IdProyecto` AS `IdProyecto`,`p`.`Nombre` AS `Nombre`,`p`.`Descripcion` AS `Descripcion`,`p`.`FechaInicio` AS `FechaInicio`,`p`.`FechaTermino` AS `FechaTermino`,`p`.`Estatus` AS `Estatus`,`p`.`CreadoEn` AS `CreadoEn`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `CreadoPorNombre`,(to_days(`p`.`FechaTermino`) - to_days(curdate())) AS `DiasRestantes`,(select count(0) from `proyectopersonal` `pp` where (`pp`.`IdProyecto` = `p`.`IdProyecto`)) AS `TotalPersonal`,(select count(0) from `proyectoactivo` `pa` where (`pa`.`IdProyecto` = `p`.`IdProyecto`)) AS `TotalActivos` from (`proyecto` `p` join `usuario` `u` on((`p`.`CreadoPor` = `u`.`IdUsuario`))) order by `p`.`CreadoEn` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_resumen_activos_usuario`
--

/*!50001 DROP VIEW IF EXISTS `v_resumen_activos_usuario`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_resumen_activos_usuario` AS select `u`.`IdUsuario` AS `IdUsuario`,`u`.`Nombre` AS `Nombre`,`u`.`ApellidoPaterno` AS `ApellidoPaterno`,`u`.`Correo` AS `Correo`,`u`.`IdRol` AS `IdRol`,count(distinct `e`.`IdElectronico`) AS `TotalEquipos`,count(distinct `v`.`IdVehiculo`) AS `TotalVehiculos`,(count(distinct `e`.`IdElectronico`) + count(distinct `v`.`IdVehiculo`)) AS `TotalActivos`,(coalesce(sum(distinct `e`.`Costo`),0) + coalesce(sum(distinct `v`.`Valor`),0)) AS `ValorTotal` from ((`usuario` `u` left join `electronico` `e` on(((`u`.`IdUsuario` = `e`.`IdUsuario`) and (`e`.`Estado` <> 'baja')))) left join `vehiculo` `v` on(((`u`.`IdUsuario` = `v`.`IdUsuario`) and (`v`.`Estado` = 'activo')))) where (`u`.`Estatus` = true) group by `u`.`IdUsuario`,`u`.`Nombre`,`u`.`ApellidoPaterno`,`u`.`Correo`,`u`.`IdRol` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_tecnicos_ti`
--

/*!50001 DROP VIEW IF EXISTS `v_tecnicos_ti`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_tecnicos_ti` AS select `usuario`.`IdUsuario` AS `IdUsuario`,`usuario`.`NombreUsuario` AS `NombreUsuario`,concat(`usuario`.`Nombre`,' ',`usuario`.`ApellidoPaterno`) AS `NombreCompleto`,`usuario`.`Correo` AS `Correo`,`usuario`.`NumeroTelefono` AS `NumeroTelefono`,`usuario`.`Estatus` AS `Estatus` from `usuario` where ((`usuario`.`IdRol` = 5) and (`usuario`.`Estatus` = 1)) order by `usuario`.`Nombre` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_tickets_abiertos`
--

/*!50001 DROP VIEW IF EXISTS `v_tickets_abiertos`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_tickets_abiertos` AS select `v_tickets_completo`.`IdTicket` AS `IdTicket`,`v_tickets_completo`.`NumeroTicket` AS `NumeroTicket`,`v_tickets_completo`.`Titulo` AS `Titulo`,`v_tickets_completo`.`UsuarioCreador` AS `UsuarioCreador`,`v_tickets_completo`.`EmailCreador` AS `EmailCreador`,`v_tickets_completo`.`Categoria` AS `Categoria`,`v_tickets_completo`.`CategoriaColor` AS `CategoriaColor`,`v_tickets_completo`.`Prioridad` AS `Prioridad`,`v_tickets_completo`.`PrioridadColor` AS `PrioridadColor`,`v_tickets_completo`.`PrioridadNivel` AS `PrioridadNivel`,`v_tickets_completo`.`Estado` AS `Estado`,`v_tickets_completo`.`EstadoColor` AS `EstadoColor`,`v_tickets_completo`.`AsignadoA` AS `AsignadoA`,`v_tickets_completo`.`FechaCreacion` AS `FechaCreacion`,`v_tickets_completo`.`FechaUltimaActualizacion` AS `FechaUltimaActualizacion`,`v_tickets_completo`.`HorasHastaPrimeraRespuesta` AS `HorasHastaPrimeraRespuesta`,`v_tickets_completo`.`TiempoRespuestaHoras` AS `TiempoRespuestaHoras`,`v_tickets_completo`.`SLARespuestaCumplido` AS `SLARespuestaCumplido`,`v_tickets_completo`.`TotalComentarios` AS `TotalComentarios`,`v_tickets_completo`.`TotalAdjuntos` AS `TotalAdjuntos` from `v_tickets_completo` where (`v_tickets_completo`.`Estado` in ('Abierto','En Proceso','Escalado','Pendiente')) order by `v_tickets_completo`.`PrioridadNivel` desc,`v_tickets_completo`.`FechaCreacion` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_tickets_activos`
--

/*!50001 DROP VIEW IF EXISTS `v_tickets_activos`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_tickets_activos` AS select `v_tickets_dashboard`.`IdTicket` AS `IdTicket`,`v_tickets_dashboard`.`NumeroTicket` AS `NumeroTicket`,`v_tickets_dashboard`.`Titulo` AS `Titulo`,`v_tickets_dashboard`.`Descripcion` AS `Descripcion`,`v_tickets_dashboard`.`IdUsuarioCreador` AS `IdUsuarioCreador`,`v_tickets_dashboard`.`UsuarioCreador` AS `UsuarioCreador`,`v_tickets_dashboard`.`EmailCreador` AS `EmailCreador`,`v_tickets_dashboard`.`IdCategoria` AS `IdCategoria`,`v_tickets_dashboard`.`Categoria` AS `Categoria`,`v_tickets_dashboard`.`CategoriaColor` AS `CategoriaColor`,`v_tickets_dashboard`.`CategoriaIcono` AS `CategoriaIcono`,`v_tickets_dashboard`.`IdPrioridad` AS `IdPrioridad`,`v_tickets_dashboard`.`Prioridad` AS `Prioridad`,`v_tickets_dashboard`.`PrioridadColor` AS `PrioridadColor`,`v_tickets_dashboard`.`PrioridadNivel` AS `PrioridadNivel`,`v_tickets_dashboard`.`TiempoRespuestaHoras` AS `TiempoRespuestaHoras`,`v_tickets_dashboard`.`IdEstado` AS `IdEstado`,`v_tickets_dashboard`.`Estado` AS `Estado`,`v_tickets_dashboard`.`EstadoColor` AS `EstadoColor`,`v_tickets_dashboard`.`EsEstadoFinal` AS `EsEstadoFinal`,`v_tickets_dashboard`.`IdAsignadoA` AS `IdAsignadoA`,`v_tickets_dashboard`.`AsignadoA` AS `AsignadoA`,`v_tickets_dashboard`.`EmailAsignado` AS `EmailAsignado`,`v_tickets_dashboard`.`FechaCreacion` AS `FechaCreacion`,`v_tickets_dashboard`.`FechaUltimaActualizacion` AS `FechaUltimaActualizacion`,`v_tickets_dashboard`.`FechaPrimeraRespuesta` AS `FechaPrimeraRespuesta`,`v_tickets_dashboard`.`FechaResolucion` AS `FechaResolucion`,`v_tickets_dashboard`.`FechaCierre` AS `FechaCierre`,`v_tickets_dashboard`.`SLARespuestaCumplido` AS `SLARespuestaCumplido`,`v_tickets_dashboard`.`IdDepartamento` AS `IdDepartamento`,`v_tickets_dashboard`.`IdSede` AS `IdSede`,`v_tickets_dashboard`.`IdEquipo` AS `IdEquipo` from `v_tickets_dashboard` where (`v_tickets_dashboard`.`Estado` in ('Abierto','En Proceso','Escalado','Pendiente')) order by `v_tickets_dashboard`.`PrioridadNivel` desc,`v_tickets_dashboard`.`FechaCreacion` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_tickets_asignados`
--

/*!50001 DROP VIEW IF EXISTS `v_tickets_asignados`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_tickets_asignados` AS select `v_tickets_completo`.`IdTicket` AS `IdTicket`,`v_tickets_completo`.`NumeroTicket` AS `NumeroTicket`,`v_tickets_completo`.`Titulo` AS `Titulo`,`v_tickets_completo`.`UsuarioCreador` AS `UsuarioCreador`,`v_tickets_completo`.`EmailCreador` AS `EmailCreador`,`v_tickets_completo`.`Categoria` AS `Categoria`,`v_tickets_completo`.`CategoriaColor` AS `CategoriaColor`,`v_tickets_completo`.`Prioridad` AS `Prioridad`,`v_tickets_completo`.`PrioridadColor` AS `PrioridadColor`,`v_tickets_completo`.`Estado` AS `Estado`,`v_tickets_completo`.`EstadoColor` AS `EstadoColor`,`v_tickets_completo`.`FechaCreacion` AS `FechaCreacion`,`v_tickets_completo`.`HorasHastaPrimeraRespuesta` AS `HorasHastaPrimeraRespuesta`,`v_tickets_completo`.`HorasHastaResolucion` AS `HorasHastaResolucion`,`v_tickets_completo`.`TiempoRespuestaHoras` AS `TiempoRespuestaHoras`,`v_tickets_completo`.`SLARespuestaCumplido` AS `SLARespuestaCumplido`,`v_tickets_completo`.`TotalComentarios` AS `TotalComentarios`,`v_tickets_completo`.`IdAsignadoA` AS `IdAsignadoA` from `v_tickets_completo` where (`v_tickets_completo`.`Estado` not in ('Cerrado','Sin Solución')) order by `v_tickets_completo`.`PrioridadNivel` desc,`v_tickets_completo`.`FechaCreacion` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_tickets_completo`
--

/*!50001 DROP VIEW IF EXISTS `v_tickets_completo`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_tickets_completo` AS select `t`.`IdTicket` AS `IdTicket`,`t`.`NumeroTicket` AS `NumeroTicket`,`t`.`Titulo` AS `Titulo`,`t`.`Descripcion` AS `Descripcion`,`t`.`IdUsuarioCreador` AS `IdUsuarioCreador`,`uc`.`Nombre` AS `UsuarioCreador`,`uc`.`Correo` AS `EmailCreador`,`uc`.`IdDepartamento` AS `DepartamentoCreadorId`,`t`.`IdCategoria` AS `IdCategoria`,`cat`.`Nombre` AS `Categoria`,`cat`.`Icono` AS `CategoriaIcono`,`cat`.`Color` AS `CategoriaColor`,`t`.`IdPrioridad` AS `IdPrioridad`,`pri`.`Nombre` AS `Prioridad`,`pri`.`Color` AS `PrioridadColor`,`pri`.`Nivel` AS `PrioridadNivel`,`pri`.`TiempoRespuestaHoras` AS `TiempoRespuestaHoras`,`t`.`IdEstado` AS `IdEstado`,`est`.`Nombre` AS `Estado`,`est`.`Color` AS `EstadoColor`,`est`.`EsEstadoFinal` AS `EsEstadoFinal`,`t`.`IdEquipo` AS `IdEquipo`,`t`.`IdAsignadoA` AS `IdAsignadoA`,`ua`.`Nombre` AS `AsignadoA`,`ua`.`Correo` AS `EmailAsignado`,`t`.`IdSede` AS `IdSede`,`t`.`IdDepartamento` AS `IdDepartamento`,`t`.`CanalCreacion` AS `CanalCreacion`,`t`.`FechaCreacion` AS `FechaCreacion`,`t`.`FechaUltimaActualizacion` AS `FechaUltimaActualizacion`,`t`.`FechaPrimeraRespuesta` AS `FechaPrimeraRespuesta`,`t`.`FechaResolucion` AS `FechaResolucion`,`t`.`FechaCierre` AS `FechaCierre`,`t`.`CalificacionServicio` AS `CalificacionServicio`,`t`.`ComentarioSatisfaccion` AS `ComentarioSatisfaccion`,timestampdiff(HOUR,`t`.`FechaCreacion`,coalesce(`t`.`FechaPrimeraRespuesta`,now())) AS `HorasHastaPrimeraRespuesta`,timestampdiff(HOUR,`t`.`FechaCreacion`,coalesce(`t`.`FechaResolucion`,now())) AS `HorasHastaResolucion`,timestampdiff(HOUR,`t`.`FechaCreacion`,coalesce(`t`.`FechaCierre`,now())) AS `HorasHastaCierre`,(case when ((`t`.`FechaPrimeraRespuesta` is not null) and (timestampdiff(HOUR,`t`.`FechaCreacion`,`t`.`FechaPrimeraRespuesta`) <= `pri`.`TiempoRespuestaHoras`)) then 1 when ((`t`.`FechaPrimeraRespuesta` is null) and (timestampdiff(HOUR,`t`.`FechaCreacion`,now()) > `pri`.`TiempoRespuestaHoras`)) then 0 else NULL end) AS `SLARespuestaCumplido`,(select count(0) from `comentariosticket` where (`comentariosticket`.`IdTicket` = `t`.`IdTicket`)) AS `TotalComentarios`,(select count(0) from `comentariosticket` where ((`comentariosticket`.`IdTicket` = `t`.`IdTicket`) and (`comentariosticket`.`EsInterno` = 0))) AS `ComentariosPublicos`,(select count(0) from `adjuntosticket` where (`adjuntosticket`.`IdTicket` = `t`.`IdTicket`)) AS `TotalAdjuntos` from (((((`tickets` `t` left join `usuario` `uc` on((`t`.`IdUsuarioCreador` = `uc`.`IdUsuario`))) left join `categoriasticket` `cat` on((`t`.`IdCategoria` = `cat`.`IdCategoria`))) left join `prioridadesticket` `pri` on((`t`.`IdPrioridad` = `pri`.`IdPrioridad`))) left join `estadosticket` `est` on((`t`.`IdEstado` = `est`.`IdEstado`))) left join `usuario` `ua` on((`t`.`IdAsignadoA` = `ua`.`IdUsuario`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_tickets_dashboard`
--

/*!50001 DROP VIEW IF EXISTS `v_tickets_dashboard`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_tickets_dashboard` AS select `t`.`IdTicket` AS `IdTicket`,`t`.`NumeroTicket` AS `NumeroTicket`,`t`.`Titulo` AS `Titulo`,`t`.`Descripcion` AS `Descripcion`,`t`.`IdUsuarioCreador` AS `IdUsuarioCreador`,coalesce(concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`),'Usuario Desconocido') AS `UsuarioCreador`,coalesce(`u`.`Correo`,'sin-email@empresa.com') AS `EmailCreador`,`t`.`IdCategoria` AS `IdCategoria`,`c`.`Nombre` AS `Categoria`,`c`.`Color` AS `CategoriaColor`,`c`.`Icono` AS `CategoriaIcono`,`t`.`IdPrioridad` AS `IdPrioridad`,`p`.`Nombre` AS `Prioridad`,`p`.`Color` AS `PrioridadColor`,`p`.`Nivel` AS `PrioridadNivel`,`p`.`TiempoRespuestaHoras` AS `TiempoRespuestaHoras`,`t`.`IdEstado` AS `IdEstado`,`e`.`Nombre` AS `Estado`,`e`.`Color` AS `EstadoColor`,`e`.`EsEstadoFinal` AS `EsEstadoFinal`,`t`.`IdAsignadoA` AS `IdAsignadoA`,coalesce(concat(`asig`.`Nombre`,' ',`asig`.`ApellidoPaterno`),'') AS `AsignadoA`,coalesce(`asig`.`Correo`,'') AS `EmailAsignado`,`t`.`FechaCreacion` AS `FechaCreacion`,`t`.`FechaUltimaActualizacion` AS `FechaUltimaActualizacion`,`t`.`FechaPrimeraRespuesta` AS `FechaPrimeraRespuesta`,`t`.`FechaResolucion` AS `FechaResolucion`,`t`.`FechaCierre` AS `FechaCierre`,(case when ((`t`.`FechaPrimeraRespuesta` is not null) and (timestampdiff(HOUR,`t`.`FechaCreacion`,`t`.`FechaPrimeraRespuesta`) <= `p`.`TiempoRespuestaHoras`)) then 1 when ((`t`.`FechaPrimeraRespuesta` is null) and (timestampdiff(HOUR,`t`.`FechaCreacion`,now()) > `p`.`TiempoRespuestaHoras`)) then 0 else NULL end) AS `SLARespuestaCumplido`,`t`.`IdDepartamento` AS `IdDepartamento`,`t`.`IdSede` AS `IdSede`,`t`.`IdEquipo` AS `IdEquipo` from (((((`tickets` `t` join `categoriasticket` `c` on((`t`.`IdCategoria` = `c`.`IdCategoria`))) join `prioridadesticket` `p` on((`t`.`IdPrioridad` = `p`.`IdPrioridad`))) join `estadosticket` `e` on((`t`.`IdEstado` = `e`.`IdEstado`))) left join `usuario` `u` on((`t`.`IdUsuarioCreador` = `u`.`IdUsuario`))) left join `usuario` `asig` on((`t`.`IdAsignadoA` = `asig`.`IdUsuario`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_tickets_dashboard_ti`
--

/*!50001 DROP VIEW IF EXISTS `v_tickets_dashboard_ti`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_tickets_dashboard_ti` AS select `t`.`IdTicket` AS `IdTicket`,`t`.`NumeroTicket` AS `NumeroTicket`,`t`.`Titulo` AS `Titulo`,`t`.`Descripcion` AS `Descripcion`,`t`.`IdUsuarioCreador` AS `IdUsuarioCreador`,coalesce(concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`),'Usuario Desconocido') AS `UsuarioCreador`,coalesce(`u`.`Correo`,'sin-email@empresa.com') AS `EmailCreador`,`t`.`IdCategoria` AS `IdCategoria`,`c`.`Nombre` AS `Categoria`,`c`.`Color` AS `CategoriaColor`,`c`.`Icono` AS `CategoriaIcono`,`t`.`IdPrioridad` AS `IdPrioridad`,`p`.`Nombre` AS `Prioridad`,`p`.`Color` AS `PrioridadColor`,`p`.`Nivel` AS `PrioridadNivel`,`p`.`TiempoRespuestaHoras` AS `TiempoRespuestaHoras`,`t`.`IdEstado` AS `IdEstado`,`e`.`Nombre` AS `Estado`,`e`.`Color` AS `EstadoColor`,`e`.`EsEstadoFinal` AS `EsEstadoFinal`,`t`.`IdAsignadoA` AS `IdAsignadoA`,coalesce(concat(`asig`.`Nombre`,' ',`asig`.`ApellidoPaterno`),'') AS `AsignadoA`,coalesce(`asig`.`Correo`,'') AS `EmailAsignado`,`t`.`FechaCreacion` AS `FechaCreacion`,`t`.`FechaUltimaActualizacion` AS `FechaUltimaActualizacion`,`t`.`FechaPrimeraRespuesta` AS `FechaPrimeraRespuesta`,`t`.`FechaResolucion` AS `FechaResolucion`,`t`.`FechaCierre` AS `FechaCierre`,(case when ((`t`.`FechaPrimeraRespuesta` is not null) and (timestampdiff(HOUR,`t`.`FechaCreacion`,`t`.`FechaPrimeraRespuesta`) <= `p`.`TiempoRespuestaHoras`)) then 1 when ((`t`.`FechaPrimeraRespuesta` is null) and (timestampdiff(HOUR,`t`.`FechaCreacion`,now()) > `p`.`TiempoRespuestaHoras`)) then 0 else NULL end) AS `SLARespuestaCumplido`,`t`.`IdDepartamento` AS `IdDepartamento`,`t`.`IdSede` AS `IdSede`,`t`.`IdEquipo` AS `IdEquipo` from (((((`tickets` `t` join `categoriasticket` `c` on((`t`.`IdCategoria` = `c`.`IdCategoria`))) join `prioridadesticket` `p` on((`t`.`IdPrioridad` = `p`.`IdPrioridad`))) join `estadosticket` `e` on((`t`.`IdEstado` = `e`.`IdEstado`))) left join `usuario` `u` on((`t`.`IdUsuarioCreador` = `u`.`IdUsuario`))) left join `usuario` `asig` on((`t`.`IdAsignadoA` = `asig`.`IdUsuario`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_tickets_metricas`
--

/*!50001 DROP VIEW IF EXISTS `v_tickets_metricas`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_tickets_metricas` AS select count(0) AS `TotalTickets`,sum((case when (`v_tickets_completo`.`Estado` = 'Abierto') then 1 else 0 end)) AS `TotalAbiertos`,sum((case when (`v_tickets_completo`.`Estado` = 'En Proceso') then 1 else 0 end)) AS `TotalEnProceso`,sum((case when (`v_tickets_completo`.`Estado` = 'Escalado') then 1 else 0 end)) AS `TotalEscalados`,sum((case when (`v_tickets_completo`.`Estado` = 'Pendiente') then 1 else 0 end)) AS `TotalPendientes`,sum((case when (`v_tickets_completo`.`Estado` = 'Resuelto') then 1 else 0 end)) AS `TotalResueltos`,sum((case when (`v_tickets_completo`.`Estado` = 'Cerrado') then 1 else 0 end)) AS `TotalCerrados`,sum((case when (cast(`v_tickets_completo`.`FechaCierre` as date) = curdate()) then 1 else 0 end)) AS `CerradosHoy`,sum((case when (`v_tickets_completo`.`Prioridad` = 'Urgente') then 1 else 0 end)) AS `TotalUrgentes`,sum((case when (`v_tickets_completo`.`Prioridad` = 'Alta') then 1 else 0 end)) AS `TotalAlta`,sum((case when (`v_tickets_completo`.`Prioridad` = 'Media') then 1 else 0 end)) AS `TotalMedia`,sum((case when (`v_tickets_completo`.`Prioridad` = 'Baja') then 1 else 0 end)) AS `TotalBaja`,avg(`v_tickets_completo`.`HorasHastaPrimeraRespuesta`) AS `PromedioHorasRespuesta`,avg(`v_tickets_completo`.`HorasHastaResolucion`) AS `PromedioHorasResolucion`,avg(`v_tickets_completo`.`CalificacionServicio`) AS `PromedioSatisfaccion`,sum((case when (`v_tickets_completo`.`SLARespuestaCumplido` = 1) then 1 else 0 end)) AS `TicketsSLACumplido`,sum((case when (`v_tickets_completo`.`SLARespuestaCumplido` = 0) then 1 else 0 end)) AS `TicketsSLAIncumplido` from `v_tickets_completo` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_tickets_por_usuario`
--

/*!50001 DROP VIEW IF EXISTS `v_tickets_por_usuario`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_tickets_por_usuario` AS select `v_tickets_dashboard`.`IdTicket` AS `IdTicket`,`v_tickets_dashboard`.`NumeroTicket` AS `NumeroTicket`,`v_tickets_dashboard`.`Titulo` AS `Titulo`,`v_tickets_dashboard`.`Descripcion` AS `Descripcion`,`v_tickets_dashboard`.`IdUsuarioCreador` AS `IdUsuarioCreador`,`v_tickets_dashboard`.`UsuarioCreador` AS `UsuarioCreador`,`v_tickets_dashboard`.`EmailCreador` AS `EmailCreador`,`v_tickets_dashboard`.`IdCategoria` AS `IdCategoria`,`v_tickets_dashboard`.`Categoria` AS `Categoria`,`v_tickets_dashboard`.`CategoriaColor` AS `CategoriaColor`,`v_tickets_dashboard`.`CategoriaIcono` AS `CategoriaIcono`,`v_tickets_dashboard`.`IdPrioridad` AS `IdPrioridad`,`v_tickets_dashboard`.`Prioridad` AS `Prioridad`,`v_tickets_dashboard`.`PrioridadColor` AS `PrioridadColor`,`v_tickets_dashboard`.`PrioridadNivel` AS `PrioridadNivel`,`v_tickets_dashboard`.`TiempoRespuestaHoras` AS `TiempoRespuestaHoras`,`v_tickets_dashboard`.`IdEstado` AS `IdEstado`,`v_tickets_dashboard`.`Estado` AS `Estado`,`v_tickets_dashboard`.`EstadoColor` AS `EstadoColor`,`v_tickets_dashboard`.`EsEstadoFinal` AS `EsEstadoFinal`,`v_tickets_dashboard`.`IdAsignadoA` AS `IdAsignadoA`,`v_tickets_dashboard`.`AsignadoA` AS `AsignadoA`,`v_tickets_dashboard`.`EmailAsignado` AS `EmailAsignado`,`v_tickets_dashboard`.`FechaCreacion` AS `FechaCreacion`,`v_tickets_dashboard`.`FechaUltimaActualizacion` AS `FechaUltimaActualizacion`,`v_tickets_dashboard`.`FechaPrimeraRespuesta` AS `FechaPrimeraRespuesta`,`v_tickets_dashboard`.`FechaResolucion` AS `FechaResolucion`,`v_tickets_dashboard`.`FechaCierre` AS `FechaCierre`,`v_tickets_dashboard`.`SLARespuestaCumplido` AS `SLARespuestaCumplido`,`v_tickets_dashboard`.`IdDepartamento` AS `IdDepartamento`,`v_tickets_dashboard`.`IdSede` AS `IdSede`,`v_tickets_dashboard`.`IdEquipo` AS `IdEquipo` from `v_tickets_dashboard` order by `v_tickets_dashboard`.`FechaCreacion` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_usuarios`
--

/*!50001 DROP VIEW IF EXISTS `v_usuarios`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_usuarios` AS select `usuario`.`IdUsuario` AS `id`,`usuario`.`NombreUsuario` AS `username`,`usuario`.`Correo` AS `email`,concat(`usuario`.`Nombre`,' ',`usuario`.`ApellidoPaterno`) AS `nombre_completo`,`usuario`.`Nombre` AS `nombre`,`usuario`.`IdRol` AS `rol`,`usuario`.`Estatus` AS `activo`,`usuario`.`CreadoEn` AS `creado_en` from `usuario` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_usuarios_area`
--

/*!50001 DROP VIEW IF EXISTS `v_usuarios_area`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_usuarios_area` AS select `u`.`IdUsuario` AS `IdUsuario`,`u`.`NombreUsuario` AS `NombreUsuario`,concat(`u`.`Nombre`,' ',`u`.`ApellidoPaterno`) AS `NombreCompleto`,`u`.`Correo` AS `Correo`,`u`.`NumeroTelefono` AS `NumeroTelefono`,`u`.`Estatus` AS `Estatus`,`u`.`PrimerLogin` AS `PrimerLogin`,`u`.`TipoUsuario` AS `TipoUsuario`,`u`.`IdDepartamento` AS `IdDepartamento`,`d`.`nombre` AS `NombreArea`,`r`.`IdRol` AS `IdRol`,`r`.`NombreRol` AS `NombreRol`,`u`.`IntentosFallidos` AS `IntentosFallidos`,`u`.`BloqueadoHasta` AS `BloqueadoHasta`,(case `d`.`nombre` when 'TI' then 1 when 'Tecnología' then 1 when 'Recursos Humanos' then 1 when 'Administrativo' then 1 when 'Almacén' then 1 else 0 end) AS `TieneModulo` from ((`usuario` `u` left join `departamentos` `d` on((`d`.`id` = `u`.`IdDepartamento`))) left join `rol` `r` on((`r`.`IdRol` = `u`.`IdRol`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_vehiculos`
--

/*!50001 DROP VIEW IF EXISTS `v_vehiculos`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_vehiculos` AS select `v`.`IdVehiculo` AS `id`,`v`.`Nombre` AS `nombre`,`v`.`Marca` AS `marca`,`v`.`Modelo` AS `modelo`,`v`.`Matricula` AS `matricula`,`v`.`Kilometraje` AS `kilometraje`,`v`.`TipoAdquisicion` AS `tipo_adquisicion`,`v`.`Estado` AS `estado`,`v`.`Valor` AS `valor`,`v`.`FechaAdquisicion` AS `fecha_adquisicion`,`u`.`Nombre` AS `ubicacion_nombre`,concat(`p`.`Nombre`,' ',`p`.`Apellido`) AS `conductor_nombre`,`p`.`LicenciaNumero` AS `licencia_numero`,`p`.`LicenciaVigencia` AS `licencia_vigencia`,(select count(0) from `permisosvehiculo` `pv` where ((`pv`.`IdVehiculo` = `v`.`IdVehiculo`) and (`pv`.`FechaVencimiento` between curdate() and (curdate() + interval 30 day)))) AS `permisos_por_vencer`,(select count(0) from `mantenimientovehiculo` `mv` where ((`mv`.`IdVehiculo` = `v`.`IdVehiculo`) and (`mv`.`Estatus` = 'en_proceso'))) AS `mantenimientos_activos` from (((`vehiculo` `v` left join `ubicacion` `u` on((`v`.`IdUbicacion` = `u`.`IdUbicacion`))) left join `conductorvehiculo` `cv` on(((`cv`.`IdVehiculo` = `v`.`IdVehiculo`) and (`cv`.`FechaFin` is null)))) left join `personal` `p` on((`cv`.`IdPersonal` = `p`.`IdPersonal`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_vehiculos_usuario`
--

/*!50001 DROP VIEW IF EXISTS `v_vehiculos_usuario`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_vehiculos_usuario` AS select `v`.`IdVehiculo` AS `IdVehiculo`,`v`.`IdUsuario` AS `IdUsuario`,`v`.`Nombre` AS `VehiculoNombre`,`v`.`Marca` AS `Marca`,`v`.`Modelo` AS `Modelo`,`v`.`Anio` AS `Anio`,`v`.`Matricula` AS `Matricula`,`v`.`VIN` AS `VIN`,`v`.`Color` AS `Color`,`v`.`Estado` AS `Estado`,`v`.`Valor` AS `Valor`,`v`.`Kilometraje` AS `Kilometraje`,`v`.`FechaAsignacion` AS `FechaAsignacion`,`v`.`PolizaSeguro` AS `PolizaSeguro`,`v`.`Aseguradora` AS `Aseguradora`,`v`.`VigenciaSeguro` AS `VigenciaSeguro`,`u`.`Nombre` AS `UsuarioNombre`,`u`.`ApellidoPaterno` AS `ApellidoPaterno`,`u`.`Correo` AS `Correo`,(case when (`v`.`VigenciaSeguro` is null) then 'sin_seguro' when (`v`.`VigenciaSeguro` < curdate()) then 'vencido' when ((to_days(`v`.`VigenciaSeguro`) - to_days(curdate())) <= 30) then 'por_vencer' else 'vigente' end) AS `EstadoSeguro`,(to_days(`v`.`VigenciaSeguro`) - to_days(curdate())) AS `DiasVigenciaSeguro` from (`vehiculo` `v` join `usuario` `u` on((`v`.`IdUsuario` = `u`.`IdUsuario`))) where ((`v`.`Estado` = 'activo') and (`u`.`Estatus` = true)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-21 17:10:52
