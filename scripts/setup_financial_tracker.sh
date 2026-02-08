#!/bin/bash
# Setup script for Financial Tracker Daemon

echo "🚀 Setting up Financial Tracker Daemon..."
echo ""

# Ensure directories exist
echo "Creating directories..."
mkdir -p ~/clawd/data
mkdir -p ~/clawd/logs
mkdir -p ~/Library/LaunchAgents

# Make scripts executable
echo "Making scripts executable..."
chmod +x ~/clawd/scripts/financial_tracker.py
chmod +x ~/clawd/scripts/test_financial_tracker.py
chmod +x ~/clawd/scripts/finance_entry.sh
chmod +x ~/clawd/scripts/finance_report.sh

# Run tests
echo ""
echo "Running test suite..."
python3 ~/clawd/scripts/test_financial_tracker.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
else
    echo ""
    echo "❌ Tests failed. Please check the output above."
    exit 1
fi

# Load launchd service
echo ""
echo "Loading launchd service..."
if [ -f ~/Library/LaunchAgents/com.jarvis.financial-tracker.plist ]; then
    # Unload if already loaded
    launchctl unload ~/Library/LaunchAgents/com.jarvis.financial-tracker.plist 2>/dev/null
    
    # Load the service
    launchctl load ~/Library/LaunchAgents/com.jarvis.financial-tracker.plist
    
    echo "✅ Daemon loaded! Will run daily at 6:00 AM"
    echo ""
    echo "To verify:"
    echo "  launchctl list | grep financial-tracker"
else
    echo "⚠️  launchd plist not found. Skipping daemon setup."
fi

echo ""
echo "📊 Financial Tracker Setup Complete!"
echo ""
echo "Quick commands:"
echo "  Entry:  bash ~/clawd/scripts/finance_entry.sh"
echo "  Report: bash ~/clawd/scripts/finance_report.sh"
echo "  Logs:   tail -f ~/clawd/logs/financial-daemon.log"
echo ""
echo "Next step: Run manual entry to initialize data"
echo "  bash ~/clawd/scripts/finance_entry.sh"
echo ""
