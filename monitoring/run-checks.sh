#!/bin/bash
# Monitoring check wrapper - runs all monitors and sends alerts if needed
# Usage: ./run-checks.sh [--force]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Log start
echo "[$(date -Iseconds)] Starting monitoring checks" >> logs/alerts.log

# Check current time - skip during concert (7pm-midnight)
HOUR=$(date +%H)
if [ "$1" != "--force" ] && [ $HOUR -ge 19 ]; then
    echo "[$(date -Iseconds)] Skipping check during concert hours (19:00-00:00)" >> logs/alerts.log
    exit 0
fi

# Run the aggregator (it will call individual monitors)
python3 send-alerts.py >> logs/alerts.log 2>&1

echo "[$(date -Iseconds)] Monitoring checks complete" >> logs/alerts.log
