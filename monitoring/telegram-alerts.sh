#!/bin/bash

################################################################################
# Telegram Alert Script for FitTrack Monitoring
#
# Purpose: Send instant Telegram alerts when FitTrack goes down or recovers
# Location: ~/clawd/monitoring/telegram-alerts.sh
# Usage: ./telegram-alerts.sh "URL" "REASON" "STATUS"
#
# Examples:
#   ./telegram-alerts.sh "https://fittrack.app" "502 Bad Gateway" "down"
#   ./telegram-alerts.sh "https://fittrack.app" "5 minutes" "up"
#
# Integration:
#   - Can be called by UptimeRobot webhook
#   - Can be called by custom monitoring scripts
#   - Can be run manually for testing
################################################################################

# Configuration
TELEGRAM_BOT_TOKEN="7869330755:AAEj9m1oMCLcXzHy09TlqxlCZ3E6zlZXaM4"  # Jarvis bot token
TELEGRAM_CHAT_ID="8412148376"  # Ross's Telegram user ID

# Function: Send Telegram message
send_alert() {
    local SITE_URL="$1"
    local REASON="$2"
    local STATUS="$3"  # "down" or "up"
    
    # Validate inputs
    if [ -z "$SITE_URL" ] || [ -z "$REASON" ] || [ -z "$STATUS" ]; then
        echo "ERROR: Missing required arguments"
        echo "Usage: $0 <URL> <REASON> <STATUS>"
        echo "Example: $0 'https://fittrack.app' '502 Bad Gateway' 'down'"
        exit 1
    fi
    
    # Build message based on status
    if [ "$STATUS" = "down" ]; then
        EMOJI="🚨"
        TITLE="*ALERT: FitTrack is DOWN*"
        MESSAGE="$TITLE

Site: \`$SITE_URL\`
Reason: $REASON
Time: $(date '+%Y-%m-%d %H:%M:%S')

Investigating now..."
    
    elif [ "$STATUS" = "up" ]; then
        EMOJI="✅"
        TITLE="*FitTrack is BACK UP*"
        MESSAGE="$TITLE

Site: \`$SITE_URL\`
Downtime: $REASON
Recovered: $(date '+%Y-%m-%d %H:%M:%S')

All systems operational."
    
    else
        # Unknown status
        EMOJI="ℹ️"
        TITLE="*FitTrack Status Update*"
        MESSAGE="$TITLE

Site: \`$SITE_URL\`
Info: $REASON
Status: $STATUS
Time: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    # Send via Telegram Bot API
    RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d chat_id="$TELEGRAM_CHAT_ID" \
        -d text="$EMOJI $MESSAGE" \
        -d parse_mode="Markdown")
    
    # Check if send was successful
    if echo "$RESPONSE" | grep -q '"ok":true'; then
        echo "✅ Alert sent successfully to Telegram"
        return 0
    else
        echo "❌ Failed to send Telegram alert"
        echo "Response: $RESPONSE"
        return 1
    fi
}

# Function: Send test alert
send_test_alert() {
    echo "Sending test alert..."
    send_alert "https://fittrack-test.com" "Test alert from monitoring script" "test"
    echo "Check your Telegram for the message."
}

# Main execution
case "$1" in
    test|--test|-t)
        # Test mode
        send_test_alert
        ;;
    
    help|--help|-h)
        # Help text
        cat << EOF
Telegram Alert Script for FitTrack Monitoring

Usage:
  $0 <URL> <REASON> <STATUS>
  $0 test             # Send a test alert
  $0 help             # Show this help

Arguments:
  URL     - Site URL being monitored
  REASON  - Error message or downtime duration
  STATUS  - "down" or "up"

Examples:
  # Site went down
  $0 "https://fittrack.app" "502 Bad Gateway" "down"
  
  # Site recovered
  $0 "https://fittrack.app" "5 minutes" "up"
  
  # Test the alert system
  $0 test

Integration with UptimeRobot:
  1. Create webhook endpoint in Flask app (see MONITORING_SETUP_GUIDE.md)
  2. UptimeRobot webhook calls your Flask endpoint
  3. Flask endpoint calls this script with appropriate params

Manual monitoring script example:
  #!/bin/bash
  RESPONSE=\$(curl -s -o /dev/null -w "%{http_code}" https://fittrack.app/health)
  if [ "\$RESPONSE" != "200" ]; then
    ~/clawd/monitoring/telegram-alerts.sh "https://fittrack.app" "HTTP \$RESPONSE" "down"
  fi
EOF
        ;;
    
    *)
        # Normal alert
        if [ $# -lt 3 ]; then
            echo "ERROR: Insufficient arguments"
            echo "Usage: $0 <URL> <REASON> <STATUS>"
            echo "Run '$0 help' for more info"
            exit 1
        fi
        
        send_alert "$1" "$2" "$3"
        ;;
esac

exit $?
