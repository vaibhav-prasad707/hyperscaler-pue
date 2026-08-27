"""
PDF parsing utility using PyMuPDF (fitz) for text extraction.
"""

from pathlib import Path
from typing import Optional, List, Dict
import fitz  # PyMuPDF

from utils.logger import setup_logger


logger = setup_logger(__name__)


class PDFParser:
    """Extract text and metadata from PDF files."""

    @staticmethod
    def extract_text(pdf_path: Path) -> Optional[str]:
        """
        Extract all text from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text or None if failed
        """
        if not pdf_path.exists():
            logger.error(f"PDF not found: {pdf_path}")
            return None

        try:
            logger.info(f"Extracting text from: {pdf_path.name}")
            doc = fitz.open(pdf_path)

            text_content = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                text_content.append(text)

            doc.close()

            full_text = "\n".join(text_content)
            logger.info(f"Extracted {len(full_text)} characters from {len(doc)} pages")

            return full_text

        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            return None

    @staticmethod
    def extract_text_by_page(pdf_path: Path) -> Optional[List[str]]:
        """
        Extract text page by page.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of text strings (one per page) or None if failed
        """
        if not pdf_path.exists():
            logger.error(f"PDF not found: {pdf_path}")
            return None

        try:
            logger.info(f"Extracting text by page from: {pdf_path.name}")
            doc = fitz.open(pdf_path)

            pages = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                pages.append(text)

            doc.close()

            logger.info(f"Extracted {len(pages)} pages")
            return pages

        except Exception as e:
            logger.error(f"Failed to extract pages from {pdf_path}: {e}")
            return None

    @staticmethod
    def get_metadata(pdf_path: Path) -> Optional[Dict[str, str]]:
        """
        Extract PDF metadata.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with metadata or None if failed
        """
        if not pdf_path.exists():
            logger.error(f"PDF not found: {pdf_path}")
            return None

        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            doc.close()

            return {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", ""),
            }

        except Exception as e:
            logger.error(f"Failed to extract metadata from {pdf_path}: {e}")
            return None

    @staticmethod
    def search_text(pdf_path: Path, search_term: str) -> List[Dict[str, any]]:
        """
        Search for text in PDF and return matches with page numbers.

        Args:
            pdf_path: Path to PDF file
            search_term: Text to search for

        Returns:
            List of dicts with page_num and matching text
        """
        if not pdf_path.exists():
            logger.error(f"PDF not found: {pdf_path}")
            return []

        try:
            doc = fitz.open(pdf_path)
            matches = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()

                if search_term.lower() in text.lower():
                    # Extract context around match
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        if search_term.lower() in line.lower():
                            # Get context: previous and next lines
                            context_start = max(0, i - 2)
                            context_end = min(len(lines), i + 3)
                            context = '\n'.join(lines[context_start:context_end])

                            matches.append({
                                "page_num": page_num + 1,
                                "line": line.strip(),
                                "context": context.strip(),
                            })

            doc.close()

            logger.info(f"Found {len(matches)} matches for '{search_term}'")
            return matches

        except Exception as e:
            logger.error(f"Failed to search {pdf_path}: {e}")
            return []

    @staticmethod
    def extract_tables(pdf_path: Path) -> Optional[List[List[str]]]:
        """
        Extract tables from PDF (basic implementation).

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of tables (each table is a list of rows)
        """
        # Note: PyMuPDF doesn't have advanced table extraction
        # This is a placeholder for potential enhancement with tabula-py or camelot
        logger.warning("Table extraction not fully implemented")
        return None
