#!/bin/bash
################################################################################
# Setup Macro Tracker Automation
# Adds cron jobs for daily reminders
################################################################################

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     MACRO TRACKER AUTOMATION SETUP                            ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

SCRIPT_PATH="$HOME/clawd/scripts/daily_macro_reminder.py"

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Script not found: $SCRIPT_PATH"
    exit 1
fi

echo "📋 Current cron jobs:"
crontab -l 2>/dev/null || echo "   (none)"
echo ""

echo "➕ Adding macro tracker reminders..."
echo ""

# Create temporary crontab
TEMP_CRON=$(mktemp)

# Preserve existing crontab
crontab -l 2>/dev/null > "$TEMP_CRON" || true

# Add macro tracker jobs (if not already present)
if ! grep -q "daily_macro_reminder.py" "$TEMP_CRON"; then
    echo "" >> "$TEMP_CRON"
    echo "# Macro Tracker Automation" >> "$TEMP_CRON"
    echo "0 8 * * * python3 $SCRIPT_PATH morning" >> "$TEMP_CRON"
    echo "30 12 * * * python3 $SCRIPT_PATH midday" >> "$TEMP_CRON"
    echo "0 20 * * * python3 $SCRIPT_PATH evening" >> "$TEMP_CRON"
    echo "0 9 * * 0 python3 $SCRIPT_PATH weekly" >> "$TEMP_CRON"
    
    # Install new crontab
    crontab "$TEMP_CRON"
    
    echo "✅ Cron jobs added successfully!"
else
    echo "ℹ️  Macro tracker jobs already exist in crontab"
fi

# Cleanup
rm "$TEMP_CRON"

echo ""
echo "📅 Schedule:"
echo "   • 8:00 AM  - Morning reminder"
echo "   • 12:30 PM - Midday check-in"
echo "   • 8:00 PM  - Evening summary"
echo "   • 9:00 AM (Sun) - Weekly report"
echo ""

echo "🧪 Test it now:"
echo "   python3 $SCRIPT_PATH morning"
echo ""

echo "✅ Setup complete!"
