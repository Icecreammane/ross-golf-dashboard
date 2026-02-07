#!/bin/bash
# Quick launcher for the Jarvis Command Center Dashboard

WORKSPACE="$HOME/clawd"
SCRIPT="$WORKSPACE/scripts/dashboard_server.sh"

# Check if already running
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Dashboard server already running on port 8080"
    echo "   Visit: http://10.0.0.16:8080/org-chart-dashboard.html"
    exit 1
fi

# Start server
bash "$SCRIPT"
