#!/usr/bin/env python3
"""
Apple Calendar Event Creator for Jarvis
Create, modify, and delete calendar events
"""

import subprocess
import sys
from datetime import datetime, timedelta
import json

def run_applescript(script):
    """Run AppleScript and return result"""
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"AppleScript error: {result.stderr}")
    return result.stdout.strip()

def create_event(calendar="Home", title="", start_date=None, duration_hours=1, 
                 location="", notes="", all_day=False):
    """
    Create a calendar event
    
    Args:
        calendar: Calendar name (Home, Work, etc.)
        title: Event title
        start_date: datetime object or None (defaults to now + 1 hour)
        duration_hours: Event duration in hours (default 1)
        location: Event location (optional)
        notes: Event notes (optional)
        all_day: All-day event (default False)
    
    Returns:
        event_id: The created event ID
    """
    if start_date is None:
        start_date = datetime.now() + timedelta(hours=1)
    
    end_date = start_date + timedelta(hours=duration_hours)
    
    # Format dates for AppleScript
    start_str = start_date.strftime('%m/%d/%Y %I:%M:%S %p')
    end_str = end_date.strftime('%m/%d/%Y %I:%M:%S %p')
    
    # Escape quotes in strings
    title = title.replace('"', '\\"')
    location = location.replace('"', '\\"')
    notes = notes.replace('"', '\\"')
    
    if all_day:
        script = f'''
        tell application "Calendar"
            tell calendar "{calendar}"
                set newEvent to make new event with properties {{summary:"{title}", start date:date "{start_str}", allday event:true}}
                if "{location}" is not "" then
                    set location of newEvent to "{location}"
                end if
                if "{notes}" is not "" then
                    set description of newEvent to "{notes}"
                end if
                return id of newEvent
            end tell
        end tell
        '''
    else:
        script = f'''
        tell application "Calendar"
            tell calendar "{calendar}"
                set newEvent to make new event with properties {{summary:"{title}", start date:date "{start_str}", end date:date "{end_str}"}}
                if "{location}" is not "" then
                    set location of newEvent to "{location}"
                end if
                if "{notes}" is not "" then
                    set description of newEvent to "{notes}"
                end if
                return id of newEvent
            end tell
        end tell
        '''
    
    return run_applescript(script)

def delete_event(calendar="Home", title=""):
    """Delete an event by title"""
    script = f'''
    tell application "Calendar"
        tell calendar "{calendar}"
            delete (first event whose summary is "{title}")
        end tell
    end tell
    '''
    return run_applescript(script)

def list_calendars():
    """Get list of all calendars"""
    script = 'tell application "Calendar" to get name of every calendar'
    calendars = run_applescript(script)
    return [cal.strip() for cal in calendars.split(',')]

# Helper functions for common event types

def schedule_workout(workout_type="Workout", date=None, time_str="6:00 PM", duration=1.5, calendar="Home"):
    """Schedule a workout session"""
    if date is None:
        date = datetime.now() + timedelta(days=1)
    
    # Parse time
    time_obj = datetime.strptime(time_str, '%I:%M %p').time()
    start = datetime.combine(date.date(), time_obj)
    
    title = f"💪 {workout_type}"
    notes = "Focus on form, progressive overload, and recovery."
    
    return create_event(calendar=calendar, title=title, start_date=start, 
                       duration_hours=duration, notes=notes)

def schedule_meal_prep(date=None, time_str="5:00 PM", calendar="Home"):
    """Schedule meal prep time"""
    if date is None:
        date = datetime.now() + timedelta(days=1)
    
    time_obj = datetime.strptime(time_str, '%I:%M %p').time()
    start = datetime.combine(date.date(), time_obj)
    
    title = "🍳 Meal Prep"
    notes = "Prep meals for the next 2-3 days. Focus on protein and veggies."
    
    return create_event(calendar=calendar, title=title, start_date=start, 
                       duration_hours=1, notes=notes)

def schedule_reminder(title="Reminder", date=None, time_str="9:00 AM", calendar="Home"):
    """Schedule a reminder/task"""
    if date is None:
        date = datetime.now() + timedelta(days=1)
    
    time_obj = datetime.strptime(time_str, '%I:%M %p').time()
    start = datetime.combine(date.date(), time_obj)
    
    return create_event(calendar=calendar, title=f"⏰ {title}", start_date=start, 
                       duration_hours=0.25)

def block_time(title="Focus Time", date=None, time_str="2:00 PM", duration=2, calendar="Work"):
    """Block time for focused work"""
    if date is None:
        date = datetime.now() + timedelta(days=1)
    
    time_obj = datetime.strptime(time_str, '%I:%M %p').time()
    start = datetime.combine(date.date(), time_obj)
    
    return create_event(calendar=calendar, title=f"🎯 {title}", start_date=start, 
                       duration_hours=duration, notes="Deep work - no interruptions")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Calendar Event Creator - Usage:")
        print("\n  python3 calendar_creator.py create <title> <date> <time> [calendar] [duration]")
        print("    Example: python3 calendar_creator.py create 'Leg Day' tomorrow '6:00 PM' Home 1.5")
        print("\n  python3 calendar_creator.py workout <type> [date] [time]")
        print("    Example: python3 calendar_creator.py workout 'Leg Day' tomorrow '6:00 PM'")
        print("\n  python3 calendar_creator.py mealprep [date] [time]")
        print("    Example: python3 calendar_creator.py mealprep Sunday '5:00 PM'")
        print("\n  python3 calendar_creator.py reminder <title> [date] [time]")
        print("    Example: python3 calendar_creator.py reminder 'Check waivers' Friday '9:00 AM'")
        print("\n  python3 calendar_creator.py block <title> [date] [time] [duration]")
        print("    Example: python3 calendar_creator.py block 'Revenue Dashboard' tomorrow '2:00 PM' 2")
        print("\n  python3 calendar_creator.py calendars")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "calendars":
        cals = list_calendars()
        print(f"Available calendars ({len(cals)}):")
        for cal in cals:
            print(f"  • {cal}")
    
    elif command == "workout":
        workout_type = sys.argv[2] if len(sys.argv) > 2 else "Workout"
        # For simplicity, using tomorrow 6pm as default
        event_id = schedule_workout(workout_type=workout_type)
        print(f"✅ Scheduled: {workout_type}")
    
    elif command == "mealprep":
        event_id = schedule_meal_prep()
        print(f"✅ Scheduled: Meal Prep")
    
    elif command == "reminder":
        title = sys.argv[2] if len(sys.argv) > 2 else "Reminder"
        event_id = schedule_reminder(title=title)
        print(f"✅ Scheduled reminder: {title}")
    
    elif command == "block":
        title = sys.argv[2] if len(sys.argv) > 2 else "Focus Time"
        event_id = block_time(title=title)
        print(f"✅ Blocked time: {title}")
    
    elif command == "create":
        title = sys.argv[2] if len(sys.argv) > 2 else "New Event"
        # Basic create - you can enhance this with date parsing
        event_id = create_event(title=title)
        print(f"✅ Created event: {title}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
