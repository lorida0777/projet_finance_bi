# ============================================================
#  config.py
#  Configuration de la connexion SQL Server
#  Projet : Tableau de Bord Financier – Direction Comptable
# ============================================================

import os

# ─────────────────────────────────────────
#  Paramètres SQL Server
#  → Modifier ces valeurs selon votre environnement
# ─────────────────────────────────────────

DB_CONFIG = {
    # Nom du serveur SQL Server
    # Exemples : "localhost", "DESKTOP-ABC\\SQLEXPRESS", "192.168.1.10"
    "server":   os.getenv("SQL_SERVER",   "H\SQLEXPRESS"),

    # Nom de la base de données
    "database": os.getenv("SQL_DATABASE", "FinanceDB"),

    # Authentification Windows (recommandé en local)
    "trusted_connection": os.getenv("SQL_TRUSTED", "yes"),

    # Authentification SQL Server (si trusted_connection = no)
    "username": os.getenv("SQL_USER",     "sa"),
    "password": os.getenv("SQL_PASSWORD", "VotreMotDePasse123!"),

    # Driver ODBC installé sur la machine
    # Télécharger sur : https://docs.microsoft.com/en-us/sql/connect/odbc/
    "driver":   os.getenv("SQL_DRIVER",   "ODBC Driver 17 for SQL Server"),
}

# ─────────────────────────────────────────
#  Paramètres de génération de données
# ─────────────────────────────────────────

DATA_CONFIG = {
    "nb_clients":       200,        # Nombre de clients à générer
    "nb_produits":      30,         # Nombre de produits/services
    "nb_departements":  8,          # Nombre de départements
    "nb_factures":      5000,       # Nombre de factures à simuler
    "nb_lignes_charges":3000,       # Nombre de lignes de charges
    "annee_debut":      2023,       # Première année des données
    "annee_fin":        2025,       # Dernière année des données
    "seed_aleatoire":   42,         # Graine pour reproductibilité
}

# ─────────────────────────────────────────
#  Chemins des fichiers
# ─────────────────────────────────────────

import pathlib
BASE_DIR  = pathlib.Path(__file__).parent.parent
DATA_DIR  = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

FICHIERS = {
    "clients":          DATA_DIR / "clients.csv",
    "produits":         DATA_DIR / "produits_services.csv",
    "departements":     DATA_DIR / "departements.csv",
    "factures":         DATA_DIR / "factures.csv",
    "charges":          DATA_DIR / "charges.csv",
    "budgets":          DATA_DIR / "budgets.csv",
}


def get_connection_string() -> str:
    """Retourne la chaîne de connexion SQLAlchemy pour SQL Server."""
    cfg = DB_CONFIG
    if cfg["trusted_connection"].lower() == "yes":
        return (
            f"mssql+pyodbc://{cfg['server']}/{cfg['database']}"
            f"?driver={cfg['driver'].replace(' ', '+')}"
            f"&trusted_connection=yes"
        )
    else:
        return (
            f"mssql+pyodbc://{cfg['username']}:{cfg['password']}"
            f"@{cfg['server']}/{cfg['database']}"
            f"?driver={cfg['driver'].replace(' ', '+')}"
        )


def get_odbc_connection_string() -> str:
    """Retourne la chaîne de connexion pyodbc directe."""
    cfg = DB_CONFIG
    if cfg["trusted_connection"].lower() == "yes":
        return (
            f"DRIVER={{{cfg['driver']}}};"
            f"SERVER={cfg['server']};"
            f"DATABASE={cfg['database']};"
            f"Trusted_Connection=yes;"
        )
    else:
        return (
            f"DRIVER={{{cfg['driver']}}};"
            f"SERVER={cfg['server']};"
            f"DATABASE={cfg['database']};"
            f"UID={cfg['username']};"
            f"PWD={cfg['password']};"
        )
