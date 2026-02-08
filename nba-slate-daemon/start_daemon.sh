#!/bin/bash

# NBA Slate Rankings Daemon Startup Script

echo "🏀 Starting NBA Slate Rankings Daemon..."
echo "Target Date: Monday, February 9, 2026"
echo "Dashboard: http://localhost:5051"
echo ""

cd /Users/clawdbot/clawd/nba-slate-daemon

# Check Python dependencies
echo "Checking dependencies..."
pip3 install -q -r requirements.txt

# Create data directory
mkdir -p /Users/clawdbot/clawd/data

# Start the Flask app
echo ""
echo "Starting dashboard server..."
python3 app.py
