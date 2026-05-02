# ============================================================
#  01_generate_data.py
#  Génération de données financières réalistes
#  Projet : Tableau de Bord Financier – Direction Comptable
# ============================================================

import pandas as pd
import numpy as np
from datetime import date, timedelta
import random
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from config import DATA_CONFIG, FICHIERS

# Reproductibilité
SEED = DATA_CONFIG["seed_aleatoire"]
random.seed(SEED)
np.random.seed(SEED)

print("=" * 60)
print("  GÉNÉRATION DES DONNÉES – Tableau de Bord Financier")
print("=" * 60)


# ─────────────────────────────────────────
#  1. DÉPARTEMENTS
# ─────────────────────────────────────────
print("\n[1/5] Génération des départements...")

departements_data = [
    ("DEPT-001", "Audit Légal",          "Direction Technique",   "Marie Rakoto",    850000,  "CC-100"),
    ("DEPT-002", "Expertise Comptable",  "Direction Technique",   "Jean Rasolo",     720000,  "CC-110"),
    ("DEPT-003", "Conseil Financier",    "Direction Technique",   "Sophie Randria",  640000,  "CC-120"),
    ("DEPT-004", "Fiscalité",            "Direction Technique",   "Paul Rabemanana", 580000,  "CC-130"),
    ("DEPT-005", "Ressources Humaines",  "Direction Support",     "Alice Ratsima",   310000,  "CC-200"),
    ("DEPT-006", "Informatique & SI",    "Direction Support",     "Kevin Andriana",  420000,  "CC-210"),
    ("DEPT-007", "Commercial",           "Direction Commerciale", "Marc Rabeson",    390000,  "CC-300"),
    ("DEPT-008", "Direction Générale",   "Direction Générale",    "Pierre Rakoton",  250000,  "CC-400"),
]

df_departements = pd.DataFrame(departements_data, columns=[
    "code_dept", "nom_departement", "direction", "responsable",
    "budget_annuel", "centre_cout"
])
df_departements.to_csv(FICHIERS["departements"], index=False, encoding="utf-8-sig")
print(f"  ✓ {len(df_departements)} départements générés")


# ─────────────────────────────────────────
#  2. PRODUITS / SERVICES
# ─────────────────────────────────────────
print("\n[2/5] Génération des produits/services...")

produits_data = [
    # Audit
    ("SVC-001", "Audit légal annuel – TPE",           "Audit",    "Audit légal",     "Forfait",  3500),
    ("SVC-002", "Audit légal annuel – PME",           "Audit",    "Audit légal",     "Forfait",  8500),
    ("SVC-003", "Audit légal annuel – ETI/GE",        "Audit",    "Audit légal",     "Forfait", 22000),
    ("SVC-004", "Audit contractuel",                  "Audit",    "Audit contractuel","Journée",  1200),
    ("SVC-005", "Due diligence financière",           "Audit",    "Audit contractuel","Forfait", 15000),
    # Expertise Comptable
    ("SVC-006", "Tenue comptabilité mensuelle – TPE", "Expertise","Comptabilité",    "Forfait",   450),
    ("SVC-007", "Tenue comptabilité mensuelle – PME", "Expertise","Comptabilité",    "Forfait",  1200),
    ("SVC-008", "Établissement bilan annuel",         "Expertise","Bilan",           "Forfait",  2500),
    ("SVC-009", "Déclaration TVA mensuelle",          "Expertise","Fiscalité courante","Forfait",  180),
    ("SVC-010", "Paie et charges sociales",           "Expertise","Social",          "Bulletin",   45),
    # Conseil Financier
    ("SVC-011", "Business plan & prévisionnel",       "Conseil",  "Stratégie",       "Forfait",  4500),
    ("SVC-012", "Tableau de bord de gestion",         "Conseil",  "Reporting",       "Forfait",  3200),
    ("SVC-013", "Analyse de rentabilité",             "Conseil",  "Analyse",         "Journée",  1100),
    ("SVC-014", "Conseil en restructuration",         "Conseil",  "Stratégie",       "Journée",  1500),
    ("SVC-015", "Optimisation de trésorerie",         "Conseil",  "Trésorerie",      "Forfait",  2800),
    # Fiscalité
    ("SVC-016", "Déclaration IS annuelle",            "Fiscalité","Fiscalité",       "Forfait",  1800),
    ("SVC-017", "Déclaration IRSA",                  "Fiscalité","Fiscalité",       "Forfait",   950),
    ("SVC-018", "Audit fiscal",                       "Fiscalité","Audit fiscal",    "Forfait",  6500),
    ("SVC-019", "Conseil fiscal ponctuel",            "Fiscalité","Conseil fiscal",  "Heure",     180),
    ("SVC-020", "Contentieux fiscal",                 "Fiscalité","Contentieux",     "Journée",  1400),
    # Formation
    ("SVC-021", "Formation Power BI – 2 jours",       "Formation","BI & Data",       "Journée",   800),
    ("SVC-022", "Formation Excel avancé",             "Formation","Bureautique",     "Journée",   600),
    ("SVC-023", "Formation comptabilité OHADA",       "Formation","Comptabilité",    "Journée",   750),
    ("SVC-024", "Formation fiscalité entreprises",    "Formation","Fiscalité",       "Journée",   700),
]

