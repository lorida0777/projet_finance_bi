# 📊 Guide Power BI – Tableau de Bord Financier
### Connexion SQL Server + Modèle + DAX + Mise en page

---

## 1. Connexion à SQL Server

### Étapes dans Power BI Desktop

1. **Ouvrir** Power BI Desktop
2. **Accueil → Obtenir des données → SQL Server**
3. Renseigner :
   - **Serveur** : `lH\SQLEXPRESS` (ou votre serveur)
   - **Base de données** : `FinanceDB`
   - **Mode de connectivité** : `Import` (recommandé pour la démo)
4. Sélectionner **uniquement les vues** du schéma `rpt` :
   - `rpt.vw_Revenus`
   - `rpt.vw_Charges`
   - `rpt.vw_BudgetVsRealise`
   - `rpt.vw_KPIs_Executifs`
5. Cliquer **Charger**

---

## 2. Modèle de données Power BI

### Relations à créer manuellement

Dans **Vue Modèle** (icône diagramme à gauche) :

```
vw_KPIs_Executifs                vw_Revenus
  [annee, mois]  ──────────────► [annee_emission, mois_emission]

vw_BudgetVsRealise               vw_Charges
  [annee, mois]  ──────────────► [annee, mois]
```

> 💡 **Conseil** : Créer une table Calendrier partagée dans Power BI
> via **Nouvelle table** → `Calendrier = CALENDARAUTO()`
> puis relier toutes les tables sur la colonne date.

---

## 3. Mesures DAX – À créer dans une table "Mesures"

### Créer la table de mesures
**Modélisation → Nouvelle table** → `Mesures = {}`

Puis **Modélisation → Nouvelle mesure** pour chacune :

---

### 3.1 Mesures de base – Revenus

```dax
// Chiffre d'affaires HT
CA HT =
SUM(vw_Revenus[montant_ht])

// CA avec période de comparaison
CA HT (Mois Précédent) =
CALCULATE([CA HT], PREVIOUSMONTH(vw_Revenus[date_emission]))

// Variation CA mois/mois
Variation CA % =
VAR ca_actuel = [CA HT]
VAR ca_precedent = [CA HT (Mois Précédent)]
RETURN
IF(
    ca_precedent = 0,
    BLANK(),
    DIVIDE(ca_actuel - ca_precedent, ca_precedent)
)

// CA cumulé depuis début d'année (YTD)
CA HT YTD =
TOTALYTD([CA HT], vw_Revenus[date_emission])

// Encaissements réels
Encaissements =
SUM(vw_Revenus[montant_encaisse])

// Créances restantes
Créances =
SUM(vw_Revenus[montant_restant])

// Taux de recouvrement
Taux Recouvrement % =
DIVIDE([Encaissements], [CA HT])

// Nombre de factures
Nb Factures =
COUNTROWS(vw_Revenus)

// Panier moyen
Panier Moyen =
DIVIDE([CA HT], [Nb Factures])
```

---

### 3.2 Mesures Charges

```dax
// Total charges
Charges HT =
SUM(vw_Charges[montant_ht])

// Charges cumulées YTD
Charges YTD =
TOTALYTD([Charges HT], vw_Charges[date_charge])

// Charges vs mois précédent
Charges (Mois Précédent) =
CALCULATE([Charges HT], PREVIOUSMONTH(vw_Charges[date_charge]))
```

---

### 3.3 Résultat & Marges

```dax
// Résultat net
Résultat Net =
[CA HT] - [Charges HT]

// Marge brute en %
Marge Nette % =
DIVIDE([Résultat Net], [CA HT])

// Résultat YTD
Résultat YTD =
[CA HT YTD] - [Charges YTD]
```

---

### 3.4 Indicateurs Créances (DSO)

```dax
// DSO – Days Sales Outstanding (délai moyen de paiement)
DSO (jours) =
AVERAGEX(
    FILTER(vw_Revenus, vw_Revenus[statut_paiement] = "Payée"),
    vw_Revenus[jours_retard]
)

// Montant en retard
Montant en Retard =
CALCULATE(
    [Créances],
    vw_Revenus[jours_retard] > 0
)

// Montant contentieux
Montant Contentieux =
CALCULATE(
    [Créances],
    vw_Revenus[statut_paiement] = "Contentieux"
)

// Taux de retard
Taux Retard % =
DIVIDE(
    CALCULATE([Nb Factures], vw_Revenus[jours_retard] > 0),
    [Nb Factures]
)
```

