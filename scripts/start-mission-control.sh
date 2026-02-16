#!/bin/bash
# Start Mission Control v3 Dashboard
# Run at boot or manually to start the central hub

WORKSPACE="/Users/clawdbot/clawd"
APP_DIR="$WORKSPACE/mission_control"
LOG_DIR="$WORKSPACE/logs"
PID_FILE="$LOG_DIR/mission-control.pid"
LOG_FILE="$LOG_DIR/mission-control.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "✅ Mission Control already running (PID: $OLD_PID)"
        echo "📊 Access at: http://localhost:8081/mission-control"
        exit 0
    else
        echo "🧹 Cleaning up stale PID file..."
        rm "$PID_FILE"
    fi
fi

# Kill any existing process on port 8081
echo "🔍 Checking for processes on port 8081..."
if command -v lsof > /dev/null 2>&1; then
    lsof -ti:8081 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Start Mission Control
echo "🚀 Starting Mission Control v3..."
cd "$APP_DIR"
python3 app.py > "$LOG_FILE" 2>&1 &
NEW_PID=$!

# Save PID
echo "$NEW_PID" > "$PID_FILE"

# Wait a moment and verify it started
sleep 2

if ps -p "$NEW_PID" > /dev/null 2>&1; then
    echo "✅ Mission Control started successfully!"
    echo "📊 Dashboard: http://localhost:8081/mission-control"
    echo "📋 PID: $NEW_PID"
    echo "📝 Logs: $LOG_FILE"
    echo ""
    echo "✨ NEW FEATURES:"
    echo "   • 🔴 Live Activity Feed - See what Jarvis is doing right now"
    echo "   • ⚙️ Automations Status - All scheduled tasks"
    echo "   • 🧠 Memory Health - Verify persistence"
    echo "   • 🔗 Quick Links - One-click access to everything"
    exit 0
else
    echo "❌ Failed to start Mission Control"
    echo "📝 Check logs: $LOG_FILE"
    exit 1
fi
