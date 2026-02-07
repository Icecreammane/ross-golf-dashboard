#!/bin/bash
# Jarvis Health Monitor
# Checks gateway, Flask, and logs issues

LOG_FILE="/Users/clawdbot/clawd/monitoring/health.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Check Gateway
if pgrep -f "clawdbot" > /dev/null; then
    GATEWAY_STATUS="OK"
else
    GATEWAY_STATUS="DOWN"
    echo "[$TIMESTAMP] ALERT: Gateway is DOWN" >> "$LOG_FILE"
fi

# Check Flask fitness tracker
FLASK_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null)
if [ "$FLASK_STATUS" != "200" ]; then
    echo "[$TIMESTAMP] ALERT: Flask fitness tracker not responding (HTTP $FLASK_STATUS)" >> "$LOG_FILE"
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "[$TIMESTAMP] WARNING: Disk usage at ${DISK_USAGE}%" >> "$LOG_FILE"
fi

# Output status
echo "Gateway: $GATEWAY_STATUS | Flask: $FLASK_STATUS | Disk: ${DISK_USAGE}%"
