#!/bin/bash
# Start Revenue Dashboard

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Check if .env is configured
if grep -q "your_stripe_secret_key_here" .env 2>/dev/null; then
    echo "⚠️  WARNING: .env file contains default values"
    echo "   Edit .env and add your actual Stripe API keys"
    echo ""
fi

# Start the application
echo "🚀 Starting Revenue Dashboard on port 3002..."
echo "   Dashboard: http://localhost:3002"
echo "   Health: http://localhost:3002/health"
echo ""

python app.py
