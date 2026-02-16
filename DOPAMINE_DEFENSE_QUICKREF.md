# Dopamine Defense - Quick Reference Card

## 🚀 Integration (Copy-Paste Ready)

### Message Handler
```python
from scripts.activity_tracker import record_interaction
from scripts.dopamine_defense import record_response_received

def on_user_message(message):
    record_interaction("message")
    record_response_received()
    # ... rest of handler
```

### Heartbeat Handler
```python
from scripts.dopamine_defense import check_and_interrupt

def heartbeat():
    result = check_and_interrupt()
    if result["should_interrupt"]:
        # Send via message tool
        message_tool(action="send", target="ross", message=result["message"])
```

### Evening Check-In (8pm)
```python
from scripts.dopamine_defense import generate_evening_report

def evening_checkin():
    report = generate_evening_report()
    message_tool(action="send", target="ross", message=report)
```

## 🧪 Testing Commands

```bash
# Full test suite
python3 ~/clawd/scripts/test_dopamine_defense.py

# Quick checks
python3 scripts/activity_tracker.py status
python3 scripts/dopamine_defense.py check
python3 scripts/dopamine_defense.py stats
python3 scripts/dopamine_defense.py report
```

## ⚙️ Configuration

**Files to edit:**
- Quick wins: `data/quick_wins.json`
- Thresholds: `scripts/activity_tracker.py` (IDLE_THRESHOLD, WORK_HOURS)
- Cooldown: `scripts/dopamine_defense.py` (INTERRUPT_COOLDOWN)

**Current settings:**
- Idle: 20 min
- Work hours: 9am-11pm CST
- Cooldown: 60 min

## 📚 Documentation

- Full docs: `docs/DOPAMINE_DEFENSE.md`
- Integration: `docs/DOPAMINE_DEFENSE_INTEGRATION.md`
- Deployment: `docs/DOPAMINE_DEFENSE_DEPLOYMENT.md`
- Build summary: `BUILD_DOPAMINE_DEFENSE.md`

## 🎯 Success Metrics

After 1 week:
- Interrupts sent: 5-15
- Success rate: >60%
- Ross confirms: "Caught me scrolling!"
