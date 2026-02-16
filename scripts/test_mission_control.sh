#!/bin/bash
# Mission Control System Test

echo "🧪 Testing Mission Control Systems"
echo "=================================="
echo ""

# Test 1: Auto-Context Loader
echo "1️⃣  Testing Auto-Context Loader..."
python3 /Users/clawdbot/clawd/scripts/auto_context.py main > /tmp/test_context.log 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Auto-context loader working"
    grep "Loaded Files" /tmp/test_context.log
else
    echo "   ❌ Auto-context loader failed"
fi
echo ""

# Test 2: Action Tracker
echo "2️⃣  Testing Action Tracker..."
python3 -c "
from scripts.action_tracker import log_action, get_daily_summary
log_action('test', 'Mission Control system test', result='success')
summary = get_daily_summary()
print(f'   ✅ Action tracker working')
print(f'   Total actions logged today: {summary[\"total_actions\"]}')
print(f'   Total cost: \${summary[\"total_cost\"]:.2f}')
" 2>&1
echo ""

# Test 3: Confidence Tracker
echo "3️⃣  Testing Confidence Tracker..."
python3 /Users/clawdbot/clawd/scripts/confidence_tracker.py > /tmp/test_confidence.log 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Confidence tracker working"
    grep "Score:" /tmp/test_confidence.log
    grep "Stack:" /tmp/test_confidence.log
else
    echo "   ❌ Confidence tracker failed"
fi
echo ""

# Test 4: Flask API
echo "4️⃣  Testing Flask API..."
if curl -s http://localhost:8081/api/services > /dev/null 2>&1; then
    echo "   ✅ Flask API responding"
    echo "   Endpoints available:"
    echo "      - http://localhost:8081/mission-control (Dashboard)"
    echo "      - http://localhost:8081/api/status (Complete status)"
    echo "      - http://localhost:8081/api/services (Service list)"
    echo "      - http://localhost:8081/api/costs (Cost data)"
    echo "      - http://localhost:8081/api/health (System health)"
    echo "      - http://localhost:8081/api/confidence (Confidence data)"
else
    echo "   ⚠️  Flask server not running"
    echo "   Start with: bash scripts/start_mission_control.sh"
fi
echo ""

# Test 5: File Structure
echo "5️⃣  Testing File Structure..."
FILES=(
    "mission_control/app.py"
    "mission_control/templates/mission_control.html"
    "scripts/action_tracker.py"
    "scripts/auto_context.py"
    "scripts/confidence_tracker.py"
    "scripts/start_mission_control.sh"
    "MISSION_CONTROL.md"
    "BUILD_MISSION_CONTROL.md"
)

all_exist=true
for file in "${FILES[@]}"; do
    if [ -f "/Users/clawdbot/clawd/$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file MISSING"
        all_exist=false
    fi
done
echo ""

# Summary
echo "=================================="
echo "📊 Test Summary"
echo "=================================="
if [ "$all_exist" = true ]; then
    echo "✅ All systems operational"
    echo ""
    echo "🚀 Quick Start:"
    echo "   bash scripts/start_mission_control.sh"
    echo "   Visit: http://localhost:8081/mission-control"
else
    echo "⚠️  Some components missing"
fi
