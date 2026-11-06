import os
import psycopg
from psycopg.types.json import Jsonb


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "weather"),
        user=os.getenv("DB_USER", "pipeline"),
        password=os.getenv("DB_PASSWORD", "pipeline"),
    )


def load_raw(city: str, payload: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO raw.api_responses (city, payload) VALUES (%s, %s)",
            (city, Jsonb(payload)),
        )

def load_clean(rows: list[dict]) -> int:
    sql = """
        INSERT INTO clean.hourly_weather
            (city, observed_at, temperature_c, precipitation_mm, wind_speed_kmh)
        VALUES
            (%(city)s, %(observed_at)s, %(temperature_c)s,
             %(precipitation_mm)s, %(wind_speed_kmh)s)
        ON CONFLICT (city, observed_at) DO UPDATE SET
            temperature_c    = EXCLUDED.temperature_c,
            precipitation_mm = EXCLUDED.precipitation_mm,
            wind_speed_kmh   = EXCLUDED.wind_speed_kmh,
            loaded_at        = now()
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)
    return len(rows)