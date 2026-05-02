USE FinanceDB;
GO
-- ─────────────────────────────────────────
--  VUE 2 : Charges enrichies (pour page Budget vs Réalisé)
-- ─────────────────────────────────────────
CREATE OR ALTER VIEW rpt.vw_Charges
AS
SELECT
    ch.charge_id,
    ch.numero_piece,

    -- Temps
    t.date_complete         AS date_charge,
    t.annee,
    t.mois,
    t.nom_mois,
    t.trimestre,
    t.libelle_periode       AS periode,

    -- Département
    d.code_dept,
    d.nom_departement,
    d.direction,
    d.centre_cout,

    -- Classification
    ch.categorie_charge,
    ch.sous_categorie,
    ch.fournisseur,
    ch.nature_charge,
    ch.est_budgetee,

    -- Mesures
    ch.montant_ht,
    ch.montant_tva,
    ch.montant_ttc

FROM fait.Charges ch
INNER JOIN dim.Temps        t ON ch.date_id  = t.date_id
INNER JOIN dim.Departement  d ON ch.dept_id  = d.dept_id;
GO
