# ============================================================
#  02_transform_data.py
#  Nettoyage, validation et enrichissement des données
#  Projet : Tableau de Bord Financier – Direction Comptable
# ============================================================

import pandas as pd
import numpy as np
from datetime import date, datetime
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from config import FICHIERS

print("=" * 60)
print("  TRANSFORMATION DES DONNÉES")
print("=" * 60)


def rapport_qualite(df: pd.DataFrame, nom: str) -> pd.DataFrame:
    """Affiche un rapport de qualité et retourne le df nettoyé."""
    nb_avant = len(df)
    doublons = df.duplicated().sum()
    nulls    = df.isnull().sum().sum()

    # Supprimer les doublons
    df = df.drop_duplicates()
    nb_apres = len(df)

    print(f"\n  [{nom}]")
    print(f"    Lignes avant  : {nb_avant:,}")
    print(f"    Doublons      : {doublons}")
    print(f"    Valeurs nulles: {nulls}")
    print(f"    Lignes après  : {nb_apres:,}")
    return df


# ─────────────────────────────────────────
#  CLIENTS
# ─────────────────────────────────────────
print("\n[1/4] Transformation des clients...")

df_clients = pd.read_csv(FICHIERS["clients"], encoding="utf-8-sig")
df_clients = rapport_qualite(df_clients, "clients")

# Validation
assert df_clients["code_client"].is_unique, "❌ Codes client en double !"
assert df_clients["statut"].isin(["Actif", "Inactif", "Suspendu"]).all(), "❌ Statut invalide"
assert (df_clients["conditions_paiement"] > 0).all(), "❌ Délai paiement invalide"
assert (df_clients["plafond_credit"] >= 0).all(), "❌ Plafond crédit négatif"

# Normalisation
df_clients["raison_sociale"]    = df_clients["raison_sociale"].str.strip().str.upper()
df_clients["ville"]             = df_clients["ville"].str.strip().str.title()
df_clients["date_entree"]       = pd.to_datetime(df_clients["date_entree"]).dt.date

print("    ✓ Clients validés et normalisés")


# ─────────────────────────────────────────
#  PRODUITS / SERVICES
# ─────────────────────────────────────────
print("\n[2/4] Transformation des produits/services...")

df_produits = pd.read_csv(FICHIERS["produits"], encoding="utf-8-sig")
df_produits = rapport_qualite(df_produits, "produits")

assert df_produits["code_produit"].is_unique
assert (df_produits["prix_catalogue_ht"] > 0).all(), "❌ Prix négatif ou nul"
assert df_produits["taux_tva"].between(0, 100).all(), "❌ TVA invalide"

df_produits["libelle"] = df_produits["libelle"].str.strip()
print("    ✓ Produits validés")


# ─────────────────────────────────────────
#  FACTURES
# ─────────────────────────────────────────
print("\n[3/4] Transformation des factures...")

df_factures = pd.read_csv(FICHIERS["factures"], encoding="utf-8-sig")
df_factures = rapport_qualite(df_factures, "factures")

# Dates
df_factures["date_emission"]  = pd.to_datetime(df_factures["date_emission"])
df_factures["date_echeance"]  = pd.to_datetime(df_factures["date_echeance"])
df_factures["date_paiement"]  = pd.to_datetime(df_factures["date_paiement"], errors="coerce")

# Recalcul des montants (cohérence)
df_factures["montant_ht_calc"] = (
    df_factures["prix_unitaire_ht"]
    * df_factures["quantite"]
    * (1 - df_factures["remise_pct"] / 100)
).round(2)

ecart_montants = (df_factures["montant_ht"] - df_factures["montant_ht_calc"]).abs()
nb_ecarts = (ecart_montants > 0.05).sum()
if nb_ecarts > 0:
    print(f"    ⚠ {nb_ecarts} écarts de montant corrigés")
    df_factures["montant_ht"] = df_factures["montant_ht_calc"]
df_factures.drop(columns=["montant_ht_calc"], inplace=True)

# Validation montants
assert (df_factures["montant_ht"] > 0).all(), "❌ Montant HT négatif"
assert (df_factures["montant_encaisse"] >= 0).all()
assert (df_factures["montant_encaisse"] <= df_factures["montant_ht"] + 0.01).all(), "❌ Encaissé > facturé"

