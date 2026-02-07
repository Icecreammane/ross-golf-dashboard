#!/bin/bash
###############################################################################
# NBA Top 50 Rankings Update Script
# One-command refresh: Pulls latest data + recalculates + exports
###############################################################################

set -e  # Exit on error

NBA_DIR="/Users/clawdbot/clawd/nba"
LOG_FILE="$NBA_DIR/update.log"
TIMESTAMP=$(date '+%Y-%m-%d %I:%M:%S %p CST')

echo "========================================" | tee -a "$LOG_FILE"
echo "🏀 NBA Top 50 Rankings Update" | tee -a "$LOG_FILE"
echo "Started: $TIMESTAMP" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Navigate to NBA directory
cd "$NBA_DIR"

# Run the rankings generator
echo "📊 Generating rankings..." | tee -a "$LOG_FILE"
python3 rank_generator_v3.py 2>&1 | tee -a "$LOG_FILE"

# Check if files were generated
if [ -f "rankings.json" ] && [ -f "rankings.csv" ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "✅ Update successful!" | tee -a "$LOG_FILE"
    
    # Show file sizes
    JSON_SIZE=$(ls -lh rankings.json | awk '{print $5}')
    CSV_SIZE=$(ls -lh rankings.csv | awk '{print $5}')
    echo "   rankings.json: $JSON_SIZE" | tee -a "$LOG_FILE"
    echo "   rankings.csv: $CSV_SIZE" | tee -a "$LOG_FILE"
    
    # Show top 5 players
    echo "" | tee -a "$LOG_FILE"
    echo "Top 5 Players:" | tee -a "$LOG_FILE"
    head -6 rankings.csv | tail -5 | awk -F',' '{printf "  %s. %s (%s) - %s FP\n", $1, $2, $3, $7}' | tee -a "$LOG_FILE"
    
    # Count trade-impacted players
    TRADE_COUNT=$(grep -c -E "HIGH|MED|LOW" rankings.csv || true)
    echo "" | tee -a "$LOG_FILE"
    echo "Trade-impacted players: $TRADE_COUNT" | tee -a "$LOG_FILE"
    
else
    echo "" | tee -a "$LOG_FILE"
    echo "❌ Update failed - output files not generated" | tee -a "$LOG_FILE"
    exit 1
fi

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Completed: $(date '+%Y-%m-%d %I:%M:%S %p CST')" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Optional: Open CSV in default viewer (commented out by default)
# open rankings.csv

exit 0
