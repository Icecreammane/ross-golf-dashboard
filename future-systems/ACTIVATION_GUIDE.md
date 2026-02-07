# System Activation Guide

Step-by-step activation for all three systems. Follow this tomorrow morning.

---

## Pre-Flight Check

Before activating, ensure:
- ✅ All files built and in place (`ls ~/clawd/accountability`, `voice`, `sales`)
- ✅ Python 3 working (`python3 --version`)
- ✅ Morning brief read (`morning-briefs/2026-02-07.md`)
- ✅ Coffee made ☕️

---

## System 1: Predictive Accountability

### Step 1: Test Pattern Tracker

```bash
cd ~/clawd
python3 accountability/pattern_tracker.py "test_action" 5 revenue_task
```

Expected output:
```
✅ Logged: test_action (5min, revenue_task)
   Energy: high | morning | friday
```

### Step 2: Log Your First Real Action

When you complete something today:
```bash
python3 accountability/pattern_tracker.py "morning_planning" 15 admin
```

Or use the API in your workflow:
```python
from accountability.pattern_tracker import PatternTracker

tracker = PatternTracker()
tracker.log_action(
    action="deployed_fittrack_v2",
    action_type="revenue_task",
    duration=1800,  # 30 minutes
    completed=True
)
```

### Step 3: Set Up Heartbeat Integration

Add to `HEARTBEAT.md`:
```markdown
## Accountability Check

Every 2-4 hours:
- Check if intervention needed: `python3 accountability/intervention_engine.py check`
- If HIGH RISK: Send intervention immediately
```

### Step 4: Start Logging Everything

For the next 7 days, log:
- Every task you start and complete
- Every procrastination session (be honest!)
- Every context switch

Use quick log:
```bash
# Completed task
python3 accountability/pattern_tracker.py "contacted_10_leads" 45 selling

# Procrastination
python3 accountability/pattern_tracker.py "scrolled_twitter" 30 procrastinating

# Building
python3 accountability/pattern_tracker.py "fixed_bug_in_fittrack" 20 building
```

### Step 5: First Analysis (Day 3+)

After 3 days minimum:
```bash
python3 accountability/pattern_analyzer.py 3
```

This shows early patterns. Real insights come after 7 days.

---

## System 2: Voice Commands

### Step 1: Test Parser

```bash
cd ~/clawd
python3 voice/command_parser.py "Jarvis what's my MRR"
```

Expected output:
```
✅ Parsed Command:
   Intent: get_mrr
   Category: status
   Confidence: 90%
```

### Step 2: Test Full Pipeline

```bash
python3 voice/response_generator.py "Jarvis find 5 leads"
```

Expected output:
```
🎙️  Jarvis: Sales mode activated. Finding 5 perfect leads. Time to make money. Let's hunt.
```

### Step 3: Test Via Telegram

In your Jarvis Telegram chat, send:
```
Jarvis, what should I work on?
```

Jarvis should parse and respond naturally.

### Step 4: Test All Command Categories

Try one from each category:

**Status:**
```
Jarvis, am I on track?
```

**Mode Activation:**
```
Jarvis, activate sales mode
```

**Logging:**
```
Jarvis, log workout bench press 185
```

**Guidance:**
```
Jarvis, am I procrastinating?
```

### Step 5: Build the Habit

Use voice commands 5+ times today:
- Morning: "Jarvis, what should I work on?"
- Mid-day: "Jarvis, am I on track?"
- After task: "Jarvis, log win [thing you did]"
- Evening: "Jarvis, check progress"

### Step 6: Add Custom Commands (Optional)

See `voice/VOICE_SETUP.md` section "Adding Custom Commands"

---

## System 3: Self-Optimizing Outreach

### Step 1: Generate First Variations

```bash
cd ~/clawd
python3 sales/message_generator.py
```

This generates 10 variations for the example product. Inspect output.

### Step 2: Generate for YOUR Product

Create a script:
```python
from sales.message_generator import MessageGenerator

generator = MessageGenerator()

variations = generator.generate_variations(
    product="FitTrack",  # Your product
    target_audience="indie makers",  # Your audience
    pain_point="forget to track workouts",  # Their pain
    benefit="never miss a workout again",  # Your benefit
    lead_context={"name": "Alex"}  # Lead info
)

for i, var in enumerate(variations, 1):
    print(f"\n=== Variation {i}: {var['approach']} ===")
    print(var['message'])
```

### Step 3: Send First Test Batch

When you do outreach today:

```python
from sales.message_generator import MessageGenerator
from sales.response_tracker import ResponseTracker
import time

generator = MessageGenerator()
tracker = ResponseTracker()

# For each lead:
variations = generator.generate_variations(
    product="FitTrack",
    target_audience="indie makers",
    pain_point="forget to track workouts",
    benefit="never miss a workout"
)

# Pick one
selected = generator.pick_variation(variations, strategy="random")

# Send via your method
# send_dm(lead_username, selected["message"])

# Log it
msg_id = f"msg_{int(time.time())}_{lead_username}"
tracker.log_send(
    message_id=msg_id,
    lead=lead_username,
    variation=selected["variation_id"],
    approach=selected["approach"],
    message_content=selected["message"]
)
```

### Step 4: Track Responses

When someone replies:
```python
tracker.log_reply("msg_id_here")
```

