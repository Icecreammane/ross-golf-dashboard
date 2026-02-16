#!/bin/bash
# Daily Automation Runner
# Orchestrates morning brief + job applications + background tasks

WORKSPACE="$HOME/clawd"
cd "$WORKSPACE" || exit 1

LOG_FILE="$WORKSPACE/logs/daily-automation.log"
mkdir -p "$WORKSPACE/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "============================================================"
log "🚀 Daily Automation - Starting"
log "============================================================"

# 1. Generate Morning Brief
log "🌅 Generating morning brief..."
python3 "$WORKSPACE/scripts/morning_brief_v2.py"
if [ $? -eq 0 ]; then
    log "   ✅ Morning brief complete"
else
    log "   ❌ Morning brief failed"
fi

# 2. Check for high-rated job matches and generate applications
log ""
log "💼 Checking for new job applications..."
python3 "$WORKSPACE/scripts/auto_job_apply.py" generate
if [ $? -eq 0 ]; then
    log "   ✅ Job applications processed"
else
    log "   ⚠️  Job applications skipped or failed"
fi

# 3. Summary
log ""
log "============================================================"
log "📊 Daily Automation - Summary"
log "============================================================"

# Count pending applications
PENDING_COUNT=$(ls "$WORKSPACE/applications"/*.json 2>/dev/null | wc -l | tr -d ' ')
log "   📂 Pending applications: $PENDING_COUNT"

# Check if brief was sent
if [ -f "$WORKSPACE/logs/morning-brief-latest.json" ]; then
    log "   ✅ Morning brief generated"
fi

# Show recent job matches
if [ -f "$WORKSPACE/data/job_matches.json" ]; then
    JOB_COUNT=$(grep -o '"match_score"' "$WORKSPACE/data/job_matches.json" | wc -l | tr -d ' ')
    log "   📊 Total job matches tracked: $JOB_COUNT"
fi

log ""
log "✅ Daily automation complete!"
log "============================================================"
