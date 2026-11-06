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