#!/bin/bash
# Cron Setup Script
# Installs all Jarvis automation jobs
# Idempotent - safe to run multiple times

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
AUTOMATION_DIR="$HOME/clawd/automation"
JOBS_DIR="$AUTOMATION_DIR/jobs"
LOG_DIR="$HOME/clawd/logs/cron"
BACKUP_DIR="$AUTOMATION_DIR/backups"
CRON_COMMENT="# Jarvis Automation"

# Ensure directories exist
mkdir -p "$LOG_DIR" "$BACKUP_DIR"

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Banner
echo "================================================"
echo "   Jarvis Automation Setup"
echo "================================================"
echo ""

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    log_warn "This script is designed for macOS. Your OS: $(uname)"
    echo -n "Continue anyway? [y/N] "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log_info "Setup cancelled"
        exit 0
    fi
fi

# Verify job scripts exist
log_info "Verifying job scripts..."
MISSING_SCRIPTS=0
for script in morning-brief.sh deal-flow-update.sh nba-update.sh health-check.sh evening-checkin.sh overnight-research.sh; do
    if [[ ! -f "$JOBS_DIR/$script" ]]; then
        log_error "Missing script: $script"
        MISSING_SCRIPTS=1
    else
        log_info "  ✓ Found $script"
    fi
done

if [[ $MISSING_SCRIPTS -eq 1 ]]; then
    log_error "Some scripts are missing. Cannot continue."
    exit 1
fi

# Make scripts executable
log_info "Setting execute permissions..."
chmod +x "$JOBS_DIR"/*.sh
log_info "  ✓ All scripts are executable"

# Backup existing crontab
log_info "Backing up current crontab..."
BACKUP_FILE="$BACKUP_DIR/crontab-backup-$(date +%Y%m%d-%H%M%S).txt"
if crontab -l > "$BACKUP_FILE" 2>/dev/null; then
    log_info "  ✓ Backup saved to: $BACKUP_FILE"
else
    log_warn "  No existing crontab to backup"
    echo "" > "$BACKUP_FILE"
fi

# Get current crontab
CURRENT_CRON=$(crontab -l 2>/dev/null || echo "")

# Remove old Jarvis automation entries
log_info "Removing old automation entries..."
CLEANED_CRON=$(echo "$CURRENT_CRON" | grep -v "$CRON_COMMENT" || echo "")

# Define jobs
declare -A JOBS=(
    ["morning-brief"]="30 7 * * *"
    ["deal-flow-update"]="0 9 * * *"
    ["nba-update"]="0 10 * * *"
    ["health-check"]="0 12 * * *"
    ["evening-checkin"]="0 20 * * *"
    ["overnight-research"]="0 23 * * *"
)

# Build new crontab
log_info "Installing cron jobs..."
NEW_CRON="$CLEANED_CRON"

# Add header
if [[ -n "$NEW_CRON" && ! "$NEW_CRON" =~ [[:space:]]$ ]]; then
    NEW_CRON="$NEW_CRON"$'\n'
fi

NEW_CRON="$NEW_CRON"$'\n'
NEW_CRON="$NEW_CRON$CRON_COMMENT Jobs (installed $(date +%Y-%m-%d))"$'\n'

# Add each job
for job in morning-brief deal-flow-update nba-update health-check evening-checkin overnight-research; do
    schedule="${JOBS[$job]}"
    script="$JOBS_DIR/${job}.sh"
    NEW_CRON="$NEW_CRON${schedule} ${script}  $CRON_COMMENT ${job}"$'\n'
    log_info "  ✓ Added $job (${schedule})"
done

# Install new crontab
log_info "Installing new crontab..."
echo "$NEW_CRON" | crontab -

# Verify installation
log_info "Verifying installation..."
INSTALLED_COUNT=$(crontab -l | grep -c "$CRON_COMMENT" || echo "0")

if [[ $INSTALLED_COUNT -ge 6 ]]; then
    log_info "  ✓ Successfully installed $INSTALLED_COUNT jobs"
else
    log_error "  Installation may have failed (found $INSTALLED_COUNT jobs)"
    exit 1
fi

# Create state file
STATE_FILE="$AUTOMATION_DIR/.cron-installed"
date +%Y-%m-%d-%H:%M:%S > "$STATE_FILE"

# Display schedule
echo ""
echo "================================================"
echo "   Installation Complete!"
echo "================================================"
echo ""
echo "Installed Jobs:"
echo "  7:30am - Morning Brief (voice)"
echo "  9:00am - Deal Flow Update"
echo " 10:00am - NBA Rankings Refresh"
echo " 12:00pm - System Health Check"
echo "  8:00pm - Evening Check-in"
echo " 11:00pm - Overnight Research & Maintenance"
echo ""
echo "Management:"
echo "  List jobs:      python3 $AUTOMATION_DIR/cron-manager.py list"
echo "  Check status:   python3 $AUTOMATION_DIR/cron-manager.py status"
echo "  View logs:      python3 $AUTOMATION_DIR/cron-manager.py logs <job>"
echo "  Test job:       python3 $AUTOMATION_DIR/cron-manager.py test <job>"
echo "  Enable job:     python3 $AUTOMATION_DIR/cron-manager.py enable <job>"
echo "  Disable job:    python3 $AUTOMATION_DIR/cron-manager.py disable <job>"
echo ""
echo "Documentation: $AUTOMATION_DIR/CRON_SCHEDULE.md"
echo ""
echo "Backup saved to: $BACKUP_FILE"
echo "================================================"
