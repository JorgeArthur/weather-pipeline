#!/bin/bash
cd "$(dirname "$0")" || exit 1
mkdir -p logs
echo "=== run started $(date) ===" >> logs/pipeline.log
.venv/bin/python src/main.py >> logs/pipeline.log 2>&1
status=$?
echo "=== run finished with exit code $status ===" >> logs/pipeline.log
exit $status