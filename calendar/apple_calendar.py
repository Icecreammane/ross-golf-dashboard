#!/usr/bin/env python3
"""
Apple Calendar Integration for Jarvis
Read calendar events via AppleScript - no OAuth needed!
"""

import subprocess
import json
import datetime

def run_applescript(script):
    """Run AppleScript and return result"""
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    return result.stdout.strip()

def get_calendars():
    """Get list of all calendars"""
    script = 'tell application "Calendar" to get name of every calendar'
    calendars = run_applescript(script)
    return [cal.strip() for cal in calendars.split(',')]

def get_todays_events():
    """Get all events for today"""
    today = datetime.date.today()
    start = datetime.datetime.combine(today, datetime.time.min)
    end = datetime.datetime.combine(today, datetime.time.max)
    
    script = f'''
    set startDate to date "{start.strftime('%m/%d/%Y %H:%M:%S')}"
    set endDate to date "{end.strftime('%m/%d/%Y %H:%M:%S')}"
    
    tell application "Calendar"
        set eventList to {{}}
        repeat with cal in calendars
            set theEvents to (every event of cal whose start date ≥ startDate and start date ≤ endDate)
            repeat with evt in theEvents
                set end of eventList to (summary of evt & "|" & (start date of evt as string) & "|" & (end date of evt as string))
            end repeat
        end repeat
        return eventList as string
    end tell
    '''
    
    result = run_applescript(script)
    events = []
    
    if result and result != "":
        for line in result.split(', '):
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    events.append({
                        'summary': parts[0],
                        'start': parts[1],
                        'end': parts[2]
                    })
    
    return events

def get_upcoming_events(hours=24):
    """Get events in the next N hours"""
    now = datetime.datetime.now()
    end = now + datetime.timedelta(hours=hours)
    
    script = f'''
    set startDate to date "{now.strftime('%m/%d/%Y %H:%M:%S')}"
    set endDate to date "{end.strftime('%m/%d/%Y %H:%M:%S')}"
    
    tell application "Calendar"
        set eventList to {{}}
        repeat with cal in calendars
            set theEvents to (every event of cal whose start date ≥ startDate and start date ≤ endDate)
            repeat with evt in theEvents
                set end of eventList to (summary of evt & "|" & (start date of evt as string) & "|" & (end date of evt as string))
            end repeat
        end repeat
        return eventList as string
    end tell
    '''
    
    result = run_applescript(script)
    events = []
    
    if result and result != "":
        for line in result.split(', '):
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    events.append({
                        'summary': parts[0],
                        'start': parts[1],
                        'end': parts[2]
                    })
    
    return events

def format_event(event):
    """Format event for display"""
    summary = event['summary']
    start = event['start']
    
    # Parse the start time
    try:
        # AppleScript date format: "Monday, February 3, 2026 at 9:00:00 AM"
        if ' at ' in start:
            time_part = start.split(' at ')[1]
            time_str = time_part.split(' ')[0] + ' ' + time_part.split(' ')[1]
        else:
            time_str = 'All day'
    except:
        time_str = 'All day'
    
    return f"{time_str} - {summary}"

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "calendars":
        cals = get_calendars()
        print(f"📅 Your calendars ({len(cals)}):")
        for cal in cals:
            print(f"  • {cal}")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "today":
        events = get_todays_events()
        if not events:
            print("📅 No events today!")
        else:
            print(f"📅 Today's schedule ({len(events)} events):\n")
            for event in events:
                print(f"  • {format_event(event)}")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "upcoming":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        events = get_upcoming_events(hours)
        if not events:
            print(f"📅 No events in the next {hours} hours")
        else:
            print(f"📅 Upcoming ({len(events)} events in next {hours}h):\n")
            for event in events:
                print(f"  • {format_event(event)}")
    
    else:
        print("Usage:")
        print("  python3 apple_calendar.py calendars")
        print("  python3 apple_calendar.py today")
        print("  python3 apple_calendar.py upcoming [hours]")