# Dates incohérentes
masque_date = df_factures["date_echeance"] < df_factures["date_emission"]
if masque_date.sum() > 0:
    print(f"    ⚠ {masque_date.sum()} échéances antérieures corrigées")
    df_factures.loc[masque_date, "date_echeance"] = (
        df_factures.loc[masque_date, "date_emission"]
        + pd.Timedelta(days=30)
    )

# Ajout colonnes dérivées
df_factures["annee_emission"]   = df_factures["date_emission"].dt.year
df_factures["mois_emission"]    = df_factures["date_emission"].dt.month
df_factures["trimestre"]        = df_factures["date_emission"].dt.quarter
df_factures["date_id_emission"] = df_factures["date_emission"].dt.strftime("%Y%m%d").astype(int)
df_factures["date_id_echeance"] = df_factures["date_echeance"].dt.strftime("%Y%m%d").astype(int)
df_factures["date_id_paiement"] = (
    df_factures["date_paiement"]
    .dt.strftime("%Y%m%d")
    .fillna("0")
    .astype(int)
    .replace(0, np.nan)
)

# Tranche retard
def tranche_retard(jours):
    if jours == 0:   return "Dans les délais"
    if jours <= 30:  return "Retard < 30j"
    if jours <= 60:  return "Retard 31-60j"
    if jours <= 90:  return "Retard 61-90j"
    return "Contentieux > 90j"

df_factures["tranche_retard"] = df_factures["jours_retard"].apply(tranche_retard)

df_factures.to_csv(FICHIERS["factures"], index=False, encoding="utf-8-sig")
print(f"    ✓ {len(df_factures):,} factures transformées et enrichies")


# ─────────────────────────────────────────
#  CHARGES
# ─────────────────────────────────────────
print("\n[4/4] Transformation des charges...")

df_charges = pd.read_csv(FICHIERS["charges"], encoding="utf-8-sig")
df_charges = rapport_qualite(df_charges, "charges")

df_charges["date_charge"]    = pd.to_datetime(df_charges["date_charge"])
df_charges["date_id_charge"] = df_charges["date_charge"].dt.strftime("%Y%m%d").astype(int)
df_charges["annee"]          = df_charges["date_charge"].dt.year
df_charges["mois"]           = df_charges["date_charge"].dt.month

assert (df_charges["montant_ht"] > 0).all(), "❌ Charge négative ou nulle"

# Vérification cohérence TTC = HT + TVA
ecart_ttc = (df_charges["montant_ttc"] - df_charges["montant_ht"] - df_charges["montant_tva"]).abs()
if (ecart_ttc > 0.05).sum() > 0:
    df_charges["montant_ttc"] = (df_charges["montant_ht"] + df_charges["montant_tva"]).round(2)

df_charges.to_csv(FICHIERS["charges"], index=False, encoding="utf-8-sig")
print(f"    ✓ {len(df_charges):,} charges transformées")


# ─────────────────────────────────────────
#  RÉSUMÉ STATISTIQUE
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("  RÉSUMÉ DES DONNÉES TRANSFORMÉES")
print("=" * 60)
print(f"  Clients         : {len(df_clients):>6,}")
print(f"  Produits        : {len(df_produits):>6,}")
print(f"  Factures        : {len(df_factures):>6,}")
print(f"  Lignes charges  : {len(df_charges):>6,}")
print(f"\n  CA Total HT     : {df_factures['montant_ht'].sum():>12,.0f} MGA")
print(f"  Charges Total   : {df_charges['montant_ht'].sum():>12,.0f} MGA")
print(f"  Résultat net    : {df_factures['montant_ht'].sum() - df_charges['montant_ht'].sum():>12,.0f} MGA")
print(f"  Encaissements   : {df_factures['montant_encaisse'].sum():>12,.0f} MGA")
print(f"\n  Répartition statuts :")
for statut, nb in df_factures["statut_paiement"].value_counts().items():
    pct = nb / len(df_factures) * 100
    print(f"    {statut:<20} : {nb:>5,} ({pct:.1f}%)")

print("\nProchaine étape → python 03_load_to_sqlserver.py")
