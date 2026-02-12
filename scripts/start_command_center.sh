#!/bin/bash
# Master Command Center - Auto-Start Script
# Launches the command center dashboard on http://localhost:5000

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR/../command-center"
PID_FILE="/tmp/command_center.pid"
LOG_FILE="$HOME/clawd/logs/command_center.log"

# Create logs directory if it doesn't exist
mkdir -p "$HOME/clawd/logs"

# Function to check if service is already running
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Function to stop the service
stop_service() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        echo "Stopping Command Center (PID: $PID)..."
        kill "$PID" 2>/dev/null
        rm -f "$PID_FILE"
        echo "✅ Command Center stopped"
    else
        echo "Command Center is not running"
    fi
}

# Function to start the service
start_service() {
    if is_running; then
        echo "⚠️  Command Center is already running"
        PID=$(cat "$PID_FILE")
        echo "PID: $PID"
        echo "URL: http://localhost:5000"
        exit 0
    fi
    
    echo "🚀 Starting Master Command Center..."
    
    # Change to project directory
    cd "$PROJECT_DIR" || exit 1
    
    # Start Flask app in background
    nohup python3 app.py >> "$LOG_FILE" 2>&1 &
    PID=$!
    
    # Save PID
    echo "$PID" > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 2
    
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Command Center started successfully!"
        echo "📊 Dashboard: http://localhost:5000"
        echo "📝 Logs: $LOG_FILE"
        echo "🔧 PID: $PID"
        echo ""
        echo "To stop: bash $0 stop"
    else
        echo "❌ Failed to start Command Center"
        echo "Check logs: $LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Function to restart the service
restart_service() {
    echo "🔄 Restarting Command Center..."
    stop_service
    sleep 2
    start_service
}

# Function to show status
show_status() {
    if is_running; then
        PID=$(cat "$PID_FILE")
        echo "✅ Command Center is running"
        echo "PID: $PID"
        echo "URL: http://localhost:5000"
        echo "Logs: $LOG_FILE"
    else
        echo "❌ Command Center is not running"
    fi
}

# Main command handling
case "${1:-start}" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the Command Center"
        echo "  stop    - Stop the Command Center"
        echo "  restart - Restart the Command Center"
        echo "  status  - Check if Command Center is running"
        exit 1
        ;;
esac
