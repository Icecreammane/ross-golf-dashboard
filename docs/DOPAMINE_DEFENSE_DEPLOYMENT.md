# Dopamine Defense System - Deployment Checklist

## ✅ Pre-Deployment Verification

### 1. Files Created
- [x] `scripts/activity_tracker.py` - Activity monitoring
- [x] `scripts/dopamine_defense.py` - Interrupt system
- [x] `scripts/heartbeat_dopamine_check.py` - Heartbeat wrapper
- [x] `scripts/test_dopamine_defense.py` - Test suite
- [x] `data/quick_wins.json` - Task library (10 tasks)
- [x] `data/activity_log.json` - Activity state (initialized)
- [x] `data/dopamine_defense_state.json` - System state (initialized)
- [x] `docs/DOPAMINE_DEFENSE.md` - Full documentation
- [x] `docs/DOPAMINE_DEFENSE_INTEGRATION.md` - Integration guide
- [x] `HEARTBEAT.md` - Updated with integration notes

### 2. Run Tests

```bash
# Full test suite
python3 ~/clawd/scripts/test_dopamine_defense.py

# Expected: All tests pass, evening report generates, quick wins rotate
```

**Status:** ✅ Tests pass (idle simulation shows expected behavior)

### 3. Verify Configuration

- **Work hours:** 9am - 11pm CST ✅
- **Idle threshold:** 20 minutes ✅
- **Cooldown period:** 60 minutes ✅
- **Timezone:** America/Chicago ✅
- **Dependencies:** None (uses built-in zoneinfo) ✅

### 4. Quick Wins Library

```bash
cat ~/clawd/data/quick_wins.json | jq '.quick_wins | length'
# Should output: 10
```

**Status:** ✅ 10 tasks configured across 6 categories

## 🚀 Deployment Steps

### Step 1: Integrate Activity Tracking

**In main agent's message handler:**

```python
from scripts.activity_tracker import record_interaction

def on_user_message(message):
    # First thing: record activity
    record_interaction("message")
    
    # Then process message normally
    handle_message(message)
```

**Test:** Send a message, then run:
```bash
python3 scripts/activity_tracker.py status
# Should show recent interaction, not idle
```

### Step 2: Integrate Heartbeat Check

**In heartbeat handler (runs every ~5 minutes):**

```python
from scripts.dopamine_defense import check_and_interrupt

def heartbeat():
    # ... other heartbeat tasks ...
    
    # Dopamine defense check
    result = check_and_interrupt()
    if result["should_interrupt"]:
        send_telegram_message(result["message"])
```

**Test:** Wait 20+ minutes idle during work hours, trigger heartbeat manually

### Step 3: Integrate Response Tracking

**In message handler, after recording activity:**

```python
from scripts.dopamine_defense import record_response_received

def on_user_message(message):
    record_interaction("message")
    record_response_received()  # Track re-engagement
    
    # ... rest of handler ...
```

**Test:** After receiving an interrupt, send a message. Check stats:
```bash
python3 scripts/dopamine_defense.py stats
# Should show success_rate > 0
```

### Step 4: Integrate Evening Report

**At 8pm CST, send daily report:**

```python
from scripts.dopamine_defense import generate_evening_report

def evening_checkin():
    report = generate_evening_report()
    send_telegram_message(report)
```

**Test:** Run manually:
```bash
python3 scripts/dopamine_defense.py report
# Should generate formatted report
```

## 🧪 Testing Protocol

### Test 1: Manual Idle Simulation

1. Record activity: `python3 scripts/activity_tracker.py record`
2. Edit `data/activity_log.json` - set `last_interaction` to 25 minutes ago
3. Run check: `python3 scripts/dopamine_defense.py check`
4. Should output: `"should_interrupt": true` with message

### Test 2: Live Idle Test

1. Send a message to Jarvis (records activity)
2. Wait 20+ minutes without interaction (during work hours 9am-11pm)
3. Trigger heartbeat (or wait for automatic)
4. Should receive Telegram message with quick win

### Test 3: Cooldown Verification

1. Receive one interrupt
2. Continue being idle
3. Next heartbeat check should show cooldown active
4. Should NOT receive second message within 60 minutes

### Test 4: Quick Win Rotation

```bash
for i in {1..5}; do
  python3 scripts/dopamine_defense.py check | jq -r '.quick_win.task // "No interrupt"'
done
```

Should see different tasks (or "No interrupt" if not idle).

### Test 5: Evening Report

```bash
# Simulate some activity throughout the day
python3 scripts/activity_tracker.py record

# Wait or simulate time passage

# Generate report
python3 scripts/dopamine_defense.py report
```

Should show time breakdown and productivity score.

## 📊 Monitoring (First Week)

### Daily Checks

