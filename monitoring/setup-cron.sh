#!/bin/bash
# Setup cron job for monitoring
# This will run checks every hour from 7am-11pm

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_LINE="0 7-23 * * * cd $SCRIPT_DIR && ./run-checks.sh"

echo "Installing monitoring cron job..."
echo "Will run every hour from 7am to 11pm"
echo ""
echo "Cron entry:"
echo "$CRON_LINE"
echo ""

# Check if cron entry already exists
if crontab -l 2>/dev/null | grep -q "run-checks.sh"; then
    echo "Monitoring cron job already exists!"
    echo "Remove it first with: crontab -l | grep -v run-checks.sh | crontab -"
    exit 1
fi

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -

echo "✅ Cron job installed successfully!"
echo ""
echo "To view: crontab -l"
echo "To remove: crontab -l | grep -v run-checks.sh | crontab -"
echo ""
echo "Test it now with: cd $SCRIPT_DIR && ./run-checks.sh --force"
