"""
Test suite for regex pattern extraction.
"""

import pytest
from config.regex_patterns import (
    extract_pue,
    extract_wue,
    extract_renewable_percentage,
    extract_capacity,
    extract_rack_count,
    extract_years,
)


class TestPUEExtraction:
    """Test PUE value extraction."""

    def test_standard_pue(self):
        text = "The data center achieved a PUE of 1.09 in 2025."
        results = extract_pue(text)
        assert len(results) > 0
        assert results[0]['value'] == 1.09

    def test_rolling_ttm_pue(self):
        text = "Rolling twelve-month PUE reached 1.10."
        results = extract_pue(text)
        assert len(results) > 0
        assert results[0]['type'] == 'TTM'

    def test_design_pue(self):
        text = "Designed with a PUE of 1.40."
        results = extract_pue(text)
        assert len(results) > 0
        assert results[0]['type'] == 'design'

    def test_operating_pue(self):
        text = "Operating PUE is 1.45."
        results = extract_pue(text)
        assert len(results) > 0
        assert results[0]['type'] == 'operating'

    def test_pue_with_year(self):
        text = "In 2024, the PUE was 1.12."
        results = extract_pue(text)
        assert len(results) > 0
        assert results[0]['value'] == 1.12
        assert results[0]['year'] == 2024

    def test_invalid_pue(self):
        text = "The PUE is 0.5."  # Invalid: below 1.0
        results = extract_pue(text)
        assert len(results) == 0

    def test_multiple_pue(self):
        text = "Design PUE is 1.30 while operating PUE is 1.45."
        results = extract_pue(text)
        assert len(results) >= 2


class TestWUEExtraction:
    """Test WUE value extraction."""

    def test_standard_wue(self):
        text = "Water Usage Effectiveness is 0.18 L/kWh."
        results = extract_wue(text)
        assert len(results) > 0
        assert results[0] == 0.18

    def test_wue_with_liters(self):
        text = "The facility uses 1.2 liters per kWh."
        results = extract_wue(text)
        assert len(results) > 0

    def test_no_wue(self):
        text = "No water usage data available."
        results = extract_wue(text)
        assert len(results) == 0


class TestRenewableExtraction:
    """Test renewable energy percentage extraction."""

    def test_percentage_renewable(self):
        text = "We matched 100% of electricity with renewable energy."
        results = extract_renewable_percentage(text)
        assert 100 in results

    def test_partial_renewable(self):
        text = "The facility operates on 65% renewable energy."
        results = extract_renewable_percentage(text)
        assert 65 in results

    def test_carbon_free(self):
        text = "Achieved 90% carbon-free energy."
        results = extract_renewable_percentage(text)
        assert 90 in results

    def test_no_renewable(self):
        text = "No renewable energy information."
        results = extract_renewable_percentage(text)
        assert len(results) == 0


class TestCapacityExtraction:
    """Test capacity extraction."""

    def test_mw_capacity(self):
        text = "The data center has a capacity of 50 MW."
        results = extract_capacity(text)
        assert 50.0 in results

    def test_decimal_capacity(self):
        text = "Capacity is 12.5 MW."
        results = extract_capacity(text)
        assert 12.5 in results

    def test_no_capacity(self):
        text = "No capacity information."
        results = extract_capacity(text)
        assert len(results) == 0


class TestRackCountExtraction:
    """Test rack count extraction."""

    def test_rack_count(self):
        text = "The facility has 7200 racks."
        results = extract_rack_count(text)
        assert 7200 in results

    def test_rack_count_with_comma(self):
        text = "Capacity of 5,000 server racks."
        results = extract_rack_count(text)
        assert 5000 in results


class TestYearExtraction:
    """Test year extraction."""

    def test_single_year(self):
        text = "In 2024, the facility opened."
        results = extract_years(text)
        assert 2024 in results

    def test_multiple_years(self):
        text = "Data from 2023 and 2024."
        results = extract_years(text)
        assert 2023 in results
        assert 2024 in results

    def test_invalid_year(self):
        text = "In 1999, something happened."  # Too old
        results = extract_years(text)
        # Should filter out years before 2000
        assert 1999 not in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
