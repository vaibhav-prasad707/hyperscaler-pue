"""
Search engine integration for finding company data online.
Supports DuckDuckGo and optional Google Custom Search Engine.
"""

import os
import time
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

from config.constants import REQUEST_DELAY, REQUEST_TIMEOUT
from utils.logger import setup_logger


logger = setup_logger(__name__)


class SearchEngine:
    """Search engine integration for finding sustainability data."""

    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_CSE_KEY')
        self.google_engine_id = os.getenv('GOOGLE_CSE_ENGINE_ID')

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        Search for query using available search engine.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of dicts with 'title', 'url', 'snippet'
        """
        # Try Google CSE first if configured
        if self.google_api_key and self.google_engine_id:
            try:
                return self._search_google_cse(query, max_results)
            except Exception as e:
                logger.warning(f"Google CSE failed: {e}, falling back to DuckDuckGo")

        # Fallback to DuckDuckGo
        return self._search_duckduckgo(query, max_results)

    def _search_google_cse(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """
        Search using Google Custom Search Engine API.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of search results
        """
        logger.info(f"Searching Google CSE: {query}")

        results = []
        url = "https://www.googleapis.com/customsearch/v1"

        params = {
            'key': self.google_api_key,
            'cx': self.google_engine_id,
            'q': query,
            'num': min(max_results, 10),  # Google CSE max is 10 per request
        }

        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        data = response.json()

        if 'items' in data:
            for item in data['items']:
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                })

        logger.info(f"Found {len(results)} results")
        time.sleep(REQUEST_DELAY)

        return results

    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """
        Search using DuckDuckGo HTML search (no API key required).

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of search results
        """
        logger.info(f"Searching DuckDuckGo: {query}")

        results = []
        url = "https://html.duckduckgo.com/html/"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        data = {'q': query}

        try:
            response = requests.post(url, data=data, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find result containers
            result_divs = soup.find_all('div', class_='result')

            for div in result_divs[:max_results]:
                title_elem = div.find('a', class_='result__a')
                snippet_elem = div.find('a', class_='result__snippet')

                if title_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'url': title_elem.get('href', ''),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                    })

            logger.info(f"Found {len(results)} results")
            time.sleep(REQUEST_DELAY)

        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")

        return results

    def search_company_pue(self, company: str) -> List[Dict[str, str]]:
        """
        Search for company PUE data specifically.

        Args:
            company: Company name

        Returns:
            List of relevant search results
        """
        queries = [
            f"{company} PUE power usage effectiveness",
            f"{company} data center efficiency PUE",
            f"{company} sustainability report PUE",
        ]

        all_results = []

        for query in queries:
            results = self.search(query, max_results=5)
            all_results.extend(results)

        # Deduplicate by URL
        seen_urls = set()
        unique_results = []

        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)

        return unique_results

    def search_company_sustainability(self, company: str) -> List[Dict[str, str]]:
        """
        Search for company sustainability pages.

        Args:
            company: Company name

        Returns:
            List of relevant URLs
        """
        queries = [
            f"{company} sustainability ESG report",
            f"{company} renewable energy data center",
            f"{company} environmental report",
        ]

        all_results = []

        for query in queries:
            results = self.search(query, max_results=5)
            all_results.extend(results)

        # Filter for official company domains
        company_domain = company.lower().replace(' ', '')
        official_results = [
            r for r in all_results
            if company_domain in r['url'].lower()
        ]

        # Deduplicate
        seen_urls = set()
        unique_results = []

        for result in official_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)

        return unique_results
