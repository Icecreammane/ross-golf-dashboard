#!/usr/bin/env python3
"""Check macOS Calendar events"""
import subprocess
from datetime import datetime, timedelta

# Get events for today and tomorrow
script = '''
tell application "Calendar"
    set today to current date
    set tomorrow to today + (1 * days)
    set yesterday to today - (1 * days)
    
    set eventList to {}
    repeat with cal in calendars
        repeat with evt in (every event of cal whose start date is greater than yesterday and start date is less than tomorrow)
            set end of eventList to {summary of evt, start date of evt, end date of evt, name of cal}
        end repeat
    end repeat
    return eventList
end tell
'''

result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(f"Error: {result.stderr}")
