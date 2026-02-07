# Quick Calendar Shortcuts ⚡

**Status:** ACTIVE ✅  
**Built:** 2026-02-03 12:44am CST

## What It Does

Text Jarvis short commands → Instant calendar events!

No more "Please schedule leg day tomorrow at 6pm"  
Just: **"leg 6pm"**

## Commands

### Workouts
```
leg 6pm                  → Leg Day tomorrow at 6pm
chest friday 630         → Chest Day Friday at 6:30pm
back monday 7            → Back Day Monday at 7pm
arms wed 545pm           → Arms Day Wednesday at 5:45pm
cardio tomorrow 8am      → Cardio tomorrow at 8am
```

### Meal Prep
```
meal sunday 5            → Meal Prep Sunday at 5pm
prep tomorrow 6          → Meal Prep tomorrow at 6pm
mealprep sat 4pm         → Meal Prep Saturday at 4pm
```

### Reminders
```
remind friday waiver     → Reminder Friday 9am (Check waivers)
reminder monday invoice  → Reminder Monday 9am (Invoice)
remind tomorrow meeting  → Reminder tomorrow 9am (Meeting)
```

## Supported Keywords

**Workouts:**
- leg/legs → Leg Day
- chest → Chest Day
- back → Back Day
- arms/arm → Arms Day
- shoulders → Shoulders
- cardio → Cardio
- abs/core → Core/Abs
- full → Full Body
- upper → Upper Body
- lower → Lower Body

**Days:**
- today, tomorrow, tmr
- monday/mon, tuesday/tue, wednesday/wed
- thursday/thu, friday/fri, saturday/sat, sunday/sun

**Times:**
- Simple: 6pm, 7am, 5
- Detailed: 630pm, 545pm, 9:30am
- Military: 18:00, 0800

## How It Works

1. You text: "leg 6pm"
2. Jarvis parses:
   - Workout: Leg Day
   - Day: Tomorrow (default if not specified)
   - Time: 6:00 PM
3. Event created in Apple Calendar
4. Syncs to all your devices instantly

## Examples

**Ross:** "leg friday 6"  
**Jarvis:** ✅ Scheduled: 💪 Leg Day - Friday, Feb 6 at 6:00 PM

**Ross:** "meal sunday 5pm"  
**Jarvis:** ✅ Scheduled: 🍳 Meal Prep - Sunday, Feb 8 at 5:00 PM

**Ross:** "remind tomorrow waivers"  
**Jarvis:** ✅ Scheduled: ⏰ Waivers - Tomorrow at 9:00 AM

## Benefits

✅ **10x Faster** - "leg 6" vs full sentence  
✅ **Natural** - Talk like a human, not a robot  
✅ **Smart Defaults** - Workouts → 6pm, Reminders → 9am  
✅ **Flexible** - Works with tons of variations  
✅ **Instant** - Calendar updates in 1 second

## Behind the Scenes

- `quick_calendar.py` - Smart parser
- Integrates with `calendar_creator.py`
- Uses Apple Calendar API
- Zero latency, zero OAuth needed

---

**Now go schedule something and watch it work!** ⚡
