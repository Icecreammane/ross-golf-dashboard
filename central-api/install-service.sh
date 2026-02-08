#!/bin/bash
# Install Central API as launchd service

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_NAME="com.jarvis.central-api.plist"
PLIST_SRC="$SCRIPT_DIR/$PLIST_NAME"
PLIST_DST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "📦 Installing Central API service..."

# Check if gunicorn is available in venv
if [ ! -f "$SCRIPT_DIR/venv/bin/gunicorn" ]; then
    echo "❌ Virtual environment not set up. Run ./setup.sh first"
    exit 1
fi

# Update plist with correct gunicorn path
GUNICORN_PATH="$SCRIPT_DIR/venv/bin/gunicorn"
sed "s|/usr/local/bin/gunicorn|$GUNICORN_PATH|" "$PLIST_SRC" > "/tmp/$PLIST_NAME"

# Copy to LaunchAgents
mkdir -p "$HOME/Library/LaunchAgents"
cp "/tmp/$PLIST_NAME" "$PLIST_DST"
rm "/tmp/$PLIST_NAME"

echo "✓ Plist installed to $PLIST_DST"

# Unload if already loaded
if launchctl list | grep -q "com.jarvis.central-api"; then
    echo "Stopping existing service..."
    launchctl unload "$PLIST_DST" 2>/dev/null || true
fi

# Load the service
echo "Starting service..."
launchctl load "$PLIST_DST"

# Wait a moment and check status
sleep 2

if launchctl list | grep -q "com.jarvis.central-api"; then
    echo "✅ Central API service installed and running!"
    echo ""
    echo "Service management:"
    echo "  Stop:    launchctl unload ~/Library/LaunchAgents/$PLIST_NAME"
    echo "  Start:   launchctl load ~/Library/LaunchAgents/$PLIST_NAME"
    echo "  Restart: launchctl unload ~/Library/LaunchAgents/$PLIST_NAME && launchctl load ~/Library/LaunchAgents/$PLIST_NAME"
    echo ""
    echo "View logs:"
    echo "  tail -f $SCRIPT_DIR/logs/central-api.log"
    echo "  tail -f $SCRIPT_DIR/logs/error.log"
    echo ""
    echo "Test API:"
    echo "  curl http://localhost:3003/system/health"
else
    echo "❌ Failed to start service. Check logs:"
    echo "  tail -f $SCRIPT_DIR/logs/stderr.log"
    exit 1
fi
