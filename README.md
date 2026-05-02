# 📊 Tableau de Bord Financier – Direction Comptable
### Pipeline ETL SQL Server + Power BI | Analyse des performances financières

---

## 🎯 Contexte

Ce projet simule un système décisionnel pour une **Direction Comptable et Financière (DCF)**.  
Il automatise l'extraction, la transformation et le chargement (ETL) des données comptables  
vers SQL Server, puis construit un tableau de bord Power BI interactif pour piloter :

- Le **chiffre d'affaires** par client, produit et période
- Les **charges opérationnelles** par département et catégorie
- Le **résultat net** mensuel et les marges bénéficiaires
- Les **impayés et créances clients** (DSO – Days Sales Outstanding)
- Le **budget vs réalisé** par centre de coût

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     SOURCES DE DONNÉES                   │
│   Fichiers CSV simulés (clients, factures, charges...)   │
└──────────────────────┬───────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │  ETL Python     │
              │  01_generate.py │  ← Génération données réalistes
              │  02_transform.py│  ← Nettoyage & enrichissement
              │  03_load.py     │  ← Chargement SQL Server
              └────────┬────────┘
                       │
        ┌──────────────▼──────────────┐
        │       SQL SERVER            │
        │   Base : FinanceDB          │
        │   Schéma en Étoile          │
        ├─────────────────────────────┤
        │  dim_temps                  │
        │  dim_client                 │
        │  dim_produit_service        │
        │  dim_departement            │
        │  fait_revenus               │
        │  fait_charges               │
        └──────────────┬──────────────┘
                       │  DirectQuery / Import
        ┌──────────────▼──────────────┐
        │        POWER BI             │
        │   Dashboard Financier       │
        ├─────────────────────────────┤
        │  Page 1 : Vue Exécutive     │
        │  Page 2 : Revenus & Marges  │
        │  Page 3 : Charges & Budget  │
        │  Page 4 : Créances Clients  │
        └─────────────────────────────┘
```

---

## 📁 Structure du Projet

```
projet_finance_bi/
│
├── README.md
│
├── sql/
│   ├── 01_create_database.sql      ← Création base + schéma étoile
│   ├── 02_create_tables.sql        ← Tables dimensions et faits
│   ├── 03_stored_procedures.sql    ← Procédures stockées ETL
│   └── 04_analytical_views.sql     ← Vues pour Power BI
│
├── python/
│   ├── 01_generate_data.py         ← Génération données simulées
│   ├── 02_transform_data.py        ← Nettoyage & transformation
│   ├── 03_load_to_sqlserver.py     ← Chargement SQL Server
│   └── config.py                   ← Configuration connexion
│
├── data/                           ← CSV générés (gitignore en prod)
│   ├── clients.csv
│   ├── factures.csv
│   ├── charges.csv
│   └── budgets.csv
│
├── powerbi_guide/
│   └── GUIDE_POWERBI.md           ← Guide pas-à-pas Power BI
│
└── docs/
    └── MODELE_DONNEES.md          ← Documentation du modèle
```

---

## ⚙️ Installation & Lancement

### Prérequis
- Python 3.9+
- SQL Server 2019+ (ou SQL Server Express gratuit)
- Power BI Desktop (gratuit)
- Driver ODBC 17 pour SQL Server

### 1. Installer les dépendances Python
```bash
pip install pandas numpy pyodbc sqlalchemy openpyxl
```

### 2. Configurer la connexion SQL Server
Éditer `python/config.py` avec vos paramètres serveur.

### 3. Créer la base de données
```bash
# Exécuter dans SQL Server Management Studio (SSMS)
sql/01_create_database.sql
sql/02_create_tables.sql
sql/03_stored_procedures.sql
sql/04_analytical_views.sql
```

### 4. Lancer le pipeline ETL
```bash
python python/01_generate_data.py
python python/02_transform_data.py
python python/03_load_to_sqlserver.py
```

### 5. Ouvrir Power BI
Suivre le guide `powerbi_guide/GUIDE_POWERBI.md`

---

## 📊 Indicateurs Clés (KPIs)

| KPI | Description | Formule DAX |
|-----|-------------|-------------|
| Chiffre d'Affaires | Revenus bruts période | `SUM(fait_revenus[montant_ht])` |
| Marge Brute % | (CA - Charges) / CA | `DIVIDE([CA] - [Charges], [CA])` |
| DSO | Délai moyen de paiement | `AVERAGEX(clients, [jours_paiement])` |
| Budget vs Réalisé | Écart budgétaire | `[Réalisé] - [Budget]` |
| Taux de recouvrement | Factures payées / émises | `DIVIDE([Payées], [Émises])` |

---

## 🎓 Compétences Démontrées

- ✅ Modélisation dimensionnelle (schéma étoile)
- ✅ Pipeline ETL Python → SQL Server
- ✅ T-SQL : procédures stockées, vues, index
- ✅ Power BI : DAX avancé, modélisation, DirectQuery
- ✅ KPIs financiers (CA, marges, DSO, budget)
- ✅ Analyse comptable et financière
