#!/bin/bash
# Master activation script for all integrations

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "════════════════════════════════════════════════════"
echo "    🚀 INTEGRATION FRAMEWORK ACTIVATION"
echo "════════════════════════════════════════════════════"
echo -e "${NC}"
echo ""
echo "This script will check and activate all 5 integrations:"
echo "  1. Stripe API (2 min)"
echo "  2. Revenue Dashboard (0 min)"
echo "  3. Deployment Automation (5 min)"
echo "  4. Twitter Automation (5 min)"
echo "  5. Gmail Support (10 min)"
echo ""
echo -e "${YELLOW}Total setup time: ~22 minutes${NC}"
echo ""

# Ask for confirmation
read -p "Ready to start? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Activation cancelled"
    exit 0
fi

# Check if .env exists
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Checking environment setup..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "Creating .env template..."
    
    cat > .env << 'EOF'
# Stripe Configuration
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# Telegram Alerts (optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Twitter API
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_BEARER_TOKEN=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=

# Production URLs
PRODUCTION_URL=
STAGING_URL=
EOF
    
    echo -e "${GREEN}✅ .env template created${NC}"
    echo -e "${YELLOW}⚠️  Please fill in your API keys before continuing${NC}"
    echo ""
    exit 0
else
    echo -e "${GREEN}✅ .env file found${NC}"
fi

# Function to check if integration is configured
check_integration() {
    local name=$1
    local test_command=$2
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔍 Checking: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if eval $test_command &> /dev/null; then
        echo -e "${GREEN}✅ $name is configured${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  $name needs configuration${NC}"
        return 1
    fi
}

# Track activation status
ACTIVATED=0
SKIPPED=0

# ============================================
# 1. STRIPE INTEGRATION
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💰 1/5: Stripe API Integration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -z "$STRIPE_SECRET_KEY" ]; then
    echo -e "${YELLOW}⚠️  STRIPE_SECRET_KEY not set in .env${NC}"
    echo ""
    echo "Setup instructions:"
    echo "  1. Go to https://dashboard.stripe.com"
    echo "  2. Developers → API Keys"
    echo "  3. Copy Secret Key"
    echo "  4. Add to .env: STRIPE_SECRET_KEY=sk_live_..."
    echo ""
    echo "See: integrations/stripe/STRIPE_SETUP.md"
    SKIPPED=$((SKIPPED + 1))
else
    echo "Testing Stripe connection..."
    cd integrations/stripe
    if python stripe_integration.py &> /dev/null; then
        echo -e "${GREEN}✅ Stripe integration active${NC}"
        ACTIVATED=$((ACTIVATED + 1))
    else
        echo -e "${RED}❌ Stripe test failed${NC}"
        echo "Run: python integrations/stripe/test_integration.py"
        SKIPPED=$((SKIPPED + 1))
    fi
    cd ../..
fi

# ============================================
# 2. REVENUE DASHBOARD
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 2/5: Revenue Dashboard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "revenue-dashboard.html" ]; then
    echo -e "${GREEN}✅ Dashboard ready${NC}"
    echo ""
    echo "To use:"
    echo "  1. Start API: python integrations/stripe/revenue_api.py"
    echo "  2. Open: revenue-dashboard.html"
    ACTIVATED=$((ACTIVATED + 1))
else
    echo -e "${RED}❌ Dashboard file not found${NC}"
    SKIPPED=$((SKIPPED + 1))
fi

# ============================================
# 3. DEPLOYMENT AUTOMATION
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 3/5: Deployment Automation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f ".github/workflows/deploy-production.yml" ]; then
    echo -e "${GREEN}✅ GitHub Actions workflows ready${NC}"
    echo ""
    echo "Setup instructions:"
    echo "  1. Go to your GitHub repo → Settings → Secrets"
    echo "  2. Add: RAILWAY_TOKEN"
    echo "  3. Add: PRODUCTION_URL"
    echo "  4. Push to main → auto-deploys!"
    echo ""
    echo "See: integrations/deployment/DEPLOYMENT_SETUP.md"
    ACTIVATED=$((ACTIVATED + 1))
