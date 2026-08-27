"""
Company definitions and metadata for PUE benchmark data collection.
Organized by tier: Global Hyperscalers, Indian Operators, Global Colocation.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Company:
    """Company metadata for data collection."""
    name: str
    tier: str
    region: str
    sustainability_urls: List[str]
    known_facilities: Optional[List[Dict]] = None


# Tier 1: Global Hyperscalers
GLOBAL_HYPERSCALERS = [
    Company(
        name="Google",
        tier="Tier 1 - Global Hyperscaler",
        region="Global",
        sustainability_urls=[
            "https://sustainability.google/reports/",
            "https://www.google.com/about/datacenters/efficiency/",
        ],
    ),
    Company(
        name="AWS",
        tier="Tier 1 - Global Hyperscaler",
        region="Global",
        sustainability_urls=[
            "https://sustainability.aboutamazon.com/environment/sustainable-operations/carbon-free-energy",
            "https://aws.amazon.com/about-aws/sustainability/",
        ],
    ),
    Company(
        name="Microsoft",
        tier="Tier 1 - Global Hyperscaler",
        region="Global",
        sustainability_urls=[
            "https://www.microsoft.com/en-us/corporate-responsibility/sustainability/report",
            "https://query.prod.cms.rt.microsoft.com/cms/api/am/binary/RE4RwfV",
        ],
    ),
    Company(
        name="Meta",
        tier="Tier 1 - Global Hyperscaler",
        region="Global",
        sustainability_urls=[
            "https://sustainability.fb.com/",
            "https://sustainability.fb.com/data-centers/",
        ],
    ),
    Company(
        name="Equinix",
        tier="Tier 1 - Global Hyperscaler",
        region="Global",
        sustainability_urls=[
            "https://www.equinix.com/about/sustainability",
            "https://sustainability.equinix.com/",
        ],
    ),
    Company(
        name="Digital Realty",
        tier="Tier 1 - Global Hyperscaler",
        region="Global",
        sustainability_urls=[
            "https://www.digitalrealty.com/sustainability",
            "https://sustainability.digitalrealty.com/",
        ],
    ),
]

# Tier 2: Indian Operators
INDIAN_OPERATORS = [
    Company(
        name="Yotta Infrastructure",
        tier="Tier 2 - Indian Operator",
        region="India",
        sustainability_urls=[
            "https://yotta.com/sustainability/",
            "https://yotta.com/data-centers/",
        ],
        known_facilities=[
            {
                "facility_name": "Yotta NM1",
                "city": "Navi Mumbai",
                "capacity_mw": 50,
                "rack_count": 7200,
                "pue_design": 1.40,
                "source_type": "specification",
            },
            {
                "facility_name": "Yotta D1",
                "city": "Greater Noida",
                "capacity_mw": 30,
                "rack_count": 4500,
                "pue_design": 1.38,
                "source_type": "specification",
            },
        ],
    ),
    Company(
        name="CtrlS Datacenters",
        tier="Tier 2 - Indian Operator",
        region="India",
        sustainability_urls=[
            "https://www.ctrlsdatacenters.com/sustainability",
            "https://www.ctrlsdatacenters.com/",
        ],
        known_facilities=[
            {
                "facility_name": "CtrlS Mumbai DC1",
                "city": "Mumbai",
                "capacity_mw": 30,
                "rack_count": 3000,
                "pue_design": 1.45,
                "source_type": "press_release",
            },
            {
                "facility_name": "CtrlS Hyderabad DC1",
                "city": "Hyderabad",
                "capacity_mw": 45,
                "rack_count": 4200,
                "pue_design": 1.42,
                "source_type": "press_release",
            },
        ],
    ),
    Company(
        name="AdaniConneX",
        tier="Tier 2 - Indian Operator",
        region="India",
        sustainability_urls=[
            "https://www.adaniconnex.com/sustainability",
            "https://www.adaniconnex.com/data-centers",
        ],
        known_facilities=[
            {
                "facility_name": "AdaniConneX Chennai DC1",
                "city": "Chennai",
                "capacity_mw": 60,
                "rack_count": 5000,
                "pue_design": 1.40,
                "source_type": "announcement",
            },
        ],
    ),
    Company(
        name="Nxtra by Airtel",
        tier="Tier 2 - Indian Operator",
        region="India",
        sustainability_urls=[
            "https://nxtra.in/sustainability/",
            "https://nxtra.in/data-centres/",
        ],
        known_facilities=[
            {
                "facility_name": "Nxtra Pune DC",
                "city": "Pune",
                "capacity_mw": 20,
                "rack_count": 2500,
                "pue_design": 1.48,
                "source_type": "specification",
            },
        ],
    ),
    Company(
        name="ST Telemedia GDC India",
        tier="Tier 2 - Indian Operator",
        region="India",
        sustainability_urls=[
            "https://www.sttelemediagdc.in/sustainability",
            "https://www.sttelemediagdc.in/",
        ],
        known_facilities=[
            {
                "facility_name": "STT GDC Mumbai DC1",
                "city": "Mumbai",
                "capacity_mw": 25,
                "rack_count": 3200,
                "pue_design": 1.43,
                "source_type": "specification",
            },
        ],
    ),
    Company(
        name="NTT Global Data Centers India",
        tier="Tier 2 - Indian Operator",
        region="India",
        sustainability_urls=[
            "https://www.global.ntt/en/services/data-centers",
            "https://in.global.ntt/",
        ],
        known_facilities=[
            {
                "facility_name": "NTT Mumbai DC6",
                "city": "Mumbai",
                "capacity_mw": 18,
                "rack_count": 2000,
                "pue_design": 1.50,
                "source_type": "specification",
            },
        ],
    ),
    Company(
        name="Sify Technologies",
        tier="Tier 2 - Indian Operator",
        region="India",
        sustainability_urls=[
            "https://www.sifytechnologies.com/data-centers/",
            "https://www.sifytechnologies.com/sustainability/",
        ],
        known_facilities=[
            {
                "facility_name": "Sify Rabale DC",
                "city": "Navi Mumbai",
                "capacity_mw": 12,
                "rack_count": 1500,
                "pue_design": 1.52,
                "source_type": "specification",
            },
        ],
    ),
    Company(
        name="Web Werks",
        tier="Tier 2 - Indian Operator",
        region="India",
        sustainability_urls=[
            "https://www.webwerks.in/",
            "https://www.webwerks.in/data-center-infrastructure",
        ],
        known_facilities=[
            {
                "facility_name": "Web Werks DC1",
                "city": "Mumbai",
                "capacity_mw": 8,
                "rack_count": 800,
                "pue_design": 1.55,
                "source_type": "specification",
            },
        ],
    ),
    Company(
        name="Pi DATACENTERS",
        tier="Tier 2 - Indian Operator",
        region="India",
        sustainability_urls=[
            "https://www.pidatacenters.com/",
            "https://www.pidatacenters.com/sustainability",
        ],
        known_facilities=[
            {
                "facility_name": "Pi Amaravati DC",
                "city": "Amaravati",
                "capacity_mw": 15,
                "rack_count": 1800,
                "pue_design": 1.47,
                "source_type": "specification",
            },
        ],
    ),
    Company(
        name="ESDS",
        tier="Tier 2 - Indian Operator",
        region="India",
        sustainability_urls=[
            "https://www.esds.co.in/",
            "https://www.esds.co.in/data-center/",
        ],
        known_facilities=[
            {
                "facility_name": "ESDS Nashik DC",
                "city": "Nashik",
                "capacity_mw": 5,
                "rack_count": 600,
                "pue_design": 1.60,
                "source_type": "specification",
            },
        ],
    ),
    Company(
        name="GPX Global",
        tier="Tier 2 - Indian Operator",
        region="India",
        sustainability_urls=[
            "https://www.gpxglobal.net/",
            "https://www.gpxglobal.net/data-centers/india",
        ],
        known_facilities=[
            {
                "facility_name": "GPX Mumbai DC",
                "city": "Mumbai",
                "capacity_mw": 10,
                "rack_count": 1200,
                "pue_design": 1.50,
                "source_type": "specification",
            },
        ],
    ),
    Company(
        name="Colt DCS India",
        tier="Tier 2 - Indian Operator",
        region="India",
        sustainability_urls=[
            "https://www.colt.net/data-centre-services/",
            "https://www.colt.net/resources/sustainability/",
        ],
        known_facilities=[
            {
                "facility_name": "Colt Mumbai DC",
                "city": "Mumbai",
                "capacity_mw": 7,
                "rack_count": 900,
                "pue_design": 1.53,
                "source_type": "specification",
            },
        ],
    ),
]

# Tier 3: Global Colocation
GLOBAL_COLOCATION = [
    Company(
        name="NTT DATA Global",
        tier="Tier 3 - Global Colocation",
        region="Global",
        sustainability_urls=[
            "https://www.global.ntt/en/services/data-centers",
            "https://services.global.ntt/en-us/why-us/sustainability",
        ],
    ),
    Company(
        name="CyrusOne",
        tier="Tier 3 - Global Colocation",
        region="Global",
        sustainability_urls=[
            "https://cyrusone.com/about/sustainability/",
            "https://cyrusone.com/data-centers/",
        ],
    ),
    Company(
        name="QTS Realty Trust",
        tier="Tier 3 - Global Colocation",
        region="Global",
        sustainability_urls=[
            "https://www.qtsdatacenters.com/sustainability",
            "https://www.qtsdatacenters.com/",
        ],
    ),
    Company(
        name="Vantage Data Centers",
        tier="Tier 3 - Global Colocation",
        region="Global",
        sustainability_urls=[
            "https://vantage-dc.com/sustainability/",
            "https://vantage-dc.com/data-centers/",
        ],
    ),
    Company(
        name="Aligned Data Centers",
        tier="Tier 3 - Global Colocation",
        region="Global",
        sustainability_urls=[
            "https://www.alignedenergy.com/sustainability",
            "https://www.alignedenergy.com/",
        ],
    ),
    Company(
        name="Iron Mountain",
        tier="Tier 3 - Global Colocation",
        region="Global",
        sustainability_urls=[
            "https://www.ironmountain.com/about-us/sustainability",
            "https://www.ironmountain.com/data-centers",
        ],
    ),
]

# Combined lists
ALL_COMPANIES = GLOBAL_HYPERSCALERS + INDIAN_OPERATORS + GLOBAL_COLOCATION


def get_company_by_name(name: str) -> Optional[Company]:
    """Retrieve company by exact name match."""
    for company in ALL_COMPANIES:
        if company.name.lower() == name.lower():
            return company
    return None


def get_companies_by_tier(tier: str) -> List[Company]:
    """Get all companies in a specific tier."""
    return [c for c in ALL_COMPANIES if tier.lower() in c.tier.lower()]


def get_companies_by_region(region: str) -> List[Company]:
    """Get all companies in a specific region."""
    return [c for c in ALL_COMPANIES if region.lower() in c.region.lower()]


# Fallback PUE estimates when no data is found
DEFAULT_PUE_BY_TIER = {
    "Tier 1 - Global Hyperscaler": 1.15,  # Hyperscalers are highly efficient
    "Tier 2 - Indian Operator": 1.45,     # Indian facilities are improving
    "Tier 3 - Global Colocation": 1.35,   # Enterprise colocation
}
