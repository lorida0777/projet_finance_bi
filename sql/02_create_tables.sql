-- ============================================================
--  02_create_tables.sql
--  Schéma en étoile : dimensions + faits
--  Projet : Tableau de Bord Financier – Direction Comptable
-- ============================================================

USE FinanceDB;
GO

-- ─────────────────────────────────────────
--  DIMENSION TEMPS
-- ─────────────────────────────────────────
CREATE TABLE dim.Temps (
    date_id         INT             NOT NULL PRIMARY KEY,   -- Format YYYYMMDD
    date_complete   DATE            NOT NULL,
    jour            TINYINT         NOT NULL,
    mois            TINYINT         NOT NULL,
    nom_mois        VARCHAR(20)     NOT NULL,
    trimestre       TINYINT         NOT NULL,
    semestre        TINYINT         NOT NULL,
    annee           SMALLINT        NOT NULL,
    semaine_annee   TINYINT         NOT NULL,
    jour_semaine    TINYINT         NOT NULL,               -- 1=Lundi ... 7=Dimanche
    nom_jour        VARCHAR(15)     NOT NULL,
    est_weekend     BIT             NOT NULL DEFAULT 0,
    est_ferie       BIT             NOT NULL DEFAULT 0,
    libelle_periode VARCHAR(30)     NOT NULL               -- Ex : "Janvier 2024"
);
GO

-- ─────────────────────────────────────────
--  DIMENSION CLIENT
-- ─────────────────────────────────────────
CREATE TABLE dim.Client (
    client_id           INT             NOT NULL PRIMARY KEY IDENTITY(1,1),
    code_client         VARCHAR(20)     NOT NULL UNIQUE,
    raison_sociale      VARCHAR(150)    NOT NULL,
    secteur_activite    VARCHAR(80)     NOT NULL,
    taille_entreprise   VARCHAR(20)     NOT NULL,           -- TPE, PME, ETI, GE
    ville               VARCHAR(80)     NOT NULL,
    region              VARCHAR(80)     NOT NULL,
    pays                VARCHAR(50)     NOT NULL DEFAULT 'Madagascar',
    date_entree         DATE            NOT NULL,
    statut              VARCHAR(20)     NOT NULL DEFAULT 'Actif', -- Actif, Inactif, Suspendu
    segment             VARCHAR(30)     NOT NULL,           -- Grand Compte, Standard, Prospect
    plafond_credit      DECIMAL(15,2)   NOT NULL DEFAULT 0,
    conditions_paiement TINYINT         NOT NULL DEFAULT 30 -- Délai en jours
);
GO

-- ─────────────────────────────────────────
--  DIMENSION PRODUIT / SERVICE
-- ─────────────────────────────────────────
CREATE TABLE dim.ProduitService (
    produit_id          INT             NOT NULL PRIMARY KEY IDENTITY(1,1),
    code_produit        VARCHAR(20)     NOT NULL UNIQUE,
    libelle             VARCHAR(150)    NOT NULL,
    categorie           VARCHAR(80)     NOT NULL,           -- Audit, Conseil, Expertise, Formation
    sous_categorie      VARCHAR(80)     NOT NULL,
    unite_facturation   VARCHAR(30)     NOT NULL,           -- Heure, Forfait, Journée
    prix_catalogue_ht   DECIMAL(15,2)   NOT NULL,
    taux_tva            DECIMAL(5,2)    NOT NULL DEFAULT 20.00,
    actif               BIT             NOT NULL DEFAULT 1
);
GO

-- ─────────────────────────────────────────
--  DIMENSION DÉPARTEMENT
-- ─────────────────────────────────────────
CREATE TABLE dim.Departement (
    dept_id             INT             NOT NULL PRIMARY KEY IDENTITY(1,1),
    code_dept           VARCHAR(10)     NOT NULL UNIQUE,
    nom_departement     VARCHAR(80)     NOT NULL,
    direction           VARCHAR(80)     NOT NULL,
    responsable         VARCHAR(100)    NOT NULL,
    budget_annuel       DECIMAL(15,2)   NOT NULL DEFAULT 0,
    centre_cout         VARCHAR(20)     NOT NULL
);
GO

