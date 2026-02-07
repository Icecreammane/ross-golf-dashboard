#!/bin/bash
# Quick system status check - run anytime
# Usage: bash ~/clawd/scripts/status-check.sh

echo "🤖 JARVIS SYSTEM STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Gateway
if pgrep -f "clawdbot-gateway" > /dev/null; then
    PID=$(pgrep -f "clawdbot-gateway")
    echo "✅ Gateway: Running (PID $PID)"
else
    echo "❌ Gateway: DOWN"
fi

# Fitness Tracker
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Fitness Tracker: Running (port 3000)"
else
    echo "❌ Fitness Tracker: DOWN"
fi

# Disk Space
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "✅ Disk Space: ${DISK_USAGE}% used"
elif [ "$DISK_USAGE" -lt 90 ]; then
    echo "⚠️  Disk Space: ${DISK_USAGE}% used (getting full)"
else
    echo "❌ Disk Space: ${DISK_USAGE}% CRITICAL"
fi

# Memory
MEM_PRESSURE=$(memory_pressure | grep "System-wide memory free percentage" | awk '{print $5}' | tr -d '%')
if [ ! -z "$MEM_PRESSURE" ]; then
    echo "✅ Memory: ${MEM_PRESSURE}% free"
fi

# Heartbeat Status
if [ -f ~/.clawdbot/clawdbot.json ]; then
    HB=$(grep -A1 '"heartbeat"' ~/.clawdbot/clawdbot.json | grep '"every"' | cut -d'"' -f4)
    if [ ! -z "$HB" ]; then
        echo "✅ Heartbeat: Every $HB"
    else
        echo "⚠️  Heartbeat: Not configured"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⏰ $(date '+%Y-%m-%d %H:%M:%S %Z')"
