#!/bin/bash
# Setup script for Hinge Auto-Pilot

set -e

echo "🚀 Setting up Hinge Auto-Pilot..."

# Install Playwright
echo "📦 Installing Playwright..."
pip3 install playwright

# Install browser
echo "🌐 Installing Chromium browser..."
python3 -m playwright install chromium

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ~/clawd/data/hinge_browser_profile
mkdir -p ~/clawd/dashboard

# Make scripts executable
echo "🔧 Setting permissions..."
chmod +x ~/clawd/scripts/hinge_auto_swipe.py
chmod +x ~/clawd/scripts/hinge_browser.py
chmod +x ~/clawd/scripts/hinge_profile_analyzer.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Test login: python3 ~/clawd/scripts/hinge_browser.py"
echo "2. Run first test: python3 ~/clawd/scripts/hinge_auto_swipe.py --dry-run"
echo "3. View dashboard: open ~/clawd/dashboard/hinge_stats.html"
echo "4. Setup automation: python3 ~/clawd/scripts/setup_hinge_cron.py"
echo ""
