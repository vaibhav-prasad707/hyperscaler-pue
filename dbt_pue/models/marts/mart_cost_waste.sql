{{ config(materialized='table') }}

WITH pue_data AS (
    SELECT * FROM {{ ref('stg_pue') }}
),

cost_analysis AS (
    SELECT
        company_name,
        tier,
        facility_name,
        city,
        country,
        pue_value,
        capacity_mw,
        cooling_overhead_pct,
        annual_waste_mwh,

        -- Electricity tariff (INR per kWh)
        CASE
            WHEN country = 'India' THEN 7.0
            WHEN country = 'United States' THEN 10.0
            ELSE 8.5
        END AS tariff_inr_per_kwh,

        -- Annual waste cost in INR
        ROUND(
            (annual_waste_mwh * 1000 *
                CASE
                    WHEN country = 'India' THEN 7.0
                    WHEN country = 'United States' THEN 10.0
                    ELSE 8.5
                END
            )::NUMERIC,
            2
        ) AS annual_waste_cost_inr,

        -- Annual waste cost in Crores INR
        ROUND(
            (annual_waste_mwh * 1000 *
                CASE
                    WHEN country = 'India' THEN 7.0
                    WHEN country = 'United States' THEN 10.0
                    ELSE 8.5
                END / 10000000
            )::NUMERIC,
            2
        ) AS annual_waste_cost_crores,

        -- Potential savings if improved to PUE 1.2
        ROUND(
            (
                (pue_value - 1.2) * capacity_mw * 8760 * 1000 *
                CASE
                    WHEN country = 'India' THEN 7.0
                    WHEN country = 'United States' THEN 10.0
                    ELSE 8.5
                END / 10000000
            )::NUMERIC,
            2
        ) AS potential_savings_to_1_2_crores

    FROM pue_data
    WHERE capacity_mw IS NOT NULL
      AND annual_waste_mwh IS NOT NULL
)

SELECT
    company_name,
    tier,
    facility_name,
    city,
    country,
    pue_value,
    capacity_mw,
    ROUND(cooling_overhead_pct::NUMERIC, 2) AS cooling_overhead_pct,
    ROUND(annual_waste_mwh::NUMERIC, 2) AS annual_waste_mwh,
    tariff_inr_per_kwh,
    annual_waste_cost_inr,
    annual_waste_cost_crores,

    CASE
        WHEN pue_value > 1.2
        THEN potential_savings_to_1_2_crores
        ELSE 0
    END AS potential_savings_crores,

    -- ROI metrics
    CASE
        WHEN capacity_mw > 0
        THEN ROUND((annual_waste_cost_crores / capacity_mw)::NUMERIC, 2)
        ELSE NULL
    END AS waste_cost_per_mw_crores

FROM cost_analysis
ORDER BY annual_waste_cost_crores DESC NULLS LAST
