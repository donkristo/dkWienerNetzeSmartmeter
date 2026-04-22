"""Tests for the statistics importer."""
import logging
from datetime import datetime, timezone

import pytest

from custom_components.wnsm.importer import Importer


@pytest.mark.parametrize("bewegungsdaten", [{}, {"unitOfMeasurement": ""}])
def test_unit_factor_defaults_missing_unit_to_kwh(bewegungsdaten, caplog):
    """Missing bewegungsdaten unit metadata should not crash import."""
    caplog.set_level(logging.WARNING)

    assert Importer._unit_factor(bewegungsdaten) == 1.0
    assert "assuming KWH" in caplog.text


@pytest.mark.parametrize(
    ("unit", "factor"),
    [
        ("WH", 1e-3),
        ("KWH", 1.0),
        ("kwh", 1.0),
    ],
)
def test_unit_factor_supported_units(unit, factor):
    """Supported WienerNetze energy units are converted to kWh."""
    assert Importer._unit_factor({"unitOfMeasurement": unit}) == factor


def test_unit_factor_rejects_unknown_unit():
    """Unsupported units should still be visible as actionable failures."""
    with pytest.raises(NotImplementedError):
        Importer._unit_factor({"unitOfMeasurement": "MWH"})


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ({"wert": 1.23}, 1.23),
        ({"value": 1.23}, 1.23),
        ({"wert": None, "value": 1.23}, 1.23),
    ],
)
def test_reading_value_accepts_known_api_shapes(value, expected):
    """Consumption values can come from old or current API field names."""
    assert Importer._reading_value(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ({"zeitpunktVon": "2026-04-17T00:00:00Z"}, "2026-04-17T00:00:00Z"),
        ({"timestamp": "2026-04-17T00:00:00Z"}, "2026-04-17T00:00:00Z"),
        ({"zeitVon": "2026-04-17T00:00:00Z"}, "2026-04-17T00:00:00Z"),
    ],
)
def test_reading_timestamp_accepts_known_api_shapes(value, expected):
    """Timestamps can come from old or current API field names."""
    assert Importer._reading_timestamp(value) == expected


def test_statistic_hour_start_clears_sub_hour_fields():
    """Statistics rows are stored on clean hourly boundaries."""
    ts = datetime(2026, 4, 17, 12, 45, 30, 123456, tzinfo=timezone.utc)

    assert Importer._statistic_hour_start(ts) == datetime(2026, 4, 17, 12, tzinfo=timezone.utc)
