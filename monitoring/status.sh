#!/bin/bash
# Quick status check - shows current monitoring state at a glance

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔍 Monitoring Status"
echo "===================="
echo ""

# Last check time
if [ -f "state/health-state.json" ]; then
    echo "📊 Last Health Check:"
    python3 -c "
import json
from datetime import datetime
with open('state/health-state.json') as f:
    data = json.load(f)
    print('   ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
" 2>/dev/null || echo "    Just now"
else
    echo "📊 Last Health Check: Never"
fi
echo ""

# Recent alerts
if [ -f "logs/alerts.log" ]; then
    ALERT_COUNT=$(grep -c "Alert:" logs/alerts.log 2>/dev/null || echo "0")
    echo "🔔 Alert History:"
    echo "    Total alerts logged: $ALERT_COUNT"
    
    if [ "$ALERT_COUNT" -gt 0 ] 2>/dev/null; then
        echo "    Last 3 alerts:"
        grep "Alert:" logs/alerts.log | tail -3 | sed 's/^/      /'
    else
        echo "    ✅ No alerts yet"
    fi
else
    echo "🔔 Alert History: No log file yet"
fi
echo ""

# Cron status
echo "⏰ Cron Status:"
if crontab -l 2>/dev/null | grep -q "run-checks.sh"; then
    echo "    ✅ Cron job installed"
    echo "    Schedule: Every hour, 7am-11pm"
    
    # Next scheduled run
    CURRENT_HOUR=$(date +%H)
    if [ $CURRENT_HOUR -lt 7 ]; then
        echo "    Next run: Today at 7:00 AM"
    elif [ $CURRENT_HOUR -ge 23 ]; then
        echo "    Next run: Tomorrow at 7:00 AM"
    elif [ $CURRENT_HOUR -ge 19 ]; then
        echo "    Next run: Skipped (concert hours)"
    else
        NEXT_HOUR=$((CURRENT_HOUR + 1))
        echo "    Next run: Today at ${NEXT_HOUR}:00"
    fi
else
    echo "    ⚠️  Cron job NOT installed"
    echo "    Run: ./setup-cron.sh"
fi
echo ""

# System health snapshot
echo "💓 Quick Health Check:"
echo "    Gateway: $(clawdbot gateway status 2>&1 | grep -q 'running\|active' && echo '✅ Running' || echo '⚠️  Not running')"
echo "    Disk: $(df -h / | awk 'NR==2 {print $5}') used"
echo ""

# Email check
if command -v himalaya &> /dev/null; then
    echo "📧 Email Status:"
    echo "    Himalaya CLI: ✅ Installed"
else
    echo "📧 Email Status:"
    echo "    Himalaya CLI: ⚠️  Not installed (email monitoring disabled)"
fi
echo ""

echo "===================="
echo "Run './test-system.sh' for detailed testing"
echo "Run './run-checks.sh --force' to trigger check now"
echo "View dashboard: python3 -m http.server 8080"
