# Dopamine Defense System

**Mission:** Catch Ross mid-scroll and redirect to productive quick wins.

## Overview

The Dopamine Defense System is an intelligent idle detection and intervention system that monitors user activity and sends strategic interruptions when doom scrolling is suspected. It tracks productivity patterns and helps maintain focus during work hours.

## Architecture

### Components

1. **Activity Tracker** (`scripts/activity_tracker.py`)
   - Monitors last interaction timestamp
   - Detects idle periods >20 minutes
   - Logs activity patterns
   - Calculates daily productivity metrics

2. **Interrupt System** (`scripts/dopamine_defense.py`)
   - Checks idle status every heartbeat
   - Sends Telegram interventions with quick win tasks
   - Tracks response times and success rates
   - Generates evening productivity reports

3. **Quick Win Library** (`data/quick_wins.json`)
   - Curated list of 5-10 minute tasks
   - Rotates suggestions to avoid repetition
   - Categories: health, career, growth, productivity, etc.

### Data Files

- `data/activity_log.json` - Raw activity tracking data
- `data/quick_wins.json` - Task library and suggestion history
- `data/dopamine_defense_state.json` - Interrupt history and stats
- `memory/heartbeat-state.json` - Heartbeat integration (last_activity)

## Configuration

**Work Hours:** 9am - 11pm CST
**Idle Threshold:** 20 minutes
**Interrupt Cooldown:** 60 minutes (prevents spam)
**Timezone:** America/Chicago (CST)

## Usage

### Manual Commands

```bash
# Check current idle status
python3 ~/clawd/scripts/activity_tracker.py status

# Record an interaction
python3 ~/clawd/scripts/activity_tracker.py record

# Get daily summary
python3 ~/clawd/scripts/activity_tracker.py summary

# Check if interrupt should fire
python3 ~/clawd/scripts/dopamine_defense.py check

# Get system statistics
python3 ~/clawd/scripts/dopamine_defense.py stats

# Generate evening report
python3 ~/clawd/scripts/dopamine_defense.py report
```

### Programmatic Integration (Python)

```python
from scripts.activity_tracker import record_interaction, get_idle_status, get_daily_summary
from scripts.dopamine_defense import check_and_interrupt, generate_evening_report

# Record user activity
result = record_interaction("message")
if result["idle_detected"]:
    print(f"Was idle for {result['idle_duration_minutes']} minutes")

# Check if interrupt needed
interrupt = check_and_interrupt()
if interrupt["should_interrupt"]:
    send_telegram_message(interrupt["message"])

# Evening check-in
report = generate_evening_report()
print(report)
```

## Heartbeat Integration

Add to `HEARTBEAT.md`:

```markdown
## Dopamine Defense Check

Every heartbeat (5 min intervals):
1. Record this heartbeat as activity
2. Check if interrupt needed
3. If yes and cooldown passed, send Telegram intervention
4. Update heartbeat-state.json with last_activity time

Only interrupt once per idle period.
```

### Heartbeat Implementation

In your heartbeat handler:

```python
import json
from datetime import datetime
from pathlib import Path
from scripts.activity_tracker import record_interaction
from scripts.dopamine_defense import check_and_interrupt

# Record heartbeat as activity (internal tracking, not user interaction)
# Don't record heartbeat itself as interaction - only user messages count

# Check if we should interrupt
result = check_and_interrupt()

if result["should_interrupt"]:
    # Send via Telegram
    message_tool(
        action="send",
        target="ross",  # Or specific Telegram ID
        message=result["message"]
    )
    
    # Update heartbeat state
    heartbeat_state = Path.home() / "clawd/memory/heartbeat-state.json"
    state = json.load(open(heartbeat_state)) if heartbeat_state.exists() else {}
    state["last_dopamine_check"] = datetime.now().isoformat()
    state["last_activity"] = result.get("idle_status", {}).get("last_interaction")
    json.dump(state, open(heartbeat_state, 'w'), indent=2)
```

## Evening Check-In Integration

Add to your 8pm check-in routine:

```python
from scripts.dopamine_defense import generate_evening_report

# Generate and send report
report = generate_evening_report()

# Send via Telegram
message_tool(
    action="send",
    target="ross",
    message=report
)
```

## Response Tracking

When Ross responds to ANY message after an interrupt was sent, record it:

```python
from scripts.dopamine_defense import record_response_received

# In your message handler
record_response_received()
```

This tracks re-engagement success and calculates system effectiveness.

## Quick Win Task Format

Tasks in `data/quick_wins.json`:

```json
{
  "id": "unique_task_id",
  "task": "Human-readable task description",
  "category": "health|career|growth|productivity|organization|learning|mindfulness",
  "estimated_minutes": 3-10
}
```

### Adding New Quick Wins

Edit `data/quick_wins.json` and add to the `quick_wins` array:

```json
{
  "id": "my_new_task",
  "task": "Do something productive in <10 minutes",
  "category": "productivity",
  "estimated_minutes": 7
}
```

The system automatically rotates suggestions to avoid repetition.

## Metrics & Reports

### Daily Summary

- **Active time** - Estimated building/productive time
- **Idle time** - Total idle period duration
- **Productivity score** - Active / (Active + Idle) ratio
- **Session count** - Number of interaction clusters

