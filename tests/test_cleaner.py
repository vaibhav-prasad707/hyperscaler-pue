"""
Test suite for data cleaner functionality.
"""

import pytest
import pandas as pd
from datetime import datetime

from utils.validation import DataValidator, deduplicate_records
from config.constants import PUE_MIN, PUE_MAX


class TestDataValidator:
    """Test data validation functions."""

    def test_validate_pue_valid(self):
        assert DataValidator.validate_pue(1.09) == True
        assert DataValidator.validate_pue(1.50) == True
        assert DataValidator.validate_pue(2.00) == True

    def test_validate_pue_invalid(self):
        assert DataValidator.validate_pue(0.5) == False
        assert DataValidator.validate_pue(3.5) == False
        assert DataValidator.validate_pue(None) == False

    def test_validate_renewable_pct(self):
        assert DataValidator.validate_renewable_pct(0) == True
        assert DataValidator.validate_renewable_pct(50) == True
        assert DataValidator.validate_renewable_pct(100) == True
        assert DataValidator.validate_renewable_pct(150) == False
        assert DataValidator.validate_renewable_pct(-10) == False

    def test_validate_capacity(self):
        assert DataValidator.validate_capacity(10.0) == True
        assert DataValidator.validate_capacity(100.0) == True
        assert DataValidator.validate_capacity(None) == True  # Optional
        assert DataValidator.validate_capacity(-5.0) == False
        assert DataValidator.validate_capacity(1000.0) == False  # Too high

    def test_validate_year(self):
        current_year = datetime.now().year
        assert DataValidator.validate_year(current_year) == True
        assert DataValidator.validate_year(2020) == True
        assert DataValidator.validate_year(1999) == False
        assert DataValidator.validate_year(current_year + 2) == False

    def test_validate_record_valid(self):
        record = {
            'company': 'Google',
            'pue_value': 1.09,
            'year': 2024,
            'renewable_pct': 100,
        }
        is_valid, errors = DataValidator.validate_record(record)
        assert is_valid == True
        assert len(errors) == 0

    def test_validate_record_missing_required(self):
        record = {
            'company': 'Google',
            # Missing pue_value
        }
        is_valid, errors = DataValidator.validate_record(record)
        assert is_valid == False
        assert len(errors) > 0

    def test_validate_record_invalid_pue(self):
        record = {
            'company': 'Google',
            'pue_value': 0.5,  # Invalid
        }
        is_valid, errors = DataValidator.validate_record(record)
        assert is_valid == False


class TestDeduplication:
    """Test deduplication logic."""

    def test_deduplicate_simple(self):
        df = pd.DataFrame([
            {'company': 'Google', 'facility_name': 'DC1', 'city': 'Virginia', 'pue_value': 1.10, 'year': 2024},
            {'company': 'Google', 'facility_name': 'DC1', 'city': 'Virginia', 'pue_value': 1.15, 'year': 2023},
        ])

        result = deduplicate_records(df, keep='newest')
        assert len(result) == 1
        assert result.iloc[0]['year'] == 2024  # Keeps newest

    def test_deduplicate_different_facilities(self):
        df = pd.DataFrame([
            {'company': 'Google', 'facility_name': 'DC1', 'city': 'Virginia', 'pue_value': 1.10},
            {'company': 'Google', 'facility_name': 'DC2', 'city': 'Oregon', 'pue_value': 1.12},
        ])

        result = deduplicate_records(df)
        assert len(result) == 2  # Different facilities

    def test_deduplicate_no_duplicates(self):
        df = pd.DataFrame([
            {'company': 'Google', 'facility_name': 'DC1', 'city': 'Virginia', 'pue_value': 1.10},
            {'company': 'AWS', 'facility_name': 'DC1', 'city': 'Virginia', 'pue_value': 1.15},
        ])

        result = deduplicate_records(df)
        assert len(result) == 2


class TestDerivedMetrics:
    """Test calculated metrics."""

    def test_cooling_overhead(self):
        from utils.validation import calculate_derived_metrics

        df = pd.DataFrame([
            {'pue_value': 1.50, 'capacity_mw': 10.0},
            {'pue_value': 1.20, 'capacity_mw': 20.0},
        ])

        result = calculate_derived_metrics(df)

        assert 'cooling_overhead_pct' in result.columns
        assert result.iloc[0]['cooling_overhead_pct'] == pytest.approx(50.0)
        assert result.iloc[1]['cooling_overhead_pct'] == pytest.approx(20.0)

    def test_annual_waste(self):
        from utils.validation import calculate_derived_metrics

        df = pd.DataFrame([
            {'pue_value': 1.50, 'capacity_mw': 10.0},
        ])

        result = calculate_derived_metrics(df)

        assert 'annual_waste_mwh' in result.columns
        # (1.5 - 1.0) * 10 * 8760 = 43800
        assert result.iloc[0]['annual_waste_mwh'] == pytest.approx(43800.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
