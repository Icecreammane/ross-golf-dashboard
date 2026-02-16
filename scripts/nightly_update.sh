#!/bin/bash
# Nightly update check - runs at 4am
# Updates Clawdbot if new version available

echo "🔄 Checking for Clawdbot updates..."
cd ~/clawd

# Pull latest changes
git pull origin main

# Check if clawdbot has updates
# (This would use the gateway update command when it's working)

echo "✅ Update check complete"
