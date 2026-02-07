#!/bin/bash
# System Health Check Job Wrapper
# Runs health diagnostics at 12:00pm

set -euo pipefail

# Configuration
JOB_NAME="health-check"
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
log "=== System Health Check Started ==="

# Check disk space
log "Checking disk space..."
df -h / | tail -1 | awk '{print "Disk usage: " $5 " used"}' >> "$LOG_FILE"

# Check memory
log "Checking memory..."
vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages free:\s+(\d+)/ and printf("Memory free: %.2f GB\n", $1 * $size / 1073741824);' >> "$LOG_FILE"

# Check load average
log "Checking load average..."
uptime | awk -F'load averages:' '{print "Load: " $2}' >> "$LOG_FILE"

# Check Clawdbot process
log "Checking Clawdbot status..."
if pgrep -f "clawdbot" > /dev/null; then
    log "Clawdbot: Running"
else
    log "WARNING: Clawdbot process not found"
fi

# Check log directory size
LOG_SIZE=$(du -sh "$LOG_DIR" 2>/dev/null | awk '{print $1}')
log "Log directory size: $LOG_SIZE"

# Clean old logs (keep last 30 days)
log "Cleaning old logs..."
find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true
log "Old logs cleaned"

log "SUCCESS: Health check completed"
