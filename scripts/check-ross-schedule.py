#!/usr/bin/env python3
"""
Check Ross's calendar and determine current availability status.
Used by heartbeat and main agent to know when Ross is busy vs. free.
"""

import sys
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path.append('/Users/clawdbot/clawd/calendar')
from google_calendar import get_todays_events

def get_current_status():
    """
    Returns Ross's current status based on calendar and time patterns.
    
    Returns:
        {
            "status": "available" | "in_office" | "gym" | "busy" | "sleeping",
            "current_event": "Event title or None",
            "next_event": "Next event details",
            "context": "Additional context",
            "can_interrupt": bool,
            "response_expected": "immediate" | "text_only" | "delayed" | "none"
        }
    """
    
    cst = ZoneInfo('America/Chicago')
    now = datetime.now(cst)
    hour = now.hour
    weekday = now.weekday()  # 0=Monday, 6=Sunday
    
    # Get today's calendar events
    try:
        events = get_todays_events()
    except Exception as e:
        print(f"Warning: Could not fetch calendar: {e}", file=sys.stderr)
        events = []
    
    # Check if currently in an event
    current_event = None
    for event in events:
        start = event.get('start', {}).get('dateTime')
        end = event.get('end', {}).get('dateTime')
        if start and end:
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00')).astimezone(cst)
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00')).astimezone(cst)
            if start_dt <= now <= end_dt:
                current_event = event.get('summary', 'Busy')
                break
    
    # Find next event
    next_event = None
    for event in events:
        start = event.get('start', {}).get('dateTime')
        if start:
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00')).astimezone(cst)
            if start_dt > now:
                next_event = {
                    "title": event.get('summary', 'Event'),
                    "start": start_dt.strftime('%I:%M %p'),
                    "minutes_until": int((start_dt - now).total_seconds() / 60)
                }
                break
    
    # Determine status based on patterns
    status = {
        "status": "available",
        "current_event": current_event,
        "next_event": next_event,
        "context": "",
        "can_interrupt": True,
        "response_expected": "immediate"
    }
    
    # Sleeping (11pm - 7am)
    if hour >= 23 or hour < 7:
        status.update({
            "status": "sleeping",
            "context": "Ross is sleeping. Build deep projects, report in morning brief.",
            "can_interrupt": False,
            "response_expected": "none"
        })
        return status
    
    # Current event from calendar
    if current_event:
        status.update({
            "status": "busy",
            "context": f"In event: {current_event}",
            "can_interrupt": False,
            "response_expected": "delayed"
        })
        return status
    
    # Gym time (4:30pm - 6:00pm)
    gym_start = now.replace(hour=16, minute=30, second=0, microsecond=0)
    gym_end = now.replace(hour=18, minute=0, second=0, microsecond=0)
    if gym_start <= now < gym_end:
        status.update({
            "status": "gym",
            "context": "Ross is at the gym. Low priority messages only.",
            "can_interrupt": False,
            "response_expected": "delayed"
        })
        return status
    
    # Office hours (9am - 4:30pm, Tue/Wed/Thu)
    if weekday in [1, 2, 3] and 9 <= hour < 17:  # Tue/Wed/Thu, 9am-5pm
        # Check for WFH indicators (voice messages = WFH)
        status.update({
            "status": "in_office",
            "context": "Ross is at the office. Text-only responses expected.",
            "can_interrupt": True,
            "response_expected": "text_only"
        })
        return status
    
    # Evening tinkering time (7pm - 11pm)
    if 19 <= hour < 23:
        status.update({
            "status": "available",
            "context": "Ross is free for tinkering. Prime time for deep discussions.",
            "can_interrupt": True,
            "response_expected": "immediate"
        })
        return status
    
    # Default: available but might be busy
    status.update({
        "context": "Ross might be available. Check for responsiveness.",
        "can_interrupt": True,
        "response_expected": "delayed"
    })
    
    return status

def main():
    """Print current status as JSON."""
    status = get_current_status()
    print(json.dumps(status, indent=2))
    
    # Also print human-readable summary
    print(f"\n📅 Current Status: {status['status'].upper()}", file=sys.stderr)
    print(f"📝 {status['context']}", file=sys.stderr)
    if status['next_event']:
        ne = status['next_event']
        print(f"⏰ Next: {ne['title']} at {ne['start']} ({ne['minutes_until']} min)", file=sys.stderr)

if __name__ == '__main__':
    main()
