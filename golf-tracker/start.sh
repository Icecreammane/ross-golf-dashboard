#!/bin/bash
# Golf Tracker Startup Script
# Quick launcher for the Golf Tracker web application

echo "⛳ Starting Golf Tracker..."
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "Error: app.py not found. Are you in the golf-tracker directory?"
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check dependencies
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
fi

# Create data directory if it doesn't exist
mkdir -p /Users/clawdbot/clawd/data

echo "Starting web server on http://localhost:5050"
echo "Press Ctrl+C to stop"
echo ""

# Start the application
python app.py
