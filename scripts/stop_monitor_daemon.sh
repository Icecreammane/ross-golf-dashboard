#!/bin/bash
# Stop the Proactive Monitor Daemon

WORKSPACE="/Users/clawdbot/clawd"
PID_FILE="$WORKSPACE/logs/monitor-daemon.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  No PID file found. Daemon may not be running."
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p $PID > /dev/null 2>&1; then
    echo "🛑 Stopping monitor daemon (PID: $PID)..."
    kill $PID
    rm "$PID_FILE"
    echo "✅ Monitor daemon stopped"
else
    echo "⚠️  Process $PID not running. Removing stale PID file."
    rm "$PID_FILE"
fi