df_produits = pd.DataFrame(produits_data, columns=[
    "code_produit", "libelle", "categorie", "sous_categorie",
    "unite_facturation", "prix_catalogue_ht"
])
df_produits["taux_tva"] = 20.0
df_produits["actif"] = 1
df_produits.to_csv(FICHIERS["produits"], index=False, encoding="utf-8-sig")
print(f"  ✓ {len(df_produits)} produits/services générés")


# ─────────────────────────────────────────
#  3. CLIENTS
# ─────────────────────────────────────────
print("\n[3/5] Génération des clients...")

secteurs = ["BTP", "Commerce", "Transport", "Agriculture", "Industrie",
            "Services", "Hôtellerie", "Technologie", "Santé", "Éducation"]
tailles  = ["TPE"] * 50 + ["PME"] * 35 + ["ETI"] * 12 + ["GE"] * 3
segments = {"TPE": "Standard", "PME": "Standard", "ETI": "Grand Compte", "GE": "Grand Compte"}
villes   = ["Antananarivo", "Toamasina", "Antsirabe", "Fianarantsoa",
            "Mahajanga", "Toliara", "Antsiranana", "Ambatondrazaka"]
regions  = {"Antananarivo": "Analamanga", "Toamasina": "Atsinanana",
            "Antsirabe": "Vakinankaratra", "Fianarantsoa": "Haute Matsiatra",
            "Mahajanga": "Boeny", "Toliara": "Atsimo-Andrefana",
            "Antsiranana": "Diana", "Ambatondrazaka": "Alaotra-Mangoro"}

noms_entreprises = [
    "SOMATRANS", "AGRI-MADAG", "HOTEL TROPICAL", "TECH MADA", "CONSTRUCTION PLUS",
    "PHARMA ISLAND", "MEDIA GROUP", "AGRO EXPORT", "LOGISTIC PRO", "IMMO INVEST",
    "ELECTRICITE MADA", "BRASSERIE STAR", "CIMENT MADA", "COTONA", "SUCOMA",
    "JIRAMA NORD", "TELMA", "ORANGE MADA", "AIRTEL MADA", "MVOLA",
    "CREDIT FONCIER", "BOA MADA", "BMOI", "SBM BANK", "ACCESS BANK",
    "SOPROGIM", "SOCOLAIT", "SOVI", "TIKO GROUP", "SME MADA",
]

clients = []
date_min = date(2020, 1, 1)
date_max = date(2023, 6, 30)

for i in range(DATA_CONFIG["nb_clients"]):
    taille = random.choice(tailles)
    ville  = random.choice(villes)
    cond   = {"TPE": 30, "PME": 45, "ETI": 60, "GE": 90}[taille]
    plafond= {"TPE": 10000, "PME": 50000, "ETI": 200000, "GE": 500000}[taille]
    nom    = noms_entreprises[i % len(noms_entreprises)] + (f" {i//len(noms_entreprises)+1}" if i >= len(noms_entreprises) else "")
    delta  = (date_max - date_min).days
    d_entree = date_min + timedelta(days=random.randint(0, delta))

    clients.append({
        "code_client":        f"CLI-{i+1:04d}",
        "raison_sociale":     nom,
        "secteur_activite":   random.choice(secteurs),
        "taille_entreprise":  taille,
        "ville":              ville,
        "region":             regions[ville],
        "pays":               "Madagascar",
        "date_entree":        d_entree.isoformat(),
        "statut":             random.choices(["Actif", "Inactif", "Suspendu"], weights=[85, 10, 5])[0],
        "segment":            segments[taille],
        "plafond_credit":     plafond,
        "conditions_paiement":cond,
    })

