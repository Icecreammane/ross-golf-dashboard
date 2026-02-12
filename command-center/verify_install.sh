#!/bin/bash
# Command Center - Installation Verification Script
# This script checks if everything is set up correctly

echo "🔍 Master Command Center - Installation Verification"
echo "===================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counters
PASS=0
FAIL=0

# Function to check something
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC} - $1"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC} - $1"
        ((FAIL++))
    fi
}

# Check Python 3
echo "Checking Python 3..."
python3 --version > /dev/null 2>&1
check "Python 3 is installed"

# Check pip3
echo "Checking pip3..."
pip3 --version > /dev/null 2>&1
check "pip3 is installed"

# Check if directory exists
echo "Checking project directory..."
if [ -d ~/clawd/command-center ]; then
    echo -e "${GREEN}✅ PASS${NC} - Command Center directory exists"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC} - Command Center directory missing"
    ((FAIL++))
fi

# Check if files exist
echo "Checking project files..."
FILES=(
    "~/clawd/command-center/app.py"
    "~/clawd/command-center/requirements.txt"
    "~/clawd/command-center/templates/dashboard.html"
    "~/clawd/command-center/static/css/style.css"
    "~/clawd/command-center/static/js/dashboard.js"
    "~/clawd/scripts/start_command_center.sh"
)

for FILE in "${FILES[@]}"; do
    EXPANDED=$(eval echo $FILE)
    if [ -f "$EXPANDED" ]; then
        echo -e "${GREEN}✅${NC} $(basename $EXPANDED)"
        ((PASS++))
    else
        echo -e "${RED}❌${NC} $(basename $EXPANDED) missing"
        ((FAIL++))
    fi
done

# Check if Flask is installed
echo "Checking Flask installation..."
python3 -c "import flask" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    VERSION=$(python3 -c "import flask; print(flask.__version__)")
    echo -e "${GREEN}✅ PASS${NC} - Flask installed (version $VERSION)"
    ((PASS++))
else
    echo -e "${YELLOW}⚠️  WARN${NC} - Flask not installed (run: pip3 install -r requirements.txt)"
    ((FAIL++))
fi

# Check if start script is executable
echo "Checking script permissions..."
if [ -x ~/clawd/scripts/start_command_center.sh ]; then
    echo -e "${GREEN}✅ PASS${NC} - Start script is executable"
    ((PASS++))
else
    echo -e "${YELLOW}⚠️  WARN${NC} - Start script needs execute permission (run: chmod +x ~/clawd/scripts/start_command_center.sh)"
    ((FAIL++))
fi

# Check if port 5000 is available
echo "Checking port 5000..."
if lsof -i :5000 > /dev/null 2>&1; then
    PID=$(lsof -ti :5000)
    echo -e "${YELLOW}⚠️  WARN${NC} - Port 5000 is already in use (PID: $PID)"
    echo "  You may need to stop the existing process first"
else
    echo -e "${GREEN}✅ PASS${NC} - Port 5000 is available"
    ((PASS++))
fi

# Check if logs directory exists
echo "Checking logs directory..."
if [ -d ~/clawd/logs ]; then
    echo -e "${GREEN}✅ PASS${NC} - Logs directory exists"
    ((PASS++))
else
    echo -e "${YELLOW}⚠️  INFO${NC} - Logs directory will be created on first run"
fi

# Summary
echo ""
echo "===================================================="
echo "Summary:"
echo -e "  ${GREEN}Passed: $PASS${NC}"
echo -e "  ${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed!${NC}"
    echo ""
    echo "Ready to launch! Run:"
    echo "  bash ~/clawd/scripts/start_command_center.sh start"
    echo ""
    echo "Or install dependencies first:"
    echo "  cd ~/clawd/command-center"
    echo "  pip3 install -r requirements.txt"
    echo ""
elif [ $FAIL -le 2 ]; then
    echo -e "${YELLOW}⚠️  Minor issues detected${NC}"
    echo "Review the warnings above and fix them."
    echo ""
    echo "Quick fixes:"
    echo "  pip3 install -r ~/clawd/command-center/requirements.txt"
    echo "  chmod +x ~/clawd/scripts/start_command_center.sh"
    echo ""
else
    echo -e "${RED}❌ Installation incomplete${NC}"
    echo "Please review the failed checks above."
    echo ""
fi

echo "For help, see:"
echo "  ~/clawd/command-center/QUICKSTART.md"
echo "  ~/clawd/command-center/INSTALL_SUMMARY.md"
echo ""
