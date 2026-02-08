#!/bin/bash
# Start Unified Dashboard

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 Starting Unified Dashboard..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Kill any existing process on port 3000
echo "🔍 Checking for existing processes on port 3000..."
PID=$(lsof -ti:3000) || true
if [ ! -z "$PID" ]; then
    echo "⚠️  Killing existing process (PID: $PID)..."
    kill -9 $PID
    sleep 2
fi

echo ""
echo "✅ Unified Dashboard starting on port 3000"
echo "🌐 Access: http://localhost:3000"
echo "📊 Central API: http://localhost:3003/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start with Python (use gunicorn for production)
exec python3 app.py
