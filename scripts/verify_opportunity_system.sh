#!/bin/bash
# Opportunity Aggregator System Verification Script

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 OPPORTUNITY AGGREGATOR SYSTEM VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

WORKSPACE="/Users/clawdbot/clawd"
PASS=0
FAIL=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $2${NC}"
        PASS=$((PASS + 1))
        return 0
    else
        echo -e "${RED}❌ $2 - NOT FOUND${NC}"
        FAIL=$((FAIL + 1))
        return 1
    fi
}

check_executable() {
    if [ -x "$1" ]; then
        echo -e "${GREEN}✅ $2 is executable${NC}"
        PASS=$((PASS + 1))
        return 0
    else
        echo -e "${RED}❌ $2 - NOT EXECUTABLE${NC}"
        FAIL=$((FAIL + 1))
        return 1
    fi
}

check_daemon() {
    if launchctl list | grep -q "$1"; then
        echo -e "${GREEN}✅ Daemon $1 is loaded${NC}"
        PASS=$((PASS + 1))
        return 0
    else
        echo -e "${RED}❌ Daemon $1 - NOT LOADED${NC}"
        FAIL=$((FAIL + 1))
        return 1
    fi
}

echo "📋 Checking Files..."
echo "─────────────────────────────────────────────────────────────────────────────────"
check_file "$WORKSPACE/scripts/opportunity_aggregator.py" "Aggregator script"
check_file "$WORKSPACE/scripts/view_opportunities.py" "Viewer script"
check_file "$WORKSPACE/configs/com.jarvis.opportunity-aggregator.plist" "launchd config (configs)"
check_file "$HOME/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist" "launchd config (installed)"
check_file "$WORKSPACE/OPPORTUNITY_AGGREGATOR.md" "Documentation"
echo

echo "🔧 Checking Executables..."
echo "─────────────────────────────────────────────────────────────────────────────────"
check_executable "$WORKSPACE/scripts/opportunity_aggregator.py" "Aggregator"
check_executable "$WORKSPACE/scripts/view_opportunities.py" "Viewer"
echo

echo "📂 Checking Data Files..."
echo "─────────────────────────────────────────────────────────────────────────────────"
check_file "$WORKSPACE/data/twitter-opportunities.json" "Twitter input"
check_file "$WORKSPACE/data/email-summary.json" "Email input"
check_file "$WORKSPACE/data/revenue-tasks.json" "Revenue input"
check_file "$WORKSPACE/data/opportunities.json" "Output file"
echo

echo "🔄 Checking Daemon..."
echo "─────────────────────────────────────────────────────────────────────────────────"
check_daemon "com.jarvis.opportunity-aggregator"
echo

echo "📝 Checking Log File..."
echo "─────────────────────────────────────────────────────────────────────────────────"
if [ -f "$WORKSPACE/logs/opportunity-aggregator.log" ]; then
    echo -e "${GREEN}✅ Log file exists${NC}"
    PASS=$((PASS + 1))
    
    # Check if log has recent entries
    if tail -n 1 "$WORKSPACE/logs/opportunity-aggregator.log" | grep -q "COMPLETED"; then
        echo -e "${GREEN}✅ Last run completed successfully${NC}"
        PASS=$((PASS + 1))
        
        # Show last update time
        LAST_LINE=$(tail -n 1 "$WORKSPACE/logs/opportunity-aggregator.log")
        TIMESTAMP=$(echo "$LAST_LINE" | awk '{print $1, $2}' | cut -d',' -f1)
        echo -e "   Last run: ${YELLOW}$TIMESTAMP${NC}"
    else
        echo -e "${YELLOW}⚠️  Last run may have had issues${NC}"
    fi
else
    echo -e "${RED}❌ Log file not found${NC}"
    FAIL=$((FAIL + 1))
fi
echo

echo "🧪 Testing Functionality..."
echo "─────────────────────────────────────────────────────────────────────────────────"

# Test aggregator can run
if python3 "$WORKSPACE/scripts/opportunity_aggregator.py" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Aggregator runs successfully${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${RED}❌ Aggregator failed to run${NC}"
    FAIL=$((FAIL + 1))
fi

# Test viewer can run
if python3 "$WORKSPACE/scripts/view_opportunities.py" --summary-only > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Viewer runs successfully${NC}"
    PASS=$((PASS + 1))
else
    echo -e "${RED}❌ Viewer failed to run${NC}"
    FAIL=$((FAIL + 1))
fi

# Check if opportunities.json is valid JSON
if python3 -m json.tool "$WORKSPACE/data/opportunities.json" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ opportunities.json is valid JSON${NC}"
    PASS=$((PASS + 1))
    
    # Get stats
    TOTAL=$(python3 -c "import json; data = json.load(open('$WORKSPACE/data/opportunities.json')); print(data.get('total_opportunities', 0))")
    echo -e "   Total opportunities: ${YELLOW}$TOTAL${NC}"
else
    echo -e "${RED}❌ opportunities.json is invalid${NC}"
    FAIL=$((FAIL + 1))
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 RESULTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Passed: $PASS${NC}"
echo -e "${RED}❌ Failed: $FAIL${NC}"
echo

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! System is production-ready.${NC}"
    echo
    echo "Next steps:"
    echo "  • View opportunities: python3 ~/clawd/scripts/view_opportunities.py"
    echo "  • Check logs: tail -f ~/clawd/logs/opportunity-aggregator.log"
    echo "  • Read docs: ~/clawd/OPPORTUNITY_AGGREGATOR.md"
    exit 0
else
    echo -e "${RED}⚠️  Some checks failed. Review issues above.${NC}"
    exit 1
fi
