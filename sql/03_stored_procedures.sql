-- ============================================================
--  03_stored_procedures.sql
--  Procédures stockées : ETL, maintenance, agrégations
--  Projet : Tableau de Bord Financier – Direction Comptable
-- ============================================================

USE FinanceDB;
GO

-- ─────────────────────────────────────────
--  SP : Génération du calendrier
-- ─────────────────────────────────────────
CREATE OR ALTER PROCEDURE dim.usp_GenerateCalendar
    @DateDebut  DATE = '2022-01-01',
    @DateFin    DATE = '2025-12-31'
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @CurrentDate DATE = @DateDebut;

    -- Jours fériés Madagascar (simplifiés)
    CREATE TABLE #Feries (date_ferie DATE PRIMARY KEY);
    INSERT INTO #Feries VALUES
        ('2024-01-01'), ('2024-03-29'), ('2024-04-01'), ('2024-05-01'),
        ('2024-05-09'), ('2024-05-19'), ('2024-06-26'), ('2024-08-15'),
        ('2024-11-01'), ('2024-12-25'),
        ('2023-01-01'), ('2023-03-29'), ('2023-04-10'), ('2023-05-01'),
        ('2023-06-26'), ('2023-08-15'), ('2023-11-01'), ('2023-12-25'),
        ('2025-01-01'), ('2025-03-29'), ('2025-04-21'), ('2025-05-01'),
        ('2025-06-26'), ('2025-08-15'), ('2025-11-01'), ('2025-12-25');

    WHILE @CurrentDate <= @DateFin
    BEGIN
        DECLARE @DateID     INT     = CONVERT(INT, FORMAT(@CurrentDate, 'yyyyMMdd'));
        DECLARE @Jour       TINYINT = DAY(@CurrentDate);
        DECLARE @Mois       TINYINT = MONTH(@CurrentDate);
        DECLARE @Annee      SMALLINT= YEAR(@CurrentDate);
        DECLARE @DowSQL     TINYINT = DATEPART(WEEKDAY, @CurrentDate); -- 1=Dim, 2=Lun...
        DECLARE @DowISO     TINYINT = CASE WHEN @DowSQL = 1 THEN 7 ELSE @DowSQL - 1 END;
        DECLARE @EstWeekend BIT     = CASE WHEN @DowISO IN (6,7) THEN 1 ELSE 0 END;
        DECLARE @EstFerie   BIT     = CASE WHEN EXISTS(SELECT 1 FROM #Feries WHERE date_ferie = @CurrentDate) THEN 1 ELSE 0 END;

        DECLARE @NomsMois TABLE (num TINYINT, nom VARCHAR(20));
        INSERT INTO @NomsMois VALUES
            (1,'Janvier'),(2,'Février'),(3,'Mars'),(4,'Avril'),
            (5,'Mai'),(6,'Juin'),(7,'Juillet'),(8,'Août'),
            (9,'Septembre'),(10,'Octobre'),(11,'Novembre'),(12,'Décembre');

        DECLARE @NomMois VARCHAR(20) = (SELECT nom FROM @NomsMois WHERE num = @Mois);

        IF NOT EXISTS (SELECT 1 FROM dim.Temps WHERE date_id = @DateID)
        BEGIN
            INSERT INTO dim.Temps (
                date_id, date_complete, jour, mois, nom_mois, trimestre,
                semestre, annee, semaine_annee, jour_semaine, nom_jour,
                est_weekend, est_ferie, libelle_periode
            ) VALUES (
                @DateID, @CurrentDate, @Jour, @Mois, @NomMois,
                DATEPART(QUARTER, @CurrentDate),
                CASE WHEN @Mois <= 6 THEN 1 ELSE 2 END,
                @Annee,
                DATEPART(WEEK, @CurrentDate),
                @DowISO,
                CASE @DowISO
                    WHEN 1 THEN 'Lundi' WHEN 2 THEN 'Mardi'
                    WHEN 3 THEN 'Mercredi' WHEN 4 THEN 'Jeudi'
                    WHEN 5 THEN 'Vendredi' WHEN 6 THEN 'Samedi'
                    ELSE 'Dimanche' END,
                @EstWeekend, @EstFerie,
                @NomMois + ' ' + CAST(@Annee AS VARCHAR(4))
            );
        END

        SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
        DELETE FROM @NomsMois;
    END

    DROP TABLE #Feries;
    PRINT 'Calendrier généré : ' + CAST(@DateDebut AS VARCHAR) + ' → ' + CAST(@DateFin AS VARCHAR);
END
GO

-- ─────────────────────────────────────────
--  SP : Calcul des jours de retard
-- ─────────────────────────────────────────
CREATE OR ALTER PROCEDURE fait.usp_UpdateJoursRetard
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE r
    SET
        jours_retard = CASE
            WHEN r.statut_paiement IN ('Payée') THEN
                DATEDIFF(DAY, te.date_complete, tp.date_complete)
            WHEN r.statut_paiement IN ('En attente', 'Partielle', 'Retard', 'Contentieux') THEN
                CASE WHEN GETDATE() > te.date_complete
                     THEN DATEDIFF(DAY, te.date_complete, GETDATE())
                     ELSE 0 END
            ELSE 0
        END,
        updated_at = SYSDATETIME()
    FROM fait.Revenus r
    INNER JOIN dim.Temps te ON r.date_echeance_id = te.date_id
    LEFT  JOIN dim.Temps tp ON r.date_paiement_id = tp.date_id;

    -- Mettre à jour le statut automatiquement
    UPDATE fait.Revenus
    SET statut_paiement = 'Retard',
        updated_at = SYSDATETIME()
    WHERE statut_paiement = 'En attente'
      AND jours_retard > 0;

    UPDATE fait.Revenus
    SET statut_paiement = 'Contentieux',
        updated_at = SYSDATETIME()
    WHERE statut_paiement = 'Retard'
      AND jours_retard > 90;

    PRINT 'Jours de retard mis à jour.';
END
GO

-- ─────────────────────────────────────────
--  SP : Tableau de bord résumé mensuel
-- ─────────────────────────────────────────
CREATE OR ALTER PROCEDURE rpt.usp_ResumeMensuel
    @Annee  SMALLINT = NULL,
    @Mois   TINYINT  = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SET @Annee = ISNULL(@Annee, YEAR(GETDATE()));
    SET @Mois  = ISNULL(@Mois,  MONTH(GETDATE()));

    SELECT
        t.annee,
        t.mois,
        t.nom_mois,
        -- Revenus
        COUNT(r.revenu_id)                              AS nb_factures,
        SUM(r.montant_ht)                               AS ca_ht,
        SUM(r.montant_ttc)                              AS ca_ttc,
        SUM(r.montant_encaisse)                         AS encaisse,
        SUM(r.montant_ht - r.montant_encaisse)          AS reste_a_recouvrer,
        -- Charges
        ISNULL(SUM(ch.montant_ht), 0)                  AS total_charges,
        -- Résultat
        SUM(r.montant_ht) - ISNULL(SUM(ch.montant_ht),0) AS resultat_net,
        -- DSO simplifié (jours moyen de paiement)
        AVG(CASE WHEN r.statut_paiement = 'Payée' THEN r.jours_retard ELSE NULL END) AS dso_jours
    FROM dim.Temps t
    INNER JOIN fait.Revenus r  ON r.date_id = t.date_id
    LEFT  JOIN fait.Charges ch ON ch.date_id = t.date_id
    WHERE t.annee = @Annee AND t.mois = @Mois
    GROUP BY t.annee, t.mois, t.nom_mois;
END
GO

PRINT 'Procédures stockées créées avec succès.';
GO
