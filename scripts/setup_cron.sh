#!/bin/bash
# Setup cron job for morning brief at 7:30am CST daily

WORKSPACE="$HOME/clawd"
SCRIPT="$WORKSPACE/scripts/morning_brief_v2.py"

echo "Setting up morning brief cron job..."

# Create cron entry (7:30 AM CST = 13:30 UTC in winter, 12:30 UTC in summer)
# Using 13:30 UTC for CST winter time
CRON_ENTRY="30 13 * * * /usr/bin/python3 $SCRIPT >> $WORKSPACE/logs/morning-brief-cron.log 2>&1"

# Check if entry already exists
if crontab -l 2>/dev/null | grep -q "morning_brief_v2.py"; then
    echo "⚠️  Cron job already exists"
    echo "Current cron jobs:"
    crontab -l | grep morning_brief
    echo ""
    echo "To update, remove old job first: crontab -e"
else
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    echo "✅ Cron job added!"
    echo ""
    echo "Scheduled for: 7:30 AM CST daily"
    echo "Script: $SCRIPT"
    echo "Log: $WORKSPACE/logs/morning-brief-cron.log"
fi

echo ""
echo "To test manually: python3 $SCRIPT"
