#!/bin/bash
# Morning Brief Setup Script
# Installs launchd service for daily 7:30am CST execution

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_SOURCE="$SCRIPT_DIR/com.jarvis.morningbrief.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.jarvis.morningbrief.plist"
PYTHON_SCRIPT="$SCRIPT_DIR/morning_brief.py"

echo "🌅 Morning Brief Setup"
echo "====================="
echo ""

# Make Python script executable
echo "📝 Making script executable..."
chmod +x "$PYTHON_SCRIPT"

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Copy plist file
echo "📋 Installing launchd configuration..."
cp "$PLIST_SOURCE" "$PLIST_DEST"

# Unload if already loaded (ignore errors)
echo "🔄 Unloading existing service (if any)..."
launchctl unload "$PLIST_DEST" 2>/dev/null || true

# Load the service
echo "⚡ Loading launchd service..."
launchctl load "$PLIST_DEST"

echo ""
echo "✅ Morning Brief service installed successfully!"
echo ""
echo "📅 Schedule: Daily at 7:30 AM CST"
echo "📝 Log file: ~/clawd/logs/morning-brief.log"
echo "📊 Output: ~/clawd/logs/morning-brief-latest.json"
echo ""
echo "Commands:"
echo "  • Test now:    python3 $PYTHON_SCRIPT"
echo "  • Check status: launchctl list | grep morningbrief"
echo "  • View logs:    tail -f ~/clawd/logs/morning-brief.log"
echo "  • Uninstall:    launchctl unload $PLIST_DEST && rm $PLIST_DEST"
echo ""
