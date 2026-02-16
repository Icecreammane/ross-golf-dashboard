#!/bin/bash
# Auto-backup to GitHub every 2 hours
# Preserves memory, decisions, and all context

cd ~/clawd || exit 1

# Check if there are changes
if [[ -z $(git status -s) ]]; then
    echo "✅ No changes to backup"
    exit 0
fi

# Commit and push
timestamp=$(date "+%Y-%m-%d %H:%M:%S")
git add -A
git commit -m "Auto-backup: $timestamp" --quiet
git push origin main --quiet

echo "✅ Backup complete: $timestamp"
