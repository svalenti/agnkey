-- MySQL dump 10.13  Distrib 5.6.17, for osx10.7 (x86_64)
--
-- Host: localhost    Database: lcogt
-- ------------------------------------------------------
-- Server version	5.6.17

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `datarawfloyds`
--

DROP TABLE IF EXISTS `datarawfloyds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datarawfloyds` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `namefile` varchar(50) DEFAULT NULL,
  `directory` varchar(100) DEFAULT NULL,
  `objname` varchar(50) DEFAULT NULL,
  `jd` double DEFAULT NULL,
  `dateobs` date DEFAULT NULL,
  `exptime` float DEFAULT NULL,
  `filter` varchar(20) DEFAULT NULL,
  `grism` varchar(20) DEFAULT NULL,
  `telescope` varchar(20) DEFAULT NULL,
  `instrument` varchar(20) DEFAULT NULL,
  `type` varchar(20) DEFAULT NULL,
  `category` varchar(20) DEFAULT NULL,
  `tech` varchar(20) DEFAULT NULL,
  `airmass` float DEFAULT NULL,
  `ut` time DEFAULT NULL,
  `slit` varchar(20) DEFAULT NULL,
  `lamp` varchar(20) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `input` varchar(50) DEFAULT NULL,
  `note` varchar(100) DEFAULT NULL,
  `ra0` float DEFAULT NULL,
  `dec0` float DEFAULT NULL,
  `fwhm` float DEFAULT '9999',
  `OBID` varchar(50) DEFAULT NULL,
  `temperature` float DEFAULT NULL,
  `PROPID` varchar(30) DEFAULT NULL,
  `rotskypa` float DEFAULT NULL,
  `observer` varchar(30) DEFAULT NULL,
  `USERID` varchar(30) DEFAULT NULL,
  `dateobs2` varchar(23) DEFAULT NULL,
  `targid` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `namefile` (`namefile`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataredulco`
--

DROP TABLE IF EXISTS `dataredulco`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dataredulco` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `namefile` varchar(50) DEFAULT NULL,
  `wdirectory` varchar(100) DEFAULT NULL,
  `objname` varchar(50) DEFAULT NULL,
  `jd` double DEFAULT '9999',
  `dateobs` date DEFAULT NULL,
  `exptime` float DEFAULT NULL,
  `filter` varchar(20) DEFAULT NULL,
  `telescope` varchar(20) DEFAULT NULL,
  `instrument` varchar(20) DEFAULT NULL,
  `airmass` float DEFAULT NULL,
  `ut` time DEFAULT NULL,
  `wcs` float DEFAULT '9999',
  `psf` varchar(50) DEFAULT 'X',
  `apmag` double DEFAULT '9999',
  `psfx` double DEFAULT '9999',
  `psfy` double DEFAULT '9999',
  `psfmag` double DEFAULT '9999',
  `psfdmag` float DEFAULT '9999',
  `z1` float DEFAULT '9999',
  `z2` float DEFAULT '9999',
  `c1` float DEFAULT '9999',
  `c2` float DEFAULT '9999',
  `dz1` float DEFAULT '9999',
  `dz2` float DEFAULT '9999',
  `dc1` float DEFAULT '9999',
  `dc2` float DEFAULT '9999',
  `zcol1` varchar(2) DEFAULT NULL,
  `zcol2` varchar(2) DEFAULT NULL,
  `mag` double DEFAULT '9999',
  `dmag` float DEFAULT '9999',
  `quality` tinyint(1) DEFAULT '127',
  `zcat` varchar(50) DEFAULT 'X',
  `abscat` varchar(50) DEFAULT 'X',
  `fwhm` float DEFAULT '9999',
  `magtype` int(11) DEFAULT '1',
  `ra0` double DEFAULT '9999',
  `dec0` double DEFAULT '9999',
  `filetype` int(11) DEFAULT '9999',
  `targid` int(11) DEFAULT '0',
  `ZPN` float DEFAULT NULL,
  `ZPNERR` float DEFAULT NULL,
  `ZPNNUM` float DEFAULT NULL,
  `PROPID` varchar(30) DEFAULT NULL,
  `observer` varchar(30) DEFAULT NULL,
  `dateobs2` varchar(23) DEFAULT NULL,
  `USERID` varchar(30) DEFAULT NULL,
  `rotskypa` float DEFAULT NULL,
  `temperature` float DEFAULT NULL,
  `instmagap1` double DEFAULT NULL,
  `appmagap1` double DEFAULT NULL,
  `appmagap2` double DEFAULT NULL,
  `instmagap2` double DEFAULT NULL,
  `dappmagap2` double DEFAULT NULL,
  `dappmagap1` double DEFAULT NULL,
  `dappmagap3` double DEFAULT NULL,
  `instmagap3` double DEFAULT NULL,
  `appmagap3` double DEFAULT NULL,
  `apflux1` double DEFAULT NULL,
  `dapflux1` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `namefile` (`namefile`)
) ENGINE=MyISAM AUTO_INCREMENT=13185 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datareduspectra`
--

DROP TABLE IF EXISTS `datareduspectra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datareduspectra` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `namefile` varchar(100) DEFAULT NULL,
  `directory` varchar(100) DEFAULT NULL,
  `objname` varchar(50) DEFAULT NULL,
  `jd` double DEFAULT NULL,
  `dateobs` date DEFAULT NULL,
  `exptime` float DEFAULT NULL,
  `filter` varchar(20) DEFAULT NULL,
  `grism` varchar(20) DEFAULT NULL,
  `telescope` varchar(20) DEFAULT NULL,
  `instrument` varchar(20) DEFAULT NULL,
  `airmass` float DEFAULT NULL,
  `ut` time DEFAULT NULL,
  `slit` varchar(20) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `original` varchar(50) DEFAULT NULL,
  `note` varchar(100) DEFAULT NULL,
  `ra0` float DEFAULT NULL,
  `dec0` float DEFAULT NULL,
  `PROPID` varchar(30) DEFAULT NULL,
  `observer` varchar(30) DEFAULT NULL,
  `dateobs2` varchar(23) DEFAULT NULL,
  `targid` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `namefile` (`namefile`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dataspectraexternal`
