-- ============================================================
--  01_create_database.sql
--  Création de la base FinanceDB
--  Projet : Tableau de Bord Financier – Direction Comptable
-- ============================================================

USE master;
GO

-- Suppression si existante (développement uniquement)
IF EXISTS (SELECT name FROM sys.databases WHERE name = 'FinanceDB')
BEGIN
    ALTER DATABASE FinanceDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE FinanceDB;
END
GO

-- Création de la base
CREATE DATABASE FinanceDB
    COLLATE French_CI_AS;
GO

USE FinanceDB;
GO

-- Schémas logiques
CREATE SCHEMA dim;   -- Tables de dimensions
GO
CREATE SCHEMA fait;  -- Tables de faits
GO
CREATE SCHEMA rpt;   -- Vues de reporting
GO

PRINT 'Base FinanceDB créée avec succès.';
GO