df_clients = pd.DataFrame(clients)
df_clients.to_csv(FICHIERS["clients"], index=False, encoding="utf-8-sig")
print(f"  ✓ {len(df_clients)} clients générés")


# ─────────────────────────────────────────
#  4. FACTURES
# ─────────────────────────────────────────
print("\n[4/5] Génération des factures...")

annee_debut = DATA_CONFIG["annee_debut"]
annee_fin   = DATA_CONFIG["annee_fin"]
date_debut  = date(annee_debut, 1, 1)
date_fin    = date(annee_fin, 12, 31)
nb_jours    = (date_fin - date_debut).days

# Clients actifs uniquement
clients_actifs = df_clients[df_clients["statut"] == "Actif"]["code_client"].tolist()
produits_list  = df_produits["code_produit"].tolist()
depts_tech     = ["DEPT-001", "DEPT-002", "DEPT-003", "DEPT-004", "DEPT-007"]

factures = []
for i in range(DATA_CONFIG["nb_factures"]):
    code_client  = random.choice(clients_actifs)
    client_row   = df_clients[df_clients["code_client"] == code_client].iloc[0]
    code_produit = random.choice(produits_list)
    produit_row  = df_produits[df_produits["code_produit"] == code_produit].iloc[0]

    # Date d'émission (pondération : plus de factures en fin d'année)
    date_emission = date_debut + timedelta(days=random.randint(0, nb_jours))
    cond_paiement = int(client_row["conditions_paiement"])
    date_echeance = date_emission + timedelta(days=cond_paiement)

    # Quantité selon unité
    if produit_row["unite_facturation"] == "Bulletin":
        quantite = random.randint(1, 50)
    elif produit_row["unite_facturation"] == "Heure":
        quantite = random.randint(2, 20)
    elif produit_row["unite_facturation"] == "Journée":
        quantite = random.randint(1, 10)
    else:
        quantite = 1

    prix_ht     = float(produit_row["prix_catalogue_ht"])
    remise      = random.choices([0, 5, 10, 15], weights=[60, 20, 15, 5])[0]
    montant_ht  = round(prix_ht * quantite * (1 - remise / 100), 2)
    tva         = float(produit_row["taux_tva"])
    montant_tva = round(montant_ht * tva / 100, 2)
    montant_ttc = round(montant_ht + montant_tva, 2)

    # Statut paiement
    jours_depuis_echeance = (date.today() - date_echeance).days
    if date_echeance > date.today():
        statut = "En attente"
        date_paiement = None
        encaisse = 0.0
        jours_retard = 0
    else:
        statut_choix = random.choices(
            ["Payée", "Retard", "Partielle", "Contentieux"],
            weights=[65, 20, 10, 5]
        )[0]
        if statut_choix == "Payée":
            retard = max(0, random.randint(-5, 30))
            date_paiement = (date_echeance + timedelta(days=retard)).isoformat()
            encaisse = montant_ht
            jours_retard = retard
            statut = "Payée"
        elif statut_choix == "Partielle":
            date_paiement = None
            encaisse = round(montant_ht * random.uniform(0.3, 0.8), 2)
            jours_retard = max(0, jours_depuis_echeance)
            statut = "Partielle"
        elif statut_choix == "Contentieux":
            date_paiement = None
            encaisse = 0.0
            jours_retard = max(91, jours_depuis_echeance)
            statut = "Contentieux"
        else:
            date_paiement = None
            encaisse = 0.0
            jours_retard = max(0, jours_depuis_echeance)
            statut = "Retard"

    factures.append({
        "numero_facture":   f"FAC-{annee_debut + i // 1700}-{i+1:05d}",
        "date_emission":    date_emission.isoformat(),
        "date_echeance":    date_echeance.isoformat(),
        "date_paiement":    date_paiement,
        "code_client":      code_client,
        "code_produit":     code_produit,
        "code_dept":        random.choice(depts_tech),
        "quantite":         quantite,
        "prix_unitaire_ht": prix_ht,
        "remise_pct":       remise,
        "montant_ht":       montant_ht,
        "montant_tva":      montant_tva,
        "montant_ttc":      montant_ttc,
        "statut_paiement":  statut,
        "montant_encaisse": encaisse,
        "jours_retard":     jours_retard,
    })

df_factures = pd.DataFrame(factures)
df_factures.to_csv(FICHIERS["factures"], index=False, encoding="utf-8-sig")
print(f"  ✓ {len(df_factures)} factures générées")
print(f"     CA total HT : {df_factures['montant_ht'].sum():,.0f} MGA")
print(f"     Taux de recouvrement : {(df_factures['montant_encaisse'].sum() / df_factures['montant_ht'].sum() * 100):.1f}%")


