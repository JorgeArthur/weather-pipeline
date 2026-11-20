#!/bin/bash
PSQL="docker compose exec -T db psql -U pipeline -d weather -t -A -c"

echo "count before:"
$PSQL "SELECT count(*) FROM clean.hourly_weather;"

.venv/bin/python src/main.py
echo "exit code: $?"

echo "count after:"
$PSQL "SELECT count(*) FROM clean.hourly_weather;"