--

DROP TABLE IF EXISTS `dataspectraexternal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dataspectraexternal` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `namefile` varchar(50) DEFAULT NULL,
  `directory` varchar(100) DEFAULT NULL,
  `objname` varchar(50) DEFAULT NULL,
  `jd` double DEFAULT NULL,
  `dateobs` date DEFAULT NULL,
  `exptime` float DEFAULT NULL,
  `filter` varchar(20) DEFAULT NULL,
  `grism` varchar(20) DEFAULT NULL,
  `telescope` varchar(20) DEFAULT NULL,
  `instrument` varchar(20) DEFAULT NULL,
  `airmass` float DEFAULT NULL,
  `ut` time DEFAULT NULL,
  `slit` varchar(20) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `original` varchar(50) DEFAULT NULL,
  `note` varchar(100) DEFAULT NULL,
  `ra0` float DEFAULT NULL,
  `dec0` float DEFAULT NULL,
  `PROPID` varchar(30) DEFAULT NULL,
  `observer` varchar(30) DEFAULT NULL,
  `dateobs2` varchar(23) DEFAULT NULL,
  `targid` int(11) DEFAULT '0',
  `access` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `namefile` (`namefile`)
) ENGINE=MyISAM AUTO_INCREMENT=21 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `groupstab`
--

DROP TABLE IF EXISTS `groupstab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groupstab` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `groups` varchar(20) DEFAULT NULL,
  `groupid` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inoutredu`
--

DROP TABLE IF EXISTS `inoutredu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inoutredu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `namein` varchar(100) DEFAULT NULL,
  `tablein` varchar(20) DEFAULT NULL,
  `nameout` varchar(100) DEFAULT NULL,
  `tableout` varchar(20) DEFAULT NULL,
  `nametemp` varchar(100) DEFAULT NULL,
  `tabletemp` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=300 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lsc_sn_pos`
--

DROP TABLE IF EXISTS `lsc_sn_pos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lsc_sn_pos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `ra_sn` double DEFAULT NULL,
  `dec_sn` double DEFAULT NULL,
  `redshift` double DEFAULT NULL,
  `psf_string` varchar(50) DEFAULT NULL,
  `sloan_cat` varchar(50) DEFAULT NULL,
  `landolt_cat` varchar(50) DEFAULT NULL,
  `objtype` varchar(10) DEFAULT 'sn',
  `apass_cat` varchar(50) DEFAULT NULL,
  `targid` int(11) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=51 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `noteobjects`
--

DROP TABLE IF EXISTS `noteobjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `noteobjects` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `targid` int(11) DEFAULT '0',
  `note` varchar(200) DEFAULT NULL,
  `datenote` date DEFAULT NULL,
  `user` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=24 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `obslog`
--

DROP TABLE IF EXISTS `obslog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `obslog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(20) DEFAULT NULL,
  `targid` bigint(20) DEFAULT NULL,
  `triggerjd` double DEFAULT NULL,
  `windowstart` double DEFAULT NULL,
  `windowend` double DEFAULT NULL,
  `filters` varchar(30) DEFAULT NULL,
  `exptime` varchar(30) DEFAULT NULL,
  `numexp` varchar(30) DEFAULT NULL,
  `proposal` varchar(30) DEFAULT NULL,
  `site` varchar(10) DEFAULT NULL,
  `instrument` varchar(30) DEFAULT NULL,
  `sky` float DEFAULT '9999',
  `seeing` float DEFAULT '9999',
  `airmass` float DEFAULT '9999',
  `slit` float DEFAULT '9999',
  `acqmode` varchar(20) DEFAULT NULL,
  `priority` float DEFAULT '9999',
  `reqnumber` int(11) DEFAULT NULL,
  `tracknumber` int(11) DEFAULT NULL,
  `tarfile` varchar(60) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=166 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `permissionlog`
--

DROP TABLE IF EXISTS `permissionlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permissionlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `targid` int(11) DEFAULT NULL,
  `groupname` bigint(20) DEFAULT NULL,
  `jd` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=51 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `recobjects`
--

DROP TABLE IF EXISTS `recobjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recobjects` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `targid` int(11) DEFAULT '0',
  `name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=52 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `userslog`
--

DROP TABLE IF EXISTS `userslog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `userslog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `targid` int(11) DEFAULT '0',
  `note` varchar(200) DEFAULT NULL,
  `command` varchar(50) DEFAULT NULL,
  `dateobs` date DEFAULT NULL,
  `tables` varchar(50) DEFAULT NULL,
  `users` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=239 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `userstab`
--

DROP TABLE IF EXISTS `userstab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `userstab` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(20) DEFAULT NULL,
  `groupname` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user` (`user`)
) ENGINE=MyISAM AUTO_INCREMENT=19 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-10-17 22:24:42
