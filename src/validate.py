def find_bad_temperatures(rows: list[dict], low: float = -90, high: float = 60) -> list[dict]:
    bad = []
    for row in rows:
        temp = row["temperature_c"]
        if temp is None:
            continue
        if temp < low or temp > high:
            bad.append(row)
    return bad


def validate_rows(rows: list[dict]) -> None:
    problems = []

    bad_temps = find_bad_temperatures(rows)
    if bad_temps:
        problems.append(f"{len(bad_temps)} rows with impossible temperature, first: {bad_temps[0]}")

    bad_rain = find_negative_values(rows, "precipitation_mm")
    if bad_rain:
        problems.append(f"{len(bad_rain)} rows with negative precipitation, first: {bad_rain[0]}")

    bad_wind = find_negative_values(rows, "wind_speed_kmh")
    if bad_wind:
        problems.append(f"{len(bad_wind)} rows with negative wind speed, first: {bad_wind[0]}")

    if problems:
        raise ValueError("; ".join(problems))


def find_negative_values(rows: list[dict], field: str) -> list[dict]:
    bad = []
    for row in rows:
        value = row.get(field)
        if value is None:
            continue
        if value < 0:
            bad.append(row)
    return bad