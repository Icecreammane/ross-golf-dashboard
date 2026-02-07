#!/bin/bash

# Quick preview script for golf coaching landing page

echo "🏌️  Opening Golf Coaching Landing Page..."
echo ""
echo "📱 Preview on your phone:"
echo "   1. Make sure your phone is on same WiFi"
echo "   2. Your computer's IP: $(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "Unable to detect")"
echo "   3. Visit: http://$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "localhost"):8000"
echo ""
echo "🌐 Starting local server..."
echo "   Press Ctrl+C to stop"
echo ""

# Start simple HTTP server in the directory
cd /Users/clawdbot/clawd
python3 -m http.server 8000
