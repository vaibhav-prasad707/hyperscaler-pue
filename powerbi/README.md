# Power BI Setup Guide

## Connecting to Supabase PostgreSQL

### Prerequisites
- Power BI Desktop installed
- Supabase project credentials

### Step 1: Get PostgreSQL Connection Details

From your Supabase dashboard:
1. Go to **Settings** → **Database**
2. Note down:
   - Host: `db.<your-project-ref>.supabase.co`
   - Database: `postgres`
   - Port: `5432`
   - User: `postgres`
   - Password: Your database password

### Step 2: Connect Power BI to Supabase

1. Open **Power BI Desktop**
2. Click **Get Data** → **More...**
3. Search for **PostgreSQL database**
4. Select **PostgreSQL database** and click **Connect**
5. Enter connection details:
   - **Server**: `db.<your-project-ref>.supabase.co:5432`
   - **Database**: `postgres`
6. Click **OK**
7. Choose **Database** authentication
8. Enter credentials:
   - **User name**: `postgres`
   - **Password**: Your database password
9. Click **Connect**

### Step 3: Import Tables

From the Navigator window, select:
- `fact_efficiency`
- `dim_company`
- `dim_location`
- Views (optional):
  - `v_efficiency_leaderboard`
  - `v_india_vs_global`
  - `v_tier_comparison`
  - `v_climate_impact`

Click **Load** to import data.

## Data Model Setup

### Relationships

Power BI should auto-detect these relationships. Verify:

1. `fact_efficiency[company_id]` → `dim_company[company_id]`
   - Cardinality: Many to One
   - Cross filter direction: Single

2. `fact_efficiency[location_id]` → `dim_location[location_id]`
   - Cardinality: Many to One
   - Cross filter direction: Single

### Calculated Columns

#### Efficiency Category
```dax
Efficiency Category = 
SWITCH(
    TRUE(),
    fact_efficiency[pue_value] < 1.2, "Exceptional",
    fact_efficiency[pue_value] < 1.4, "Excellent",
    fact_efficiency[pue_value] < 1.6, "Good",
    fact_efficiency[pue_value] < 1.8, "Fair",
    "Needs Improvement"
)
```

#### Is India
```dax
Is India = 
IF(
    RELATED(dim_location[country]) = "India",
    "India",
    "Global"
)
```

## DAX Measures

### Key Performance Indicators

#### Average PUE
```dax
Avg PUE = 
AVERAGE(fact_efficiency[pue_value])
```

#### Best PUE
```dax
Best PUE = 
MIN(fact_efficiency[pue_value])
```

#### Worst PUE
```dax
Worst PUE = 
MAX(fact_efficiency[pue_value])
```

#### Total Facilities
```dax
Total Facilities = 
DISTINCTCOUNT(fact_efficiency[fact_id])
```

#### Total Companies
```dax
Total Companies = 
DISTINCTCOUNT(dim_company[company_id])
```

#### Total Capacity
```dax
Total Capacity MW = 
SUM(fact_efficiency[capacity_mw])
```

### Cost & Waste Metrics

#### Annual Waste Energy
```dax
Annual Waste MWh = 
SUMX(
    fact_efficiency,
    fact_efficiency[annual_waste_mwh]
)
```

#### Annual Waste Cost (INR Crores)
```dax
Annual Waste Cost Crores = 
SUMX(
    fact_efficiency,
    (fact_efficiency[annual_waste_mwh] * 1000 * 7) / 10000000
)
```

#### Potential Savings (to PUE 1.2)
```dax
Potential Savings Crores = 
SUMX(
    FILTER(
        fact_efficiency,
        fact_efficiency[pue_value] > 1.2 
        && NOT(ISBLANK(fact_efficiency[capacity_mw]))
    ),
    (
        (fact_efficiency[pue_value] - 1.2) * 
        fact_efficiency[capacity_mw] * 
        8760 * 1000 * 7
    ) / 10000000
)
```

### Climate Metrics

#### Annual CO2 Emissions (Tons)
```dax
Annual CO2 Tons = 
SUMX(
    fact_efficiency,
    fact_efficiency[annual_waste_mwh] * 1000 * 0.82 / 1000
)
```

#### Average Renewable %
```dax
Avg Renewable % = 
AVERAGE(fact_efficiency[renewable_pct])
```

### Comparison Metrics

#### India vs Global Avg PUE
```dax
India Avg PUE = 
CALCULATE(
    AVERAGE(fact_efficiency[pue_value]),
    dim_location[country] = "India"
)
```

```dax
Global Avg PUE = 
CALCULATE(
    AVERAGE(fact_efficiency[pue_value]),
    dim_location[country] <> "India"
)
```

#### PUE Gap (India - Global)
```dax
PUE Gap = 
[India Avg PUE] - [Global Avg PUE]
```

## Report Pages

