#!/bin/bash
# Start Spending Tracker Dashboard

WORKSPACE="$HOME/clawd"

echo "🚀 Starting Spending Tracker Dashboard..."

# Check if transactions exist
if [ ! -f "$WORKSPACE/data/transactions.json" ]; then
    echo "⚠️  No transactions found!"
    echo "Run: python3 scripts/sync_transactions.py --initial"
    exit 1
fi

# Start API in background
echo "📊 Starting API server..."
cd "$WORKSPACE"
python3 scripts/spending_api.py &
API_PID=$!

# Wait for API to start
sleep 2

# Open dashboard
echo "🌐 Opening dashboard..."
open dashboard/spending.html

echo "✅ Dashboard running!"
echo "📍 API: http://localhost:5002"
echo "🛑 To stop: kill $API_PID"

# Keep script running
wait $API_PID
