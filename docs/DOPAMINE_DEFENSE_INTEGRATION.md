# Dopamine Defense - Agent Integration Guide

Quick guide for integrating the Dopamine Defense System into the main agent's heartbeat.

## Quick Start

### 1. Track User Activity

Every time Ross sends a message, record it:

```python
from scripts.activity_tracker import record_interaction

# In your message handler
def handle_user_message(message):
    # Record the interaction
    result = record_interaction("message")
    
    # If this ended an idle period, optionally log it
    if result["idle_detected"]:
        log(f"Idle period ended: {result['idle_duration_minutes']}m")
    
    # Continue with normal message handling
    process_message(message)
```

### 2. Heartbeat Check

In your heartbeat handler (every ~5 minutes):

```python
from scripts.dopamine_defense import check_and_interrupt

# During heartbeat
def heartbeat_handler():
    # Check if intervention needed
    result = check_and_interrupt()
    
    if result["should_interrupt"]:
        # Send via Telegram using message tool
        send_telegram(result["message"])
        
        # Optionally log
        log(f"Sent dopamine defense interrupt after {result['idle_minutes']}m idle")
```

### 3. Track Responses

When Ross responds to ANY message after an interrupt, record it:

```python
from scripts.dopamine_defense import record_response_received

# In message handler, if an interrupt was recently sent
def handle_user_message(message):
    # First, record the activity
    record_interaction("message")
    
    # Then record as response to interrupt (if applicable)
    # The system automatically finds the last unresponded interrupt
    record_response_received()
    
    # Continue normal handling
    process_message(message)
```

### 4. Evening Report

At 8pm, include dopamine defense stats in check-in:

```python
from scripts.dopamine_defense import generate_evening_report

# In evening check-in routine
def evening_checkin():
    report = generate_evening_report()
    send_telegram(report)
```

## Simple Integration Example

Here's a complete minimal integration:

```python
#!/usr/bin/env python3
"""
Minimal Dopamine Defense Integration Example
"""

from scripts.activity_tracker import record_interaction
from scripts.dopamine_defense import check_and_interrupt, record_response_received, generate_evening_report
from datetime import datetime
from zoneinfo import ZoneInfo

CST = ZoneInfo('America/Chicago')


def on_user_message(message_text):
    """Called when Ross sends a message."""
    # Record activity
    result = record_interaction("message")
    
    # Record as response to any pending interrupt
    record_response_received()
    
    # Process message normally...
    print(f"Processing: {message_text}")


def on_heartbeat():
    """Called every ~5 minutes."""
    # Check if intervention needed
    result = check_and_interrupt()
    
    if result["should_interrupt"]:
        # Send intervention via Telegram
        send_telegram_message(result["message"])
        print(f"✅ Sent dopamine defense interrupt")
    
    # Check if it's evening check-in time (8pm)
    now = datetime.now(CST)
    if now.hour == 20 and 0 <= now.minute <= 5:
        report = generate_evening_report()
        send_telegram_message(report)


def send_telegram_message(text):
    """Your Telegram sending implementation."""
    print(f"[TELEGRAM] {text}")


# Example usage
if __name__ == "__main__":
    # Simulate Ross sending a message
    on_user_message("Hey Jarvis, what's up?")
    
    # Simulate heartbeat
    on_heartbeat()
```

## Using the Shell Wrapper

For quick integration without importing Python modules:

```bash
# In heartbeat script
result=$(python3 ~/clawd/scripts/heartbeat_dopamine_check.py)
exit_code=$?

if [ $exit_code -eq 1 ]; then
    # Extract message from JSON result
    message=$(echo "$result" | jq -r '.message')
    
    # Send via your messaging system
    send_telegram "$message"
fi
```

## Testing Your Integration

### Test 1: Activity Recording

```python
from scripts.activity_tracker import record_interaction, get_idle_status

# Record activity
record_interaction("message")

# Check status immediately
status = get_idle_status()
assert status["minutes_idle"] < 1, "Should not be idle immediately after activity"
print("✅ Activity recording works")
```

### Test 2: Idle Detection

```python
import json
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from scripts.activity_tracker import load_activity_log, save_activity_log, get_idle_status

# Simulate 25 minutes of idle
CST = ZoneInfo('America/Chicago')
now = datetime.now(CST)
fake_last = now - timedelta(minutes=25)

log = load_activity_log()
log["last_interaction"] = fake_last.isoformat()
save_activity_log(log)

# Check status
status = get_idle_status()
assert status["is_idle"] == True, "Should be idle after 25 minutes"
assert status["minutes_idle"] >= 20, "Should detect 20+ minute idle"
print("✅ Idle detection works")
```

