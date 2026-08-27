"""
Data validation utilities for PUE benchmark data.
"""

from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime

from config.constants import (
    PUE_MIN, PUE_MAX,
    RENEWABLE_MIN, RENEWABLE_MAX,
    WUE_MIN, WUE_MAX,
    CAPACITY_MIN, CAPACITY_MAX,
    RACK_COUNT_MAX,
)
from utils.logger import setup_logger


logger = setup_logger(__name__)


class DataValidator:
    """Validate and sanitize PUE benchmark data."""

    @staticmethod
    def validate_pue(value: float) -> bool:
        """
        Validate PUE value is within acceptable range.

        Args:
            value: PUE value

        Returns:
            True if valid, False otherwise
        """
        if value is None:
            return False
        try:
            value = float(value)
            return PUE_MIN <= value <= PUE_MAX
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_renewable_pct(value: int) -> bool:
        """Validate renewable energy percentage."""
        if value is None:
            return False
        try:
            value = int(value)
            return RENEWABLE_MIN <= value <= RENEWABLE_MAX
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_wue(value: float) -> bool:
        """Validate WUE value."""
        if value is None:
            return True  # WUE is optional
        try:
            value = float(value)
            return WUE_MIN <= value <= WUE_MAX
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_capacity(value: float) -> bool:
        """Validate capacity in MW."""
        if value is None:
            return True  # Capacity is optional
        try:
            value = float(value)
            return CAPACITY_MIN < value <= CAPACITY_MAX
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_rack_count(value: int) -> bool:
        """Validate rack count."""
        if value is None:
            return True  # Rack count is optional
        try:
            value = int(value)
            return 0 < value <= RACK_COUNT_MAX
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_year(value: int) -> bool:
        """Validate year is reasonable."""
        if value is None:
            return True  # Year is optional
        try:
            value = int(value)
            current_year = datetime.now().year
            return 2000 <= value <= current_year + 1
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_record(record: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate entire record.

        Args:
            record: Dictionary containing facility data

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Required fields
        required_fields = ["company", "pue_value"]
        for field in required_fields:
            if field not in record or record[field] is None:
                errors.append(f"Missing required field: {field}")

        # Validate PUE
        if "pue_value" in record and not DataValidator.validate_pue(record["pue_value"]):
            errors.append(f"Invalid PUE value: {record.get('pue_value')}")

        # Validate optional fields
        if "renewable_pct" in record and record["renewable_pct"] is not None:
            if not DataValidator.validate_renewable_pct(record["renewable_pct"]):
                errors.append(f"Invalid renewable %: {record.get('renewable_pct')}")

        if "wue_l_per_kwh" in record and record["wue_l_per_kwh"] is not None:
            if not DataValidator.validate_wue(record["wue_l_per_kwh"]):
                errors.append(f"Invalid WUE: {record.get('wue_l_per_kwh')}")

        if "capacity_mw" in record and record["capacity_mw"] is not None:
            if not DataValidator.validate_capacity(record["capacity_mw"]):
                errors.append(f"Invalid capacity: {record.get('capacity_mw')}")

        if "rack_count" in record and record["rack_count"] is not None:
            if not DataValidator.validate_rack_count(record["rack_count"]):
                errors.append(f"Invalid rack count: {record.get('rack_count')}")

        if "year" in record and record["year"] is not None:
            if not DataValidator.validate_year(record["year"]):
                errors.append(f"Invalid year: {record.get('year')}")

        is_valid = len(errors) == 0
        return is_valid, errors

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, List[str]]:
        """
        Validate entire DataFrame and filter invalid rows.

        Args:
            df: DataFrame with PUE data

        Returns:
            Tuple of (valid_df, list_of_error_messages)
        """
        errors = []
        valid_rows = []

        for idx, row in df.iterrows():
            record = row.to_dict()
            is_valid, row_errors = DataValidator.validate_record(record)

            if is_valid:
                valid_rows.append(idx)
            else:
                error_msg = f"Row {idx} ({row.get('company', 'Unknown')}): {', '.join(row_errors)}"
                errors.append(error_msg)
                logger.warning(error_msg)

        valid_df = df.loc[valid_rows].copy()

        logger.info(f"Validated {len(df)} rows: {len(valid_df)} valid, {len(errors)} invalid")

        return valid_df, errors


def deduplicate_records(
    df: pd.DataFrame,
    key_columns: List[str] = None,
    keep: str = 'newest'
) -> pd.DataFrame:
    """
    Remove duplicate records, keeping the best quality entry.

    Args:
        df: DataFrame with PUE data
        key_columns: Columns that define uniqueness
        keep: 'newest' (most recent year), 'first', or 'last'

    Returns:
        Deduplicated DataFrame
    """
    if key_columns is None:
        key_columns = ['company', 'facility_name', 'city']

    # Fill NA in key columns to avoid issues
    for col in key_columns:
        if col in df.columns:
            df[col] = df[col].fillna('')

    initial_count = len(df)

    if keep == 'newest':
        # Sort by year descending, then by source quality
        if 'year' in df.columns:
            df = df.sort_values('year', ascending=False)

    # Drop duplicates based on key columns
    df = df.drop_duplicates(subset=key_columns, keep='first')

    final_count = len(df)
    removed = initial_count - final_count

    logger.info(f"Deduplication: {initial_count} → {final_count} rows (removed {removed} duplicates)")

    return df


def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate derived metrics from PUE data.

    Args:
        df: DataFrame with PUE data

    Returns:
        DataFrame with additional calculated columns
    """
    # Cooling overhead percentage
    if 'pue_value' in df.columns:
        df['cooling_overhead_pct'] = (df['pue_value'] - 1.0) * 100

    # Annual waste energy (MWh)
    if 'capacity_mw' in df.columns and 'pue_value' in df.columns:
        df['annual_waste_mwh'] = (df['pue_value'] - 1.0) * df['capacity_mw'] * 8760

    return df
