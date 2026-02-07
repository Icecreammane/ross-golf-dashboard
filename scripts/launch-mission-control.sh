#!/bin/bash
# Launch Mission Control Dashboard
# Opens the dashboard in your default browser with a local server

cd ~/clawd

# Kill any existing server on port 8080
lsof -ti:8080 | xargs kill 2>/dev/null

# Start HTTP server in background
python3 -m http.server 8080 &>/dev/null &
SERVER_PID=$!

# Wait for server to start
sleep 1

# Open in default browser
open "http://localhost:8080/mission-control.html"

echo "🚀 Mission Control launched!"
echo "   URL: http://localhost:8080/mission-control.html"
echo "   Server PID: $SERVER_PID"
echo ""
echo "To stop: kill $SERVER_PID"
