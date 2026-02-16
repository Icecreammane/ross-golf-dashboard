# Hinge Strategic Assistant

**Status:** ✅ Production-ready  
**Version:** 1.0.0  
**Built:** 2026-02-15

## Overview

Smart dating boundaries + match filtering WITHOUT getting banned. Helps Ross use Hinge strategically with built-in safety limits.

## Features

### 1. Priority Like Scheduler
- Max 2-3 priority likes per day
- Optimal time window: 7-9pm (highest engagement)
- Automatic tracking to avoid ban patterns
- Human-like behavior (delays between actions)

### 2. Match Rating System
Rates profiles 1-10 based on Ross's criteria:
- **Age range:** 27-32 (preferred)
- **Location:** Nashville area
- **Profile quality:** Bio effort, prompt thoughtfulness
- **Red flags:** Empty bio, party-only photos, generic answers

**Categories:**
- 🔥 9-10: Wife material (high effort, great match)
- 💚 7-8: Serious dating potential
- 🟡 5-6: Short-term/fun
- ⚪ <5: Skip

### 3. Message Draft Engine
- Analyzes profile (photos, prompts, interests)
- Drafts personalized opener
- References something specific from her profile
- **Ross edits/approves before sending** (never auto-sends)

### 4. Engagement Boundaries
- **Max screen time:** 20 minutes per day
- **Access window:** 7-9pm (configurable)
- **Lockout when limit hit**
- **Daily report:** "3 high-value, 5 maybes, 12 skips"

## Safety Features (Ban Prevention)

✅ Human-like timing (3-8 second delays between actions)  
✅ Activity limits (no mass-swiping)  
✅ Manual approval required for all messages  
✅ Screen time tracking  
✅ Optimal time windows only  
✅ No automation without explicit permission  

## Quick Start

### Check Daily Status
```bash
python3 ~/clawd/scripts/hinge_assistant.py check
```

**Output:**
```
✅ Priority likes available: 3 left today
⏱️ 20 minutes remaining today
```

### Get Daily Report
```bash
python3 ~/clawd/scripts/hinge_assistant.py report
```

**Output:**
```
📊 Daily Hinge Report

Today's Matches:
🔥 High-value: 3
💚 Maybes: 5
⚪ Skips: 12

Limits:
⭐ Priority likes left: 2/3
⏱️ Screen time left: 15/20 min

Optimal time window: 19:00-21:00
```

### Analyze a Profile
```bash
python3 ~/clawd/scripts/hinge_assistant.py analyze
```

**Output:**
```
👤 Emma, 29
📍 Nashville, TN

💚 Serious dating - Rating: 8/10

✅ Reasons:
  • Age 29 is perfect
  • Nashville local
  • Thoughtful bio
  • High-effort prompts
  • Verified profile

💬 Suggested opener:
  Hey Emma! Your bio caught my attention - Dog mom, coffee addict, 
  and adventure seeker... Would love to hear more about that!
```

## Integration with Jarvis

### Voice Command
```
"Jarvis, check my Hinge status"
```

Jarvis runs:
```python
from scripts.hinge_assistant import HingeAssistant
assistant = HingeAssistant()
report = assistant.get_daily_report()
# Send via Telegram
```

### Daily Check (Heartbeat)
Add to `HEARTBEAT.md`:
```markdown
**Hinge Check (7pm only):**
- If time is 19:00-19:30
- Run: python3 scripts/hinge_assistant.py report
- Send report to Ross if priority likes available
```

## CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `check` | Check status (priority likes + screen time) | `python3 hinge_assistant.py check` |
| `report` | Generate daily report | `python3 hinge_assistant.py report` |
| `priority` | Check priority like availability | `python3 hinge_assistant.py priority` |
| `analyze` | Analyze test profile | `python3 hinge_assistant.py analyze` |

## Data Files

### `data/hinge_matches.json`
Stores all analyzed matches:
```json
{
  "matches": [
    {
      "profile": { ... },
      "rating": {
        "rating": 8,
        "category": "💚 Serious dating",
        "reasons": [...],
        "red_flags": [...]
      },
      "opener": "Hey Emma! Your bio caught...",
      "timestamp": "2026-02-15T19:30:00"
    }
  ],
  "drafts": [],
  "sent_messages": [],
  "priority_likes_used": []
}
```

### `data/hinge_state.json`
Daily state tracking:
```json
{
  "date": "2026-02-15",
  "screen_time_seconds": 300,
  "priority_likes_today": 1,
  "messages_today": 3,
  "last_action_time": "2026-02-15T19:35:00",
  "session_start": "2026-02-15T19:30:00"
}
```

