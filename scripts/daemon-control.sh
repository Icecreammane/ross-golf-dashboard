#!/bin/bash
# Jarvis Daemon Control Script

PLIST="$HOME/Library/LaunchAgents/com.clawdbot.jarvis-daemon.plist"
LABEL="com.clawdbot.jarvis-daemon"

case "$1" in
    start)
        echo "Starting Jarvis daemon..."
        launchctl load "$PLIST"
        echo "✓ Daemon started"
        ;;
    stop)
        echo "Stopping Jarvis daemon..."
        launchctl unload "$PLIST"
        echo "✓ Daemon stopped"
        ;;
    restart)
        echo "Restarting Jarvis daemon..."
        launchctl unload "$PLIST" 2>/dev/null
        sleep 1
        launchctl load "$PLIST"
        echo "✓ Daemon restarted"
        ;;
    status)
        if launchctl list | grep -q "$LABEL"; then
            echo "✓ Jarvis daemon is running"
            echo ""
            echo "Recent log entries:"
            tail -n 10 ~/clawd/monitoring/daemon.log
        else
            echo "✗ Jarvis daemon is not running"
        fi
        ;;
    logs)
        echo "=== Daemon Log (last 50 lines) ==="
        tail -n 50 ~/clawd/monitoring/daemon.log
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
