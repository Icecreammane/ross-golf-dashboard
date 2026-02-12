#!/bin/bash

# Fitness Dashboard Startup Script

cd ~/clawd/fitness-dashboard

echo "🏋️  Starting Fitness Progress Dashboard..."
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing Flask..."
    pip3 install Flask
    echo ""
fi

# Make app.py executable
chmod +x app.py

echo "✅ Starting server on http://localhost:3001"
echo ""
echo "📊 Dashboard features:"
echo "   - Calorie tracking (2200 cal goal)"
echo "   - Workout logging"
echo "   - Weight tracking"
echo "   - Macro breakdown (200g protein goal)"
echo "   - Auto-refresh every 30 seconds"
echo ""
echo "Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the Flask app
python3 app.py
