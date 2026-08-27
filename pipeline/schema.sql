-- Supabase PostgreSQL Schema for PUE Benchmark Data
-- Star schema with fact and dimension tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS fact_efficiency CASCADE;
DROP TABLE IF EXISTS dim_location CASCADE;
DROP TABLE IF EXISTS dim_company CASCADE;
DROP TABLE IF EXISTS raw_pue_data CASCADE;

-- Raw data table (staging)
CREATE TABLE raw_pue_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company VARCHAR(255) NOT NULL,
    facility_name VARCHAR(255),
    city VARCHAR(255),
    country VARCHAR(255),
    region VARCHAR(255),
    year INTEGER,
    pue_value DECIMAL(5,3),
    pue_type VARCHAR(50),
    capacity_mw DECIMAL(10,2),
    rack_count INTEGER,
    renewable_pct INTEGER,
    wue_l_per_kwh DECIMAL(10,3),
    source_url TEXT,
    source_type VARCHAR(100),
    extraction_date DATE,
    tier VARCHAR(100),
    avg_temp_celsius DECIMAL(5,2),
    country_code VARCHAR(2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Dimension: Company
CREATE TABLE dim_company (
    company_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(255) UNIQUE NOT NULL,
    tier VARCHAR(100),
    region VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Dimension: Location
CREATE TABLE dim_location (
    location_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    city VARCHAR(255),
    country VARCHAR(255),
    country_code VARCHAR(2),
    region VARCHAR(255),
    avg_temp_celsius DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(city, country)
);

-- Fact: Efficiency Metrics
CREATE TABLE fact_efficiency (
    fact_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES dim_company(company_id),
    location_id UUID REFERENCES dim_location(location_id),

    -- Facility info
    facility_name VARCHAR(255),
    year INTEGER NOT NULL,

    -- Core metrics
    pue_value DECIMAL(5,3) NOT NULL,
    pue_type VARCHAR(50),

    -- Capacity metrics
    capacity_mw DECIMAL(10,2),
    rack_count INTEGER,

    -- Sustainability metrics
    renewable_pct INTEGER,
    wue_l_per_kwh DECIMAL(10,3),

    -- Calculated metrics
    cooling_overhead_pct DECIMAL(6,3) GENERATED ALWAYS AS ((pue_value - 1.0) * 100) STORED,
    annual_waste_mwh DECIMAL(15,2) GENERATED ALWAYS AS (
        CASE
            WHEN capacity_mw IS NOT NULL
            THEN (pue_value - 1.0) * capacity_mw * 8760
            ELSE NULL
        END
    ) STORED,

    -- Metadata
    source_url TEXT,
    source_type VARCHAR(100),
    extraction_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT pue_range CHECK (pue_value >= 1.0 AND pue_value <= 3.0),
    CONSTRAINT renewable_range CHECK (renewable_pct IS NULL OR (renewable_pct >= 0 AND renewable_pct <= 100))
);

-- Indexes for performance
CREATE INDEX idx_raw_company ON raw_pue_data(company);
CREATE INDEX idx_raw_year ON raw_pue_data(year);
CREATE INDEX idx_raw_tier ON raw_pue_data(tier);

CREATE INDEX idx_fact_company ON fact_efficiency(company_id);
CREATE INDEX idx_fact_location ON fact_efficiency(location_id);
CREATE INDEX idx_fact_year ON fact_efficiency(year);
CREATE INDEX idx_fact_pue ON fact_efficiency(pue_value);

CREATE INDEX idx_company_name ON dim_company(company_name);
CREATE INDEX idx_location_city ON dim_location(city);

-- Views for common queries

-- View: Efficiency Leaderboard
CREATE OR REPLACE VIEW v_efficiency_leaderboard AS
SELECT
    c.company_name,
    c.tier,
    f.facility_name,
    l.city,
    l.country,
    f.year,
    f.pue_value,
    f.pue_type,
    f.cooling_overhead_pct,
    f.capacity_mw,
    f.renewable_pct,
    f.wue_l_per_kwh,
    f.annual_waste_mwh
FROM fact_efficiency f
JOIN dim_company c ON f.company_id = c.company_id
LEFT JOIN dim_location l ON f.location_id = l.location_id
ORDER BY f.pue_value ASC;

-- View: India vs Global Comparison
CREATE OR REPLACE VIEW v_india_vs_global AS
SELECT
    CASE
        WHEN l.country = 'India' THEN 'India'
        ELSE 'Global'
    END AS region_group,
    COUNT(*) as facility_count,
    ROUND(AVG(f.pue_value)::NUMERIC, 3) as avg_pue,
    ROUND(MIN(f.pue_value)::NUMERIC, 3) as min_pue,
    ROUND(MAX(f.pue_value)::NUMERIC, 3) as max_pue,
    ROUND(AVG(f.renewable_pct)::NUMERIC, 1) as avg_renewable_pct,
    ROUND(SUM(f.capacity_mw)::NUMERIC, 1) as total_capacity_mw,
    ROUND(SUM(f.annual_waste_mwh)::NUMERIC, 1) as total_waste_mwh
FROM fact_efficiency f
LEFT JOIN dim_location l ON f.location_id = l.location_id
GROUP BY region_group;

-- View: Tier Comparison
CREATE OR REPLACE VIEW v_tier_comparison AS
SELECT
    c.tier,
    COUNT(*) as facility_count,
    ROUND(AVG(f.pue_value)::NUMERIC, 3) as avg_pue,
    ROUND(MIN(f.pue_value)::NUMERIC, 3) as best_pue,
    ROUND(AVG(f.renewable_pct)::NUMERIC, 1) as avg_renewable_pct,
    COUNT(CASE WHEN f.pue_type = 'operating' THEN 1 END) as operating_pue_count,
    COUNT(CASE WHEN f.pue_type = 'design' THEN 1 END) as design_pue_count
FROM fact_efficiency f
JOIN dim_company c ON f.company_id = c.company_id
GROUP BY c.tier
ORDER BY avg_pue ASC;

-- View: Climate Impact
CREATE OR REPLACE VIEW v_climate_impact AS
SELECT
    c.company_name,
    c.tier,
    l.country,
    l.avg_temp_celsius,
    f.pue_value,
    f.capacity_mw,
    f.cooling_overhead_pct,
    f.annual_waste_mwh,
    -- CO2 impact (using India grid factor: 0.82 kg/kWh)
    ROUND((f.annual_waste_mwh * 1000 * 0.82)::NUMERIC, 2) as annual_co2_tons
FROM fact_efficiency f
JOIN dim_company c ON f.company_id = c.company_id
LEFT JOIN dim_location l ON f.location_id = l.location_id
WHERE f.capacity_mw IS NOT NULL
ORDER BY annual_co2_tons DESC NULLS LAST;

-- View: Design vs Operating PUE
CREATE OR REPLACE VIEW v_design_vs_operating AS
SELECT
    c.company_name,
    f.pue_type,
    f.pue_value,
    f.year,
    f.facility_name
FROM fact_efficiency f
JOIN dim_company c ON f.company_id = c.company_id
WHERE f.pue_type IN ('design', 'operating', 'TTM')
ORDER BY c.company_name, f.year DESC;

-- Function: Update timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_raw_pue_data_timestamp
    BEFORE UPDATE ON raw_pue_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_dim_company_timestamp
    BEFORE UPDATE ON dim_company
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_dim_location_timestamp
    BEFORE UPDATE ON dim_location
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_fact_efficiency_timestamp
    BEFORE UPDATE ON fact_efficiency
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Comments for documentation
COMMENT ON TABLE raw_pue_data IS 'Raw staging table for all collected PUE data';
COMMENT ON TABLE dim_company IS 'Dimension table for company information';
COMMENT ON TABLE dim_location IS 'Dimension table for facility locations';
COMMENT ON TABLE fact_efficiency IS 'Fact table for data center efficiency metrics';

COMMENT ON COLUMN fact_efficiency.cooling_overhead_pct IS 'Calculated cooling overhead: (PUE - 1) × 100';
COMMENT ON COLUMN fact_efficiency.annual_waste_mwh IS 'Annual waste energy: (PUE - 1) × capacity_mw × 8760';
