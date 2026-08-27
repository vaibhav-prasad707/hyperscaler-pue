"""
Test suite for pipeline ingestion.
"""

import pytest
import pandas as pd
from pathlib import Path


class TestPipelineIntegration:
    """Integration tests for data pipeline."""

    def test_csv_structure(self):
        """Test that benchmark CSV has required columns."""
        required_columns = [
            'company',
            'pue_value',
            'tier',
            'city',
            'country',
            'year',
            'pue_type',
        ]

        # This test would run after data collection
        # For now, it's a template
        csv_path = Path(__file__).parent.parent / 'data' / 'processed' / 'pue_benchmark.csv'

        if csv_path.exists():
            df = pd.read_csv(csv_path)

            for col in required_columns:
                assert col in df.columns, f"Missing required column: {col}"

            assert len(df) > 0, "CSV is empty"

    def test_data_quality(self):
        """Test data quality in final CSV."""
        csv_path = Path(__file__).parent.parent / 'data' / 'processed' / 'pue_benchmark.csv'

        if csv_path.exists():
            df = pd.read_csv(csv_path)

            # All PUE values should be valid
            assert df['pue_value'].min() >= 1.0
            assert df['pue_value'].max() <= 3.0

            # No missing companies
            assert df['company'].notna().all()

            # Year should be reasonable
            assert df['year'].min() >= 2000
            assert df['year'].max() <= 2030


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
