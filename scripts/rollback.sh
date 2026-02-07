#!/bin/bash
# Emergency rollback script

set -e

echo "🔄 FitTrack Rollback Script"
echo "============================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ENVIRONMENT=${1:-production}

echo -e "${RED}⚠️  WARNING: This will rollback $ENVIRONMENT to previous deployment${NC}"
echo ""

# Show recent deployments
if [ -f "deployments/deploy.log" ]; then
    echo "Recent deployments:"
    tail -n 5 deployments/deploy.log
    echo ""
fi

# Confirm rollback
read -p "Are you SURE you want to rollback? (type 'ROLLBACK' to confirm) " -r
echo ""

if [ "$REPLY" != "ROLLBACK" ]; then
    echo "Rollback cancelled"
    exit 0
fi

# Get previous commit
CURRENT_COMMIT=$(git rev-parse HEAD)
PREVIOUS_COMMIT=$(git rev-parse HEAD~1)

echo "Current commit: $CURRENT_COMMIT"
echo "Rolling back to: $PREVIOUS_COMMIT"
echo ""

# Revert to previous commit
echo "⏪ Reverting to previous commit..."
git checkout $PREVIOUS_COMMIT

# Deploy previous version
echo "🚀 Deploying previous version..."

if [ "$ENVIRONMENT" = "production" ]; then
    railway up --service production
elif [ "$ENVIRONMENT" = "staging" ]; then
    railway up --service staging
else
    echo -e "${RED}❌ Invalid environment: $ENVIRONMENT${NC}"
    git checkout -
    exit 1
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Rollback deployment failed!${NC}"
    git checkout -
    exit 1
fi

# Health check
echo ""
echo "⏳ Waiting 30s for deployment..."
sleep 30

echo "🏥 Running health check..."

if [ "$ENVIRONMENT" = "production" ]; then
    HEALTH_URL="${PRODUCTION_URL:-https://fittrack.app}/health"
else
    HEALTH_URL="${STAGING_URL:-https://staging.fittrack.app}/health"
fi

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Rollback successful!${NC}"
else
    echo -e "${RED}⚠️  Health check returned: $HTTP_STATUS${NC}"
    echo "Please verify manually"
fi

# Log rollback
mkdir -p deployments
echo "$(date): ROLLBACK from $CURRENT_COMMIT to $PREVIOUS_COMMIT ($ENVIRONMENT)" >> deployments/rollback.log

# Send Telegram alert
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    MESSAGE="🔄 <b>ROLLBACK EXECUTED</b>%0A%0A"
    MESSAGE+="🌐 Environment: $ENVIRONMENT%0A"
    MESSAGE+="⏪ Reverted to: ${PREVIOUS_COMMIT:0:7}%0A"
    MESSAGE+="✅ Status: $HTTP_STATUS%0A"
    MESSAGE+="%0A⚠️ Investigate the issue!"
    
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "text=${MESSAGE}" \
        -d "parse_mode=HTML" > /dev/null
    
    echo "📱 Alert sent to Telegram"
fi

echo ""
echo -e "${GREEN}✅ Rollback complete${NC}"
echo "============================"
echo ""
echo "Next steps:"
echo "1. Investigate what went wrong"
echo "2. Fix the issue"
echo "3. Deploy again when ready"
echo ""
echo "Current state: Detached HEAD at $PREVIOUS_COMMIT"
echo "Run 'git checkout main' when done investigating"
