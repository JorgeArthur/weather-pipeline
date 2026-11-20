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
    bad = find_bad_temperatures(rows)
    if bad:
        raise ValueError(f"{len(bad)} rows with impossible temperature, first: {bad[0]}")