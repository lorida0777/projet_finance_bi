# 📐 Documentation du Modèle de Données
### Projet : Tableau de Bord Financier – Direction Comptable

---

## Schéma en Étoile

```
                    ┌──────────────────┐
                    │   dim.Temps      │
                    ├──────────────────┤
                    │ date_id (PK)     │
                    │ date_complete    │
                    │ jour/mois/annee  │
                    │ trimestre        │
                    │ libelle_periode  │
                    │ est_weekend      │
                    │ est_ferie        │
                    └────────┬─────────┘
                             │
      ┌──────────────────────┼──────────────────────┐
      │                      │                      │
┌─────┴────────┐   ┌─────────┴──────────┐   ┌──────┴────────────┐
│ dim.Client   │   │   fait.Revenus     │   │dim.ProduitService │
├──────────────┤   ├────────────────────┤   ├───────────────────┤
│ client_id(PK)│◄──│ client_id (FK)     │   │ produit_id (PK)   │
│ code_client  │   │ produit_id (FK)  ──┼──►│ code_produit      │
│ raison_sociale│  │ dept_id (FK)    ───┼─┐ │ libelle           │
│ secteur      │   │ date_id (FK)       │ │ │ categorie         │
│ taille       │   │ date_echeance_id   │ │ │ prix_catalogue_ht │
│ segment      │   │ date_paiement_id   │ │ └───────────────────┘
│ conditions_  │   │ numero_facture     │ │
│   paiement   │   │ montant_ht         │ │ ┌───────────────────┐
└──────────────┘   │ montant_tva        │ └►│ dim.Departement   │
                   │ montant_encaisse   │   ├───────────────────┤
                   │ statut_paiement    │   │ dept_id (PK)      │
                   │ jours_retard       │   │ code_dept         │
                   └────────────────────┘   │ nom_departement   │
                                            │ direction         │
                   ┌────────────────────┐   │ budget_annuel     │
                   │   fait.Charges     │   └───────────────────┘
                   ├────────────────────┤
                   │ charge_id (PK)     │
                   │ date_id (FK)    ───┼──► dim.Temps
                   │ dept_id (FK)    ───┼──► dim.Departement
                   │ categorie_charge   │
                   │ montant_ht         │
                   └────────────────────┘

                   ┌────────────────────┐
                   │   fait.Budget      │
                   ├────────────────────┤
                   │ budget_id (PK)     │
                   │ annee, mois        │
                   │ dept_id (FK)    ───┼──► dim.Departement
                   │ montant_budget     │
                   │ type_budget        │
                   └────────────────────┘
```

---

## Dictionnaire des données

### fait.Revenus – Champs clés

| Champ | Type | Description |
|-------|------|-------------|
| `montant_ht` | DECIMAL(15,2) | Montant hors taxe après remise |
| `montant_encaisse` | DECIMAL(15,2) | Somme effectivement reçue |
| `jours_retard` | INT | Délai après échéance (mis à jour automatiquement) |
| `statut_paiement` | VARCHAR | En attente / Payée / Partielle / Retard / Contentieux |

### Règle de calcul DSO
```
DSO = Moyenne des jours_retard sur les factures avec statut = 'Payée'
Objectif BIOS Expertise : DSO < 45 jours
```

### Règle de calcul Marge
```
Marge Nette = (CA HT - Total Charges HT) / CA HT × 100
Seuil d'alerte : Marge < 20%
```
