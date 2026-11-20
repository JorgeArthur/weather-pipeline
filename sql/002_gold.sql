CREATE OR REPLACE VIEW gold.daily_weather AS
SELECT
    city,
    (observed_at AT TIME ZONE 'UTC')::date   AS day_utc,
    round(avg(temperature_c), 1)             AS avg_temp_c,
    min(temperature_c)                       AS min_temp_c,
    max(temperature_c)                       AS max_temp_c,
    round(sum(precipitation_mm), 1)          AS total_precip_mm,
    count(*)                                 AS hours_reported
FROM silver.hourly_weather
GROUP BY city, (observed_at AT TIME ZONE 'UTC')::date;

CREATE OR REPLACE VIEW gold.latest_by_city AS
SELECT city, observed_at, temperature_c, precipitation_mm, wind_speed_kmh
FROM (
    SELECT
        city, observed_at, temperature_c, precipitation_mm, wind_speed_kmh,
        ROW_NUMBER() OVER (PARTITION BY city ORDER BY observed_at DESC) AS rn
    FROM silver.hourly_weather
    WHERE observed_at <= now()
) ranked
WHERE rn = 1;