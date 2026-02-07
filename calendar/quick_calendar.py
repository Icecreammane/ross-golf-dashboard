#!/usr/bin/env python3
"""
Quick Calendar Shortcuts for Jarvis
Parse natural shortcuts like "leg 6pm" and create calendar events
"""

import re
from datetime import datetime, timedelta
from calendar_creator import create_event, schedule_workout, schedule_meal_prep, schedule_reminder

# Workout keywords
WORKOUTS = {
    'leg': 'Leg Day',
    'legs': 'Leg Day',
    'chest': 'Chest Day',
    'back': 'Back Day',
    'arms': 'Arms Day',
    'arm': 'Arms Day',
    'shoulders': 'Shoulders',
    'cardio': 'Cardio',
    'abs': 'Abs',
    'core': 'Core',
    'full': 'Full Body',
    'upper': 'Upper Body',
    'lower': 'Lower Body'
}

# Day keywords
DAYS = {
    'today': 0,
    'tomorrow': 1,
    'tmr': 1,
    'monday': None,  # Will calculate
    'mon': None,
    'tuesday': None,
    'tue': None,
    'wednesday': None,
    'wed': None,
    'thursday': None,
    'thu': None,
    'friday': None,
    'fri': None,
    'saturday': None,
    'sat': None,
    'sunday': None,
    'sun': None
}

# Meal/reminder keywords
SPECIAL = {
    'meal': 'meal_prep',
    'mealprep': 'meal_prep',
    'prep': 'meal_prep',
    'remind': 'reminder',
    'reminder': 'reminder'
}


def parse_day(day_str):
    """Convert day string to datetime object"""
    day_str = day_str.lower()
    
    if day_str in ['today', 'tmr', 'tomorrow']:
        offset = DAYS[day_str]
        return datetime.now() + timedelta(days=offset)
    
    # Day of week
    day_map = {
        'monday': 0, 'mon': 0,
        'tuesday': 1, 'tue': 1,
        'wednesday': 2, 'wed': 2,
        'thursday': 3, 'thu': 3,
        'friday': 4, 'fri': 4,
        'saturday': 5, 'sat': 5,
        'sunday': 6, 'sun': 6
    }
    
    if day_str in day_map:
        target_day = day_map[day_str]
        today = datetime.now()
        current_day = today.weekday()
        
        # Calculate days until target
        if target_day > current_day:
            days_ahead = target_day - current_day
        elif target_day < current_day:
            days_ahead = 7 - (current_day - target_day)
        else:
            # Same day - assume next week
            days_ahead = 7
        
        return today + timedelta(days=days_ahead)
    
    # Default to tomorrow if can't parse
    return datetime.now() + timedelta(days=1)


def parse_time(time_str):
    """Convert time string to datetime.time object"""
    time_str = time_str.lower().strip()
    
    # Remove spaces
    time_str = time_str.replace(' ', '')
    
    # Handle formats: 6pm, 630pm, 6:30pm, 18:00, 1800
    patterns = [
        (r'^(\d{1,2})pm$', lambda m: int(m.group(1)) + 12 if int(m.group(1)) != 12 else 12, 0),
        (r'^(\d{1,2})am$', lambda m: int(m.group(1)) % 12, 0),
        (r'^(\d{1,2})(\d{2})pm$', lambda m: int(m.group(1)) + 12 if int(m.group(1)) != 12 else 12, lambda m: int(m.group(2))),
        (r'^(\d{1,2})(\d{2})am$', lambda m: int(m.group(1)) % 12, lambda m: int(m.group(2))),
        (r'^(\d{1,2}):(\d{2})pm$', lambda m: int(m.group(1)) + 12 if int(m.group(1)) != 12 else 12, lambda m: int(m.group(2))),
        (r'^(\d{1,2}):(\d{2})am$', lambda m: int(m.group(1)) % 12, lambda m: int(m.group(2))),
        (r'^(\d{1,2}):(\d{2})$', lambda m: int(m.group(1)), lambda m: int(m.group(2))),
        (r'^(\d{2})(\d{2})$', lambda m: int(m.group(1)), lambda m: int(m.group(2)))
    ]
    
    for pattern, hour_fn, min_fn in patterns:
        match = re.match(pattern, time_str)
        if match:
            hour = hour_fn(match) if callable(hour_fn) else hour_fn
            minute = min_fn(match) if callable(min_fn) else min_fn
            return datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0).time()
    
    # Default to 6pm if can't parse
    return datetime.now().replace(hour=18, minute=0, second=0, microsecond=0).time()


