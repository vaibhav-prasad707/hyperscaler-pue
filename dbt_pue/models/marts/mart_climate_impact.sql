{{ config(materialized='table') }}

WITH pue_data AS (
    SELECT * FROM {{ ref('stg_pue') }}
),

city_temps AS (
    SELECT * FROM {{ ref('city_temperatures') }}
),

climate_impact AS (
    SELECT
        p.company_name,
        p.tier,
        p.facility_name,
        p.city,
        p.country,
        t.avg_temp_celsius,
        p.pue_value,
        p.capacity_mw,
        p.cooling_overhead_pct,
        p.annual_waste_mwh,

        -- CO2 impact calculations
        -- Using India grid factor: 0.82 kg CO2 per kWh
        -- Using US grid factor: 0.42 kg CO2 per kWh
        -- Using Global average: 0.47 kg CO2 per kWh
        CASE
            WHEN p.country = 'India' THEN 0.82
            WHEN p.country = 'United States' THEN 0.42
            ELSE 0.47
        END AS grid_emission_factor,

        ROUND(
            (p.annual_waste_mwh * 1000 *
                CASE
                    WHEN p.country = 'India' THEN 0.82
                    WHEN p.country = 'United States' THEN 0.42
                    ELSE 0.47
                END
            )::NUMERIC,
            2
        ) AS annual_co2_tons,

        -- Water usage
        CASE
            WHEN p.wue_l_per_kwh IS NOT NULL AND p.capacity_mw IS NOT NULL
            THEN ROUND((p.wue_l_per_kwh * p.capacity_mw * 8760 * 1000)::NUMERIC, 0)
            ELSE NULL
        END AS annual_water_liters

    FROM pue_data p
    LEFT JOIN city_temps t ON p.city = t.city
    WHERE p.capacity_mw IS NOT NULL
)

SELECT
    company_name,
    tier,
    facility_name,
    city,
    country,
    avg_temp_celsius,
    pue_value,
    capacity_mw,
    ROUND(cooling_overhead_pct::NUMERIC, 2) AS cooling_overhead_pct,
    ROUND(annual_waste_mwh::NUMERIC, 2) AS annual_waste_mwh,
    grid_emission_factor,
    annual_co2_tons,
    annual_water_liters,

    -- Climate efficiency score (lower is better)
    -- Combines PUE with climate considerations
    ROUND(
        (pue_value * (1 + (COALESCE(avg_temp_celsius, 25) - 10) * 0.01))::NUMERIC,
        3
    ) AS climate_adjusted_pue

FROM climate_impact
ORDER BY annual_co2_tons DESC NULLS LAST