When someone signs up:
```python
tracker.log_signup("msg_id_here")
```

Or via CLI:
```bash
python3 sales/response_tracker.py reply msg_001
python3 sales/response_tracker.py signup msg_001
```

### Step 5: View Dashboard

```bash
open ~/clawd/sales/outreach_dashboard.html
```

Leave it open while you work. Auto-refreshes every 30 seconds.

### Step 6: First Learning Report (50+ sends)

After 50+ messages sent:
```bash
python3 sales/learning_engine.py
```

This generates your first insights and recommendations.

### Step 7: First Evolution (100+ sends)

After 100+ messages:
```bash
python3 sales/evolution_engine.py
```

If ready to evolve, it generates Generation 2 variations based on winners.

---

## Integration: All Systems Working Together

### Morning Routine (7:30 AM)

```bash
# 1. Check yesterday's patterns
python3 accountability/pattern_analyzer.py 1

# 2. Plan today via voice
# (In Telegram) "Jarvis, what should I work on?"

# 3. Check outreach performance
python3 sales/response_tracker.py
```

### Work Session (9:00 AM)

```bash
# 1. Log start of work
python3 accountability/pattern_tracker.py "morning_focus_session" 90 building

# 2. Check for intervention risk
python3 accountability/intervention_engine.py check

# 3. If doing outreach, use optimized messages
python3 sales/message_generator.py
```

### Mid-Day Check (12:00 PM)

```bash
# Via voice in Telegram:
"Jarvis, am I on track?"
"Jarvis, log win [whatever you completed]"
```

### Afternoon Session (2:00 PM)

This is typical procrastination time. System should detect and warn.

```bash
# Intervention should trigger:
"🚨 It's 1:55pm Thursday. You usually procrastinate at 2pm.
Today's task: Deploy update. DO IT NOW."
```

### Evening Wrap (6:00 PM)

```bash
# 1. Log final tasks
python3 accountability/pattern_tracker.py "evening_wrap_up" 30 admin

# 2. Check outreach results
python3 sales/response_tracker.py

# 3. Status via voice
"Jarvis, check progress"
```

---

## Daily Checklist (Week 1)

### Every Day:
- [ ] Log at least 5 actions to pattern tracker
- [ ] Use voice commands 5+ times
- [ ] Send 10+ outreach messages (if doing sales)
- [ ] Track any replies/signups immediately

### Every 2-3 Days:
- [ ] Run pattern analysis
- [ ] Check outreach metrics
- [ ] Review intervention effectiveness

### End of Week 1:
- [ ] Generate full pattern report (7 days)
- [ ] Generate learning report (if 50+ sends)
- [ ] Decide if ready to evolve outreach

---

## Troubleshooting

### Pattern Tracker: "File not found"
```bash
mkdir -p ~/clawd/memory/patterns
```

### Voice Commands: "Could not parse"
Check wake word. Must start with "Jarvis" or "Hey Jarvis".

### Outreach: "Not enough data"
Keep sending. Need minimum 50 sends for insights.

### All Systems: Import errors
```bash
cd ~/clawd
export PYTHONPATH="$PYTHONPATH:$(pwd)"
```

Or run from clawd directory.

---

## Configuration Files to Create

### `~/.jarvis/systems.conf`
```json
{
  "pattern_tracking": {
    "enabled": true,
    "auto_log": false,
    "heartbeat_check": true,
    "intervention_threshold": 0.7
  },
  "voice_commands": {
    "enabled": true,
    "wake_word": "jarvis",
    "voice_output": false
  },
  "outreach_optimization": {
    "enabled": true,
    "auto_track": true,
    "min_sends_for_learning": 50,
    "evolution_threshold": 100
  }
}
```

### `HEARTBEAT.md` Addition
```markdown
## Future Systems Check

Every heartbeat (2-4 times daily):

1. **Accountability**: Check for high-risk procrastination windows
   ```bash
   python3 accountability/intervention_engine.py check
   ```
   If HIGH RISK → Send intervention immediately

2. **Outreach**: Check for new replies
   - Update response tracker
   - If >= 50 sends, check if ready to generate insights

3. **Voice**: Log command usage patterns
```

---

## Week 1 Activation Schedule

### Day 1 (Friday, Feb 7)
- Morning: Activate all systems
- Test each system independently
- Start logging patterns
- Send first outreach batch (10 messages)

### Day 2 (Saturday)
- Continue logging patterns
- Test voice commands 10+ times
- Send outreach batch #2 (10 messages)

### Day 3 (Sunday)
- First mini-analysis (3 days of patterns)
- Review voice command usage
- Track outreach responses

### Day 4-5 (Mon-Tue)
- Keep logging everything
- Voice commands become habit
- Outreach batches 3-4

### Day 6-7 (Wed-Thu)
- Full week pattern analysis
- Should have 50+ outreach sends
- First learning insights
- Decide on evolution

### End of Week 1
All systems:
- ✅ Collecting data
- ✅ Showing early patterns
- ✅ Integrated into workflow
- ✅ Ready for Week 2 optimization

---

## Support

If anything breaks or you're confused:
1. Check `SYSTEM_OVERVIEW.md` for how it works
2. Check individual system docs (in each folder)
3. Ask Jarvis: "Jarvis, how do I [thing]?"

---

**Let's activate tomorrow morning. Make it count.** 🚀
