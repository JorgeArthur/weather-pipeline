# Weather Pipeline

A small data pipeline that downloads hourly weather data for four cities
(London, Tokyo, New York, Sao Paulo) from the Open-Meteo API and stores it
in a PostgreSQL database.

## How it works

1. **Extract:** `extract.py` calls the API for each city.
2. **Save raw:** the full API response is stored as-is in the table `raw.api_responses`.
3. **Transform:** `transform.py` converts the response into one row per city per hour.
4. **Load:** `load.py` saves those rows in the table `clean.hourly_weather`.

Running the pipeline twice does not create duplicate rows in `clean.hourly_weather`.
The table has a primary key on (city, observed_at), and the load updates a row if
it already exists instead of inserting it again.

## Tech

Python, PostgreSQL, Docker Compose, pytest, Git.

## How to run

You need Docker Desktop, Python 3, and Git.

```bash
git clone https://github.com/JorgeArthur/weather-pipeline.git
cd weather-pipeline

# start the database
docker compose up -d

# set up Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# run the pipeline
python3 src/main.py
```

## Check the result

```bash
docker compose exec db psql -U pipeline -d weather \
  -c "SELECT city, count(*) FROM clean.hourly_weather GROUP BY city;"
```

Run the pipeline again and repeat the query. The counts stay the same.

## Run the tests

```bash
pytest -v
```

## Decisions I made

- **Raw and clean tables:** I keep the original API response, so if my transform
  has a bug I can fix it and reprocess without calling the API again.
- **Timestamps in UTC:** avoids confusion between time zones.
- **Missing values stay empty (NULL):** no measurement is not the same as zero rain.
- **If one city fails:** the error is logged, the other cities still run, and the
  script exits with an error code at the end.

## Limitations

- Only the transform step has automated tests.
- There is no scheduler yet. I run it by hand.
- There are no data quality checks yet.
- The raw table grows with every run and is never cleaned up.

## Next steps

- [ ] Add data quality checks
- [ ] Schedule daily runs with Airflow
- [ ] Add tests for the load step