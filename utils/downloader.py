"""
HTTP downloader utility with retry logic, caching, and progress tracking.
"""

import time
from pathlib import Path
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm

from config.constants import (
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_BACKOFF_FACTOR,
    REQUEST_DELAY,
    USER_AGENT,
    PDF_DIR,
)
from utils.logger import setup_logger


logger = setup_logger(__name__)


class Downloader:
    """HTTP downloader with retry logic and caching."""

    def __init__(
        self,
        timeout: int = REQUEST_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        backoff_factor: float = RETRY_BACKOFF_FACTOR,
    ):
        """
        Initialize downloader with retry configuration.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff multiplier for retries
        """
        self.timeout = timeout
        self.session = self._create_session(max_retries, backoff_factor)

    def _create_session(self, max_retries: int, backoff_factor: float) -> requests.Session:
        """Create requests session with retry strategy."""
        session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })

        return session

    def download_pdf(
        self,
        url: str,
        filename: Optional[str] = None,
        force: bool = False,
    ) -> Optional[Path]:
        """
        Download PDF file with caching.

        Args:
            url: URL to download
            filename: Optional custom filename
            force: Force re-download even if cached

        Returns:
            Path to downloaded PDF or None if failed
        """
        if not filename:
            filename = url.split("/")[-1]
            if not filename.endswith(".pdf"):
                filename += ".pdf"

        output_path = PDF_DIR / filename

        # Check cache
        if output_path.exists() and not force:
            logger.info(f"Using cached PDF: {output_path.name}")
            return output_path

        logger.info(f"Downloading: {url}")

        try:
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()

            # Get file size for progress bar
            total_size = int(response.headers.get('content-length', 0))

            # Download with progress bar
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f, tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc=filename,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

            logger.info(f"Downloaded: {output_path.name} ({total_size / 1024 / 1024:.2f} MB)")
            time.sleep(REQUEST_DELAY)  # Rate limiting

            return output_path

        except requests.exceptions.RequestException as e:
            logger.error(f"Download failed for {url}: {e}")
            return None

    def fetch_html(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from URL.

        Args:
            url: URL to fetch

        Returns:
            HTML content as string or None if failed
        """
        logger.debug(f"Fetching HTML: {url}")

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            time.sleep(REQUEST_DELAY)  # Rate limiting
            return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def download_file(
        self,
        url: str,
        output_path: Path,
        force: bool = False,
    ) -> bool:
        """
        Download any file type.

        Args:
            url: URL to download
            output_path: Where to save the file
            force: Force re-download even if exists

        Returns:
            True if successful, False otherwise
        """
        if output_path.exists() and not force:
            logger.info(f"File already exists: {output_path}")
            return True

        logger.info(f"Downloading: {url}")

        try:
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Saved: {output_path}")
            time.sleep(REQUEST_DELAY)
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Download failed: {e}")
            return False

    def check_url(self, url: str) -> bool:
        """
        Check if URL is accessible.

        Args:
            url: URL to check

        Returns:
            True if accessible, False otherwise
        """
        try:
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
