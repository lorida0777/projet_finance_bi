USE FinanceDB;
GO
-- ─────────────────────────────────────────
--  VUE 4 : KPIs exécutifs (pour page Vue Exécutive)
-- ─────────────────────────────────────────
CREATE OR ALTER VIEW rpt.vw_KPIs_Executifs
AS
SELECT
    t.annee,
    t.mois,
    t.nom_mois,
    t.trimestre,
    t.libelle_periode,

    -- CA
    SUM(r.montant_ht)                                           AS ca_ht,
    SUM(r.montant_encaisse)                                     AS encaisse,
    SUM(r.montant_ht - r.montant_encaisse)                     AS creances,

    -- Charges
    ISNULL(SUM(DISTINCT ch_agg.total_charges), 0)              AS total_charges,

    -- Résultat
    SUM(r.montant_ht) - ISNULL(SUM(DISTINCT ch_agg.total_charges), 0) AS resultat_net,

    -- Marges
    CASE
        WHEN SUM(r.montant_ht) = 0 THEN 0
        ELSE CAST(
            (SUM(r.montant_ht) - ISNULL(SUM(DISTINCT ch_agg.total_charges), 0))
            / SUM(r.montant_ht) * 100
        AS DECIMAL(5,1))
    END                                                         AS marge_nette_pct,

    -- Factures
    COUNT(r.revenu_id)                                          AS nb_factures,
    SUM(CASE WHEN r.statut_paiement = 'Payée'      THEN 1 ELSE 0 END) AS nb_payees,
    SUM(CASE WHEN r.statut_paiement = 'Retard'     THEN 1 ELSE 0 END) AS nb_retard,
    SUM(CASE WHEN r.statut_paiement = 'Contentieux'THEN 1 ELSE 0 END) AS nb_contentieux,

    -- DSO
    AVG(CASE WHEN r.statut_paiement = 'Payée' THEN r.jours_retard ELSE NULL END) AS dso_jours

FROM dim.Temps t
INNER JOIN fait.Revenus r ON r.date_id = t.date_id
LEFT JOIN (
    SELECT date_id, SUM(montant_ht) AS total_charges
    FROM fait.Charges
    GROUP BY date_id
) ch_agg ON ch_agg.date_id = t.date_id
GROUP BY t.annee, t.mois, t.nom_mois, t.trimestre, t.libelle_periode;
GO

PRINT 'Vues analytiques créées avec succès.';
GO