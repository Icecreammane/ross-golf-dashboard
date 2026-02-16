#!/bin/bash
# ClawBack checkpoint script
# Usage: bash scripts/checkpoint.sh "reason for checkpoint"

set -e

REASON="$1"
WORKSPACE="/Users/clawdbot/clawd"

if [ -z "$REASON" ]; then
    echo "Error: Checkpoint reason required"
    echo "Usage: bash scripts/checkpoint.sh \"reason for checkpoint\""
    exit 1
fi

cd "$WORKSPACE"

# Commit everything
git add -A
HASH=$(git commit -m "🔖 CHECKPOINT: $REASON" --allow-empty | grep -oE '[a-f0-9]{7}' | head -1)

if [ -z "$HASH" ]; then
    HASH=$(git rev-parse --short HEAD)
fi

echo "✅ Checkpoint created: $HASH"
echo "Reason: $REASON"
echo ""
echo "To rollback if needed:"
echo "bash scripts/rollback.sh $HASH \"what broke\" \"why\" \"principle tested\""
