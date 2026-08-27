"""
Regex patterns for extracting sustainability metrics from reports and web pages.
Supports PUE, WUE, renewable energy, capacity, and location data.
"""

import re
from typing import Dict, List, Pattern


# PUE Extraction Patterns
PUE_PATTERNS: List[Pattern] = [
    # Standard formats
    re.compile(r"PUE\s*(?:of|is|:)?\s*(\d+\.\d+)", re.IGNORECASE),
    re.compile(r"Power Usage Effectiveness\s*(?:of|is|:)?\s*(\d+\.\d+)", re.IGNORECASE),

    # Rolling/Annual/TTM PUE
    re.compile(r"(?:rolling|annual|trailing)\s+(?:twelve[- ]month|TTM|12[- ]month)?\s*PUE\s*(?:of|is|:)?\s*(\d+\.\d+)", re.IGNORECASE),
    re.compile(r"(?:rolling|annual)\s+(?:average\s+)?PUE\s*(?:of|is|reached)?\s*(\d+\.\d+)", re.IGNORECASE),

    # Design PUE
    re.compile(r"design\s+PUE\s*(?:of|is|:)?\s*(\d+\.\d+)", re.IGNORECASE),
    re.compile(r"designed\s+(?:with\s+)?(?:a\s+)?PUE\s*(?:of|:)?\s*(\d+\.\d+)", re.IGNORECASE),

    # Operating PUE
    re.compile(r"operating\s+PUE\s*(?:of|is|:)?\s*(\d+\.\d+)", re.IGNORECASE),
    re.compile(r"operational\s+PUE\s*(?:of|is|:)?\s*(\d+\.\d+)", re.IGNORECASE),

    # Fleet-wide PUE
    re.compile(r"fleet[- ]wide\s+PUE\s*(?:of|is|:)?\s*(\d+\.\d+)", re.IGNORECASE),
    re.compile(r"global\s+PUE\s*(?:of|is|:)?\s*(\d+\.\d+)", re.IGNORECASE),

    # Context-aware patterns
    re.compile(r"achieved\s+(?:a\s+)?PUE\s*(?:of|:)?\s*(\d+\.\d+)", re.IGNORECASE),
    re.compile(r"maintains?\s+(?:a\s+)?PUE\s*(?:of|:)?\s*(\d+\.\d+)", re.IGNORECASE),
    re.compile(r"average\s+PUE\s*(?:of|is|:)?\s*(\d+\.\d+)", re.IGNORECASE),

    # With year context
    re.compile(r"(?:in|for)\s+(\d{4}).*?PUE\s*(?:of|is|was|:)?\s*(\d+\.\d+)", re.IGNORECASE),
    re.compile(r"PUE\s*(?:of|is|was|:)?\s*(\d+\.\d+).*?(?:in|for)\s+(\d{4})", re.IGNORECASE),
]

# PUE Type Classification
PUE_TYPE_PATTERNS = {
    "TTM": re.compile(r"(?:rolling|trailing|TTM|twelve[- ]month|12[- ]month)", re.IGNORECASE),
    "operating": re.compile(r"(?:operating|operational|actual)", re.IGNORECASE),
    "design": re.compile(r"(?:design|designed|target)", re.IGNORECASE),
    "annual": re.compile(r"(?:annual|yearly)", re.IGNORECASE),
}

# WUE Extraction Patterns
WUE_PATTERNS: List[Pattern] = [
    re.compile(r"WUE\s*(?:of|is|:)?\s*(\d+\.?\d*)", re.IGNORECASE),
    re.compile(r"Water Usage Effectiveness\s*(?:of|is|:)?\s*(\d+\.?\d*)", re.IGNORECASE),
    re.compile(r"(\d+\.?\d*)\s*(?:liters?|L)\s+per\s+kWh", re.IGNORECASE),
    re.compile(r"WUE.*?(\d+\.?\d*)\s*L/kWh", re.IGNORECASE),
    re.compile(r"water\s+consumption.*?(\d+\.?\d*)\s*(?:liters?|L)\s*per\s*kWh", re.IGNORECASE),
]

# Renewable Energy Patterns
RENEWABLE_PATTERNS: List[Pattern] = [
    # Percentage formats
    re.compile(r"(\d+)%\s+renewable", re.IGNORECASE),
    re.compile(r"renewable.*?(\d+)%", re.IGNORECASE),
    re.compile(r"(\d+)%\s+(?:clean|carbon[- ]free)\s+energy", re.IGNORECASE),

    # 100% renewable variations
    re.compile(r"100%\s+renewable\s+energy", re.IGNORECASE),
    re.compile(r"fully\s+renewable", re.IGNORECASE),
    re.compile(r"powered\s+by\s+100%\s+renewable", re.IGNORECASE),

    # Matched renewable energy
    re.compile(r"matched\s+(\d+)%.*?renewable", re.IGNORECASE),
    re.compile(r"(\d+)%.*?matched.*?renewable", re.IGNORECASE),

    # Carbon-free energy
    re.compile(r"(\d+)%\s+carbon[- ]free", re.IGNORECASE),
    re.compile(r"carbon[- ]free.*?(\d+)%", re.IGNORECASE),
]

