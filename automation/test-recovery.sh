#!/bin/bash
# Test script for auto-recovery system

echo "======================================"
echo "🧪 Testing Auto-Recovery System"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Verify all components are present
echo "Test 1: Checking components..."
if [ -f ~/clawd/automation/health_monitor.py ] && \
   [ -f ~/clawd/automation/auto_recovery.py ] && \
   [ -f ~/clawd/automation/alert.py ] && \
   [ -f ~/clawd/automation/health-system.py ]; then
    echo -e "${GREEN}✅ All components present${NC}"
else
    echo -e "${RED}❌ Missing components${NC}"
    exit 1
fi

# Test 2: Check dependencies
echo ""
echo "Test 2: Checking dependencies..."
if python3 -c "import psutil" 2>/dev/null; then
    echo -e "${GREEN}✅ psutil installed${NC}"
else
    echo -e "${RED}❌ psutil not installed${NC}"
    echo "Install: pip3 install psutil"
    exit 1
fi

# Test 3: Run single health check
echo ""
echo "Test 3: Running health check..."
cd ~/clawd/automation
if python3 health-system.py --once >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi

# Test 4: Check state files created
echo ""
echo "Test 4: Checking state files..."
if [ -f ~/clawd/monitoring/health-state.json ]; then
    echo -e "${GREEN}✅ Health state created${NC}"
else
    echo -e "${YELLOW}⚠️  Health state not created${NC}"
fi

# Test 5: Check service is running
echo ""
echo "Test 5: Checking service status..."
if launchctl list | grep -q "com.jarvis.health-system"; then
    echo -e "${GREEN}✅ Service is loaded${NC}"
else
    echo -e "${YELLOW}⚠️  Service not loaded${NC}"
    echo "Load with: launchctl load ~/Library/LaunchAgents/com.jarvis.health-system.plist"
fi

# Test 6: Check logs are being written
echo ""
echo "Test 6: Checking log files..."
if [ -f ~/clawd/monitoring/health.log ] && [ -s ~/clawd/monitoring/health.log ]; then
    LOG_LINES=$(wc -l < ~/clawd/monitoring/health.log)
    echo -e "${GREEN}✅ Health log active ($LOG_LINES lines)${NC}"
else
    echo -e "${YELLOW}⚠️  No health log yet${NC}"
fi

# Test 7: Check dashboard exists
echo ""
echo "Test 7: Checking dashboard..."
if [ -f ~/clawd/dashboard/health.html ]; then
    echo -e "${GREEN}✅ Dashboard available${NC}"
    echo "   Open: file://$(realpath ~/clawd/dashboard/health.html)"
else
    echo -e "${RED}❌ Dashboard missing${NC}"
fi

# Summary
echo ""
echo "======================================"
echo "📊 Test Summary"
echo "======================================"
echo ""
echo "Current system status:"
python3 -c "
import json
from pathlib import Path

state_file = Path.home() / 'clawd/monitoring/health-state.json'
if state_file.exists():
    with open(state_file) as f:
        state = json.load(f)
    
    if state.get('check_history'):
        latest = state['check_history'][-1]['results']
        
        ok = sum(1 for r in latest.values() if r['status'] == 'ok')
        warning = sum(1 for r in latest.values() if r['status'] == 'warning')
        error = sum(1 for r in latest.values() if r['status'] in ['down', 'error'])
        
        print(f'  ✅ OK: {ok}')
        print(f'  ⚠️  Warnings: {warning}')
        print(f'  ❌ Errors: {error}')
    else:
        print('  No health data yet')
else:
    print('  No state file yet')
"

echo ""
echo "To view real-time logs:"
echo "  tail -f ~/clawd/monitoring/health.log"
echo ""
echo "To manage the service:"
echo "  ~/clawd/automation/manage-health.sh {start|stop|restart|status|logs}"
echo ""