### Defense Statistics

- **Total interrupts** - Interventions sent
- **Successful engagements** - Ross responded after interrupt
- **Success rate** - Percentage of interrupts that got responses
- **Avg response time** - How long until re-engagement

### Evening Report Format

```
📊 **Today's Dopamine Defense Report**

⏱️ **Time Breakdown:**
• Building: 3.5h
• Idle periods: 2h
• Productivity score: 64%

🎯 **Interventions:**
• Interrupts sent: 3
• Successful re-engagements: 2
• Success rate: 67%
• Avg response time: 8.5m

💪 Solid day. A few scroll sessions, but you stayed productive.
```

## Technical Details

### Idle Detection Logic

1. Every interaction updates `last_interaction` timestamp
2. Heartbeat checks: `current_time - last_interaction`
3. If >20 minutes during work hours → idle detected
4. Cooldown prevents multiple interrupts for same idle period

### Activity Estimation

Active time is estimated using session clustering:
- Group interactions within 30 minutes
- Each cluster = ~15 minutes of active work
- Rough but useful for productivity scoring

### Data Retention

- Activity sessions: 7 days
- Idle periods: 7 days
- Interrupt history: 30 days
- Suggestion history: Last 5 tasks

## Testing

### Manual Test: Idle Detection

1. Send a message to Jarvis (records activity)
2. Wait 20+ minutes without interaction
3. Run: `python3 ~/clawd/scripts/dopamine_defense.py check`
4. Should return `"should_interrupt": true` with a message

### Manual Test: Quick Win Rotation

```bash
for i in {1..5}; do
  python3 ~/clawd/scripts/dopamine_defense.py check | grep -A 5 "quick_win"
done
```

Should see different tasks each time.

### Manual Test: Evening Report

```bash
# Simulate some activity
python3 ~/clawd/scripts/activity_tracker.py record
sleep 3600  # Wait or fake timestamp

# Generate report
python3 ~/clawd/scripts/dopamine_defense.py report
```

### Integration Test: Full Flow

1. **Simulate idle period:**
   - Edit `data/activity_log.json` to set `last_interaction` 25 minutes ago
   
2. **Run check:**
   ```bash
   python3 ~/clawd/scripts/dopamine_defense.py check
   ```
   
3. **Should output:**
   ```json
   {
     "should_interrupt": true,
     "message": "🎯 Working on something?...",
     "quick_win": {...}
   }
   ```

4. **Send message via Telegram** (manually or via tool)

5. **Simulate response:**
   ```bash
   python3 ~/clawd/scripts/activity_tracker.py record message
   python3 ~/clawd/scripts/dopamine_defense.py record_response
   ```

6. **Check stats:**
   ```bash
   python3 ~/clawd/scripts/dopamine_defense.py stats
   ```
   Should show 100% success rate for 1 interrupt.

## Customization

### Adjust Timing

Edit constants in `scripts/dopamine_defense.py`:

```python
IDLE_THRESHOLD_MINUTES = 20  # Change idle detection threshold
INTERRUPT_COOLDOWN_MINUTES = 60  # Change cooldown period
```

Edit work hours in `scripts/activity_tracker.py`:

```python
WORK_HOURS_START = 9  # 9am
WORK_HOURS_END = 23   # 11pm
```

### Customize Messages

Edit the `send_interrupt_message()` function in `dopamine_defense.py` to add new message templates:

```python
messages = [
    f"Your custom message here with {quick_win['task']}",
    # ... more templates
]
```

### Add Task Categories

Edit `data/quick_wins.json` and add tasks in new categories. The system handles any category name.

## Troubleshooting

### Interrupts Not Firing

1. Check work hours: `python3 scripts/activity_tracker.py status`
2. Check cooldown: `python3 scripts/dopamine_defense.py stats`
3. Verify last_interrupt timestamp in `data/dopamine_defense_state.json`

### Wrong Timezone

System uses `America/Chicago` (CST). To change:

```python
# In both activity_tracker.py and dopamine_defense.py
CST = pytz.timezone('Your/Timezone')  # e.g., 'America/New_York'
```

### Activity Not Recording

Check that `record_interaction()` is called on user messages. Verify:

```bash
cat data/activity_log.json
```

Should show recent timestamps in `last_interaction` and `sessions`.

## Future Enhancements

Potential improvements:

- **Smart scheduling** - Learn best times to interrupt based on past success
- **Context awareness** - Different quick wins based on time of day
- **Habit tracking** - Track completion of suggested tasks
- **Integration with calendar** - Avoid interrupts during meetings
- **Custom task lists** - Per-day or per-mood task libraries
- **Progressive urgency** - Escalate message tone for longer idle periods
- **Weekend mode** - Different thresholds/tasks for non-work days

## Success Metrics

After 1 week of operation, review:

- **Catch rate** - % of scroll sessions interrupted
- **Re-engagement rate** - % of interrupts that worked
- **Productivity trend** - Is score improving?
- **Ross feedback** - "Did this actually catch you mid-scroll?"

Goal: 60%+ success rate within 2 weeks of tuning.

## License

Part of the Clawdbot workspace. For Ross's personal use.

---

**Built:** 2026-02-13  
**Status:** Ready for deployment  
**Next:** Integrate with heartbeat and test with real idle periods
