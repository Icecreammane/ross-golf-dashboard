#!/bin/bash
# Setup script for Core Assistant Features
# Run: bash scripts/setup_assistant_features.sh

set -e  # Exit on error

echo "🚀 Setting up Core Assistant Features..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama not found. Email triage requires Ollama.${NC}"
    echo "   Install: brew install ollama"
else
    echo -e "${GREEN}✅ Ollama found${NC}"
    
    # Pull qwen2.5 model if not present
    if ! ollama list | grep -q qwen2.5; then
        echo "📦 Pulling qwen2.5 model for email classification..."
        ollama pull qwen2.5
    fi
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p ~/clawd/data
mkdir -p ~/clawd/logs
mkdir -p ~/clawd/credentials
echo -e "${GREEN}✅ Directories created${NC}"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -q -r requirements-assistant-features.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Make scripts executable
echo ""
echo "🔧 Making scripts executable..."
chmod +x scripts/financial_dashboard.py
chmod +x scripts/financial_sync_daemon.py
chmod +x scripts/find_reservation.py
chmod +x scripts/reservation_check_daemon.py
chmod +x scripts/email_triage.py
chmod +x scripts/email_triage_daemon.py
echo -e "${GREEN}✅ Scripts made executable${NC}"

# Setup instructions
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ SETUP COMPLETE!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1️⃣  FINANCIAL DASHBOARD"
echo "   Setup Plaid credentials (sandbox for testing):"
echo "   → export PLAID_CLIENT_ID='sandbox'"
echo "   → export PLAID_SECRET='sandbox'"
echo "   → export PLAID_ENV='sandbox'"
echo ""
echo "   Start dashboard:"
echo "   → python3 scripts/financial_dashboard.py"
echo "   → Open: http://localhost:8082/finances"
echo ""
echo "2️⃣  RESERVATION FINDER"
echo "   Search for reservations:"
echo "   → python3 scripts/find_reservation.py --party 2 --time '7pm' --cuisine Italian --location Nashville"
echo ""
echo "3️⃣  EMAIL TRIAGE"
echo "   Setup Gmail API credentials:"
echo "   → Get credentials from: https://console.cloud.google.com/"
echo "   → Place at: ~/clawd/credentials/gmail_credentials.json"
echo ""
echo "   Authenticate:"
echo "   → python3 scripts/email_triage.py --setup"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Documentation:"
echo "   → docs/QUICK_START.md (5-minute guide)"
echo "   → docs/ASSISTANT_FEATURES_README.md (full documentation)"
echo ""
echo "🎉 Ready to impress people!"
echo ""