### Test 3: Interrupt Logic

```python
from scripts.dopamine_defense import check_and_interrupt

# After setting up 25-minute idle (see Test 2)
result = check_and_interrupt()

# During work hours, should interrupt
if datetime.now(CST).hour >= 9 and datetime.now(CST).hour < 23:
    assert result["should_interrupt"] == True, "Should interrupt during work hours"
    assert result["message"] is not None, "Should have message"
    print(f"✅ Interrupt logic works")
    print(f"Message preview: {result['message'][:100]}...")
else:
    print("⏭️  Outside work hours, skipping interrupt test")
```

### Test 4: Full Flow

Run the complete test suite:

```bash
python3 ~/clawd/scripts/test_dopamine_defense.py
```

## Configuration

### Adjust Idle Threshold

Edit `scripts/activity_tracker.py`:

```python
IDLE_THRESHOLD_MINUTES = 20  # Change to 15, 30, etc.
```

### Adjust Work Hours

Edit `scripts/activity_tracker.py`:

```python
WORK_HOURS_START = 9   # 9am
WORK_HOURS_END = 23    # 11pm
```

### Adjust Cooldown

Edit `scripts/dopamine_defense.py`:

```python
INTERRUPT_COOLDOWN_MINUTES = 60  # Change to 30, 90, etc.
```

### Add Custom Quick Wins

Edit `data/quick_wins.json`:

```json
{
  "quick_wins": [
    {
      "id": "my_custom_task",
      "task": "Your task description here",
      "category": "productivity",
      "estimated_minutes": 5
    }
  ]
}
```

## Troubleshooting

### Interrupts Not Firing

1. Check idle status: `python3 scripts/activity_tracker.py status`
2. Check work hours (9am-11pm CST)
3. Check cooldown: `python3 scripts/dopamine_defense.py stats`
4. Verify `last_interrupt` in `data/dopamine_defense_state.json`

### Activity Not Recording

1. Verify `record_interaction()` is called on user messages
2. Check `data/activity_log.json` for recent timestamps
3. Make sure timezone is correct (CST = America/Chicago)

### Wrong Time Detection

System uses CST (America/Chicago). If Ross is in different timezone, update both:
- `scripts/activity_tracker.py`
- `scripts/dopamine_defense.py`

Change `CST = ZoneInfo('America/Chicago')` to your timezone.

## Data Files

- **activity_log.json** - Raw activity tracking
- **dopamine_defense_state.json** - Interrupt history and stats
- **quick_wins.json** - Task library
- **heartbeat-state.json** - Can optionally track `last_dopamine_check`

All files are in `~/clawd/data/` except `heartbeat-state.json` in `~/clawd/memory/`.

## Monitoring

### Check System Health

```bash
# Activity status
python3 ~/clawd/scripts/activity_tracker.py status

# Defense statistics
python3 ~/clawd/scripts/dopamine_defense.py stats

# Daily summary
python3 ~/clawd/scripts/activity_tracker.py summary

# Evening report preview
python3 ~/clawd/scripts/dopamine_defense.py report
```

### View Raw Data

```bash
# Activity log
cat ~/clawd/data/activity_log.json | jq

# Defense state
cat ~/clawd/data/dopamine_defense_state.json | jq

# Quick wins
cat ~/clawd/data/quick_wins.json | jq
```

## Performance

- **Activity recording:** <1ms (simple JSON write)
- **Idle check:** <1ms (timestamp comparison)
- **Interrupt check:** <5ms (includes quick win selection)
- **Daily summary:** <10ms (7-day window calculation)

No external dependencies, all computation is local.

## Success Metrics

After 1 week, review:

```python
from scripts.dopamine_defense import get_defense_stats

stats = get_defense_stats()
print(f"Total interrupts: {stats['total_interrupts']}")
print(f"Success rate: {int(stats['success_rate'] * 100)}%")
print(f"Avg response time: {stats['avg_response_time_minutes']}m")
```

**Target:** 60%+ success rate within 2 weeks

## Next Steps

1. ✅ Scripts created and tested
2. ✅ HEARTBEAT.md updated
3. ⏭️  Integrate into main agent message handler
4. ⏭️  Integrate into heartbeat routine
5. ⏭️  Test with real idle periods
6. ⏭️  Monitor for 1 week and tune

## Support

See full documentation: `docs/DOPAMINE_DEFENSE.md`

For issues or questions, check the test output:
```bash
python3 ~/clawd/scripts/test_dopamine_defense.py
```
