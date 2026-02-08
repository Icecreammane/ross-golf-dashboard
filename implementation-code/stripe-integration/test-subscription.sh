#!/bin/bash

# Stripe Subscription Test Script
# Tests your Stripe integration setup

echo "🧪 Testing Stripe Integration..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Run: cp .env.example .env"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required environment variables
echo "✓ Checking environment variables..."
if [ -z "$STRIPE_SECRET_KEY" ]; then
    echo "❌ STRIPE_SECRET_KEY not set in .env"
    exit 1
fi
if [ -z "$STRIPE_PRICE_ID" ]; then
    echo "❌ STRIPE_PRICE_ID not set in .env"
    exit 1
fi
echo "✓ Environment variables OK"
echo ""

# Check if Flask app is running
echo "✓ Checking if Flask app is running..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✓ Flask app is running on port 3000"
else
    echo "⚠️  Warning: Flask app not running on port 3000"
    echo "   Start your app first: python app.py"
fi
echo ""

# Test Stripe API connection
echo "✓ Testing Stripe API connection..."
TEST_RESPONSE=$(curl -s https://api.stripe.com/v1/customers \
  -u "$STRIPE_SECRET_KEY:" \
  -d limit=1)

if echo "$TEST_RESPONSE" | grep -q "error"; then
    echo "❌ Stripe API Error:"
    echo "$TEST_RESPONSE" | python3 -m json.tool
    exit 1
else
    echo "✓ Connected to Stripe API"
fi
echo ""

# Create test customer
echo "✓ Creating test customer..."
TEST_EMAIL="test+$(date +%s)@example.com"
CUSTOMER_RESPONSE=$(curl -s https://api.stripe.com/v1/customers \
  -u "$STRIPE_SECRET_KEY:" \
  -d "email=$TEST_EMAIL" \
  -d "name=Test User")

CUSTOMER_ID=$(echo "$CUSTOMER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")

if [ -z "$CUSTOMER_ID" ]; then
    echo "❌ Failed to create customer"
    echo "$CUSTOMER_RESPONSE" | python3 -m json.tool
    exit 1
fi

echo "✓ Test customer created: $CUSTOMER_ID"
echo ""

# Create test checkout session
echo "✓ Creating test checkout session..."
CHECKOUT_RESPONSE=$(curl -s https://api.stripe.com/v1/checkout/sessions \
  -u "$STRIPE_SECRET_KEY:" \
  -d "customer=$CUSTOMER_ID" \
  -d "payment_method_types[]=card" \
  -d "line_items[0][price]=$STRIPE_PRICE_ID" \
  -d "line_items[0][quantity]=1" \
  -d "mode=subscription" \
  -d "success_url=http://localhost:3000/subscription/success?session_id={CHECKOUT_SESSION_ID}" \
  -d "cancel_url=http://localhost:3000/subscription/cancel")

CHECKOUT_URL=$(echo "$CHECKOUT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('url', ''))")

if [ -z "$CHECKOUT_URL" ]; then
    echo "❌ Failed to create checkout session"
    echo "$CHECKOUT_RESPONSE" | python3 -m json.tool
    exit 1
fi

echo "✓ Checkout session created"
echo ""

# Test webhook endpoint (if app is running)
if curl -s http://localhost:3000/webhooks/stripe-webhook > /dev/null 2>&1; then
    echo "✓ Testing webhook endpoint..."
    
    # Send test webhook (will fail signature verification, but tests endpoint exists)
    WEBHOOK_TEST=$(curl -s -X POST http://localhost:3000/webhooks/stripe-webhook \
      -H "Content-Type: application/json" \
      -d '{"test": true}')
    
    if echo "$WEBHOOK_TEST" | grep -q "Invalid signature"; then
        echo "✓ Webhook endpoint responding (signature verification working)"
    elif echo "$WEBHOOK_TEST" | grep -q "error"; then
        echo "✓ Webhook endpoint exists"
    fi
else
    echo "⚠️  Webhook endpoint not accessible (app not running)"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Test Customer: $CUSTOMER_ID"
echo "Test Email: $TEST_EMAIL"
echo ""
echo "🔗 Test Checkout URL:"
echo "$CHECKOUT_URL"
echo ""
echo "To test subscription flow:"
echo "1. Open the URL above in your browser"
echo "2. Use test card: 4242 4242 4242 4242"
echo "3. Use any future expiry, any CVC"
echo "4. Complete checkout"
echo "5. Check webhook events in Stripe Dashboard"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Cleanup option
echo ""
read -p "Delete test customer? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    curl -s -X DELETE "https://api.stripe.com/v1/customers/$CUSTOMER_ID" \
      -u "$STRIPE_SECRET_KEY:" > /dev/null
    echo "✓ Test customer deleted"
fi
