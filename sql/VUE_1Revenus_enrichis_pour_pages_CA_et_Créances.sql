USE FinanceDB;
GO

-- ─────────────────────────────────────────
--  VUE 1 : Revenus enrichis (pour pages CA et Créances)
-- ─────────────────────────────────────────
CREATE OR ALTER VIEW rpt.vw_Revenus
AS
SELECT
    r.revenu_id,
    r.numero_facture,

    -- Dimensions Temps (émission)
    te.date_complete        AS date_emission,
    te.annee                AS annee,
    te.mois                 AS mois,
    te.nom_mois             AS nom_mois,
    te.trimestre            AS trimestre,
    te.libelle_periode      AS periode,

    -- Dimensions Temps (échéance)
    tec.date_complete       AS date_echeance,

    -- Dimensions Temps (paiement)
    tp.date_complete        AS date_paiement,

    -- Dimension Client
    c.code_client,
    c.raison_sociale,
    c.secteur_activite,
    c.taille_entreprise,
    c.segment,
    c.ville                 AS ville_client,
    c.region                AS region_client,
    c.conditions_paiement,

    -- Dimension Produit
    ps.code_produit,
    ps.libelle              AS produit,
    ps.categorie            AS categorie_produit,
    ps.sous_categorie,
    ps.unite_facturation,

    -- Dimension Département
    d.code_dept,
    d.nom_departement,
    d.direction,

    -- Mesures financières
    r.quantite,
    r.prix_unitaire_ht,
    r.remise_pct,
    r.montant_ht,
    r.montant_tva,
    r.montant_ttc,
    r.montant_encaisse,
    r.montant_ht - r.montant_encaisse       AS montant_restant,
    r.statut_paiement,
    r.jours_retard,

    -- Calculs dérivés utiles en DAX
    CASE
        WHEN r.jours_retard = 0             THEN 'Dans les délais'
        WHEN r.jours_retard BETWEEN 1 AND 30 THEN 'Retard < 30j'
        WHEN r.jours_retard BETWEEN 31 AND 60 THEN 'Retard 31-60j'
        WHEN r.jours_retard BETWEEN 61 AND 90 THEN 'Retard 61-90j'
        ELSE 'Retard > 90j (Contentieux)'
    END                                     AS tranche_retard,

    CASE
        WHEN r.montant_ht > 50000           THEN 'Grande facture'
        WHEN r.montant_ht > 10000           THEN 'Facture moyenne'
        ELSE 'Petite facture'
    END                                     AS categorie_montant

FROM fait.Revenus r
INNER JOIN dim.Temps          te  ON r.date_id           = te.date_id
INNER JOIN dim.Temps          tec ON r.date_echeance_id  = tec.date_id
LEFT  JOIN dim.Temps          tp  ON r.date_paiement_id  = tp.date_id
INNER JOIN dim.Client         c   ON r.client_id         = c.client_id
INNER JOIN dim.ProduitService ps  ON r.produit_id        = ps.produit_id
INNER JOIN dim.Departement    d   ON r.dept_id           = d.dept_id;
GO
