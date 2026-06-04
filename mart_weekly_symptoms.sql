{{ config(materialized='table') }}

WITH raw_reports AS (
    SELECT * FROM public.chw_reports
),

-- Step 1: Pre-calculate the week date so Postgres doesn't evaluate functions during aggregation
prepared_reports AS (
    SELECT
        DATE_TRUNC('week', timestamp)::date AS report_week,
        county,
        sub_county,
        report_id,
        symptom_fever,
        symptom_cough,
        symptom_diarrhea,
        symptom_vomiting
    FROM raw_reports
),

-- Step 2: Perform clean, uncomplicated grouping
weekly_aggregates AS (
    SELECT 
        report_week,
        county,
        sub_county,
        COUNT(report_id) AS total_visits,
        
        -- Aggregate Symptoms
        SUM(CASE WHEN symptom_fever THEN 1 ELSE 0 END) AS total_fever,
        SUM(CASE WHEN symptom_cough THEN 1 ELSE 0 END) AS total_cough,
        SUM(CASE WHEN symptom_diarrhea THEN 1 ELSE 0 END) AS total_diarrhea,
        SUM(CASE WHEN symptom_vomiting THEN 1 ELSE 0 END) AS total_vomiting
        
    FROM prepared_reports
    GROUP BY report_week, county, sub_county
)

SELECT * FROM weekly_aggregates
ORDER BY report_week DESC, county ASC