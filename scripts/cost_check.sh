#!/bin/bash
# Quick cost check commands

case "$1" in
  today)
    python3 ~/clawd/scripts/cost_tracker.py daily
    ;;
  month)
    python3 ~/clawd/scripts/cost_tracker.py monthly
    ;;
  week)
    # Get last 7 days
    echo "Last 7 days cost summary:"
    for i in {0..6}; do
      date=$(date -v-${i}d +%Y-%m-%d)
      python3 ~/clawd/scripts/cost_tracker.py daily "$date" 2>/dev/null | jq -r '"\(.date): $\(.total_cost)"'
    done
    ;;
  *)
    echo "Usage: bash cost_check.sh {today|month|week}"
    exit 1
    ;;
esac