### Page 1: Executive Dashboard

**Visuals:**
1. **KPI Cards** (top row)
   - Total Facilities
   - Average PUE
   - Best PUE
   - Total Capacity

2. **PUE Leaderboard** (left)
   - Table visual
   - Columns: Company, Facility, City, PUE, Tier
   - Sort by PUE ascending

3. **PUE Distribution** (right top)
   - Histogram
   - X-axis: PUE Value (bins)
   - Y-axis: Count

4. **Tier Comparison** (right bottom)
   - Clustered bar chart
   - X-axis: Tier
   - Y-axis: Average PUE

**Filters:**
- Slicer: Tier
- Slicer: Country
- Slicer: PUE Type

### Page 2: India Deep Dive

**Visuals:**
1. **KPI Cards**
   - India Avg PUE
   - India Best PUE
   - India Total Facilities
   - PUE Gap (India - Global)

2. **Map Visualization**
   - Location: City
   - Size: Capacity MW
   - Color: PUE Value

3. **City Performance**
   - Bar chart
   - X-axis: City
   - Y-axis: Average PUE

4. **Operator Ranking**
   - Table with conditional formatting
   - Columns: Company, Avg PUE, Facilities, Total Capacity

5. **Waste Cost Analysis**
   - Card: Annual Waste Cost Crores
   - Card: Potential Savings Crores

### Page 3: Design vs Operating

**Visuals:**
1. **PUE Type Distribution**
   - Pie chart
   - Legend: PUE Type
   - Values: Count

2. **Average by Type**
   - Bar chart
   - X-axis: PUE Type
   - Y-axis: Average PUE

3. **Scatter Plot**
   - X-axis: Company
   - Y-axis: PUE Value
   - Legend: PUE Type
   - Size: Capacity MW

4. **Insight Card**
   - Text box with explanation

### Page 4: Climate Impact

**Visuals:**
1. **Climate KPIs**
   - Total CO2 Emissions (Tons)
   - Average Renewable %
   - Total Waste Energy (MWh)

2. **CO2 by Company**
   - Treemap
   - Group: Company
   - Size: Annual CO2 Tons

3. **Temperature vs PUE**
   - Scatter plot
   - X-axis: Avg Temp Celsius
   - Y-axis: PUE Value
   - Size: Capacity MW

4. **Renewable Energy Adoption**
   - Gauge chart
   - Value: Avg Renewable %
   - Min: 0, Max: 100

## Formatting Guidelines

### Color Scheme
- **Excellent PUE (< 1.3)**: Green (#2ca02c)
- **Good PUE (1.3-1.5)**: Yellow (#ffbb00)
- **Fair PUE (1.5-1.7)**: Orange (#ff7f0e)
- **Poor PUE (> 1.7)**: Red (#d62728)

### Conditional Formatting
Apply to PUE columns:
- Rules: Based on ranges
- < 1.3: Green background
- 1.3-1.5: Yellow background
- 1.5-1.7: Orange background
- \> 1.7: Red background

### Number Formatting
- **PUE Values**: 0.000
- **Currency (Crores)**: ₹0.00
- **Percentages**: 0%
- **Capacity**: 0.0 MW
- **Energy**: 0,000 MWh

## Data Refresh

### Manual Refresh
1. Click **Refresh** in the Home ribbon
2. Data updates from Supabase

### Scheduled Refresh (Power BI Service)
1. Publish report to Power BI Service
2. Go to **Settings** → **Datasets**
3. Configure **Scheduled refresh**
4. Set frequency: Daily at preferred time
5. Enter Supabase credentials in **Data source credentials**

### Refresh via Power BI Gateway
For on-premises or private networks:
1. Install **On-premises data gateway**
2. Configure gateway to connect to Supabase
3. Set up scheduled refresh through gateway

## Best Practices

1. **Data Model Optimization**
   - Remove unused columns
   - Use appropriate data types
   - Create hierarchies (Tier → Company → Facility)

2. **Performance**
   - Limit visual count per page (max 10)
   - Use aggregated views for large datasets
   - Enable query reduction

3. **User Experience**
   - Add bookmarks for key insights
   - Create drill-through pages
   - Use tooltips for additional context

4. **Security**
   - Use Row-Level Security if needed
   - Manage access via Power BI Service
   - Keep credentials secure

## Troubleshooting

### Connection Issues
- Verify Supabase project is not paused
- Check firewall rules
- Ensure correct host and port

### Slow Performance
- Reduce data volume with filters
- Use DirectQuery instead of Import
- Optimize DAX measures

### Missing Data
- Verify tables loaded correctly
- Check relationship cardinality
- Refresh data source

## Additional Resources

- [Power BI Documentation](https://docs.microsoft.com/power-bi/)
- [DAX Function Reference](https://dax.guide/)
- [Supabase Database Documentation](https://supabase.com/docs/guides/database)