-- ─────────────────────────────────────────
--  FAIT : REVENUS (Facturation)
-- ─────────────────────────────────────────
CREATE TABLE fait.Revenus (
    revenu_id           BIGINT          NOT NULL PRIMARY KEY IDENTITY(1,1),
    date_id             INT             NOT NULL REFERENCES dim.Temps(date_id),
    client_id           INT             NOT NULL REFERENCES dim.Client(client_id),
    produit_id          INT             NOT NULL REFERENCES dim.ProduitService(produit_id),
    dept_id             INT             NOT NULL REFERENCES dim.Departement(dept_id),

    -- Identifiants métier
    numero_facture      VARCHAR(30)     NOT NULL UNIQUE,
    date_echeance_id    INT             NOT NULL REFERENCES dim.Temps(date_id),

    -- Mesures financières
    quantite            DECIMAL(10,2)   NOT NULL DEFAULT 1,
    prix_unitaire_ht    DECIMAL(15,2)   NOT NULL,
    remise_pct          DECIMAL(5,2)    NOT NULL DEFAULT 0,
    montant_ht          DECIMAL(15,2)   NOT NULL,
    montant_tva         DECIMAL(15,2)   NOT NULL,
    montant_ttc         DECIMAL(15,2)   NOT NULL,

    -- Statut de paiement
    statut_paiement     VARCHAR(20)     NOT NULL DEFAULT 'En attente',
                                        -- En attente, Payée, Partielle, Retard, Contentieux
    date_paiement_id    INT             NULL REFERENCES dim.Temps(date_id),
    montant_encaisse    DECIMAL(15,2)   NOT NULL DEFAULT 0,
    jours_retard        INT             NOT NULL DEFAULT 0,

    -- Métadonnées
    created_at          DATETIME2       NOT NULL DEFAULT SYSDATETIME(),
    updated_at          DATETIME2       NOT NULL DEFAULT SYSDATETIME()
);
GO

-- ─────────────────────────────────────────
--  FAIT : CHARGES (Dépenses)
-- ─────────────────────────────────────────
CREATE TABLE fait.Charges (
    charge_id           BIGINT          NOT NULL PRIMARY KEY IDENTITY(1,1),
    date_id             INT             NOT NULL REFERENCES dim.Temps(date_id),
    dept_id             INT             NOT NULL REFERENCES dim.Departement(dept_id),

    -- Classification comptable
    numero_piece        VARCHAR(30)     NOT NULL,
    categorie_charge    VARCHAR(80)     NOT NULL,
                                        -- Salaires, Loyer, Matériel, Déplacement, Sous-traitance
    sous_categorie      VARCHAR(80)     NOT NULL,
    fournisseur         VARCHAR(150)    NOT NULL,
    nature_charge       VARCHAR(20)     NOT NULL DEFAULT 'Exploitation',
                                        -- Exploitation, Financière, Exceptionnelle

    -- Mesures
    montant_ht          DECIMAL(15,2)   NOT NULL,
    montant_tva         DECIMAL(15,2)   NOT NULL DEFAULT 0,
    montant_ttc         DECIMAL(15,2)   NOT NULL,
    est_budgetee        BIT             NOT NULL DEFAULT 1,

    created_at          DATETIME2       NOT NULL DEFAULT SYSDATETIME()
);
GO

-- ─────────────────────────────────────────
--  TABLE BUDGET (pour comparaison Budget vs Réalisé)
-- ─────────────────────────────────────────
CREATE TABLE fait.Budget (
    budget_id           INT             NOT NULL PRIMARY KEY IDENTITY(1,1),
    annee               SMALLINT        NOT NULL,
    mois                TINYINT         NOT NULL,
    dept_id             INT             NOT NULL REFERENCES dim.Departement(dept_id),
    categorie           VARCHAR(80)     NOT NULL,
    montant_budget      DECIMAL(15,2)   NOT NULL,
    type_budget         VARCHAR(20)     NOT NULL            -- Revenu, Charge
);
GO

-- ─────────────────────────────────────────
--  INDEX pour performances Power BI
-- ─────────────────────────────────────────
CREATE INDEX IX_Revenus_Date     ON fait.Revenus(date_id);
CREATE INDEX IX_Revenus_Client   ON fait.Revenus(client_id);
CREATE INDEX IX_Revenus_Produit  ON fait.Revenus(produit_id);
CREATE INDEX IX_Revenus_Statut   ON fait.Revenus(statut_paiement);
CREATE INDEX IX_Charges_Date     ON fait.Charges(date_id);
CREATE INDEX IX_Charges_Dept     ON fait.Charges(dept_id);
CREATE INDEX IX_Budget_AnnMois   ON fait.Budget(annee, mois, dept_id);
GO

PRINT 'Tables créées avec succès.';
GO
