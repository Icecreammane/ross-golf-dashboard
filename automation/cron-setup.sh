#!/bin/bash
# Cron Automation Setup Script
# Installs all automated jobs for Jarvis Integration Hub

set -e  # Exit on error

echo "🤖 Jarvis Cron Automation Setup"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base directory
CLAWD_DIR="$HOME/clawd"
LOG_DIR="$CLAWD_DIR/logs/cron"
AUTOMATION_DIR="$CLAWD_DIR/automation"

# Create log directories
echo "📁 Creating log directories..."
mkdir -p "$LOG_DIR"
mkdir -p "$CLAWD_DIR/monitoring"
echo -e "${GREEN}✓${NC} Directories created"

# Check if required scripts exist
echo ""
echo "🔍 Checking for required scripts..."

REQUIRED_SCRIPTS=(
    "$AUTOMATION_DIR/health-monitor.py"
    "$CLAWD_DIR/systems/hub-api.py"
)

OPTIONAL_SCRIPTS=(
    "$CLAWD_DIR/systems/morning-brief-generator.py"
    "$CLAWD_DIR/revenue/deal-flow/scraper.py"
    "$CLAWD_DIR/nba/update-rankings.py"
    "$CLAWD_DIR/systems/evening-checkin.py"
    "$CLAWD_DIR/systems/overnight-tasks.py"
)

for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        echo -e "${GREEN}✓${NC} Found: $script"
    else
        echo -e "${RED}✗${NC} Missing: $script"
        echo -e "${YELLOW}⚠${NC}  This is required! Setup incomplete."
        exit 1
    fi
done

for script in "${OPTIONAL_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        echo -e "${GREEN}✓${NC} Found: $script"
    else
        echo -e "${YELLOW}⚠${NC}  Optional script not found: $script"
        echo "   (Will skip this cron job)"
    fi
done

# Verify Python dependencies
echo ""
echo "🐍 Checking Python dependencies..."
python3 -c "import flask, psutil, requests" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Python dependencies installed"
else
    echo -e "${YELLOW}⚠${NC}  Missing Python packages. Installing..."
    pip3 install flask flask-cors psutil requests -q
    echo -e "${GREEN}✓${NC} Dependencies installed"
fi

# Backup existing crontab
echo ""
echo "💾 Backing up existing crontab..."
crontab -l > "$CLAWD_DIR/automation/crontab.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || echo "No existing crontab"

# Build new cron entries
echo ""
echo "📝 Building cron entries..."

CRON_ENTRIES="# Jarvis Integration Hub - Automated Jobs
# Generated: $(date)

# Health Monitor - Every 5 minutes
*/5 * * * * python3 $AUTOMATION_DIR/health-monitor.py >> $LOG_DIR/health-monitor.log 2>&1

# Hub API - Auto-start on reboot
@reboot sleep 30 && cd $CLAWD_DIR/systems && python3 hub-api.py >> $LOG_DIR/hub-api.log 2>&1 &
"

# Add optional jobs only if scripts exist
if [ -f "$CLAWD_DIR/systems/morning-brief-generator.py" ]; then
    CRON_ENTRIES+="
# Morning Brief - 7:30 AM daily
30 7 * * * cd $CLAWD_DIR && python3 systems/morning-brief-generator.py >> $LOG_DIR/morning-brief.log 2>&1
"
fi

if [ -f "$CLAWD_DIR/revenue/deal-flow/scraper.py" ]; then
    CRON_ENTRIES+="
# Deal Flow Scraper - 9:00 AM daily
0 9 * * * cd $CLAWD_DIR/revenue/deal-flow && python3 scraper.py >> $LOG_DIR/deal-flow.log 2>&1
"
fi

if [ -f "$CLAWD_DIR/nba/update-rankings.py" ]; then
    CRON_ENTRIES+="
# NBA Rankings Update - 10:00 AM daily
0 10 * * * cd $CLAWD_DIR/nba && python3 update-rankings.py >> $LOG_DIR/nba-update.log 2>&1
"
fi

if [ -f "$CLAWD_DIR/systems/evening-checkin.py" ]; then
    CRON_ENTRIES+="
# Evening Check-in - 8:00 PM daily
0 20 * * * cd $CLAWD_DIR && python3 systems/evening-checkin.py >> $LOG_DIR/evening-checkin.log 2>&1
"
fi

if [ -f "$CLAWD_DIR/systems/overnight-tasks.py" ]; then
    CRON_ENTRIES+="
# Overnight Tasks - 11:00 PM daily
0 23 * * * cd $CLAWD_DIR && python3 systems/overnight-tasks.py >> $LOG_DIR/overnight.log 2>&1
"
fi

# Dry run option
if [ "$1" = "--dry-run" ]; then
    echo ""
    echo -e "${YELLOW}DRY RUN MODE${NC} - Cron entries that would be installed:"
    echo "================================================================"
    echo "$CRON_ENTRIES"
    echo "================================================================"
    echo ""
    echo "Run without --dry-run to install"
    exit 0
fi

# Install cron jobs
echo ""
echo "⚙️  Installing cron jobs..."

# Get existing crontab (excluding old Jarvis entries)
EXISTING_CRONTAB=$(crontab -l 2>/dev/null | grep -v "# Jarvis Integration Hub" | grep -v "health-monitor.py" | grep -v "hub-api.py" | grep -v "morning-brief" | grep -v "deal-flow" | grep -v "nba" | grep -v "evening-checkin" | grep -v "overnight-tasks" || true)

# Combine and install
{
    echo "$EXISTING_CRONTAB"
    echo ""
    echo "$CRON_ENTRIES"
} | crontab -

echo -e "${GREEN}✓${NC} Cron jobs installed"

# Display installed jobs
echo ""
echo "📋 Installed cron jobs:"
echo "================================================================"
crontab -l | grep -A 20 "# Jarvis Integration Hub"
echo "================================================================"

# Test health monitor manually
echo ""
echo "🧪 Testing health monitor..."
python3 "$AUTOMATION_DIR/health-monitor.py"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Health monitor test passed"
else
    echo -e "${RED}✗${NC} Health monitor test failed"
fi

echo ""
echo -e "${GREEN}✅ Cron automation setup complete!${NC}"
echo ""
echo "📊 Next steps:"
echo "  1. Check logs: tail -f $LOG_DIR/health-monitor.log"
echo "  2. View cron jobs: crontab -l"
echo "  3. Start Hub API now: cd $CLAWD_DIR/systems && python3 hub-api.py"
echo "  4. Monitor system: open http://10.0.0.18:8080/dashboard/status.html"
echo ""
echo "💡 Tip: Run 'bash $0 --dry-run' to see what would be installed"
