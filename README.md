Weather Pipeline

A batch ETL pipeline that pulls hourly weather data for four cities from the Open-Meteo API, stores the raw responses in PostgreSQL, and loads a cleaned, deduplicated table. Rerunning it is safe: it never creates duplicate rows.

Architecture
Open-Meteo API
      |
      v
  extract.py   (HTTP requests with retries)
      |
      +--> raw.api_responses      (unmodified JSON, append-only)
      |
      v
  transform.py (parallel arrays -> one row per city per hour, typed, UTC)
      |
      v
  load.py      (upsert)
      |
      v
  clean.hourly_weather            (one row per city per hour)
Tech stack
Python 3.11+ (requests, psycopg v3)
PostgreSQL 16 (Docker)
Docker Compose
pytest
Git
Project structure
weather-pipeline/
├── docker-compose.yml     # Postgres container, runs sql/ on first start
├── pytest.ini             # tells pytest to look for modules in src/
├── requirements.txt
├── sql/
│   └── 001_schema.sql     # raw and clean schemas and tables
├── src/
│   ├── extract.py         # API calls, retry logic, city list
│   ├── transform.py       # JSON payload -> list of row dicts
│   ├── load.py            # DB connection, raw insert, clean upsert
│   └── main.py            # entry point, runs all cities
└── tests/
    └── test_transform.py
How to run

Prerequisites: Docker Desktop, Python 3.11+, Git.

bash
git clone https://github.com/JorgeArthur/weather-pipeline.git
cd weather-pipeline

# 1. Start the database (creates the schemas and tables on first start)
docker compose up -d

# 2. Create a virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Run the pipeline
python3 src/main.py

Database connection settings are read from environment variables, with defaults that match docker-compose.yml:

Variable	Default
DB_HOST	localhost
DB_PORT	5432
DB_NAME	weather
DB_USER	pipeline
DB_PASSWORD	pipeline

The defaults are for local development only.

Verifying it works

Check the clean table:

bash
docker compose exec db psql -U pipeline -d weather \
  -c "SELECT city, count(*), min(observed_at), max(observed_at) FROM clean.hourly_weather GROUP BY city;"

Run the pipeline a second time and repeat the query. The counts in clean.hourly_weather do not change. The row count in raw.api_responses grows by one per city per run, by design.

Run the tests:

bash
pytest -v
Design decisions

Two layers (raw and clean). The raw table keeps the exact API response as JSONB. If a bug is found in the transform, the data can be reprocessed from raw without calling the API again.

Idempotent loads. clean.hourly_weather has a composite primary key on (city, observed_at), and the load uses INSERT ... ON CONFLICT DO UPDATE. Running the pipeline twice produces the same table as running it once. The update also means that forecast values are replaced when the API later returns revised data for the same hour.

Timestamps in UTC. The API is requested with timezone=UTC, parsed into timezone-aware datetimes, and stored as TIMESTAMPTZ.

Nulls are preserved. If the API returns no measurement for an hour, the value is stored as NULL, not 0. "No measurement" and "zero rainfall" are different facts.

Partial failure policy. If one city fails (network error, bad response), the pipeline logs the full error, continues with the remaining cities, and exits with code 1 at the end. A scheduler can detect the failure from the exit code, while one bad city does not block the others.

Retries. HTTP calls retry up to 3 times with backoff on rate-limit and server errors (429, 500, 502, 503, 504).

Known limitations
Only the transform step has automated tests. The extract and load steps are verified manually (see "Verifying it works").
There is no scheduler yet. The pipeline runs when started by hand.
There are no data quality checks yet (null rate, range checks, freshness).
The request window is the previous day plus the next day (48 hours per city), so each run overlaps with the previous one. This overlap is handled by the upsert.
Database credentials are local development defaults.

 Schedule daily runs with Apache Airflow
 Add data quality checks that stop the pipeline on bad data
 Add tests for the load step against a temporary database
 Add a star-schema model on top of the clean table