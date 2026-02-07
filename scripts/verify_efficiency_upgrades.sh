#!/bin/bash
# Verification script for efficiency upgrades

echo "🧪 Verifying Efficiency Upgrades Installation"
echo "=" | tr '=' '='| head -c 60; echo "="

WORKSPACE="$HOME/clawd"
SCRIPTS="$WORKSPACE/scripts"
PASS=0
FAIL=0

check_file() {
    if [ -f "$1" ]; then
        echo "✅ $2"
        ((PASS++))
        return 0
    else
        echo "❌ $2 - NOT FOUND: $1"
        ((FAIL++))
        return 1
    fi
}

check_executable() {
    if [ -x "$1" ]; then
        echo "✅ $2 (executable)"
        ((PASS++))
        return 0
    else
        echo "⚠️  $2 - NOT EXECUTABLE: $1"
        ((FAIL++))
        return 1
    fi
}

echo ""
echo "📁 Checking Files..."
echo "---"

# New files
check_file "$SCRIPTS/sub_agent_progress.py" "Progress Tracking System"
check_file "$SCRIPTS/cost_tracker.py" "Cost Tracker"
check_file "$SCRIPTS/cleanup_memory.py" "Memory Cleanup Script"
check_file "$SCRIPTS/build_status.py" "Build Status Script"
check_file "$SCRIPTS/jarvis_quick.sh" "Quick Commands Script"
check_file "$WORKSPACE/EFFICIENCY_UPGRADES.md" "Documentation"
check_file "$WORKSPACE/QUICK_START_EFFICIENCY.md" "Quick Start Guide"

# Upgraded files
check_file "$SCRIPTS/autonomous_check.py" "Autonomous Check (upgraded)"
check_file "$WORKSPACE/org-chart-dashboard.html" "Dashboard (upgraded)"

echo ""
echo "🔧 Checking Executables..."
echo "---"

check_executable "$SCRIPTS/sub_agent_progress.py" "sub_agent_progress.py"
check_executable "$SCRIPTS/cost_tracker.py" "cost_tracker.py"
check_executable "$SCRIPTS/cleanup_memory.py" "cleanup_memory.py"
check_executable "$SCRIPTS/build_status.py" "build_status.py"
check_executable "$SCRIPTS/jarvis_quick.sh" "jarvis_quick.sh"
check_executable "$SCRIPTS/autonomous_check.py" "autonomous_check.py"

echo ""
echo "🧪 Running Functional Tests..."
echo "---"

# Test autonomous_check.py
if python3 "$SCRIPTS/autonomous_check.py" > /dev/null 2>&1; then
    echo "✅ autonomous_check.py runs without errors"
    ((PASS++))
else
    echo "❌ autonomous_check.py has errors"
    ((FAIL++))
fi

# Test cost_tracker.py
if python3 "$SCRIPTS/cost_tracker.py" --today > /dev/null 2>&1; then
    echo "✅ cost_tracker.py runs without errors"
    ((PASS++))
else
    echo "❌ cost_tracker.py has errors"
    ((FAIL++))
fi

# Test build_status.py
if python3 "$SCRIPTS/build_status.py" > /dev/null 2>&1; then
    echo "✅ build_status.py runs without errors"
    ((PASS++))
else
    echo "❌ build_status.py has errors"
    ((FAIL++))
fi

# Test jarvis_quick.sh
if bash "$SCRIPTS/jarvis_quick.sh" help > /dev/null 2>&1; then
    echo "✅ jarvis_quick.sh runs without errors"
    ((PASS++))
else
    echo "❌ jarvis_quick.sh has errors"
    ((FAIL++))
fi

echo ""
echo "=" | tr '=' '='| head -c 60; echo "="
echo "📊 Results: $PASS passed, $FAIL failed"

if [ $FAIL -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED - System ready for production"
    exit 0
else
    echo "⚠️  SOME CHECKS FAILED - Review errors above"
    exit 1
fi
