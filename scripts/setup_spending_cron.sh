#!/bin/bash
# Setup cron jobs for spending tracker

WORKSPACE="$HOME/clawd"

echo "🔧 Setting up spending tracker cron jobs..."

# Create cron entries
CRON_ENTRIES="
# Spending Tracker - Daily transaction sync (2am)
0 2 * * * cd $WORKSPACE && /usr/bin/python3 scripts/sync_transactions.py >> logs/spending_sync.log 2>&1

# Spending Tracker - Evening summary (8pm) - integrate with evening check-in
# 0 20 * * * cd $WORKSPACE && /usr/bin/python3 scripts/spending_alerts.py evening >> logs/spending_alerts.log 2>&1
"

echo "$CRON_ENTRIES"
echo ""
echo "📋 To install these cron jobs:"
echo "1. Run: crontab -e"
echo "2. Paste the entries above"
echo "3. Save and exit"
echo ""
echo "💡 For evening summary integration:"
echo "Add this to your evening check-in script:"
echo "python3 $WORKSPACE/scripts/spending_alerts.py evening"
echo ""
echo "✅ Done!"
