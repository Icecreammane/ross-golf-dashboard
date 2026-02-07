#!/bin/bash
# Evening Check-in Job Wrapper
# Triggers evening check-in at 8:00pm

set -euo pipefail

# Configuration
JOB_NAME="evening-checkin"
LOG_DIR="$HOME/clawd/logs/cron"
LOG_FILE="$LOG_DIR/${JOB_NAME}-$(date +%Y-%m-%d).log"
TIMEOUT=60  # 1 minute

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Start job
log "=== Evening Check-in Job Started ==="

# Create a flag file that the main agent can check during heartbeat
CHECKIN_FLAG="$HOME/clawd/tmp/evening-checkin-pending"
mkdir -p "$(dirname "$CHECKIN_FLAG")"

log "Creating evening check-in flag..."
echo "$(date '+%Y-%m-%d %H:%M:%S')" > "$CHECKIN_FLAG"

log "Evening check-in flag created at: $CHECKIN_FLAG"
log "Main agent will process during next heartbeat"
log "SUCCESS: Evening check-in trigger completed"
