#!/bin/bash

################################################################################
# Automated Git Backup System
# 
# Purpose: Automatically commits and pushes changes to GitHub every hour
# Location: ~/clawd/scripts/auto-backup.sh
# Runs via: cron (0 * * * *)
# 
# What it does:
# - Checks for uncommitted changes in workspace
# - Commits with timestamp
# - Pushes to GitHub (origin/main)
# - Logs all activity
# 
# Benefits:
# - Never lose more than 1 hour of work
# - Full Git history on GitHub
# - Zero manual effort
# - Peace of mind
################################################################################

# Configuration
WORKSPACE="$HOME/clawd"
LOG_FILE="$WORKSPACE/logs/auto-backup.log"
MAX_LOG_SIZE=5242880  # 5MB - rotate log when larger

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Log function with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Rotate log file if too large
rotate_log_if_needed() {
    if [ -f "$LOG_FILE" ]; then
        LOG_SIZE=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null)
        if [ "$LOG_SIZE" -gt "$MAX_LOG_SIZE" ]; then
            mv "$LOG_FILE" "$LOG_FILE.old"
            log "Log rotated (size: $LOG_SIZE bytes)"
        fi
    fi
}

# Change to workspace directory
cd "$WORKSPACE" || {
    log "❌ ERROR: Cannot access workspace directory: $WORKSPACE"
    exit 1
}

log "🔍 Starting auto-backup check..."

# Check if this is a git repository
if [ ! -d ".git" ]; then
    log "❌ ERROR: Not a git repository. Initialize with: git init"
    exit 1
fi

# Check for changes (including untracked files)
if [[ -n $(git status -s) ]]; then
    log "📝 Changes detected, starting backup..."
    
    # Get change summary for log
    CHANGES=$(git status -s | wc -l | tr -d ' ')
    log "   Files changed: $CHANGES"
    
    # Add all changes (tracked and untracked)
    git add . >> "$LOG_FILE" 2>&1
    
    if [ $? -ne 0 ]; then
        log "❌ ERROR: 'git add' failed"
        exit 1
    fi
    
    # Create commit with timestamp
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    COMMIT_MSG="Auto-backup: $TIMESTAMP"
    
    git commit -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "✅ Changes committed successfully"
        
        # Push to GitHub
        log "📤 Pushing to GitHub..."
        git push origin main >> "$LOG_FILE" 2>&1
        
        if [ $? -eq 0 ]; then
            log "✅ Pushed to GitHub successfully"
            log "🎉 Backup complete: $CHANGES files backed up"
        else
            log "❌ ERROR: Push failed"
            log "   Possible causes:"
            log "   - No internet connection"
            log "   - Git authentication failed"
            log "   - Remote repository doesn't exist"
            log "   - Branch protection rules"
            
            # Check if remote exists
            git remote -v >> "$LOG_FILE" 2>&1
            
            # Attempt to fetch to test connectivity
            git fetch origin --dry-run >> "$LOG_FILE" 2>&1
            
            exit 1
        fi
    else
        log "❌ ERROR: Commit failed"
        log "   Possible causes:"
        log "   - Git user.name or user.email not configured"
        log "   - Files conflict"
        
        # Show git config
        log "   Current git config:"
        git config user.name >> "$LOG_FILE" 2>&1
        git config user.email >> "$LOG_FILE" 2>&1
        
        exit 1
    fi
else
    log "ℹ️  No changes to backup"
fi

# Rotate log if needed
rotate_log_if_needed

# Clean up old log files (keep last 10)
LOG_DIR="$(dirname "$LOG_FILE")"
if [ -d "$LOG_DIR" ]; then
    find "$LOG_DIR" -name "auto-backup.log.old*" -type f | sort -r | tail -n +11 | xargs rm -f 2>/dev/null
fi

log "✅ Auto-backup check complete"
log "---"

exit 0
