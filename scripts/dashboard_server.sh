#!/bin/bash
# Dashboard Server - serves the org chart dashboard with auto-updating data

WORKSPACE="$HOME/clawd"
PORT=8080

echo "🚀 Starting Jarvis Command Center Dashboard..."
echo "   Dashboard: http://10.0.0.16:$PORT/org-chart-dashboard.html"
echo "   Press Ctrl+C to stop"
echo ""

# Start data updater in background
echo "📊 Starting data updater (10s refresh)..."
while true; do
    python3 "$WORKSPACE/scripts/update_dashboard_data.py" > /dev/null 2>&1
    sleep 10
done &
UPDATER_PID=$!

# Start HTTP server
echo "🌐 Starting HTTP server on port $PORT..."
cd "$WORKSPACE"
python3 -m http.server $PORT 2>&1 | grep -v "GET /"

# Cleanup on exit
trap "echo 'Stopping...'; kill $UPDATER_PID 2>/dev/null; exit" INT TERM

wait
