#!/bin/bash
# Quick status check for the dashboard

echo "🎯 Jarvis Command Center Dashboard - Status Check"
echo ""

# Check if server is running
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✅ Server: Running on port 8080"
    echo "   URL: http://10.0.0.16:8080/org-chart-dashboard.html"
else
    echo "❌ Server: Not running"
    echo "   Start with: bash ~/clawd/scripts/dashboard_start.sh"
fi

echo ""

# Check if data file exists and is recent
DATA_FILE="$HOME/clawd/dashboard-data.json"
if [ -f "$DATA_FILE" ]; then
    AGE=$(($(date +%s) - $(stat -f %m "$DATA_FILE")))
    echo "✅ Data: dashboard-data.json exists"
    echo "   Last updated: ${AGE}s ago"
    
    if [ $AGE -lt 20 ]; then
        echo "   Status: 🟢 Fresh (auto-updating)"
    elif [ $AGE -lt 60 ]; then
        echo "   Status: 🟡 Recent"
    else
        echo "   Status: 🔴 Stale (updater may not be running)"
    fi
else
    echo "❌ Data: dashboard-data.json not found"
    echo "   Generate with: python3 ~/clawd/scripts/update_dashboard_data.py"
fi

echo ""

# Show current stats
if [ -f "$DATA_FILE" ]; then
    echo "📊 Current Stats:"
    python3 -c "
import json
with open('$DATA_FILE') as f:
    data = json.load(f)
print(f\"   Agents: {len(data['agents'])} ({data['stats']['active']} active)\")
print(f\"   Queue: {len(data['queue'])} items\")
print(f\"   Completed Today: {data['stats']['completedToday']}\")
print(f\"   Success Rate: {data['stats']['successRate']}\")
"
fi

echo ""
echo "📚 Documentation: ~/clawd/DASHBOARD_README.md"
