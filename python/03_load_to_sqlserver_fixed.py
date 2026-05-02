# ============================================================
#  03_load_to_sqlserver.py
#  Chargement des données dans SQL Server (FinanceDB)
#  Projet : Tableau de Bord Financier – Direction Comptable
# ============================================================

import pandas as pd
import numpy as np
from datetime import date, timedelta
import pyodbc
import sqlalchemy
from sqlalchemy import create_engine, text
import sys, os, time

sys.path.insert(0, os.path.dirname(__file__))
from config import FICHIERS, get_connection_string, get_odbc_connection_string

print("=" * 60)
print("  CHARGEMENT SQL SERVER – FinanceDB")
print("=" * 60)


# ─────────────────────────────────────────
#  Connexion
# ─────────────────────────────────────────
print("\n[0] Connexion à SQL Server...")
try:
    engine = create_engine(
        get_connection_string(),
        fast_executemany=True,          # Performance bulk insert
        connect_args={"timeout": 30},
    )
    with engine.connect() as conn:
        version = conn.execute(text("SELECT @@VERSION")).fetchone()[0]
        print(f"  ✓ Connecté : {version[:50]}...")
except Exception as e:
    print(f"  ❌ Échec de connexion : {e}")
    print("\n  Vérifiez :")
    print("    1. SQL Server est démarré")
    print("    2. config.py contient les bons paramètres")
    print("    3. Driver ODBC 17 est installé")
    sys.exit(1)


def charger_table(df: pd.DataFrame, schema: str, table: str,
                  engine, if_exists: str = "append", chunksize: int = 500) -> int:
    """Charge un DataFrame dans SQL Server avec gestion des erreurs."""
    t0 = time.time()
    df.to_sql(
        name=table, schema=schema, con=engine,
        if_exists=if_exists, index=False, chunksize=chunksize
    )
    duree = time.time() - t0
    print(f"    ✓ {len(df):,} lignes → {schema}.{table} ({duree:.1f}s)")
    return len(df)


# ─────────────────────────────────────────
#  1. CALENDRIER via procédure stockée
# ─────────────────────────────────────────
print("\n[0/5] Nettoyage préalable (désactivation FK + suppression)...")
with engine.connect() as conn:
    # Désactiver toutes les contraintes FK pour éviter les conflits
    conn.execute(text("EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL'"))
    # Vider faits en premier, puis dimensions
    for tbl in [
        "fait.Budget", "fait.Charges", "fait.Revenus",
        "dim.Client", "dim.ProduitService", "dim.Departement", "dim.Temps"
    ]:
        try:
            conn.execute(text(f"DELETE FROM {tbl}"))
            print(f"    ✓ {tbl} vidée")
        except Exception as e:
            print(f"    ⚠ {tbl} ignorée : {e}")
    # Réactiver les contraintes
    conn.execute(text("EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL'"))
    conn.commit()
print("    ✓ Nettoyage terminé")

print("\n[1/5] Génération du calendrier (procédure stockée)...")
with engine.connect() as conn:
    conn.execute(text("EXEC dim.usp_GenerateCalendar @DateDebut='2022-01-01', @DateFin='2026-12-31'"))
    nb_dates = conn.execute(text("SELECT COUNT(*) FROM dim.Temps")).fetchone()[0]
    conn.commit()
print(f"    ✓ {nb_dates:,} dates dans dim.Temps")


# ─────────────────────────────────────────
#  2. DÉPARTEMENTS
# ─────────────────────────────────────────
print("\n[2/5] Chargement des départements...")
df_depts = pd.read_csv(FICHIERS["departements"], encoding="utf-8-sig")
charger_table(df_depts, "dim", "Departement", engine)

# Récupérer les IDs générés
with engine.connect() as conn:
    dept_map = pd.read_sql("SELECT dept_id, code_dept FROM dim.Departement", conn)
dept_id_map = dict(zip(dept_map["code_dept"], dept_map["dept_id"]))


# ─────────────────────────────────────────
#  3. CLIENTS
# ─────────────────────────────────────────
print("\n[3/5] Chargement des clients...")
df_clients = pd.read_csv(FICHIERS["clients"], encoding="utf-8-sig")
charger_table(df_clients, "dim", "Client", engine)

with engine.connect() as conn:
    client_map = pd.read_sql("SELECT client_id, code_client FROM dim.Client", conn)
client_id_map = dict(zip(client_map["code_client"], client_map["client_id"]))


# ─────────────────────────────────────────
#  4. PRODUITS / SERVICES
# ─────────────────────────────────────────
print("\n[4/5] Chargement des produits/services...")
df_produits = pd.read_csv(FICHIERS["produits"], encoding="utf-8-sig")

charger_table(df_produits, "dim", "ProduitService", engine)

with engine.connect() as conn:
    produit_map = pd.read_sql("SELECT produit_id, code_produit FROM dim.ProduitService", conn)
produit_id_map = dict(zip(produit_map["code_produit"], produit_map["produit_id"]))


# ─────────────────────────────────────────
#  5. FAITS : REVENUS (Factures)
# ─────────────────────────────────────────
print("\n[5/6] Chargement des factures (fait.Revenus)...")
df_factures = pd.read_csv(FICHIERS["factures"], encoding="utf-8-sig")

