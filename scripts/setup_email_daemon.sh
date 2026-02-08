#!/bin/bash
# Setup script for Jarvis Email Daemon

set -e

WORKSPACE="/Users/clawdbot/clawd"
PLIST_PATH="$HOME/Library/LaunchAgents/com.jarvis.email-daemon.plist"

echo "========================================="
echo "Jarvis Email Daemon Setup"
echo "========================================="
echo ""

# Check if .env exists
if [ ! -f "$WORKSPACE/.env" ]; then
    echo "❌ .env file not found!"
    exit 1
fi

# Check if password is set
if grep -q "your-gmail-app-password-here" "$WORKSPACE/.env"; then
    echo "⚠️  Gmail app password not configured yet"
    echo ""
    echo "To set up Gmail IMAP access:"
    echo "1. Go to: https://myaccount.google.com/apppasswords"
    echo "2. Sign in as bigmeatyclawd@gmail.com"
    echo "3. Create app password for 'Mail' on 'Mac mini'"
    echo "4. Copy the 16-character password (remove spaces)"
    echo "5. Edit .env file:"
    echo "   nano $WORKSPACE/.env"
    echo "6. Replace 'your-gmail-app-password-here' with actual password"
    echo ""
    read -p "Press Enter after you've set the password, or Ctrl+C to exit..."
fi

# Verify python dependencies
echo "Checking Python dependencies..."
if ! python3 -c "import imaplib, email, json, dotenv" 2>/dev/null; then
    echo "❌ Missing Python dependencies"
    echo "Installing python-dotenv..."
    pip3 install python-dotenv
fi

echo "✅ Python dependencies OK"
echo ""

# Make daemon executable
echo "Setting permissions..."
chmod +x "$WORKSPACE/scripts/email_daemon.py"
echo "✅ Script executable"
echo ""

# Test daemon once
echo "Testing daemon (dry run)..."
if python3 "$WORKSPACE/scripts/email_daemon.py"; then
    echo "✅ Daemon test successful"
else
    echo "❌ Daemon test failed - check logs:"
    echo "   tail $WORKSPACE/logs/email-daemon.log"
    exit 1
fi
echo ""

# Load launchd service
echo "Loading launchd service..."
if launchctl list | grep -q "com.jarvis.email-daemon"; then
    echo "Service already loaded, reloading..."
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
fi

launchctl load "$PLIST_PATH"
echo "✅ Service loaded"
echo ""

# Verify service is loaded
if launchctl list | grep -q "com.jarvis.email-daemon"; then
    echo "✅ Service verified in launchctl"
else
    echo "⚠️  Service not found in launchctl list"
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "The daemon will now check emails every 30 minutes."
echo ""
echo "View logs:"
echo "  tail -f $WORKSPACE/logs/email-daemon.log"
echo ""
echo "View summaries:"
echo "  cat $WORKSPACE/data/email-summary.json | python3 -m json.tool"
echo ""
echo "Manual run:"
echo "  python3 $WORKSPACE/scripts/email_daemon.py"
echo ""
echo "Force run now:"
echo "  launchctl start com.jarvis.email-daemon"
echo ""
echo "Documentation:"
echo "  cat $WORKSPACE/EMAIL_DAEMON.md"
echo ""
