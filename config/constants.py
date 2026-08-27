"""
Global constants and configuration values for the PUE benchmark platform.
"""

from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
PDF_DIR = RAW_DATA_DIR / "pdfs"

# Ensure directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, PDF_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Output files
COLLECTION_LOG = DATA_DIR / "collection_log.txt"
GLOBAL_PUE_JSON = RAW_DATA_DIR / "global_pue.json"
INDIAN_PUE_JSON = RAW_DATA_DIR / "indian_pue.json"
COLOCATION_PUE_JSON = RAW_DATA_DIR / "colocation_pue.json"
BENCHMARK_CSV = PROCESSED_DATA_DIR / "pue_benchmark.csv"

# HTTP Configuration
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2  # exponential backoff multiplier
REQUEST_DELAY = 1.0  # seconds between requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Data Validation Ranges
PUE_MIN = 1.0
PUE_MAX = 3.0
RENEWABLE_MIN = 0
RENEWABLE_MAX = 100
WUE_MIN = 0.0
WUE_MAX = 10.0
CAPACITY_MIN = 0.0
CAPACITY_MAX = 500.0  # MW
RACK_COUNT_MAX = 50000

# Missing Value Estimation
DEFAULT_PUE_BY_TYPE = {
    "Enterprise": 1.58,
    "India Colocation": 1.45,
    "Global Colocation": 1.35,
    "Hyperscaler": 1.15,
}

# PUE Type Priority (higher is better)
PUE_TYPE_PRIORITY = {
    "TTM": 5,           # Rolling 12-month is highest quality
    "operating": 4,     # Actual operating data
    "annual": 3,        # Annual average
    "measured": 2,      # One-time measurement
    "design": 1,        # Design specification
    "estimated": 0,     # Fallback estimate
}

# Source Type Priority
SOURCE_TYPE_PRIORITY = {
    "sustainability_report": 10,
    "esg_report": 9,
    "specification": 8,
    "investor_presentation": 7,
    "press_release": 6,
    "announcement": 5,
    "interview": 4,
    "news_article": 3,
    "estimate": 2,
    "benchmark": 1,
}

# Carbon Emission Factors (kg CO2 per kWh)
GRID_EMISSION_FACTORS = {
    "India": 0.82,      # Indian grid average
    "US": 0.42,         # US grid average
    "EU": 0.30,         # European grid average
    "Global": 0.47,     # Global average
    "Singapore": 0.41,
}

# Electricity Tariffs (INR per kWh)
ELECTRICITY_TARIFFS = {
    "India_Industrial": 7.0,
    "India_Commercial": 8.5,
    "US_Commercial": 10.0,
    "EU_Commercial": 12.0,
}

# City Climate Data (Average annual temperature in Celsius)
CITY_TEMPERATURES = {
    # India
    "Mumbai": 27.2,
    "Hyderabad": 26.1,
    "Chennai": 28.6,
    "Bangalore": 23.6,
    "Noida": 25.3,
    "Pune": 25.0,
    "Nashik": 24.5,
    "Navi Mumbai": 27.2,
    "Amaravati": 27.8,
    "Greater Noida": 25.3,

    # Global
    "Singapore": 27.0,
    "Virginia": 14.6,
    "Oregon": 11.4,
    "Belgium": 10.5,
    "Frankfurt": 10.6,
    "Tokyo": 15.4,
    "London": 11.0,
    "Dublin": 9.8,
    "Amsterdam": 10.2,
}

# Search Query Templates
SEARCH_QUERIES = {
    "pue": "{company} PUE power usage effectiveness",
    "design_pue": "{company} design PUE data center",
    "operating_pue": "{company} operating PUE efficiency",
    "renewable": "{company} renewable energy percentage data center",
    "capacity": "{company} MW capacity racks data center",
    "sustainability": "{company} sustainability report ESG",
}

# Minimum data quality requirements
MIN_FACILITIES_REQUIRED = 20
MIN_COMPANIES_REQUIRED = 15

# Dashboard Configuration
DASHBOARD_TITLE = "Hyperscaler PUE Benchmark Dashboard"
DASHBOARD_PAGE_ICON = "⚡"

# Color palette for visualizations
COLOR_PALETTE = {
    "primary": "#1f77b4",
    "success": "#2ca02c",
    "warning": "#ff7f0e",
    "danger": "#d62728",
    "info": "#17becf",
    "tier1": "#2ca02c",    # Green for hyperscalers
    "tier2": "#ff7f0e",    # Orange for Indian operators
    "tier3": "#1f77b4",    # Blue for colocation
}

# Region mappings
REGION_MAPPING = {
    "Mumbai": "India - West",
    "Navi Mumbai": "India - West",
    "Pune": "India - West",
    "Nashik": "India - West",
    "Hyderabad": "India - South",
    "Chennai": "India - South",
    "Bangalore": "India - South",
    "Amaravati": "India - South",
    "Noida": "India - North",
    "Greater Noida": "India - North",
    "Singapore": "Asia Pacific",
    "Virginia": "North America - East",
    "Oregon": "North America - West",
    "Frankfurt": "Europe - Central",
    "Belgium": "Europe - West",
    "London": "Europe - West",
    "Dublin": "Europe - West",
    "Amsterdam": "Europe - West",
    "Tokyo": "Asia Pacific",
}

# Country ISO codes
COUNTRY_CODES = {
    "India": "IN",
    "United States": "US",
    "Singapore": "SG",
    "Germany": "DE",
    "Belgium": "BE",
    "United Kingdom": "GB",
    "Ireland": "IE",
    "Netherlands": "NL",
    "Japan": "JP",
}