# Capacity Patterns (MW)
CAPACITY_PATTERNS: List[Pattern] = [
    re.compile(r"(\d+\.?\d*)\s*MW\s+(?:capacity|power)", re.IGNORECASE),
    re.compile(r"capacity\s*(?:of|:)?\s*(\d+\.?\d*)\s*MW", re.IGNORECASE),
    re.compile(r"(\d+\.?\d*)\s*megawatts?", re.IGNORECASE),
    re.compile(r"(\d+\.?\d*)\s*MW\s+(?:data\s+center|facility)", re.IGNORECASE),
]

# Rack Count Patterns
RACK_PATTERNS: List[Pattern] = [
    re.compile(r"(\d+(?:,\d+)?)\s+racks?", re.IGNORECASE),
    re.compile(r"(\d+(?:,\d+)?)\s+server\s+racks?", re.IGNORECASE),
    re.compile(r"rack\s+capacity.*?(\d+(?:,\d+)?)", re.IGNORECASE),
]

# Year Extraction
YEAR_PATTERNS: List[Pattern] = [
    re.compile(r"\b(20[12]\d)\b"),  # Years 2010-2029
    re.compile(r"(?:in|for|during)\s+(20[12]\d)", re.IGNORECASE),
]

# Location Patterns
LOCATION_PATTERNS: List[Pattern] = [
    re.compile(r"(?:located\s+in|facility\s+in|data\s+center\s+in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", re.IGNORECASE),
    re.compile(r"([A-Z][a-z]+),\s*([A-Z][a-z]+)", re.IGNORECASE),  # City, State/Country
]


def extract_pue(text: str) -> List[Dict[str, any]]:
    """
    Extract all PUE values from text with context.
    Returns list of dicts with 'value', 'type', and optional 'year'.
    """
    results = []

    for pattern in PUE_PATTERNS:
        matches = pattern.finditer(text)
        for match in matches:
            pue_value = None
            year = None

            # Extract value and year based on groups
            groups = match.groups()
            if len(groups) == 1:
                pue_value = float(groups[0])
            elif len(groups) == 2:
                # Could be (year, pue) or (pue, year)
                try:
                    pue_value = float(groups[1])
                    year = int(groups[0])
                except ValueError:
                    try:
                        pue_value = float(groups[0])
                        year = int(groups[1])
                    except ValueError:
                        continue

            if pue_value and 1.0 <= pue_value <= 3.0:
                # Determine PUE type from context
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                pue_type = "operating"  # Default

                for type_name, type_pattern in PUE_TYPE_PATTERNS.items():
                    if type_pattern.search(context):
                        pue_type = type_name
                        break

                results.append({
                    "value": pue_value,
                    "type": pue_type,
                    "year": year,
                    "context": context.strip()
                })

    return results


def extract_wue(text: str) -> List[float]:
    """Extract WUE values (liters per kWh)."""
    results = []
    for pattern in WUE_PATTERNS:
        matches = pattern.findall(text)
        for match in matches:
            try:
                wue = float(match)
                if 0 <= wue <= 10:  # Reasonable WUE range
                    results.append(wue)
            except (ValueError, TypeError):
                continue
    return results


def extract_renewable_percentage(text: str) -> List[int]:
    """Extract renewable energy percentages."""
    results = []

    # Check for 100% patterns first
    for pattern in RENEWABLE_PATTERNS:
        if "100" in pattern.pattern or "fully" in pattern.pattern:
            if pattern.search(text):
                results.append(100)
                return results  # 100% is definitive

    # Extract other percentages
    for pattern in RENEWABLE_PATTERNS:
        matches = pattern.findall(text)
        for match in matches:
            try:
                pct = int(match) if match else 100
                if 0 <= pct <= 100:
                    results.append(pct)
            except (ValueError, TypeError):
                continue

    return results


def extract_capacity(text: str) -> List[float]:
    """Extract capacity in MW."""
    results = []
    for pattern in CAPACITY_PATTERNS:
        matches = pattern.findall(text)
        for match in matches:
            try:
                capacity = float(match.replace(",", ""))
                if 0 < capacity <= 500:  # Reasonable MW range
                    results.append(capacity)
            except (ValueError, TypeError):
                continue
    return results


def extract_rack_count(text: str) -> List[int]:
    """Extract rack counts."""
    results = []
    for pattern in RACK_PATTERNS:
        matches = pattern.findall(text)
        for match in matches:
            try:
                racks = int(match.replace(",", ""))
                if 0 < racks <= 50000:  # Reasonable rack range
                    results.append(racks)
            except (ValueError, TypeError):
                continue
    return results


def extract_years(text: str) -> List[int]:
    """Extract years from text."""
    years = []
    for pattern in YEAR_PATTERNS:
        matches = pattern.findall(text)
        years.extend([int(y) for y in matches])
    return sorted(set(years), reverse=True)  # Most recent first
