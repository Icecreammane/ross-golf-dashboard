#!/bin/bash
# Helper script to manage the health system

case "$1" in
    start)
        echo "Starting health system..."
        launchctl load ~/Library/LaunchAgents/com.jarvis.health-system.plist
        launchctl start com.jarvis.health-system
        echo "✅ Started"
        ;;
    stop)
        echo "Stopping health system..."
        launchctl stop com.jarvis.health-system
        echo "✅ Stopped"
        ;;
    restart)
        echo "Restarting health system..."
        launchctl stop com.jarvis.health-system
        sleep 2
        launchctl start com.jarvis.health-system
        echo "✅ Restarted"
        ;;
    status)
        echo "Health system status:"
        launchctl list | grep jarvis.health-system
        echo ""
        echo "Recent logs:"
        tail -20 ~/clawd/monitoring/health.log
        ;;
    logs)
        echo "=== Health Log ==="
        tail -50 ~/clawd/monitoring/health.log
        echo ""
        echo "=== Recovery Log ==="
        tail -50 ~/clawd/monitoring/recovery.log
        echo ""
        echo "=== Alerts Log ==="
        tail -20 ~/clawd/monitoring/alerts.log 2>/dev/null || echo "(No alerts yet)"
        ;;
    test)
        echo "Running test cycle..."
        cd ~/clawd/automation
        python3 health-system.py --once
        ;;
    uninstall)
        echo "Uninstalling health system..."
        launchctl unload ~/Library/LaunchAgents/com.jarvis.health-system.plist
        rm ~/Library/LaunchAgents/com.jarvis.health-system.plist
        echo "✅ Uninstalled"
        ;;
    *)
        echo "Jarvis Health System Manager"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|test|uninstall}"
        echo ""
        echo "Commands:"
        echo "  start      - Start the health system daemon"
        echo "  stop       - Stop the health system daemon"
        echo "  restart    - Restart the health system daemon"
        echo "  status     - Show current status and recent logs"
        echo "  logs       - Show detailed logs"
        echo "  test       - Run one health check cycle"
        echo "  uninstall  - Remove the health system service"
        exit 1
        ;;
esac
