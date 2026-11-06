from datetime import datetime, timezone

from transform import transform_hourly

SAMPLE = {
    "hourly": {
        "time": ["2026-11-05T00:00", "2026-11-05T01:00"],
        "temperature_2m": [8.1, None],
        "precipitation": [0.0, 0.2],
        "wind_speed_10m": [12.3, 14.0],
    }
}


def test_one_row_per_hour():
    rows = transform_hourly("london", SAMPLE)
    assert len(rows) == 2


def test_fields_are_mapped_and_typed():
    row = transform_hourly("london", SAMPLE)[0]
    assert row["city"] == "london"
    assert row["observed_at"] == datetime(2026, 11, 5, 0, 0, tzinfo=timezone.utc)
    assert row["temperature_c"] == 8.1
    assert row["precipitation_mm"] == 0.0
    assert row["wind_speed_kmh"] == 12.3


def test_null_values_are_preserved_as_none():
    row = transform_hourly("london", SAMPLE)[1]
    assert row["temperature_c"] is None