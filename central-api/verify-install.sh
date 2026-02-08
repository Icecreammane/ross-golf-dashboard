#!/bin/bash
# Quick verification script for Central API installation

set -e

echo "🔍 Verifying Central API Installation..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

# Check directory structure
echo "📁 Checking directory structure..."
if [ -d "api" ] && [ -d "tests" ] && [ -d "config" ]; then
    echo -e "${GREEN}✓ Directory structure OK${NC}"
else
    echo -e "${RED}✗ Missing directories${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check virtual environment
echo "🐍 Checking virtual environment..."
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    echo -e "${GREEN}✓ Virtual environment OK${NC}"
else
    echo -e "${RED}✗ Virtual environment missing${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check configuration
echo "⚙️  Checking configuration..."
if [ -f ".env" ] && [ -f "config/config.yaml" ]; then
    echo -e "${GREEN}✓ Configuration files OK${NC}"
else
    echo -e "${RED}✗ Missing configuration files${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check API token
echo "🔐 Checking API token..."
if grep -q "API_TOKEN=" .env && ! grep -q "your_secure_token_here" .env; then
    TOKEN=$(grep API_TOKEN .env | cut -d= -f2)
    echo -e "${GREEN}✓ API token configured${NC}"
    echo -e "   Token: ${YELLOW}${TOKEN}${NC}"
else
    echo -e "${RED}✗ API token not configured${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check Python dependencies
echo "📦 Checking Python dependencies..."
source venv/bin/activate
if python3 -c "import flask, flask_restx, redis, pytest" 2>/dev/null; then
    echo -e "${GREEN}✓ All dependencies installed${NC}"
else
    echo -e "${RED}✗ Missing dependencies${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check if app can be imported
echo "🚀 Checking app imports..."
if python3 -c "from api.app import app" 2>&1 | grep -q "App imports successfully"; then
    echo -e "${GREEN}✓ App imports successfully${NC}"
elif python3 -c "from api.app import app" 2>/dev/null; then
    echo -e "${GREEN}✓ App imports successfully${NC}"
else
    echo -e "${RED}✗ App import failed${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check if service is installed
echo "⚙️  Checking launchd service..."
if [ -f ~/Library/LaunchAgents/com.jarvis.central-api.plist ]; then
    echo -e "${GREEN}✓ Service installed${NC}"
    if launchctl list | grep -q "com.jarvis.central-api"; then
        echo -e "${GREEN}✓ Service is running${NC}"
    else
        echo -e "${YELLOW}⚠️  Service installed but not running${NC}"
        echo "   Run: ./install-service.sh to start"
    fi
else
    echo -e "${YELLOW}⚠️  Service not installed${NC}"
    echo "   Run: ./install-service.sh to install"
fi

# Check if API responds (if running)
echo "🌐 Checking API endpoint..."
if curl -s -f http://localhost:3003/system/health > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:3003/system/health | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
    echo -e "${GREEN}✓ API is responding (status: $HEALTH)${NC}"
    echo "   📚 View docs: http://localhost:3003/docs"
else
    echo -e "${YELLOW}⚠️  API not responding on port 3003${NC}"
    echo "   This is OK if you haven't started the service yet"
    echo "   Start with: ./start.sh (manual) or ./install-service.sh (service)"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Installation verification complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start API: ./start.sh (or ./install-service.sh for service)"
    echo "2. Test: curl http://localhost:3003/system/health"
    echo "3. View docs: http://localhost:3003/docs"
    echo "4. Use client: python3 client_example.py"
else
    echo -e "${RED}❌ Found $ERRORS issue(s)${NC}"
    echo ""
    echo "Try running: ./setup.sh"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
