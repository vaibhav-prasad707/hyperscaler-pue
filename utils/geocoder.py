"""
Geocoding and location utilities for city/country normalization.
"""

from typing import Optional, Tuple
import pycountry

from config.constants import REGION_MAPPING, CITY_TEMPERATURES
from utils.logger import setup_logger


logger = setup_logger(__name__)


class Geocoder:
    """Utilities for location data normalization and enrichment."""

    @staticmethod
    def normalize_city_name(city: str) -> str:
        """
        Normalize city names to standard format.

        Args:
            city: City name

        Returns:
            Normalized city name
        """
        if not city:
            return ""

        # Title case
        city = city.strip().title()

        # Known variations
        city_map = {
            "Bombay": "Mumbai",
            "Noida/Greater Noida": "Noida",
            "Gurgaon": "Gurugram",
            "Bengaluru": "Bangalore",
            "Madras": "Chennai",
        }

        return city_map.get(city, city)

    @staticmethod
    def get_country(city: str) -> Optional[str]:
        """
        Infer country from city name.

        Args:
            city: City name

        Returns:
            Country name or None
        """
        indian_cities = [
            "Mumbai", "Navi Mumbai", "Pune", "Nashik",
            "Hyderabad", "Chennai", "Bangalore",
            "Noida", "Greater Noida", "Gurugram",
            "Amaravati", "Kolkata", "Ahmedabad"
        ]

        city = Geocoder.normalize_city_name(city)

        if city in indian_cities:
            return "India"

        # US cities
        us_cities = ["Virginia", "Oregon", "California", "Texas", "New York"]
        if city in us_cities:
            return "United States"

        # European cities
        eu_cities = {
            "Frankfurt": "Germany",
            "Belgium": "Belgium",
            "London": "United Kingdom",
            "Dublin": "Ireland",
            "Amsterdam": "Netherlands",
        }
        if city in eu_cities:
            return eu_cities[city]

        # Asia Pacific
        apac_cities = {
            "Singapore": "Singapore",
            "Tokyo": "Japan",
            "Hong Kong": "Hong Kong",
        }
        if city in apac_cities:
            return apac_cities[city]

        return None

    @staticmethod
    def get_region(city: str) -> Optional[str]:
        """
        Get region from city name.

        Args:
            city: City name

        Returns:
            Region name or None
        """
        city = Geocoder.normalize_city_name(city)
        return REGION_MAPPING.get(city)

    @staticmethod
    def get_country_code(country: str) -> Optional[str]:
        """
        Get ISO 3166-1 alpha-2 country code.

        Args:
            country: Country name

        Returns:
            Two-letter country code or None
        """
        if not country:
            return None

        try:
            country_obj = pycountry.countries.search_fuzzy(country)[0]
            return country_obj.alpha_2
        except LookupError:
            logger.warning(f"Country code not found for: {country}")
            return None

    @staticmethod
    def get_climate_data(city: str) -> Optional[float]:
        """
        Get average annual temperature for city.

        Args:
            city: City name

        Returns:
            Average temperature in Celsius or None
        """
        city = Geocoder.normalize_city_name(city)
        return CITY_TEMPERATURES.get(city)

    @staticmethod
    def enrich_location_data(record: dict) -> dict:
        """
        Add country, region, and climate data to record.

        Args:
            record: Dictionary with at least 'city' field

        Returns:
            Record with additional location fields
        """
        city = record.get("city", "")

        if city:
            city = Geocoder.normalize_city_name(city)
            record["city"] = city

            if not record.get("country"):
                record["country"] = Geocoder.get_country(city)

            if not record.get("region"):
                record["region"] = Geocoder.get_region(city)

            record["avg_temp_celsius"] = Geocoder.get_climate_data(city)

            if record.get("country"):
                record["country_code"] = Geocoder.get_country_code(record["country"])

        return record


def infer_location_from_text(text: str) -> Optional[Tuple[str, str]]:
    """
    Attempt to extract city and country from text.

    Args:
        text: Text that may contain location information

    Returns:
        Tuple of (city, country) or None
    """
    # This is a simplified implementation
    # A production version might use NER (Named Entity Recognition)

    text_lower = text.lower()

    # Check for Indian cities
    indian_cities = [
        "mumbai", "navi mumbai", "pune", "nashik",
        "hyderabad", "chennai", "bangalore", "bengaluru",
        "noida", "greater noida", "amaravati"
    ]

    for city in indian_cities:
        if city in text_lower:
            return (city.title(), "India")

    # Check for global cities
    global_cities = {
        "singapore": ("Singapore", "Singapore"),
        "virginia": ("Virginia", "United States"),
        "oregon": ("Oregon", "United States"),
        "frankfurt": ("Frankfurt", "Germany"),
        "london": ("London", "United Kingdom"),
        "dublin": ("Dublin", "Ireland"),
        "tokyo": ("Tokyo", "Japan"),
    }

    for city_key, (city, country) in global_cities.items():
        if city_key in text_lower:
            return (city, country)

    return None
