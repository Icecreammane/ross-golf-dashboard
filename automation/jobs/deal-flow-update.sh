#!/bin/bash
# Deal Flow Update Job Wrapper
# Updates deal flow pipeline at 9:00am

set -euo pipefail

# Configuration
JOB_NAME="deal-flow-update"
LOG_DIR="$HOME/clawd/logs/cron"
LOG_FILE="$LOG_DIR/${JOB_NAME}-$(date +%Y-%m-%d).log"
TIMEOUT=600  # 10 minutes
SCRIPT="$HOME/clawd/revenue/deal-flow/scraper.py"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Start job
log "=== Deal Flow Update Job Started ==="
log "Script: $SCRIPT"

# Check if script exists
if [[ ! -f "$SCRIPT" ]]; then
    log "ERROR: Script not found: $SCRIPT"
    exit 1
fi

# Set environment variables
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:$PATH"
export PYTHONUNBUFFERED=1

# Change to script directory
cd "$(dirname "$SCRIPT")"

# Run with timeout
log "Executing deal flow scraper..."
if timeout "$TIMEOUT" python3 "$SCRIPT" >> "$LOG_FILE" 2>&1; then
    log "SUCCESS: Deal flow update completed"
    exit 0
else
    EXIT_CODE=$?
    if [[ $EXIT_CODE -eq 124 ]]; then
        log "ERROR: Job timed out after ${TIMEOUT}s"
    else
        log "ERROR: Job failed with exit code $EXIT_CODE"
    fi
    exit $EXIT_CODE
fi
