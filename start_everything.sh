#!/bin/bash
# Ross's Dashboard Launcher - One Command to Start Everything

echo "🚀 Starting Ross's Dashboard Suite..."
echo ""

# Check Python/Flask
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing Flask..."
    python3 -m pip install -q flask
fi

# Start Command Center
echo "🎯 Starting Command Center (port 5000)..."
cd ~/clawd/command-center
python3 app.py > ~/clawd/logs/command_center.log 2>&1 &
COMMAND_CENTER_PID=$!
echo "   PID: $COMMAND_CENTER_PID"

# Start Fitness Tracker
echo "💪 Starting Fitness Tracker (port 3001)..."
cd ~/clawd/fitness-dashboard
python3 app.py > ~/clawd/logs/fitness_dashboard.log 2>&1 &
FITNESS_PID=$!
echo "   PID: $FITNESS_PID"

# Wait a moment
sleep 3

echo ""
echo "✅ Dashboard suite started!"
echo ""
echo "📱 Open these in your browser:"
echo "   🎯 Command Center:  http://localhost:5000"
echo "   💪 Fitness Tracker: http://localhost:3001"
echo ""
echo "💡 Bookmark http://localhost:5000 - that's your home base!"
echo ""
echo "🛑 To stop everything:"
echo "   kill $COMMAND_CENTER_PID $FITNESS_PID"
echo ""
