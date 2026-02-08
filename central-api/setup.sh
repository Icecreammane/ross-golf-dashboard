#!/bin/bash
# Central API Setup Script

set -e

echo "🚀 Setting up Central API..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    
    # Generate secure token
    TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Update .env with generated token
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/your_secure_token_here/$TOKEN/" .env
    else
        sed -i "s/your_secure_token_here/$TOKEN/" .env
    fi
    
    echo -e "${GREEN}✓ .env created with secure token${NC}"
    echo -e "${YELLOW}⚠️  Your API token: $TOKEN${NC}"
    echo -e "${YELLOW}⚠️  Save this token! You'll need it for authentication.${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Update config.yaml with generated token
echo "Updating config..."
TOKEN=$(grep API_TOKEN .env | cut -d'=' -f2)
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/YOUR_SECURE_TOKEN_HERE/$TOKEN/" config/config.yaml
else
    sed -i "s/YOUR_SECURE_TOKEN_HERE/$TOKEN/" config/config.yaml
fi

# Create necessary directories
mkdir -p logs data

# Check if Redis is available
echo "Checking Redis..."
if command -v redis-cli &> /dev/null && redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Redis is running${NC}"
    sed -i.bak 's/REDIS_ENABLED=.*/REDIS_ENABLED=true/' .env
else
    echo -e "${YELLOW}⚠️  Redis not available, using in-memory cache${NC}"
    sed -i.bak 's/REDIS_ENABLED=.*/REDIS_ENABLED=false/' .env
fi

# Run tests
echo "Running tests..."
pytest tests/ -v
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  Some tests failed (may be auth-related)${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Central API setup complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Review your .env file and config/config.yaml"
echo "2. Start the API:"
echo "   ${GREEN}./start.sh${NC}"
echo ""
echo "3. Or install as launchd service:"
echo "   ${GREEN}./install-service.sh${NC}"
echo ""
echo "4. Test the API:"
echo "   ${GREEN}curl http://localhost:3003/system/health${NC}"
echo ""
echo "5. View API docs:"
echo "   ${GREEN}http://localhost:3003/docs${NC}"
echo ""
echo "Your API token is in .env file"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
