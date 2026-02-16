#!/bin/bash
# Start the Proactive Monitor Daemon
# Runs in background, checking systems every 5 minutes using FREE local AI

WORKSPACE="/Users/clawdbot/clawd"
LOG_FILE="$WORKSPACE/logs/monitor-daemon.log"
PID_FILE="$WORKSPACE/logs/monitor-daemon.pid"

mkdir -p "$WORKSPACE/logs"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Monitor daemon already running (PID: $PID)"
        echo "   To stop: bash $WORKSPACE/scripts/stop_monitor_daemon.sh"
        exit 1
    else
        echo "Removing stale PID file"
        rm "$PID_FILE"
    fi
fi

# Start daemon
echo "🚀 Starting Proactive Monitor Daemon..."
echo "   Log: $LOG_FILE"
echo "   PID file: $PID_FILE"

nohup python3 "$WORKSPACE/scripts/proactive_monitor.py" --daemon --interval 5 >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

echo "✅ Monitor daemon started (PID: $(cat $PID_FILE))"
echo "   Checking systems every 5 minutes using FREE local AI"
echo "   To stop: bash $WORKSPACE/scripts/stop_monitor_daemon.sh"
echo "   To view logs: tail -f $LOG_FILE"
