#!/usr/bin/env python3
"""
Current Context Helper
Always returns accurate current date/time and day information
"""

from datetime import datetime
import pytz

def get_current_context():
    """Get current date/time/day context"""
    # Ross's timezone
    tz = pytz.timezone('America/Chicago')
    now = datetime.now(tz)
    
    return {
        'datetime': now,
        'date': now.strftime('%Y-%m-%d'),
        'time': now.strftime('%H:%M:%S'),
        'day_name': now.strftime('%A'),
        'day_short': now.strftime('%a'),
        'month': now.strftime('%B'),
        'year': now.year,
        'hour': now.hour,
        'minute': now.minute,
        'is_weekend': now.weekday() >= 5,
        'is_weekday': now.weekday() < 5,
        'time_of_day': get_time_of_day(now.hour),
        'formatted': now.strftime('%A, %B %d, %Y at %I:%M %p %Z')
    }

def get_time_of_day(hour):
    """Get time of day category"""
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 21:
        return 'evening'
    else:
        return 'night'

def print_context():
    """Print current context"""
    ctx = get_current_context()
    print(f"📅 {ctx['formatted']}")
    print(f"   Day: {ctx['day_name']} ({'weekend' if ctx['is_weekend'] else 'weekday'})")
    print(f"   Time of day: {ctx['time_of_day']}")

if __name__ == "__main__":
    print_context()
