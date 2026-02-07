#!/bin/bash
# Manual deployment script (backup/alternative to GitHub Actions)

set -e  # Exit on error

echo "🚀 FitTrack Deployment Script"
echo "=============================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BRANCH=${1:-main}
ENVIRONMENT=${2:-production}

echo -e "${YELLOW}Branch: $BRANCH${NC}"
echo -e "${YELLOW}Environment: $ENVIRONMENT${NC}"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI not found${NC}"
    echo "Install with: npm i -g @railway/cli"
    exit 1
fi

# Check if on correct branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo -e "${YELLOW}⚠️  Currently on branch: $CURRENT_BRANCH${NC}"
    echo "Switching to $BRANCH..."
    git checkout $BRANCH
fi

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin $BRANCH

# Run tests (if test file exists)
if [ -f "tests/test_suite.py" ]; then
    echo "🧪 Running tests..."
    python tests/test_suite.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Tests failed! Aborting deployment.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  No tests found, skipping...${NC}"
fi

# Confirm deployment
echo ""
echo -e "${YELLOW}About to deploy to $ENVIRONMENT${NC}"
echo "Last commit: $(git log -1 --oneline)"
echo ""
read -p "Continue with deployment? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

# Deploy to Railway
echo "🚀 Deploying to Railway..."

if [ "$ENVIRONMENT" = "production" ]; then
    railway up --service production
elif [ "$ENVIRONMENT" = "staging" ]; then
    railway up --service staging
else
    echo -e "${RED}❌ Invalid environment: $ENVIRONMENT${NC}"
    exit 1
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Deployment failed!${NC}"
    exit 1
fi

# Health check
echo ""
echo "⏳ Waiting 30s for deployment to stabilize..."
sleep 30

echo "🏥 Running health check..."

# Load environment URL
if [ "$ENVIRONMENT" = "production" ]; then
    HEALTH_URL="${PRODUCTION_URL:-https://fittrack.app}/health"
else
    HEALTH_URL="${STAGING_URL:-https://staging.fittrack.app}/health"
fi

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
    echo "🌐 Live at: $HEALTH_URL"
else
    echo -e "${RED}⚠️  Health check returned status: $HTTP_STATUS${NC}"
    echo "Please verify deployment manually"
fi

# Log deployment
mkdir -p deployments
echo "$(date): Deployed $BRANCH to $ENVIRONMENT ($(git rev-parse --short HEAD))" >> deployments/deploy.log

# Send Telegram notification (if configured)
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    MESSAGE="🚀 <b>Manual Deploy Complete</b>%0A%0A"
    MESSAGE+="🌐 Environment: $ENVIRONMENT%0A"
    MESSAGE+="📝 Commit: $(git rev-parse --short HEAD)%0A"
    MESSAGE+="✅ Status: $HTTP_STATUS%0A"
    MESSAGE+="%0A🎉 Live now!"
    
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "text=${MESSAGE}" \
        -d "parse_mode=HTML" > /dev/null
    
    echo "📱 Telegram notification sent"
fi

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo "=============================="