---

### 3.5 Budget vs Réalisé

```dax
// Écart budgétaire total
Écart Budget =
SUM(vw_BudgetVsRealise[ecart])

// Taux de réalisation moyen
Taux Réalisation % =
AVERAGE(vw_BudgetVsRealise[taux_realisation_pct])

// Budget total
Budget Total =
SUM(vw_BudgetVsRealise[budget])

// Réalisé total
Réalisé Total =
SUM(vw_BudgetVsRealise[realise])
```

---

## 4. Structure des pages du rapport

### Page 1 – Vue Exécutive
> Destinée à la Direction Générale – synthèse en un coup d'œil

**Visuels :**
- 4 cartes KPI en haut :
  - `[CA HT]` avec variation `[Variation CA %]`
  - `[Résultat Net]` avec `[Marge Nette %]`
  - `[Encaissements]`
  - `[DSO (jours)]`
- Graphique en courbes : CA HT et Charges HT par mois
- Graphique en barres : Résultat net par trimestre
- Jauge : Taux de recouvrement (objectif : 90%)

---

### Page 2 – Revenus & Marges
> Analyse détaillée du chiffre d'affaires

**Visuels :**
- Histogramme empilé : CA HT par catégorie produit et mois
- Graphique en anneau : Répartition CA par secteur client
- Tableau détaillé : Top 10 clients par CA (raison_sociale, CA HT, Nb factures, Panier moyen)
- Segment (slicer) : Année / Trimestre / Département
- Graphique en barres : CA par ville client (carte géographique si possible)

**Filtres de page :**
- Année, Trimestre, Catégorie produit, Segment client

---

### Page 3 – Charges & Budget vs Réalisé
> Pilotage des dépenses et suivi budgétaire

**Visuels :**
- Graphique en barres groupées : Budget vs Réalisé par département
- Graphique en cascade (waterfall) : Décomposition des charges par catégorie
- Tableau : Charges par département avec taux de réalisation et écart
- Jauge : Taux de réalisation global du budget
- Histogramme : Évolution mensuelle des charges par nature

---

### Page 4 – Créances & Recouvrement
> Suivi des impayés et de la trésorerie

**Visuels :**
- 3 cartes KPI : Créances totales, Montant en retard, Montant contentieux
- Graphique en barres : Répartition par tranche de retard (dans les délais / < 30j / 31-60j / > 90j)
- Tableau clients à risque : raison_sociale, montant_restant, jours_retard, statut
- Graphique en courbes : Évolution DSO par mois
- Matrice : Statut paiement × Secteur activité (heatmap de risque)

---

## 5. Mise en forme recommandée

### Couleurs 
```
Principal (Orange)  : #E8611A
Secondaire (Noir)   : #1A1A1A
Fond clair          : #F7F7F7
Blanc               : #FFFFFF
Texte gris          : #555555
Succès (vert)       : #2E7D32
Danger (rouge)      : #C62828
```

### Thème personnalisé
1. **Affichage → Thèmes → Personnaliser le thème actuel**
2. Couleur principale : `#E8611A`
3. Police : Segoe UI
4. Arrière-plan des visuels : blanc, coins arrondis

---

## 6. Publication & Partage

1. **Fichier → Publier → Power BI Service**
2. Choisir l'espace de travail `Demo`
3. Configurer une **actualisation planifiée** (quotidienne à 6h00)
4. Créer un **tableau de bord** en épinglant les KPIs clés
5. Partager le lien avec les évaluateurs

---

## 7. Checklist finale avant présentation

- [ ] Toutes les mesures DAX sont dans la table "Mesures"
- [ ] Les relations entre tables sont vérifiées (sans ambiguïté)
- [ ] Les 4 pages sont nommées et ont un titre clair
- [ ] Les slicers (filtres) fonctionnent sur toutes les pages
- [ ] Les formats sont cohérents (monétaire, %, dates)
- [ ] Le rapport est publié sur Power BI Service
- [ ] Un export PDF du rapport est disponible
