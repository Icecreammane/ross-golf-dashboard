#!/bin/bash
# NBA Rankings Update Job Wrapper
# Refreshes NBA Top 50 rankings at 10:00am (on game days)

set -euo pipefail

# Configuration
JOB_NAME="nba-update"
LOG_DIR="$HOME/clawd/logs/cron"
LOG_FILE="$LOG_DIR/${JOB_NAME}-$(date +%Y-%m-%d).log"
TIMEOUT=300  # 5 minutes
SCRIPT="$HOME/clawd/nba/update_top_50.sh"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Start job
log "=== NBA Rankings Update Job Started ==="
log "Script: $SCRIPT"

# Check if script exists
if [[ ! -f "$SCRIPT" ]]; then
    log "ERROR: Script not found: $SCRIPT"
    exit 1
fi

# Set environment variables
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:$PATH"

# Change to script directory
cd "$(dirname "$SCRIPT")"

# Run with timeout
log "Executing NBA rankings update..."
if timeout "$TIMEOUT" bash "$SCRIPT" >> "$LOG_FILE" 2>&1; then
    log "SUCCESS: NBA rankings update completed"
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
