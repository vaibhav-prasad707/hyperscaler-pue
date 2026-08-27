"""
Global colocation data center scraper.
Scrapes sustainability data from major colocation providers:
- NTT DATA Global
- CyrusOne
- QTS Realty Trust
- Vantage Data Centers
- Aligned Data Centers
- Iron Mountain
"""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from tqdm import tqdm

from config.companies import GLOBAL_COLOCATION
from config.constants import COLOCATION_PUE_JSON, COLLECTION_LOG
from config.regex_patterns import (
    extract_pue, extract_wue, extract_renewable_percentage,
    extract_capacity, extract_rack_count, extract_years
)
from utils.downloader import Downloader
from utils.scraper_utils import extract_sustainability_metrics
from utils.pdf_parser import PDFParser
from utils.logger import setup_logger, log_collection_summary
from scrapers.search_sources import SearchEngine


logger = setup_logger(__name__)


class GlobalColocationScraper:
    """Scrape sustainability data from global colocation providers."""

    def __init__(self):
        self.downloader = Downloader()
        self.pdf_parser = PDFParser()
        self.search_engine = SearchEngine()
        self.results: List[Dict] = []

    def scrape_all(self) -> List[Dict]:
        """
        Scrape all global colocation providers.

        Returns:
            List of extracted records
        """
        logger.info("Starting global colocation scraping")

        for company in tqdm(GLOBAL_COLOCATION, desc="Colocation Companies"):
            logger.info(f"Processing {company.name}")
            company_data = self.scrape_company(company)
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

        # Try official URLs
        for url in company.sustainability_urls:
            if url.endswith('.pdf') or 'pdf' in url.lower():
                records.extend(self._extract_from_pdf_url(company.name, url))
            else:
                records.extend(self._extract_from_html(company.name, url))

        # If no data, search online
        if not records:
            logger.info(f"No data from official pages, searching for {company.name}")
            records = self._search_for_data(company.name)

        # Add company metadata
        for record in records:
            record['tier'] = company.tier
            record['region'] = company.region

        return records

    def _extract_from_pdf_url(self, company: str, url: str) -> List[Dict]:
        """
        Download and extract data from PDF.

        Args:
            company: Company name
            url: PDF URL

        Returns:
            List of extracted records
        """
        records = []

        filename = f"{company.replace(' ', '_').lower()}_sustainability.pdf"
        pdf_path = self.downloader.download_pdf(url, filename=filename)

        if pdf_path:
            text = self.pdf_parser.extract_text(pdf_path)

            if text:
                records = self._extract_metrics_from_text(
                    company,
                    text,
                    url,
                    "sustainability_report"
                )

        return records

    def _extract_from_html(self, company: str, url: str) -> List[Dict]:
        """
        Extract data from HTML page.

        Args:
            company: Company name
            url: Page URL

        Returns:
            List of extracted records
        """
        records = []

        html = self.downloader.fetch_html(url)

        if html:
            metrics = extract_sustainability_metrics(html)
            full_text = metrics.get('full_text', '')

            if full_text:
                records = self._extract_metrics_from_text(
                    company,
                    full_text,
                    url,
                    "web_page"
                )

            # Check for PDF links
            if metrics.get('pdf_links'):
                for pdf_link in metrics['pdf_links'][:2]:
                    if not pdf_link.startswith('http'):
                        from urllib.parse import urljoin
                        pdf_link = urljoin(url, pdf_link)

                    records.extend(self._extract_from_pdf_url(company, pdf_link))

        return records

    def _search_for_data(self, company: str) -> List[Dict]:
        """
        Search for company PUE data online.

        Args:
            company: Company name

        Returns:
            List of extracted records
        """
        records = []

        search_results = self.search_engine.search_company_pue(company)

        for result in search_results[:5]:
            url = result['url']

            if url.endswith('.pdf'):
                continue

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

                    if records:
                        break

        return records

    def _extract_metrics_from_text(
        self,
        company: str,
        text: str,
        source_url: str,
        source_type: str
    ) -> List[Dict]:
        """
        Extract metrics from text.

        Args:
            company: Company name
            text: Text content
            source_url: Source URL
            source_type: Type of source

        Returns:
            List of extracted records
        """
        records = []

        # Extract all metrics
        pue_values = extract_pue(text)
        wue_values = extract_wue(text)
        renewable_pcts = extract_renewable_percentage(text)
        capacities = extract_capacity(text)
        rack_counts = extract_rack_count(text)
        years = extract_years(text)

        year = years[0] if years else datetime.now().year

        # Create records
        if pue_values:
            for pue_data in pue_values:
                record = {
                    "company": company,
                    "facility_name": None,
                    "city": None,
                    "country": None,
                    "region": None,
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

                records.append(record)

                logger.info(
                    f"Extracted {company}: PUE={pue_data['value']} ({pue_data['type']})"
                )

        return records

    def save_results(self, output_path: Path = COLOCATION_PUE_JSON) -> None:
        """
        Save results to JSON.

        Args:
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self.results)} records to {output_path}")

        # Log summary
        summary = {
            "Scraper": "Global Colocation",
            "Companies Processed": len(GLOBAL_COLOCATION),
            "Records Extracted": len(self.results),
            "Companies with Data": len(set(r['company'] for r in self.results)),
        }

        log_collection_summary(COLLECTION_LOG, summary)


def main():
    """Run global colocation scraper."""
    try:
        scraper = GlobalColocationScraper()
        results = scraper.scrape_all()

        if results:
            scraper.save_results()
            logger.info("✓ Global colocation scraping completed successfully")
        else:
            logger.warning("⚠ No data extracted from colocation providers")

    except Exception as e:
        logger.error(f"✗ Global colocation scraping failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
