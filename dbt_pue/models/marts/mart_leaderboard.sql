{{ config(materialized='table') }}

WITH pue_data AS (
    SELECT * FROM {{ ref('stg_pue') }}
),

ranked_companies AS (
    SELECT
        company_name,
        tier,
        facility_name,
        city,
        country,
        metric_year,
        pue_value,
        pue_type,
        cooling_overhead_pct,
        capacity_mw,
        renewable_pct,
        wue_l_per_kwh,
        annual_waste_mwh,

        -- Ranking
        ROW_NUMBER() OVER (ORDER BY pue_value ASC) AS pue_rank,

        -- Tier-based ranking
        ROW_NUMBER() OVER (PARTITION BY tier ORDER BY pue_value ASC) AS tier_rank

    FROM pue_data
)

SELECT
    pue_rank,
    tier_rank,
    company_name,
    tier,
    facility_name,
    city,
    country,
    metric_year,
    pue_value,
    pue_type,
    ROUND(cooling_overhead_pct::NUMERIC, 2) AS cooling_overhead_pct,
    capacity_mw,
    renewable_pct,
    wue_l_per_kwh,
    ROUND(annual_waste_mwh::NUMERIC, 2) AS annual_waste_mwh,

    -- Performance category
    CASE
        WHEN pue_value < 1.2 THEN 'Exceptional'
        WHEN pue_value < 1.4 THEN 'Excellent'
        WHEN pue_value < 1.6 THEN 'Good'
        WHEN pue_value < 1.8 THEN 'Fair'
        ELSE 'Needs Improvement'
    END AS efficiency_category

FROM ranked_companies
ORDER BY pue_rank
