"""
Indian data center operator scraper.
Scrapes ESG pages, press releases, and specifications from 12 Indian companies.
Includes search engine integration and fallback knowledge base.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from tqdm import tqdm

from config.companies import INDIAN_OPERATORS
from config.constants import INDIAN_PUE_JSON, COLLECTION_LOG
from config.regex_patterns import (
    extract_pue, extract_wue, extract_renewable_percentage,
    extract_capacity, extract_rack_count, extract_years
)
from utils.downloader import Downloader
from utils.scraper_utils import extract_sustainability_metrics
from utils.geocoder import Geocoder
from utils.logger import setup_logger, log_collection_summary
from scrapers.search_sources import SearchEngine


logger = setup_logger(__name__)


class IndianOperatorScraper:
    """Scrape sustainability data from Indian data center operators."""

    def __init__(self):
        self.downloader = Downloader()
        self.search_engine = SearchEngine()
        self.results: List[Dict] = []

    def scrape_all(self) -> List[Dict]:
        """
        Scrape all Indian operators.

        Returns:
            List of extracted records
        """
        logger.info("Starting Indian operator scraping")

        for company in tqdm(INDIAN_OPERATORS, desc="Indian Companies"):
            logger.info(f"Processing {company.name}")
            company_data = self.scrape_company(company)

            if not company_data:
                # Fallback to known facilities
                company_data = self._use_known_facilities(company)

            self.results.extend(company_data)

        logger.info(f"Completed: extracted {len(self.results)} records")
        return self.results

    def scrape_company(self, company) -> List[Dict]:
        """
        Scrape single company's data.

        Args:
            company: Company object

        Returns:
            List of extracted records
        """
        records = []

        # Try official URLs first
        for url in company.sustainability_urls:
            html = self.downloader.fetch_html(url)

            if html:
                metrics = extract_sustainability_metrics(html)
                full_text = metrics.get('full_text', '')

                if full_text:
                    extracted = self._extract_metrics_from_text(
                        company.name,
                        full_text,
                        url,
                        "official_page"
                    )
                    records.extend(extracted)

        # If no data found, search online
        if not records:
            logger.info(f"No data from official pages, searching online for {company.name}")
            records = self._search_for_data(company.name)

        # Add company metadata
        for record in records:
            record['tier'] = company.tier
            record['region'] = company.region

        return records

    def _search_for_data(self, company: str) -> List[Dict]:
        """
        Search for company data using search engine.

        Args:
            company: Company name

        Returns:
            List of extracted records
        """
        records = []

        # Search for PUE data
        search_results = self.search_engine.search_company_pue(company)

        # Process top results
        for result in search_results[:5]:  # Limit to top 5
            url = result['url']

            # Skip PDFs and non-relevant domains
            if url.endswith('.pdf'):
                continue

            # Fetch and extract
            html = self.downloader.fetch_html(url)

            if html:
                metrics = extract_sustainability_metrics(html)
                full_text = metrics.get('full_text', '')

                if full_text:
                    extracted = self._extract_metrics_from_text(
                        company,
                        full_text,
                        url,
                        "search_result"
                    )
                    records.extend(extracted)

                    if records:  # Found data, stop searching
                        break

        return records

    def _use_known_facilities(self, company) -> List[Dict]:
        """
        Use known facility data as fallback.

        Args:
            company: Company object

        Returns:
            List of records from known facilities
        """
        if not company.known_facilities:
            logger.warning(f"No known facilities for {company.name}")
            return []

        logger.info(f"Using known facilities for {company.name}")

        records = []

        for facility in company.known_facilities:
            record = {
                "company": company.name,
                "facility_name": facility.get('facility_name'),
                "city": facility.get('city'),
                "country": "India",
                "region": "India",
                "year": datetime.now().year,
                "pue_value": facility.get('pue_design'),
                "pue_type": "design",
                "capacity_mw": facility.get('capacity_mw'),
                "rack_count": facility.get('rack_count'),
                "renewable_pct": None,
                "wue_l_per_kwh": None,
                "source_url": company.sustainability_urls[0] if company.sustainability_urls else None,
                "source_type": "estimated",
                "extraction_date": datetime.now().strftime("%Y-%m-%d"),
                "tier": company.tier,
                "region": company.region,
            }

            # Enrich location data
            record = Geocoder.enrich_location_data(record)

            records.append(record)

            logger.info(
                f"Added known facility: {facility.get('facility_name')} - "
                f"PUE={facility.get('pue_design')}"
            )

        return records

    def _extract_metrics_from_text(
        self,
        company: str,
        text: str,
        source_url: str,
        source_type: str
    ) -> List[Dict]:
        """
        Extract all metrics from text.

        Args:
            company: Company name
            text: Text to extract from
            source_url: Source URL
            source_type: Type of source

        Returns:
            List of extracted records
        """
        records = []

        # Extract metrics
        pue_values = extract_pue(text)
        wue_values = extract_wue(text)
        renewable_pcts = extract_renewable_percentage(text)
        capacities = extract_capacity(text)
        rack_counts = extract_rack_count(text)
        years = extract_years(text)

        # Determine year
        year = years[0] if years else datetime.now().year

        # Create records for each PUE value
        if pue_values:
            for pue_data in pue_values:
                record = {
                    "company": company,
                    "facility_name": None,
                    "city": None,
                    "country": "India",
                    "region": "India",
                    "year": pue_data.get('year') or year,
                    "pue_value": pue_data['value'],
                    "pue_type": pue_data['type'],
                    "capacity_mw": capacities[0] if capacities else None,
                    "rack_count": rack_counts[0] if rack_counts else None,
                    "renewable_pct": renewable_pcts[0] if renewable_pcts else None,
                    "wue_l_per_kwh": wue_values[0] if wue_values else None,
                    "source_url": source_url,
                    "source_type": source_type,
                    "extraction_date": datetime.now().strftime("%Y-%m-%d"),
                }

                # Try to extract location from text
                from utils.geocoder import infer_location_from_text
                location = infer_location_from_text(text)
                if location:
                    record['city'], record['country'] = location

                # Enrich location data
                record = Geocoder.enrich_location_data(record)

                records.append(record)

                logger.info(
                    f"Extracted {company}: PUE={pue_data['value']} ({pue_data['type']})"
                )

        return records

    def save_results(self, output_path: Path = INDIAN_PUE_JSON) -> None:
        """
        Save extracted results to JSON.

        Args:
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self.results)} records to {output_path}")

        # Log summary
        summary = {
            "Scraper": "Indian Operators",
            "Companies Processed": len(INDIAN_OPERATORS),
            "Records Extracted": len(self.results),
            "Companies with Data": len(set(r['company'] for r in self.results)),
            "Facilities with PUE": len([r for r in self.results if r.get('pue_value')]),
        }

        log_collection_summary(COLLECTION_LOG, summary)


def main():
    """Run Indian operator scraper."""
    try:
        scraper = IndianOperatorScraper()
        results = scraper.scrape_all()

        if results:
            scraper.save_results()
            logger.info("✓ Indian operator scraping completed successfully")
        else:
            logger.warning("⚠ No data extracted from Indian operators")

    except Exception as e:
        logger.error(f"✗ Indian operator scraping failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
