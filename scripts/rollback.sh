#!/bin/bash
# ClawBack rollback script
# Usage: bash scripts/rollback.sh <hash> "what broke" "why" "principle tested"

set -e

HASH="$1"
WHAT_BROKE="$2"
WHY="$3"
PRINCIPLE="$4"
WORKSPACE="/Users/clawdbot/clawd"

if [ -z "$HASH" ] || [ -z "$WHAT_BROKE" ] || [ -z "$WHY" ] || [ -z "$PRINCIPLE" ]; then
    echo "Error: All arguments required"
    echo "Usage: bash scripts/rollback.sh <hash> \"what broke\" \"why\" \"principle tested\""
    exit 1
fi

cd "$WORKSPACE"

# Rollback to checkpoint
echo "🔄 Rolling back to $HASH..."
git reset --hard "$HASH"

# Log regression to PRINCIPLES.md
DATE=$(date +%Y-%m-%d)
REGRESSION="
### [$DATE] Rollback from failure 🔴
**What broke:** $WHAT_BROKE  
**Why:** $WHY  
**Principle tested:** $PRINCIPLE  
**Fix:** Rolled back to checkpoint $HASH  
"

# Append to regressions section
echo "$REGRESSION" >> PRINCIPLES.md

# Commit the regression log
git add PRINCIPLES.md
git commit -m "📝 LOG REGRESSION: $WHAT_BROKE"

echo "✅ Rolled back to $HASH"
echo "✅ Regression logged to PRINCIPLES.md"
echo ""
echo "Review the regression log to internalize this failure."
