"""
Web scraping utilities for HTML parsing and data extraction.
"""

from typing import Optional, List, Dict
from bs4 import BeautifulSoup
import re

from utils.logger import setup_logger


logger = setup_logger(__name__)


class HTMLParser:
    """Parse and extract data from HTML content."""

    @staticmethod
    def parse(html: str) -> Optional[BeautifulSoup]:
        """
        Parse HTML string to BeautifulSoup object.

        Args:
            html: HTML content as string

        Returns:
            BeautifulSoup object or None if parsing failed
        """
        try:
            return BeautifulSoup(html, 'lxml')
        except Exception as e:
            logger.error(f"Failed to parse HTML: {e}")
            return None

    @staticmethod
    def extract_text(soup: BeautifulSoup, selector: str = None) -> str:
        """
        Extract text from parsed HTML.

        Args:
            soup: BeautifulSoup object
            selector: Optional CSS selector

        Returns:
            Extracted text
        """
        if selector:
            elements = soup.select(selector)
            return " ".join([el.get_text(strip=True) for el in elements])
        else:
            return soup.get_text(separator=" ", strip=True)

    @staticmethod
    def find_links(soup: BeautifulSoup, pattern: Optional[str] = None) -> List[str]:
        """
        Extract all links from HTML.

        Args:
            soup: BeautifulSoup object
            pattern: Optional regex pattern to filter links

        Returns:
            List of URLs
        """
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if pattern:
                if re.search(pattern, href, re.IGNORECASE):
                    links.append(href)
            else:
                links.append(href)
        return links

    @staticmethod
    def find_pdfs(soup: BeautifulSoup) -> List[str]:
        """
        Find all PDF links in HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of PDF URLs
        """
        return HTMLParser.find_links(soup, pattern=r'\.pdf$')

    @staticmethod
    def extract_tables(soup: BeautifulSoup) -> List[List[List[str]]]:
        """
        Extract all tables from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of tables (each table is a list of rows, each row is a list of cells)
        """
        tables = []

        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append(rows)

        return tables

    @staticmethod
    def find_by_keywords(soup: BeautifulSoup, keywords: List[str]) -> List[Dict[str, str]]:
        """
        Find text blocks containing specific keywords.

        Args:
            soup: BeautifulSoup object
            keywords: List of keywords to search for

        Returns:
            List of dicts with tag and text
        """
        results = []

        # Search in paragraphs and divs
        for tag in soup.find_all(['p', 'div', 'section', 'article']):
            text = tag.get_text(strip=True)
            if any(keyword.lower() in text.lower() for keyword in keywords):
                results.append({
                    "tag": tag.name,
                    "text": text,
                    "html": str(tag)
                })

        return results

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean extracted text (remove extra whitespace, special characters).

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,;:!?%\-()]', '', text)

        return text.strip()


def extract_sustainability_metrics(html: str) -> Dict[str, any]:
    """
    Extract sustainability-related content from HTML.

    Args:
        html: HTML content

    Returns:
        Dictionary with potential metrics
    """
    soup = HTMLParser.parse(html)
    if not soup:
        return {}

    # Keywords to search for
    keywords = [
        "PUE", "Power Usage Effectiveness",
        "WUE", "Water Usage Effectiveness",
        "renewable energy", "carbon free",
        "data center efficiency", "sustainability",
        "megawatt", "MW", "capacity",
    ]

    # Find relevant sections
    relevant_sections = HTMLParser.find_by_keywords(soup, keywords)

    # Extract full text for pattern matching
    full_text = HTMLParser.extract_text(soup)

    return {
        "full_text": full_text,
        "relevant_sections": relevant_sections,
        "tables": HTMLParser.extract_tables(soup),
        "pdf_links": HTMLParser.find_pdfs(soup),
    }