```bash
# Morning: Check yesterday's activity
python3 scripts/activity_tracker.py summary

# Evening: Review defense stats
python3 scripts/dopamine_defense.py stats
```

### What to Watch

1. **Interrupt frequency** - Should be 1-3 per day initially
2. **Success rate** - Target 60%+ within 2 weeks
3. **False positives** - Interrupts during actual work?
4. **Cooldown effectiveness** - Too spammy or too quiet?

### Tuning Parameters

If too many interrupts:
- Increase `IDLE_THRESHOLD_MINUTES` to 30
- Increase `INTERRUPT_COOLDOWN_MINUTES` to 90

If too few interrupts:
- Decrease `IDLE_THRESHOLD_MINUTES` to 15
- Decrease `INTERRUPT_COOLDOWN_MINUTES` to 45

If work hours are wrong:
- Adjust `WORK_HOURS_START` and `WORK_HOURS_END`

## ✅ Success Criteria

After 1 week of operation:

- [ ] System has sent at least 5 interrupts
- [ ] Success rate ≥ 50% (Ross responds after interrupt)
- [ ] No spam complaints (cooldown working)
- [ ] Ross confirms: "Caught me mid-scroll at least once"
- [ ] Evening reports generate daily
- [ ] No system errors or crashes

## 🔧 Troubleshooting

### No Interrupts Firing

**Check:**
```bash
# Current status
python3 scripts/activity_tracker.py status

# Defense state
python3 scripts/dopamine_defense.py stats

# Raw data
cat data/activity_log.json | jq '.last_interaction'
cat data/dopamine_defense_state.json | jq '.last_interrupt'
```

**Common issues:**
- Not in work hours (9am-11pm CST)
- Not idle long enough (need 20+ min)
- Cooldown active (60 min since last interrupt)
- Activity tracking not integrated (no `last_interaction`)

### Interrupts Too Frequent

**Solutions:**
- Check cooldown is working: `jq '.last_interrupt' data/dopamine_defense_state.json`
- Increase cooldown in `scripts/dopamine_defense.py`
- Increase idle threshold

### Wrong Timezone

**Fix:**
Edit both `activity_tracker.py` and `dopamine_defense.py`:
```python
CST = ZoneInfo('Your/Timezone')  # e.g., 'America/New_York'
```

### Activity Not Recording

**Check integration:**
- Is `record_interaction()` called on every user message?
- Check `data/activity_log.json` for recent timestamps
- Run: `python3 scripts/activity_tracker.py record` manually

## 📝 Post-Deployment

### Week 1 Review (2026-02-23)

Run comprehensive analysis:

```bash
# Activity summary
python3 scripts/activity_tracker.py summary

# Defense stats
python3 scripts/dopamine_defense.py stats

# Evening report
python3 scripts/dopamine_defense.py report
```

**Questions for Ross:**
1. Did it catch you scrolling at least once?
2. Were the interrupts helpful or annoying?
3. Should we adjust timing or frequency?
4. Are the quick wins actually quick and valuable?

### Week 2 Tuning

Based on Week 1 feedback:
- Adjust thresholds
- Add/remove quick win tasks
- Customize message templates
- Fine-tune work hours

### Long-term Evolution

**Potential enhancements:**
- Learn best times to interrupt (success rate by hour)
- Context-aware quick wins (morning vs evening tasks)
- Integration with calendar (don't interrupt during meetings)
- Progressive urgency (escalate message tone for longer idles)
- Weekend mode (different thresholds)

## 🎯 Final Checklist

Before marking as "deployed":

- [ ] Activity tracking integrated in message handler
- [ ] Heartbeat check integrated
- [ ] Response tracking integrated
- [ ] Evening report scheduled
- [ ] Ran full test suite successfully
- [ ] Verified quick wins library loaded
- [ ] Tested manual idle simulation
- [ ] HEARTBEAT.md updated
- [ ] Documentation complete
- [ ] Ross briefed on system

## 📚 Documentation Index

- **Full docs:** `docs/DOPAMINE_DEFENSE.md`
- **Integration guide:** `docs/DOPAMINE_DEFENSE_INTEGRATION.md`
- **This checklist:** `docs/DOPAMINE_DEFENSE_DEPLOYMENT.md`
- **Heartbeat notes:** `HEARTBEAT.md` (search "Dopamine Defense")

## 🚦 Deployment Status

**Current Status:** 🟡 Built, Ready for Integration

**Next Action:** Integrate activity tracking in main agent's message handler

**Owner:** Main agent (Jarvis)

**Timeline:** Deploy during next heartbeat cycle, monitor for 1 week

---

**Built:** 2026-02-16  
**Deployed:** [Pending]  
**First Review:** [Scheduled 2026-02-23]
