# Weather Pipeline

A small data pipeline that downloads hourly weather data for four cities
(London, Tokyo, New York, Sao Paulo) from the Open-Meteo API and stores it
in PostgreSQL using a bronze, silver, and gold layout.

## How it works

1. **Extract:** `extract.py` calls the API for each city.
2. **Bronze:** the full API response is stored as-is in `bronze.api_responses`.
3. **Transform:** `transform.py` converts the response into one row per city per hour.
4. **Validate:** `validate.py` checks the rows before loading (see "Data quality rules").
5. **Silver:** `load.py` saves the rows in `silver.hourly_weather`.
6. **Gold:** two views for analysts, `gold.daily_weather` and `gold.latest_by_city`.

Running the pipeline twice does not create duplicate rows in `silver.hourly_weather`.
The table has a primary key on (city, observed_at), and the load updates a row if
it already exists instead of inserting it again.

## Data quality rules

Before loading to silver, each city's rows are checked:

- Temperature must be between -90 and 60 degrees Celsius.
- Precipitation and wind speed must not be negative.
- Missing values (NULL) are allowed and are not treated as zero.

If any rule fails, that city is not loaded, the error is logged, and the
pipeline exits with code 1. The raw data is still saved in bronze.

## Tech

Python, PostgreSQL, Docker Compose, pytest, Git, cron.

## How to run

You need Docker Desktop, Python 3, and Git.

```bash
git clone https://github.com/JorgeArthur/weather-pipeline.git
cd weather-pipeline

# start the database (creates the schemas and tables on first start)
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
bash check.sh
```

It prints the row count of `silver.hourly_weather`, runs the pipeline, prints the
exit code, and prints the count again. Run it twice in a row: the two counts match.

To look at the gold views:

```bash
docker compose exec db psql -U pipeline -d weather \
  -c "SELECT * FROM gold.daily_weather ORDER BY city, day_utc;"
```

## Run the tests

```bash
pytest -v
```

## Scheduling

`run_pipeline.sh` runs the pipeline and appends its output to `logs/pipeline.log`.
It is scheduled with cron (daily at 11:00 local time):

```
0 11 * * * /path/to/weather-pipeline/run_pipeline.sh
```

## Decisions I made

- **Bronze, silver, gold:** I keep the original API response, so if my transform
  has a bug I can fix it and reprocess without calling the API again.
- **Timestamps in UTC:** avoids confusion between time zones.
- **Missing values stay empty (NULL):** no measurement is not the same as zero rain.
- **If one city fails:** the error is logged, the other cities still run, and the
  script exits with an error code at the end.
- **Validation before loading silver:** bad data stops at the door, but the raw copy is kept.

## Limitations

- Only the transform and validation steps have automated tests. The load steps are
  checked by hand with `check.sh`.
- The schedule only runs while my computer is on and Docker is running.
- Days before the schedule was set up were not backfilled.
- The API returns yesterday and today (UTC), so hours later than now are forecasts.
- The bronze table grows with every run and is never cleaned up.

## Next steps

- [ ] Add a row count check per city
- [ ] Add a table that records every run
- [ ] Run the tests automatically on GitHub