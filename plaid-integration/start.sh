#!/bin/bash
# Quick start script for Plaid Finance Dashboard

echo "🚀 Starting Plaid Finance Dashboard..."
echo ""

# Check if dependencies are installed
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Start the server
echo "🔗 Dashboard starting on http://localhost:3100"
echo "💰 Click '+ Link Bank Account' to get started"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 app.py