# Résolution des clés étrangères
df_factures["client_id"]  = df_factures["code_client"].map(client_id_map)
df_factures["produit_id"] = df_factures["code_produit"].map(produit_id_map)
df_factures["dept_id"]    = df_factures["code_dept"].map(dept_id_map)

# Vérification intégrité référentielle
nb_orphelins = df_factures[["client_id","produit_id","dept_id"]].isnull().any(axis=1).sum()
if nb_orphelins > 0:
    print(f"    ⚠ {nb_orphelins} factures orphelines supprimées")
    df_factures = df_factures.dropna(subset=["client_id","produit_id","dept_id"])

# Filtrer les factures dont les dates ne sont pas dans dim.Temps
valid_dates = set()
with engine.connect() as conn:
    rows = conn.execute(text("SELECT date_id FROM dim.Temps")).fetchall()
    valid_dates = {r[0] for r in rows}

nb_avant = len(df_factures)
df_factures = df_factures[
    df_factures["date_id_emission"].isin(valid_dates) &
    df_factures["date_id_echeance"].isin(valid_dates) &
    (df_factures["date_id_paiement"].isna() | df_factures["date_id_paiement"].isin(valid_dates))
]
nb_apres = len(df_factures)
if nb_avant != nb_apres:
    print(f"    ⚠ {nb_avant - nb_apres} factures filtrées (dates hors calendrier)")
else:
    print(f"    ✓ Toutes les dates sont dans le calendrier")

# Sélection colonnes SQL
cols_revenus = [
    "date_id_emission", "client_id", "produit_id", "dept_id",
    "numero_facture", "date_id_echeance",
    "quantite", "prix_unitaire_ht", "remise_pct",
    "montant_ht", "montant_tva", "montant_ttc",
    "statut_paiement", "date_id_paiement",
    "montant_encaisse", "jours_retard",
]

df_load = df_factures[cols_revenus].rename(columns={
    "date_id_emission":  "date_id",
    "date_id_echeance":  "date_echeance_id",
    "date_id_paiement":  "date_paiement_id",
})

# Convertir NaN en None pour SQL
df_load["date_paiement_id"] = df_load["date_paiement_id"].where(
    df_load["date_paiement_id"].notna(), None
)
df_load[["client_id","produit_id","dept_id"]] = df_load[
    ["client_id","produit_id","dept_id"]
].astype(int)

charger_table(df_load, "fait", "Revenus", engine, chunksize=200)


# ─────────────────────────────────────────
#  6. FAITS : CHARGES
# ─────────────────────────────────────────
print("\n[6/6] Chargement des charges (fait.Charges)...")
df_charges = pd.read_csv(FICHIERS["charges"], encoding="utf-8-sig")

df_charges["dept_id"] = df_charges["code_dept"].map(dept_id_map)
df_charges = df_charges.dropna(subset=["dept_id"])

cols_charges = [
    "date_id_charge", "dept_id",
    "numero_piece", "categorie_charge", "sous_categorie",
    "fournisseur", "nature_charge",
    "montant_ht", "montant_tva", "montant_ttc",
    "est_budgetee",
]

df_load_ch = df_charges[cols_charges].rename(columns={"date_id_charge": "date_id"})
df_load_ch["dept_id"] = df_load_ch["dept_id"].astype(int)

charger_table(df_load_ch, "fait", "Charges", engine, chunksize=200)


# ─────────────────────────────────────────
#  POST-TRAITEMENT : jours de retard
# ─────────────────────────────────────────
print("\n[Post] Mise à jour des jours de retard...")
with engine.connect() as conn:
    conn.execute(text("EXEC fait.usp_UpdateJoursRetard"))
    conn.commit()
print("    ✓ Statuts de paiement mis à jour")


# ─────────────────────────────────────────
#  VALIDATION FINALE
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("  VALIDATION FINALE")
print("=" * 60)

with engine.connect() as conn:
    stats = {
        "dim.Temps":            conn.execute(text("SELECT COUNT(*) FROM dim.Temps")).scalar(),
        "dim.Client":           conn.execute(text("SELECT COUNT(*) FROM dim.Client")).scalar(),
        "dim.ProduitService":   conn.execute(text("SELECT COUNT(*) FROM dim.ProduitService")).scalar(),
        "dim.Departement":      conn.execute(text("SELECT COUNT(*) FROM dim.Departement")).scalar(),
        "fait.Revenus":         conn.execute(text("SELECT COUNT(*) FROM fait.Revenus")).scalar(),
        "fait.Charges":         conn.execute(text("SELECT COUNT(*) FROM fait.Charges")).scalar(),
    }
    ca_total = conn.execute(text("SELECT SUM(montant_ht) FROM fait.Revenus")).scalar()
    charges_total = conn.execute(text("SELECT SUM(montant_ht) FROM fait.Charges")).scalar()

for table, nb in stats.items():
    print(f"  {table:<25} : {nb:>6,} lignes")

print(f"\n  CA Total HT     : {ca_total:>12,.0f} MGA")
print(f"  Charges Total   : {charges_total:>12,.0f} MGA")
print(f"  Résultat net    : {ca_total - charges_total:>12,.0f} MGA")

print("\n" + "=" * 60)
print("  CHARGEMENT TERMINÉ ✓")
print("  Ouvrir Power BI Desktop et connecter à FinanceDB")
print("  Se référer à : powerbi_guide/GUIDE_POWERBI.md")
print("=" * 60)
