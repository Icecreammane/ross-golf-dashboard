#!/bin/bash
# Setup Real Autonomy - #2: Not heartbeat-dependent
# Configure cron jobs for true autonomous operation

echo "🤖 Setting up Jarvis Autonomous Operation"
echo "=========================================="

CLAWD_DIR="$HOME/clawd"

# Check if cron is accessible
if ! command -v crontab &> /dev/null; then
    echo "❌ crontab not found. Cannot setup autonomy."
    exit 1
fi

# Create cron entries
echo ""
echo "📝 Creating cron configuration..."

# Generate cron file
CRON_FILE="/tmp/jarvis_cron.txt"

cat > "$CRON_FILE" << 'EOF'
# Jarvis Autonomous Operation - Real autonomy, not heartbeat-dependent
# Every action can trigger messages to Ross via wake events

# Proactive checks every 15 minutes (food, workout, mood)
*/15 * * * * cd ~/clawd && python3 scripts/proactive_agent.py 2>&1 | logger -t jarvis-proactive

# Session continuity check every 30 minutes
*/30 * * * * cd ~/clawd && python3 scripts/session_continuity.py handoff >> logs/continuity.log 2>&1

# Pattern analysis every hour (learn behavior patterns)
0 * * * * cd ~/clawd && python3 scripts/pattern_analyzer.py analyze >> logs/patterns.log 2>&1

# Behavioral prediction every 2 hours
0 */2 * * * cd ~/clawd && python3 scripts/behavioral_predictor.py predict >> logs/predictions.log 2>&1

# Overnight autonomy (while Ross sleeps 11pm-7am)
0 23 * * * cd ~/clawd && python3 scripts/overnight_agent.py run >> logs/overnight.log 2>&1

# Morning prep at 7:00am (before morning brief)
0 7 * * * cd ~/clawd && python3 scripts/morning_prep.py prepare >> logs/morning-prep.log 2>&1

# Weekly analysis on Sundays at 5pm (before weekly report)
0 17 * * 0 cd ~/clawd && python3 scripts/weekly_analysis.py run >> logs/weekly-analysis.log 2>&1

# Daily memory consolidation at midnight
0 0 * * * cd ~/clawd && python3 scripts/memory_consolidate.py daily >> logs/memory.log 2>&1

# Health check every 5 minutes (restart services if needed)
*/5 * * * * cd ~/clawd && python3 scripts/health_monitor.py check >> logs/health.log 2>&1

EOF

echo "✓ Cron configuration generated"
echo ""
echo "⚠️  Note: Clawdbot has its own cron system via gateway"
echo "    Use: clawdbot cron list"
echo "    To add: clawdbot cron add"
echo ""
echo "📋 Proposed cron jobs:"
cat "$CRON_FILE"
echo ""
echo "🎯 This gives Jarvis:"
echo "   • Real-time proactive messaging (every 15 min)"
echo "   • Pattern learning (hourly)"
echo "   • Overnight autonomy (11pm-7am)"
echo "   • Morning preparation (7am daily)"
echo "   • Self-healing (health checks every 5 min)"
echo ""
echo "To install via Clawdbot gateway, these need to be converted to gateway cron format."
echo "Run this to see current jobs: clawdbot cron list"

rm "$CRON_FILE"