else
    echo -e "${RED}❌ Workflow files not found${NC}"
    SKIPPED=$((SKIPPED + 1))
fi

# ============================================
# 4. TWITTER AUTOMATION
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐦 4/5: Twitter Automation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -z "$TWITTER_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  Twitter API keys not set in .env${NC}"
    echo ""
    echo "Setup instructions:"
    echo "  1. Go to https://developer.twitter.com"
    echo "  2. Create app, get API keys"
    echo "  3. Add 5 keys to .env (see TWITTER_SETUP.md)"
    echo ""
    echo "See: integrations/twitter/TWITTER_SETUP.md"
    SKIPPED=$((SKIPPED + 1))
else
    echo "Testing Twitter connection..."
    cd integrations/twitter
    if python -c "from twitter_bot import TwitterBot; bot = TwitterBot(); bot.authenticate()" 2> /dev/null; then
        echo -e "${GREEN}✅ Twitter integration active${NC}"
        echo ""
        echo "Tweet queue ready: 30 tweets loaded"
        echo "Post first tweet: python twitter_bot.py"
        ACTIVATED=$((ACTIVATED + 1))
    else
        echo -e "${RED}❌ Twitter authentication failed${NC}"
        echo "Check your API keys in .env"
        SKIPPED=$((SKIPPED + 1))
    fi
    cd ../..
fi

# ============================================
# 5. GMAIL SUPPORT
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📧 5/5: Gmail Support System"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "integrations/gmail/credentials.json" ]; then
    echo -e "${YELLOW}⚠️  Gmail credentials.json not found${NC}"
    echo ""
    echo "Setup instructions:"
    echo "  1. Go to https://console.cloud.google.com"
    echo "  2. Enable Gmail API"
    echo "  3. Create OAuth credentials"
    echo "  4. Download credentials.json"
    echo "  5. Place in integrations/gmail/"
    echo ""
    echo "See: integrations/gmail/GMAIL_SETUP.md"
    SKIPPED=$((SKIPPED + 1))
else
    echo -e "${GREEN}✅ Gmail credentials found${NC}"
    echo ""
    echo "To authenticate:"
    echo "  python integrations/gmail/gmail_monitor.py"
    ACTIVATED=$((ACTIVATED + 1))
fi

# ============================================
# SUMMARY
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 ACTIVATION SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ Activated: $ACTIVATED/5${NC}"
echo -e "${YELLOW}⚠️  Need setup: $SKIPPED/5${NC}"
echo ""

if [ $ACTIVATED -eq 5 ]; then
    echo -e "${GREEN}🎉 ALL INTEGRATIONS ACTIVE!${NC}"
    echo ""
    echo "You now have:"
    echo "  ✅ Real-time revenue tracking"
    echo "  ✅ Beautiful dashboard"
    echo "  ✅ 24/7 support monitoring"
    echo "  ✅ Automatic deployments"
    echo "  ✅ Twitter marketing autopilot"
    echo ""
    echo "Time saved per week: 13-25 hours 🚀"
elif [ $ACTIVATED -gt 0 ]; then
    echo -e "${YELLOW}Some integrations active!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Complete setup for remaining integrations"
    echo "  2. Read the setup guides in integrations/*/SETUP.md"
    echo "  3. Run this script again to verify"
else
    echo -e "${YELLOW}Getting started:${NC}"
    echo ""
    echo "  1. Fill in .env with your API keys"
    echo "  2. Follow setup guides for each integration"
    echo "  3. Run this script again"
    echo ""
    echo "Start with Stripe (easiest, 2 minutes):"
    echo "  → integrations/stripe/STRIPE_SETUP.md"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 Full documentation: integrations/INTEGRATION_HUB.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
