#!/bin/bash
# Autonomous Daemon Startup Script
# Starts the daemon with proper error handling and logging

WORKSPACE="$HOME/clawd"
DAEMON_SCRIPT="$WORKSPACE/scripts/autonomous_daemon.py"
PID_FILE="$WORKSPACE/daemon.pid"
LOG_FILE="$WORKSPACE/logs/daemon_startup.log"

# Ensure log directory exists
mkdir -p "$WORKSPACE/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        log "Daemon already running (PID: $OLD_PID)"
        exit 0
    else
        log "Stale PID file found, removing"
        rm "$PID_FILE"
    fi
fi

# No dependencies needed - using standard library only

# Start daemon
log "Starting autonomous daemon..."
nohup python3 "$DAEMON_SCRIPT" >> "$LOG_FILE" 2>&1 &
DAEMON_PID=$!

# Save PID
echo "$DAEMON_PID" > "$PID_FILE"

# Verify it started
sleep 2
if ps -p "$DAEMON_PID" > /dev/null 2>&1; then
    log "Daemon started successfully (PID: $DAEMON_PID)"
    exit 0
else
    log "ERROR: Daemon failed to start"
    rm "$PID_FILE"
    exit 1
fi
