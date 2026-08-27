"""
Supabase ingestion pipeline.
Loads cleaned CSV data into Supabase PostgreSQL database.
Implements star schema with dimension and fact tables.
"""

import os
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

from config.constants import BENCHMARK_CSV
from utils.logger import setup_logger


# Load environment variables
load_dotenv()

logger = setup_logger(__name__)


class SupabaseIngestor:
    """Ingest PUE benchmark data into Supabase."""

    def __init__(self):
        """Initialize Supabase client."""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError(
                "Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env"
            )

        self.client: Client = create_client(supabase_url, supabase_key)
        logger.info("Connected to Supabase")

    def load_csv(self, csv_path: Path = BENCHMARK_CSV) -> pd.DataFrame:
        """
        Load cleaned CSV data.

        Args:
            csv_path: Path to CSV file

        Returns:
            DataFrame with data
        """
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV not found: {csv_path}")

        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} records from {csv_path}")

        return df

    def ingest_raw_data(self, df: pd.DataFrame) -> int:
        """
        Insert data into raw_pue_data table.

        Args:
            df: DataFrame with data

        Returns:
            Number of records inserted
        """
        logger.info("Ingesting raw data")

        # Convert DataFrame to list of dicts
        records = df.to_dict('records')

        # Handle NaN values
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None

        # Batch insert
        batch_size = 100
        total_inserted = 0

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]

            try:
                response = self.client.table('raw_pue_data').insert(batch).execute()
                total_inserted += len(batch)
                logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")

            except Exception as e:
                logger.error(f"Failed to insert batch: {e}")

        logger.info(f"Total raw records inserted: {total_inserted}")
        return total_inserted

    def populate_dim_company(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Populate dim_company table and return company_id mapping.

        Args:
            df: DataFrame with data

        Returns:
            Dict mapping company_name to company_id
        """
        logger.info("Populating dim_company")

        # Get unique companies
        companies = df[['company', 'tier', 'region']].drop_duplicates('company')

        company_mapping = {}

        for _, row in companies.iterrows():
            company_name = row['company']
            tier = row['tier']
            region = row['region']

            try:
                # Check if company exists
                response = self.client.table('dim_company')\
                    .select('company_id')\
                    .eq('company_name', company_name)\
                    .execute()

                if response.data:
                    # Company exists
                    company_id = response.data[0]['company_id']
                else:
                    # Insert new company
                    response = self.client.table('dim_company')\
                        .insert({
                            'company_name': company_name,
                            'tier': tier,
                            'region': region,
                        })\
                        .execute()

                    company_id = response.data[0]['company_id']

                company_mapping[company_name] = company_id

            except Exception as e:
                logger.error(f"Failed to process company {company_name}: {e}")

        logger.info(f"Processed {len(company_mapping)} companies")
        return company_mapping

    def populate_dim_location(self, df: pd.DataFrame) -> Dict[tuple, str]:
        """
        Populate dim_location table and return location_id mapping.

        Args:
            df: DataFrame with data

        Returns:
            Dict mapping (city, country) to location_id
        """
        logger.info("Populating dim_location")

        # Get unique locations
        locations = df[['city', 'country', 'country_code', 'region', 'avg_temp_celsius']]\
            .dropna(subset=['city'])\
            .drop_duplicates(['city', 'country'])

        location_mapping = {}

        for _, row in locations.iterrows():
            city = row['city']
            country = row['country']
            country_code = row.get('country_code')
            region = row.get('region')
            avg_temp = row.get('avg_temp_celsius')

            if pd.isna(city) or not city:
                continue

            try:
                # Check if location exists
                response = self.client.table('dim_location')\
                    .select('location_id')\
                    .eq('city', city)\
                    .eq('country', country if not pd.isna(country) else '')\
                    .execute()

                if response.data:
                    location_id = response.data[0]['location_id']
                else:
                    # Insert new location
                    response = self.client.table('dim_location')\
                        .insert({
                            'city': city,
                            'country': country if not pd.isna(country) else None,
                            'country_code': country_code if not pd.isna(country_code) else None,
                            'region': region if not pd.isna(region) else None,
                            'avg_temp_celsius': float(avg_temp) if not pd.isna(avg_temp) else None,
                        })\
                        .execute()

                    location_id = response.data[0]['location_id']

                location_mapping[(city, country)] = location_id

            except Exception as e:
                logger.error(f"Failed to process location {city}, {country}: {e}")

        logger.info(f"Processed {len(location_mapping)} locations")
        return location_mapping

    def populate_fact_efficiency(
        self,
        df: pd.DataFrame,
        company_mapping: Dict[str, str],
        location_mapping: Dict[tuple, str]
    ) -> int:
        """
        Populate fact_efficiency table.

        Args:
            df: DataFrame with data
            company_mapping: Company name to ID mapping
            location_mapping: Location to ID mapping

        Returns:
            Number of records inserted
        """
        logger.info("Populating fact_efficiency")

        records = []

        for _, row in df.iterrows():
            company_id = company_mapping.get(row['company'])
            location_id = location_mapping.get((row.get('city'), row.get('country')))

            if not company_id:
                logger.warning(f"No company_id for {row['company']}")
                continue

            record = {
                'company_id': company_id,
                'location_id': location_id,
                'facility_name': row.get('facility_name'),
                'year': int(row['year']) if not pd.isna(row['year']) else None,
                'pue_value': float(row['pue_value']),
                'pue_type': row.get('pue_type'),
                'capacity_mw': float(row['capacity_mw']) if not pd.isna(row.get('capacity_mw')) else None,
                'rack_count': int(row['rack_count']) if not pd.isna(row.get('rack_count')) else None,
                'renewable_pct': int(row['renewable_pct']) if not pd.isna(row.get('renewable_pct')) else None,
                'wue_l_per_kwh': float(row['wue_l_per_kwh']) if not pd.isna(row.get('wue_l_per_kwh')) else None,
                'source_url': row.get('source_url'),
                'source_type': row.get('source_type'),
                'extraction_date': row.get('extraction_date'),
            }

            records.append(record)

        # Batch insert
        batch_size = 100
        total_inserted = 0

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]

            try:
                response = self.client.table('fact_efficiency').insert(batch).execute()
                total_inserted += len(batch)
                logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")

            except Exception as e:
                logger.error(f"Failed to insert fact batch: {e}")

        logger.info(f"Total fact records inserted: {total_inserted}")
        return total_inserted

    def ingest_all(self, csv_path: Path = BENCHMARK_CSV) -> None:
        """
        Run complete ingestion pipeline.

        Args:
            csv_path: Path to CSV file
        """
        logger.info("=" * 80)
        logger.info("Starting Supabase ingestion")
        logger.info("=" * 80)

        # Load data
        df = self.load_csv(csv_path)

        # Ingest raw data
        raw_count = self.ingest_raw_data(df)

        # Populate dimensions
        company_mapping = self.populate_dim_company(df)
        location_mapping = self.populate_dim_location(df)

        # Populate fact table
        fact_count = self.populate_fact_efficiency(df, company_mapping, location_mapping)

        logger.info("=" * 80)
        logger.info("Ingestion Summary:")
        logger.info(f"  Raw records: {raw_count}")
        logger.info(f"  Companies: {len(company_mapping)}")
        logger.info(f"  Locations: {len(location_mapping)}")
        logger.info(f"  Fact records: {fact_count}")
        logger.info("=" * 80)


def main():
    """Run Supabase ingestion."""
    try:
        ingestor = SupabaseIngestor()
        ingestor.ingest_all()
        logger.info("✓ Supabase ingestion completed successfully")

    except Exception as e:
        logger.error(f"✗ Supabase ingestion failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
