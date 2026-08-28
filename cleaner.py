"""
Data cleaner and normalizer for PUE benchmark data.
Consolidates all JSON outputs, validates, deduplicates, and produces final CSV.
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from config.constants import (
    RAW_DATA_DIR,
    BENCHMARK_CSV,
    COLLECTION_LOG,
    DEFAULT_PUE_BY_TYPE,
    PUE_TYPE_PRIORITY,
    SOURCE_TYPE_PRIORITY,
    MIN_FACILITIES_REQUIRED,
    MIN_COMPANIES_REQUIRED,
)
from config.companies import DEFAULT_PUE_BY_TIER, get_company_by_name
from utils.validation import DataValidator, deduplicate_records, calculate_derived_metrics
from utils.geocoder import Geocoder
from utils.logger import setup_logger, log_collection_summary


logger = setup_logger(__name__)


class DataCleaner:
    """Clean, normalize, and validate PUE benchmark data."""

    def __init__(self):
        self.validator = DataValidator()
        self.all_records: List[Dict] = []
        self.df: pd.DataFrame = None

    def load_all_json_files(self) -> None:
        """Load all JSON files from raw data directory."""
        logger.info("Loading JSON files")

        json_files = list(RAW_DATA_DIR.glob("*.json"))

        if not json_files:
            logger.warning("No JSON files found in raw data directory")
            return

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if isinstance(data, list):
                    self.all_records.extend(data)
                    logger.info(f"Loaded {len(data)} records from {json_file.name}")
                else:
                    logger.warning(f"Unexpected format in {json_file.name}")

            except Exception as e:
                logger.error(f"Failed to load {json_file}: {e}")

        logger.info(f"Total records loaded: {len(self.all_records)}")

    def normalize_schema(self) -> pd.DataFrame:
        """
        Normalize all records to consistent schema.

        Returns:
            DataFrame with normalized schema
        """
        logger.info("Normalizing schema")

        # Define standard columns
        columns = [
            'company',
            'facility_name',
            'city',
            'country',
            'region',
            'year',
            'pue_value',
            'pue_type',
            'capacity_mw',
            'rack_count',
            'renewable_pct',
            'wue_l_per_kwh',
            'source_url',
            'source_type',
            'extraction_date',
            'tier',
        ]

        # Normalize each record
        normalized = []

        for record in self.all_records:
            # Create normalized record with all columns
            norm_record = {col: record.get(col) for col in columns}

            # Enrich location data
            norm_record = Geocoder.enrich_location_data(norm_record)

            # Add tier if missing
            if not norm_record.get('tier'):
                company_obj = get_company_by_name(norm_record['company'])
                if company_obj:
                    norm_record['tier'] = company_obj.tier

            normalized.append(norm_record)

        df = pd.DataFrame(normalized)

        logger.info(f"Normalized {len(df)} records")

        return df

    def fill_missing_pue(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fill missing PUE values with intelligent estimates.

        Args:
            df: DataFrame with PUE data

        Returns:
            DataFrame with filled PUE values
        """
        logger.info("Filling missing PUE values")

        missing_mask = df['pue_value'].isna()
        missing_count = missing_mask.sum()

        if missing_count == 0:
            logger.info("No missing PUE values")
            return df

        logger.info(f"Found {missing_count} missing PUE values")

        # Fill based on tier
        for idx, row in df[missing_mask].iterrows():
            tier = row.get('tier', '')
            company = row.get('company', '')

            # Use tier-based estimate
            estimated_pue = DEFAULT_PUE_BY_TIER.get(tier, 1.50)

            df.at[idx, 'pue_value'] = estimated_pue
            df.at[idx, 'pue_type'] = 'estimated'
            df.at[idx, 'source_type'] = 'benchmark'

            logger.debug(f"Filled PUE for {company}: {estimated_pue} (tier-based)")

        filled_count = missing_mask.sum()
        logger.info(f"Filled {filled_count} missing PUE values")

        return df

    def deduplicate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicates, keeping highest quality records.

        Args:
            df: DataFrame with PUE data

        Returns:
            Deduplicated DataFrame
        """
        logger.info("Deduplicating records")

        initial_count = len(df)

        # Add priority scores for sorting
        df['pue_type_priority'] = df['pue_type'].map(PUE_TYPE_PRIORITY).fillna(0)
        df['source_type_priority'] = df['source_type'].map(SOURCE_TYPE_PRIORITY).fillna(0)

        # Sort by quality: year (desc), pue_type priority, source_type priority
        df = df.sort_values(
            by=['year', 'pue_type_priority', 'source_type_priority'],
            ascending=[False, False, False]
        )

        # Deduplicate by company + facility + city (keep first = best quality)
        key_columns = ['company', 'facility_name', 'city']
        df = df.drop_duplicates(subset=key_columns, keep='first')

        # Drop priority columns
        df = df.drop(columns=['pue_type_priority', 'source_type_priority'])

        final_count = len(df)
        removed = initial_count - final_count

        logger.info(f"Deduplication: {initial_count} → {final_count} rows (removed {removed})")

        return df

    def validate_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate data and remove invalid records.

        Args:
            df: DataFrame to validate

        Returns:
            Clean DataFrame
        """
        logger.info("Validating data")

        # Use validator
        valid_df, errors = self.validator.validate_dataframe(df)

        if errors:
            logger.warning(f"Validation errors: {len(errors)}")
            for error in errors[:10]:  # Show first 10
                logger.debug(error)

        return valid_df

    def calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived metrics.

        Args:
            df: DataFrame with base data

        Returns:
            DataFrame with calculated metrics
        """
        logger.info("Calculating derived metrics")

        df = calculate_derived_metrics(df)

        return df

    def generate_summary_stats(self, df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for validation.

        Args:
            df: Final DataFrame

        Returns:
            Dictionary with summary stats
        """
        if len(df) == 0:
            return {
                "Total Facilities": 0,
                "Total Companies": 0,
                "Status": "No valid records after cleaning",
            }

        stats = {
            "Total Facilities": len(df),
            "Total Companies": df['company'].nunique(),
            "Companies with PUE": len(df[df['pue_value'].notna()]),
            "Average PUE (All)": round(df['pue_value'].mean(), 3) if df['pue_value'].notna().any() else "N/A",
            "Average PUE (Hyperscalers)": round(
                df[df['tier'].str.contains('Tier 1', na=False)]['pue_value'].mean(), 3
            ) if len(df[df['tier'].str.contains('Tier 1', na=False)]) > 0 else "N/A",
            "Average PUE (Indian)": round(
                df[df['tier'].str.contains('Tier 2', na=False)]['pue_value'].mean(), 3
            ) if len(df[df['tier'].str.contains('Tier 2', na=False)]) > 0 else "N/A",
            "Average PUE (Colocation)": round(
                df[df['tier'].str.contains('Tier 3', na=False)]['pue_value'].mean(), 3
            ) if len(df[df['tier'].str.contains('Tier 3', na=False)]) > 0 else "N/A",
            "Average Renewable %": round(df['renewable_pct'].mean(), 1) if df['renewable_pct'].notna().any() else "N/A",
            "Records with Operating PUE": len(df[df['pue_type'] == 'operating']),
            "Records with Design PUE": len(df[df['pue_type'] == 'design']),
            "Records with TTM PUE": len(df[df['pue_type'] == 'TTM']),
            "Records with Estimated PUE": len(df[df['pue_type'] == 'estimated']),
            "Total Capacity (MW)": round(df['capacity_mw'].sum(), 1) if df['capacity_mw'].notna().any() else "N/A",
            "Year Range": f"{int(df['year'].min())}-{int(df['year'].max())}" if df['year'].notna().any() else "N/A",
        }

        return stats

    def clean_all(self) -> pd.DataFrame:
        """
        Run complete cleaning pipeline.

        Returns:
            Final clean DataFrame
        """
        logger.info("=" * 80)
        logger.info("Starting data cleaning pipeline")
        logger.info("=" * 80)

        # Step 1: Load data
        self.load_all_json_files()

        if not self.all_records:
            raise ValueError("No data loaded from JSON files")

        # Step 2: Normalize schema
        df = self.normalize_schema()

        # Step 3: Fill missing PUE values
        df = self.fill_missing_pue(df)

        # Step 4: Validate and clean
        df = self.validate_and_clean(df)

        # Step 5: Deduplicate
        df = self.deduplicate(df)

        # Step 6: Calculate derived metrics
        df = self.calculate_metrics(df)

        # Step 7: Final sort
        df = df.sort_values(by=['tier', 'company', 'pue_value'])

        self.df = df

        logger.info("=" * 80)
        logger.info("Data cleaning completed")
        logger.info("=" * 80)

        return df

    def save_csv(self, output_path: Path = BENCHMARK_CSV) -> None:
        """
        Save cleaned data to CSV.

        Args:
            output_path: Output file path
        """
        if self.df is None:
            raise ValueError("No data to save. Run clean_all() first.")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.df.to_csv(output_path, index=False, encoding='utf-8')

        logger.info(f"Saved {len(self.df)} records to {output_path}")

    def print_summary(self) -> None:
        """Print summary statistics."""
        if self.df is None:
            logger.warning("No data available for summary")
            return

        stats = self.generate_summary_stats(self.df)

        logger.info("\n" + "=" * 80)
        logger.info("FINAL DATASET SUMMARY")
        logger.info("=" * 80)

        for key, value in stats.items():
            logger.info(f"  {key}: {value}")

        logger.info("=" * 80)

        # Log to file
        log_collection_summary(COLLECTION_LOG, stats)

    def validate_requirements(self) -> bool:
        """
        Validate that dataset meets minimum requirements.

        Returns:
            True if requirements met, False otherwise
        """
        if self.df is None:
            return False

        total_facilities = len(self.df)
        total_companies = self.df['company'].nunique()

        meets_requirements = (
            total_facilities >= MIN_FACILITIES_REQUIRED and
            total_companies >= MIN_COMPANIES_REQUIRED
        )

        if meets_requirements:
            logger.info(
                f"✓ Dataset meets requirements: "
                f"{total_facilities} facilities, {total_companies} companies"
            )
        else:
            logger.warning(
                f"✗ Dataset does not meet requirements: "
                f"{total_facilities}/{MIN_FACILITIES_REQUIRED} facilities, "
                f"{total_companies}/{MIN_COMPANIES_REQUIRED} companies"
            )

        return meets_requirements


def main():
    """Run data cleaner."""
    try:
        cleaner = DataCleaner()

        # Run cleaning pipeline
        df = cleaner.clean_all()

        # Save results
        cleaner.save_csv()

        # Print summary
        cleaner.print_summary()

        # Validate requirements
        if cleaner.validate_requirements():
            logger.info("✓ Data cleaning completed successfully")
        else:
            logger.warning("⚠ Data cleaning completed but minimum requirements not met")

    except Exception as e:
        logger.error(f"✗ Data cleaning failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
