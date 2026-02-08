#!/bin/bash

# Email Template Generator - Dashboard Startup Script

echo "🚀 Starting Email Template Generator Dashboard..."
echo ""

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "⚠️  Ollama not running. Starting Ollama..."
    ollama serve &
    sleep 3
fi

# Check if required model is available
if ! ollama list | grep -q "llama3.1:8b"; then
    echo "⚠️  Llama model not found. Pulling llama3.1:8b..."
    ollama pull llama3.1:8b
fi

cd "$(dirname "$0")/web"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r ../requirements.txt

# Kill any existing process on port 3002
echo "🧹 Cleaning up port 3002..."
lsof -ti:3002 | xargs kill -9 2>/dev/null

# Start the app
echo ""
echo "=" | head -c 70 | tr -d '\n' && echo ""
echo "✅ Email Template Generator Dashboard Ready!"
echo ""
echo "🌐 Dashboard: http://localhost:3002"
echo "📊 Stats API: http://localhost:3002/api/stats"
echo "💚 Health:    http://localhost:3002/health"
echo ""
echo "CLI Tool: Make executable and link:"
echo "  chmod +x cli/generate_email.py"
echo "  ln -sf $(pwd)/cli/generate_email.py /usr/local/bin/generate_email"
echo ""
echo "=" | head -c 70 | tr -d '\n' && echo ""
echo ""

python app.py
