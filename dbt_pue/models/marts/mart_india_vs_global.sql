{{ config(materialized='table') }}

WITH pue_data AS (
    SELECT * FROM {{ ref('stg_pue') }}
),

india_stats AS (
    SELECT
        'India' AS region_group,
        COUNT(*) AS facility_count,
        ROUND(AVG(pue_value)::NUMERIC, 3) AS avg_pue,
        ROUND(MIN(pue_value)::NUMERIC, 3) AS min_pue,
        ROUND(MAX(pue_value)::NUMERIC, 3) AS max_pue,
        ROUND(AVG(renewable_pct)::NUMERIC, 1) AS avg_renewable_pct,
        ROUND(SUM(capacity_mw)::NUMERIC, 1) AS total_capacity_mw,
        ROUND(SUM(annual_waste_mwh)::NUMERIC, 1) AS total_waste_mwh,
        ROUND(AVG(cooling_overhead_pct)::NUMERIC, 2) AS avg_cooling_overhead_pct
    FROM pue_data
    WHERE country = 'India'
),

global_stats AS (
    SELECT
        'Global' AS region_group,
        COUNT(*) AS facility_count,
        ROUND(AVG(pue_value)::NUMERIC, 3) AS avg_pue,
        ROUND(MIN(pue_value)::NUMERIC, 3) AS min_pue,
        ROUND(MAX(pue_value)::NUMERIC, 3) AS max_pue,
        ROUND(AVG(renewable_pct)::NUMERIC, 1) AS avg_renewable_pct,
        ROUND(SUM(capacity_mw)::NUMERIC, 1) AS total_capacity_mw,
        ROUND(SUM(annual_waste_mwh)::NUMERIC, 1) AS total_waste_mwh,
        ROUND(AVG(cooling_overhead_pct)::NUMERIC, 2) AS avg_cooling_overhead_pct
    FROM pue_data
    WHERE country != 'India' OR country IS NULL
)

SELECT * FROM india_stats
UNION ALL
SELECT * FROM global_stats
