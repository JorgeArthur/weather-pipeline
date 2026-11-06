CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS clean;

CREATE TABLE raw.api_responses (
    id          BIGSERIAL PRIMARY KEY,
    city        TEXT        NOT NULL,
    fetched_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    payload     JSONB       NOT NULL
);

CREATE TABLE clean.hourly_weather (
    city            TEXT        NOT NULL,
    observed_at     TIMESTAMPTZ NOT NULL,
    temperature_c   NUMERIC(5,2),
    precipitation_mm NUMERIC(6,2),
    wind_speed_kmh  NUMERIC(6,2),
    loaded_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (city, observed_at)
);