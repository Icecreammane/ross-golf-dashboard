# Calendar System 📅

**Status:** ACTIVE ✅  
**Built:** 2026-02-02

## What It Does

Full calendar integration with Apple Calendar - read AND write events!

## Files

- `apple_calendar.py` - Read calendar events
- `calendar_creator.py` - Create/manage calendar events
- `google_calendar.py` - Google Calendar (OAuth setup pending)

## Reading Calendar

```bash
# List all calendars
python3 ~/clawd/calendar/apple_calendar.py calendars

# Today's schedule
python3 ~/clawd/calendar/apple_calendar.py today

# Next 24 hours
python3 ~/clawd/calendar/apple_calendar.py upcoming 24

# Next 48 hours
python3 ~/clawd/calendar/apple_calendar.py upcoming 48
```

## Creating Events

### Quick Commands

```bash
# Schedule a workout
python3 ~/clawd/calendar/calendar_creator.py workout "Leg Day"

# Schedule meal prep
python3 ~/clawd/calendar/calendar_creator.py mealprep

# Set a reminder
python3 ~/clawd/calendar/calendar_creator.py reminder "Check fantasy waivers"

# Block focus time
python3 ~/clawd/calendar/calendar_creator.py block "Revenue Dashboard Work"
```

### Advanced Usage (from Python)

```python
from calendar_creator import create_event, schedule_workout, block_time
from datetime import datetime, timedelta

# Create custom event
tomorrow = datetime.now() + timedelta(days=1)
create_event(
    calendar="Work",
    title="Team Meeting",
    start_date=tomorrow.replace(hour=14, minute=0),
    duration_hours=1,
    location="Conference Room A",
    notes="Q1 planning discussion"
)

# Schedule workout with custom time
schedule_workout(
    workout_type="Chest Day",
    date=tomorrow,
    time_str="6:00 PM",
    duration=1.5
)

# Block deep work time
block_time(
    title="Build Dashboard",
    date=tomorrow,
    time_str="2:00 PM",
    duration=2,
    calendar="Work"
)
```

## Available Calendars

- **Home** - Personal events
- **Work** - Work-related events
- **Scheduled Reminders** - Auto-created reminders
- Birthdays, US Holidays, Siri Suggestions (read-only)

## Voice Integration

You can ask Jarvis to schedule things:
- "Schedule leg day tomorrow at 6pm"
- "Block 2 hours Friday afternoon for the dashboard"
- "Remind me Monday morning to check fantasy waivers"
- "Add meal prep to my calendar Sunday at 5pm"

Jarvis will create the events and they sync instantly to your iPhone, Mac, etc.

## What's Next

- [x] Read calendar events
- [x] Create calendar events
- [ ] Recurring events (weekly workouts, etc.)
- [ ] Smart scheduling (find free time automatically)
- [ ] Pattern detection (track when you're busiest)
- [ ] Integration with morning brief
- [ ] Proactive reminders ("Meeting in 30 min")
- [ ] Google Calendar OAuth (tomorrow's task)

## Benefits

✅ **Instant Sync** - All devices get updates immediately  
✅ **No OAuth** - Direct access via macOS Calendar  
✅ **Voice Control** - Just ask Jarvis  
✅ **Flexible** - Any calendar, any time, any duration  
✅ **Smart Defaults** - Workouts, meal prep, reminders pre-configured

---

**Ross, you now have full calendar control through Jarvis!** 🎯