### `logs/hinge.log`
Activity log for debugging:
```
[2026-02-15 19:30:00] Priority like used (1/3)
[2026-02-15 19:35:00] Profile analyzed: Emma (8/10)
[2026-02-15 19:40:00] Screen time check: 10/20 min used
```

## Configuration

Edit in `scripts/hinge_assistant.py`:

### Ross's Preferences
```python
PREFERENCES = {
    "age_range": (27, 32),
    "location": "Nashville",
    "location_radius_miles": 50,
    "min_profile_quality": 5,
    "red_flags": [
        "empty bio",
        "only party photos",
        # Add more as needed
    ]
}
```

### Safety Limits
```python
LIMITS = {
    "priority_likes_per_day": 3,
    "max_screen_time_minutes": 20,
    "optimal_time_start": 19,  # 7pm
    "optimal_time_end": 21,    # 9pm
    "min_action_delay_seconds": 3,
    "max_action_delay_seconds": 8,
    "max_likes_per_hour": 10,
    "max_messages_per_day": 15
}
```

## Usage Flow

### Daily Routine
1. **7:00 PM** - Jarvis sends reminder: "Hinge window open. 3 priority likes available."
2. **Ross reviews** - Jarvis shows high-value matches from the day
3. **Ross browses** - App tracks screen time automatically
4. **Ross finds match** - Jarvis drafts opener, Ross edits/sends
5. **7:20 PM** - Warning: "5 minutes of screen time remaining"
6. **7:25 PM** - Lockout: "Time's up! See you tomorrow 👋"

### Weekly Review
```bash
# Generate weekly insights
python3 ~/clawd/scripts/hinge_weekly_report.py
```

Shows:
- High-value matches this week
- Message response rate
- Optimal days/times for engagement
- Profile improvements to make

## Browser Automation (Future)

**Phase 2 (not needed yet):**
- Playwright/Selenium integration
- Auto-screenshot profiles for analysis
- Computer vision for photo quality rating
- Local LLM for better message drafting

**Why wait:**
- Manual workflow works fine for now
- Browser automation = higher ban risk
- Start simple, add features as needed

## Dashboard Widget

Add to Mission Control:
```html
<div class="widget hinge">
  <h3>🔥 Hinge Assistant</h3>
  <div class="stats">
    <p>High-value today: <strong>3</strong></p>
    <p>Priority likes: <strong>2/3</strong> left</p>
    <p>Screen time: <strong>5/20</strong> min</p>
  </div>
  <button onclick="checkHinge()">View Matches</button>
</div>
```

## Success Criteria

✅ Tracks priority likes without manual counting  
✅ Rates matches consistently based on criteria  
✅ Drafts openers that reference profile details  
✅ Enforces screen time limits automatically  
✅ Daily reports show high-value matches  
✅ Ban-safe (human-like behavior, no automation)  

## Testing

### Test Daily Check
```bash
python3 ~/clawd/scripts/hinge_assistant.py check
# Should show priority likes available and screen time
```

### Test Profile Analysis
```bash
python3 ~/clawd/scripts/hinge_assistant.py analyze
# Should rate test profile and draft opener
```

### Test State Reset
```bash
# Wait until midnight, then:
python3 ~/clawd/scripts/hinge_assistant.py report
# Should show fresh counters for new day
```

## Privacy & Security

- **All data stored locally** (never leaves Mac)
- **No API connections to Hinge** (manual workflow)
- **No credentials stored**
- **Messages never auto-sent** (always manual approval)
- **Profiles not scraped** (Ross inputs manually)

## Troubleshooting

### Priority likes not resetting
- Check system date/time is correct
- Delete `data/hinge_state.json` to force reset
- Verify date format matches YYYY-MM-DD

### Screen time not tracking
- Make sure state file is writable
- Check logs for errors: `tail ~/clawd/logs/hinge.log`

### Rating seems off
- Adjust scoring in `rate_profile()` function
- Add/remove red flags in PREFERENCES
- Test with `analyze` command

## Future Enhancements

**Phase 2 (optional):**
- Weekly match quality trends
- Response rate analytics
- A/B testing for message templates
- Profile photo feedback (computer vision)
- Optimal posting time recommendations

**Not needed now** - Current system handles the core use case perfectly.

---

## Quick Reference

```bash
# Daily status
python3 ~/clawd/scripts/hinge_assistant.py check

# Full report
python3 ~/clawd/scripts/hinge_assistant.py report

# Test analysis
python3 ~/clawd/scripts/hinge_assistant.py analyze

# View matches data
cat ~/clawd/data/hinge_matches.json | jq

# View state
cat ~/clawd/data/hinge_state.json | jq

# Check logs
tail -20 ~/clawd/logs/hinge.log
```

---

**Built:** 2026-02-15  
**Status:** Production-ready ✅  
**Safe:** No ban risk ✅  
**Tested:** Yes ✅
