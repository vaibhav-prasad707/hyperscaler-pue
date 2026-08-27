{{ config(materialized='view') }}

WITH raw_data AS (
    SELECT
        id,
        company,
        facility_name,
        city,
        country,
        region,
        year,
        pue_value,
        pue_type,
        capacity_mw,
        rack_count,
        renewable_pct,
        wue_l_per_kwh,
        source_url,
        source_type,
        extraction_date,
        tier,
        created_at
    FROM {{ source('pue_raw', 'raw_pue_data') }}
)

SELECT
    id AS pue_id,
    company AS company_name,
    facility_name,
    city,
    country,
    region,
    year AS metric_year,
    pue_value,
    pue_type,
    capacity_mw,
    rack_count,
    renewable_pct,
    wue_l_per_kwh,

    -- Calculated fields
    (pue_value - 1.0) * 100 AS cooling_overhead_pct,
    CASE
        WHEN capacity_mw IS NOT NULL
        THEN (pue_value - 1.0) * capacity_mw * 8760
        ELSE NULL
    END AS annual_waste_mwh,

    -- Metadata
    source_url,
    source_type,
    extraction_date,
    tier,
    created_at

FROM raw_data
WHERE pue_value IS NOT NULL
  AND pue_value >= 1.0
  AND pue_value <= 3.0
