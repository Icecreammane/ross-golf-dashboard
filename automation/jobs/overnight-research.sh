#!/bin/bash
# Overnight Builds & Research Job Wrapper
# Runs maintenance tasks at 11:00pm

set -euo pipefail

# Configuration
JOB_NAME="overnight-research"
LOG_DIR="$HOME/clawd/logs/cron"
LOG_FILE="$LOG_DIR/${JOB_NAME}-$(date +%Y-%m-%d).log"
TIMEOUT=1800  # 30 minutes

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Start job
log "=== Overnight Research & Maintenance Started ==="

# Git status check
log "Checking git status..."
cd "$HOME/clawd"
if git status --porcelain | grep -q '^'; then
    log "Uncommitted changes found:"
    git status --short >> "$LOG_FILE"
else
    log "No uncommitted changes"
fi

# Pull latest changes
log "Pulling latest changes..."
if git pull >> "$LOG_FILE" 2>&1; then
    log "Git pull successful"
else
    log "WARNING: Git pull failed"
fi

# Create overnight research flag for main agent
RESEARCH_FLAG="$HOME/clawd/tmp/overnight-research-pending"
mkdir -p "$(dirname "$RESEARCH_FLAG")"
echo "$(date '+%Y-%m-%d %H:%M:%S')" > "$RESEARCH_FLAG"
log "Created research flag for main agent"

# Clean up temp files
log "Cleaning temporary files..."
find "$HOME/clawd/tmp" -name "*.tmp" -mtime +1 -delete 2>/dev/null || true
log "Temp files cleaned"

# Archive old memory files (>90 days)
log "Archiving old memory files..."
ARCHIVE_DIR="$HOME/clawd/memory/archive"
mkdir -p "$ARCHIVE_DIR"
find "$HOME/clawd/memory" -maxdepth 1 -name "20*.md" -mtime +90 -exec mv {} "$ARCHIVE_DIR/" \; 2>/dev/null || true
log "Old memory files archived"

log "SUCCESS: Overnight maintenance completed"
