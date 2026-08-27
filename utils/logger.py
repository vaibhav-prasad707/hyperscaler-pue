"""
Centralized logging utility with color-coded console output and file logging.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import colorlog


def setup_logger(
    name: str,
    log_file: Optional[Path] = None,
    level: str = "INFO",
    console: bool = True,
) -> logging.Logger:
    """
    Create a configured logger with color-coded console and optional file output.

    Args:
        name: Logger name (typically __name__)
        log_file: Optional path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console: Whether to output to console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers = []  # Clear existing handlers

    # Console handler with colors
    if console:
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)s%(reset)s - %(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        )

        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler (plain text)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


class LoggerMixin:
    """Mixin class to add logging capability to any class."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, '_logger'):
            self._logger = setup_logger(self.__class__.__name__)
        return self._logger


def log_collection_summary(log_file: Path, summary: dict) -> None:
    """
    Append collection summary to the collection log file.

    Args:
        log_file: Path to collection log
        summary: Dictionary with collection statistics
    """
    log_file.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*80}\n")
        f.write(f"Collection Run: {timestamp}\n")
        f.write(f"{'='*80}\n")

        for key, value in summary.items():
            f.write(f"{key}: {value}\n")

        f.write(f"{'='*80}\n\n")


def log_error_detail(log_file: Path, error_type: str, details: str) -> None:
    """
    Log detailed error information.

    Args:
        log_file: Path to log file
        error_type: Type of error
        details: Detailed error message
    """
    log_file.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n[ERROR] {timestamp} - {error_type}\n")
        f.write(f"{details}\n")
        f.write("-" * 80 + "\n")


# Create module-level logger
logger = setup_logger(__name__)
