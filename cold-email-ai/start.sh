#!/bin/bash
# Cold Email AI - Start Script

echo "🚀 Starting Cold Email AI Platform..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY not set in environment"
    echo "Please set it: export OPENAI_API_KEY='your-key-here'"
    echo ""
fi

# Kill any existing process on port 3001
echo "🔍 Checking for existing process on port 3001..."
lsof -ti:3001 | xargs kill -9 2>/dev/null || true

# Start the app
echo "✨ Starting Flask app on http://localhost:3001"
echo "🌐 App: http://localhost:3001"
echo "📄 Landing page: http://localhost:3001/landing"
echo ""
python app.py
