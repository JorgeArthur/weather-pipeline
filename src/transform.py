from datetime import datetime, timezone


def transform_hourly(city: str, payload: dict) -> list[dict]:
    hourly = payload["hourly"]
    rows = []

    for t, temp, precip, wind in zip(
        hourly["time"],
        hourly["temperature_2m"],
        hourly["precipitation"],
        hourly["wind_speed_10m"],
    ):
        row = {
            "city": city,
            "observed_at": datetime.fromisoformat(t).replace(tzinfo=timezone.utc),
            "temperature_c": temp,
            "precipitation_mm": precip,
            "wind_speed_kmh": wind,
        }
        rows.append(row)

    return rows