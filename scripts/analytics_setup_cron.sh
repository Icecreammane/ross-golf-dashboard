#!/bin/bash
# Setup cron jobs for analytics system

WORKSPACE="$HOME/clawd"

echo "📊 Setting up Analytics Cron Jobs"
echo "=================================="

# Create cron entries
CRON_ENTRIES="
# Analytics System - Auto-generated
# Runner checks every 15 minutes
*/15 * * * * cd $WORKSPACE && python3 scripts/analytics_runner.py >> logs/analytics_cron.log 2>&1

# Weekly report (Sunday @ 6pm) - backup trigger
0 18 * * 0 cd $WORKSPACE && python3 scripts/analytics_weekly_report.py >> logs/analytics_weekly.log 2>&1
"

# Backup existing crontab
echo "📋 Backing up existing crontab..."
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null

# Check if analytics jobs already exist
if crontab -l 2>/dev/null | grep -q "Analytics System"; then
    echo "⚠️  Analytics cron jobs already exist"
    echo "To update, remove existing entries and re-run this script"
    exit 0
fi

# Add new entries
echo "➕ Adding analytics cron jobs..."
(crontab -l 2>/dev/null; echo "$CRON_ENTRIES") | crontab -

# Verify
echo ""
echo "✅ Cron jobs installed!"
echo ""
echo "Current cron schedule:"
echo "====================="
crontab -l | grep -A 5 "Analytics System"

echo ""
echo "📝 Logs will be written to:"
echo "  • $WORKSPACE/logs/analytics_cron.log (runner output)"
echo "  • $WORKSPACE/logs/analytics_weekly.log (weekly reports)"
echo ""
echo "🔍 Monitor with: tail -f ~/clawd/logs/analytics_cron.log"
