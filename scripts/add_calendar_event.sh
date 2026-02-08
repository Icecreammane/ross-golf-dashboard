#!/bin/bash
# Quick script to add calendar event
# Usage: bash add_calendar_event.sh "Event Title" "02/08/2026 6:00 PM" "02/08/2026 10:00 PM"

TITLE="$1"
START="$2"
END="$3"

osascript -e "tell application \"Calendar\"
    tell calendar \"Home\"
        make new event with properties {summary:\"$TITLE\", start date:date \"$START\", end date:date \"$END\"}
    end tell
end tell"

echo "✅ Event added to Calendar: $TITLE"