def parse_shortcut(text):
    """
    Parse calendar shortcut and return event details
    
    Examples:
        "leg 6pm" → Leg Day tomorrow at 6pm
        "chest wed 630" → Chest Day Wednesday at 6:30pm
        "meal sunday 5" → Meal Prep Sunday at 5pm
        "remind friday waiver" → Reminder Friday 9am about waivers
    
    Returns:
        dict with: type, title, date, time
    """
    text = text.lower().strip()
    words = text.split()
    
    result = {
        'type': 'workout',
        'title': None,
        'date': None,
        'time': None,
        'calendar': 'Home'
    }
    
    # Check for special types (meal, remind)
    for word in words:
        if word in SPECIAL:
            result['type'] = SPECIAL[word]
            break
    
    # Check for workout keywords
    if result['type'] == 'workout':
        for word in words:
            if word in WORKOUTS:
                result['title'] = WORKOUTS[word]
                break
    
    # Parse day
    for word in words:
        if word in DAYS or word in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
            result['date'] = parse_day(word)
            break
    
    # Default to tomorrow if no day specified
    if result['date'] is None:
        result['date'] = datetime.now() + timedelta(days=1)
    
    # Parse time
    time_pattern = r'\d{1,4}(am|pm)?'
    for word in words:
        if re.match(time_pattern, word):
            result['time'] = parse_time(word)
            break
    
    # Default times based on type
    if result['time'] is None:
        if result['type'] == 'workout':
            result['time'] = parse_time('6pm')
        elif result['type'] == 'meal_prep':
            result['time'] = parse_time('5pm')
        elif result['type'] == 'reminder':
            result['time'] = parse_time('9am')
    
    # Extract reminder text
    if result['type'] == 'reminder':
        # Everything after "remind" or "reminder" and day/time
        reminder_words = []
        skip_words = ['remind', 'reminder'] + list(DAYS.keys()) + ['today', 'tomorrow', 'tmr']
        for word in words:
            if word not in skip_words and not re.match(time_pattern, word):
                reminder_words.append(word)
        result['title'] = ' '.join(reminder_words).title() if reminder_words else 'Reminder'
    
    return result


def create_from_shortcut(text):
    """Parse shortcut and create calendar event"""
    parsed = parse_shortcut(text)
    
    # Combine date and time
    start_datetime = datetime.combine(
        parsed['date'].date(),
        parsed['time']
    )
    
    if parsed['type'] == 'workout':
        return schedule_workout(
            workout_type=parsed['title'],
            date=start_datetime,
            time_str=parsed['time'].strftime('%I:%M %p'),
            calendar=parsed['calendar']
        )
    
    elif parsed['type'] == 'meal_prep':
        return schedule_meal_prep(
            date=start_datetime,
            time_str=parsed['time'].strftime('%I:%M %p'),
            calendar=parsed['calendar']
        )
    
    elif parsed['type'] == 'reminder':
        return schedule_reminder(
            title=parsed['title'],
            date=start_datetime,
            time_str=parsed['time'].strftime('%I:%M %p'),
            calendar=parsed['calendar']
        )
    
    else:
        # Generic event
        return create_event(
            calendar=parsed['calendar'],
            title=parsed['title'] or 'Event',
            start_date=start_datetime,
            duration_hours=1
        )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Quick Calendar - Usage:")
        print('  python3 quick_calendar.py "leg 6pm"')
        print('  python3 quick_calendar.py "chest wed 630"')
        print('  python3 quick_calendar.py "meal sunday 5"')
        print('  python3 quick_calendar.py "remind friday waiver"')
        sys.exit(1)
    
    shortcut = ' '.join(sys.argv[1:])
    
    # Parse and show what we understood
    parsed = parse_shortcut(shortcut)
    print(f"\n📝 Parsed: {shortcut}")
    print(f"  Type: {parsed['type']}")
    print(f"  Title: {parsed['title']}")
    print(f"  Date: {parsed['date'].strftime('%A, %B %d')}")
    print(f"  Time: {parsed['time'].strftime('%I:%M %p')}")
    
    # Create event
    print(f"\n✅ Creating event...")
    event_id = create_from_shortcut(shortcut)
    print(f"✅ Event created! Check your calendar.")
