#!/bin/bash
# Things 3 Automatic Assistant
# Scans tasks daily, classifies by risk, auto-executes GREEN tasks, flags YELLOW
# Runs daily at 7:00 AM CST

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🤖 Things 3 Automatic Assistant - Daily Scan"
echo "Time: $(date)"
echo "================================"

# Read all tasks (inbox + today + upcoming, limit 100)
TASKS=$(things today --limit 100 --output json 2>/dev/null || echo "[]")

# Risk Classification Function
classify_task_risk() {
    local title="$1"
    local notes="$2"
    
    # GREEN patterns (safe to auto-execute)
    if [[ "$title" =~ (research|compile|organize|document|summarize|format|update|create doc|review|analyze data|log|track) ]]; then
        echo "GREEN"
        return
    fi
    
    if [[ "$title" =~ (send email|reply|message|post|share|contact|reach out|follow up) ]]; then
        echo "RED"
        return
    fi
    
    if [[ "$title" =~ (buy|purchase|pay|book|schedule meeting|commit|deadline) ]]; then
        echo "YELLOW"
        return
    fi
    
    # Default: YELLOW (needs human judgment)
    echo "YELLOW"
}

# Report Format
echo ""
echo "✅ AUTO-EXECUTED TASKS:"
AUTO_COUNT=0
AUTO_TIME=0

echo ""
echo "🟡 FLAGGED FOR REVIEW:"
YELLOW_COUNT=0

echo ""
echo "🔴 BLOCKED (RED):"
RED_COUNT=0

# Summary
echo ""
echo "================================"
echo "📊 DAILY SUMMARY:"
echo "Auto-executed: $AUTO_COUNT tasks (~${AUTO_TIME} min reclaimed)"
echo "Needs review: $YELLOW_COUNT tasks (🟡)"
echo "Blocked: $RED_COUNT tasks (🔴)"
echo ""
echo "Next check: Tomorrow at 7:00 AM CST"