# ─────────────────────────────────────────
#  5. CHARGES
# ─────────────────────────────────────────
print("\n[5/5] Génération des charges...")

categories_charges = {
    "Salaires & Charges sociales": {
        "sous": ["Salaires bruts", "Charges patronales", "Avantages en nature"],
        "depts": ["DEPT-001","DEPT-002","DEPT-003","DEPT-004","DEPT-005","DEPT-006","DEPT-007","DEPT-008"],
        "montant": (5000, 80000), "budgetee": 0.98
    },
    "Loyer & Charges locatives": {
        "sous": ["Loyer bureaux", "Charges communes", "Assurance locaux"],
        "depts": ["DEPT-008"],
        "montant": (2000, 8000), "budgetee": 1.0
    },
    "Informatique & Licences": {
        "sous": ["Licences logiciels", "Matériel informatique", "Cloud & hébergement", "Maintenance SI"],
        "depts": ["DEPT-006", "DEPT-008"],
        "montant": (500, 15000), "budgetee": 0.85
    },
    "Déplacements & Missions": {
        "sous": ["Transport", "Hôtel & restauration", "Carburant"],
        "depts": ["DEPT-001","DEPT-002","DEPT-003","DEPT-007"],
        "montant": (200, 3000), "budgetee": 0.70
    },
    "Fournitures & Consommables": {
        "sous": ["Fournitures de bureau", "Consommables informatique", "Documentation"],
        "depts": ["DEPT-005", "DEPT-008"],
        "montant": (100, 1500), "budgetee": 0.90
    },
    "Formation & Développement": {
        "sous": ["Formations externes", "Certifications", "Abonnements professionnels"],
        "depts": ["DEPT-005", "DEPT-001", "DEPT-002"],
        "montant": (500, 5000), "budgetee": 0.75
    },
    "Sous-traitance": {
        "sous": ["Expertise externe", "Consultants", "Prestations ponctuelles"],
        "depts": ["DEPT-001","DEPT-002","DEPT-003","DEPT-004"],
        "montant": (1000, 20000), "budgetee": 0.60
    },
}

fournisseurs = [
    "TOTAL MADA", "ORANGE PRO", "MICROSOFT MADA", "IBM MADA", "ORACLE",
    "BAILLEUR IMMO", "AGENCE VOYAGE", "HOTEL COLBERT", "FOURNITURES PRO", "CONSULTANTS SA",
    "FORMATION PLUS", "TRANSPORT EXPRESS", "SECURITE MADA", "NETTOYAGE SERVICE", "IT SOLUTIONS"
]

charges = []
for i in range(DATA_CONFIG["nb_lignes_charges"]):
    categorie = random.choice(list(categories_charges.keys()))
    cfg_cat   = categories_charges[categorie]
    date_charge = date_debut + timedelta(days=random.randint(0, nb_jours))
    montant_ht  = round(random.uniform(*cfg_cat["montant"]), 2)
    tva_deductible = 0.20 if categorie not in ["Salaires & Charges sociales", "Loyer & Charges locatives"] else 0.0
    montant_tva = round(montant_ht * tva_deductible, 2)
    est_budgetee = 1 if random.random() < cfg_cat["budgetee"] else 0

    charges.append({
        "numero_piece":     f"PCE-{i+1:06d}",
        "date_charge":      date_charge.isoformat(),
        "code_dept":        random.choice(cfg_cat["depts"]),
        "categorie_charge": categorie,
        "sous_categorie":   random.choice(cfg_cat["sous"]),
        "fournisseur":      random.choice(fournisseurs),
        "nature_charge":    "Exploitation",
        "montant_ht":       montant_ht,
        "montant_tva":      montant_tva,
        "montant_ttc":      round(montant_ht + montant_tva, 2),
        "est_budgetee":     est_budgetee,
    })

df_charges = pd.DataFrame(charges)
df_charges.to_csv(FICHIERS["charges"], index=False, encoding="utf-8-sig")
print(f"  ✓ {len(df_charges)} lignes de charges générées")
print(f"     Total charges HT : {df_charges['montant_ht'].sum():,.0f} MGA")

print("\n" + "=" * 60)
print("  GÉNÉRATION TERMINÉE – Fichiers CSV sauvegardés dans /data")
print("=" * 60)
print("\nProchaine étape → python 02_transform_data.py")
