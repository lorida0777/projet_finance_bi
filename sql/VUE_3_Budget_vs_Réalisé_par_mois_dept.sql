USE FinanceDB;
GO

-- ─────────────────────────────────────────
--  VUE 3 : Budget vs Réalisé (par mois / dept)
-- ─────────────────────────────────────────
CREATE OR ALTER VIEW rpt.vw_BudgetVsRealise
AS
WITH
Revenus_Agg AS (
    SELECT
        t.annee, t.mois, t.nom_mois, t.trimestre, t.libelle_periode,
        r.dept_id,
        SUM(r.montant_ht)   AS realise
    FROM fait.Revenus r
    INNER JOIN dim.Temps t ON r.date_id = t.date_id
    GROUP BY t.annee, t.mois, t.nom_mois, t.trimestre, t.libelle_periode, r.dept_id
),
Charges_Agg AS (
    SELECT
        t.annee, t.mois, t.nom_mois, t.trimestre, t.libelle_periode,
        c.dept_id,
        SUM(c.montant_ht)   AS realise
    FROM fait.Charges c
    INNER JOIN dim.Temps t ON c.date_id = t.date_id
    GROUP BY t.annee, t.mois, t.nom_mois, t.trimestre, t.libelle_periode, c.dept_id
)
SELECT
    b.annee,
    b.mois,
    d.nom_departement,
    d.direction,
    d.centre_cout,
    b.categorie,
    b.type_budget,
    b.montant_budget                                AS budget,
    CASE
        WHEN b.type_budget = 'Revenu'
        THEN ISNULL(ra.realise, 0)
        ELSE ISNULL(ca.realise, 0)
    END                                             AS realise,
    CASE
        WHEN b.type_budget = 'Revenu'
        THEN ISNULL(ra.realise, 0) - b.montant_budget
        ELSE b.montant_budget - ISNULL(ca.realise, 0)
    END                                             AS ecart,
    CASE
        WHEN b.montant_budget = 0 THEN NULL
        WHEN b.type_budget = 'Revenu'
        THEN CAST(ISNULL(ra.realise,0) / b.montant_budget * 100 AS DECIMAL(5,1))
        ELSE CAST(ISNULL(ca.realise,0) / b.montant_budget * 100 AS DECIMAL(5,1))
    END                                             AS taux_realisation_pct

FROM fait.Budget b
INNER JOIN dim.Departement d ON b.dept_id = d.dept_id
LEFT  JOIN Revenus_Agg    ra ON b.type_budget = 'Revenu'
                             AND ra.annee = b.annee AND ra.mois = b.mois AND ra.dept_id = b.dept_id
LEFT  JOIN Charges_Agg    ca ON b.type_budget = 'Charge'
                             AND ca.annee = b.annee AND ca.mois = b.mois AND ca.dept_id = b.dept_id;
GO
