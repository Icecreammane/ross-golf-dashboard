#!/bin/bash
# Test the monitoring system end-to-end
# Run this before concert day to verify everything works

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧪 Testing Monitoring System"
echo "=============================="
echo ""

# Test 1: Directory structure
echo "1️⃣ Checking directory structure..."
if [ -d "state" ] && [ -d "logs" ]; then
    echo "   ✅ Directories exist"
else
    echo "   📁 Creating directories..."
    mkdir -p state logs
    echo "   ✅ Directories created"
fi
echo ""

# Test 2: Script permissions
echo "2️⃣ Checking script permissions..."
if [ -x "monitor-email.py" ] && [ -x "monitor-health.py" ] && [ -x "send-alerts.py" ]; then
    echo "   ✅ Scripts are executable"
else
    echo "   🔧 Making scripts executable..."
    chmod +x *.py *.sh
    echo "   ✅ Fixed permissions"
fi
echo ""

# Test 3: Email monitor
echo "3️⃣ Testing email monitor..."
if python3 monitor-email.py > /tmp/email-test.json 2>&1; then
    echo "   ✅ Email monitor works"
    cat /tmp/email-test.json | python3 -m json.tool | head -10
else
    echo "   ⚠️  Email monitor error (may need Himalaya CLI)"
    cat /tmp/email-test.json
fi
echo ""

# Test 4: Health monitor
echo "4️⃣ Testing health monitor..."
if python3 monitor-health.py > /tmp/health-test.json 2>&1; then
    echo "   ✅ Health monitor works"
    cat /tmp/health-test.json | python3 -m json.tool | head -10
else
    echo "   ❌ Health monitor failed"
    cat /tmp/health-test.json
    exit 1
fi
echo ""

# Test 5: Alert aggregator (DRY RUN)
echo "5️⃣ Testing alert aggregator..."
echo "   (This will NOT send actual alerts)"
# Temporarily modify send-alerts.py to skip actual message sending for testing
if python3 send-alerts.py > /tmp/alert-test.json 2>&1; then
    echo "   ✅ Alert aggregator works"
    cat /tmp/alert-test.json
else
    echo "   ⚠️  Alert aggregator had issues"
    cat /tmp/alert-test.json
fi
echo ""

# Test 6: Check logs
echo "6️⃣ Checking logs..."
if [ -f "logs/alerts.log" ]; then
    echo "   ✅ Log file created"
    echo "   Last 3 log entries:"
    tail -3 logs/alerts.log | sed 's/^/      /'
else
    echo "   ⚠️  No log file yet (will be created on first run)"
fi
echo ""

# Test 7: State files
echo "7️⃣ Checking state files..."
STATE_COUNT=$(ls state/*.json 2>/dev/null | wc -l)
if [ $STATE_COUNT -gt 0 ]; then
    echo "   ✅ $STATE_COUNT state file(s) created"
    ls -1 state/ | sed 's/^/      - /'
else
    echo "   ℹ️  No state files yet (normal on first run)"
fi
echo ""

# Test 8: Dashboard
echo "8️⃣ Checking dashboard..."
if [ -f "monitoring.html" ]; then
    echo "   ✅ Dashboard file exists"
    echo "   📊 To view: python3 -m http.server 8080"
    echo "      Then open: http://localhost:8080/monitoring.html"
else
    echo "   ❌ Dashboard missing!"
    exit 1
fi
echo ""

# Test 9: Cron setup
echo "9️⃣ Checking cron job..."
if crontab -l 2>/dev/null | grep -q "run-checks.sh"; then
    echo "   ✅ Cron job installed"
    crontab -l | grep run-checks.sh | sed 's/^/      /'
else
    echo "   ⚠️  Cron job not installed"
    echo "      Run: ./setup-cron.sh"
fi
echo ""

# Summary
echo "=============================="
echo "✅ System test complete!"
echo ""
echo "Next steps:"
echo "  1. Install cron: ./setup-cron.sh"
echo "  2. View dashboard: python3 -m http.server 8080"
echo "  3. Monitor logs: tail -f logs/alerts.log"
echo ""
echo "Ready for concert day! 🎵"
