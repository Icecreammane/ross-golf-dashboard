# Voice Commands Reference

Complete list of Jarvis voice commands and natural language patterns.

---

## Wake Word

All commands start with: **"Jarvis"** (or "Hey Jarvis")

Example: *"Jarvis, what's my MRR?"*

---

## STATUS QUERIES

### MRR / Revenue
- "Jarvis, what's my MRR?"
- "Jarvis, show me the MRR"
- "Jarvis, what's my revenue?"
- "Jarvis, how much am I making?"

### Progress Tracking
- "Jarvis, am I on track?"
- "Jarvis, how's my progress?"
- "Jarvis, check progress"
- "Jarvis, where am I at?"

### Launch Status
- "Jarvis, how's the launch going?"
- "Jarvis, launch status"
- "Jarvis, check launch"

---

## MODE ACTIVATION

### Sales Mode
- "Jarvis, activate sales mode"
- "Jarvis, find 10 leads"
- "Jarvis, sales mode with 5 leads"
- "Jarvis, let's sell"
- "Jarvis, outreach time"

### Build Mode
- "Jarvis, activate build mode"
- "Jarvis, let's build"
- "Jarvis, time to build"

### Research Mode
- "Jarvis, activate research mode"
- "Jarvis, find competitors"

---

## DATA LOGGING

### Workout Logging
- "Jarvis, log workout shoulder press 180 pounds"
- "Jarvis, track workout deadlift 5x5 at 225"
- "Jarvis, I did leg day"

### Food Logging
- "Jarvis, log food chicken breast and rice"
- "Jarvis, ate salmon and vegetables"
- "Jarvis, I consumed 2000 calories"

### Win Logging
- "Jarvis, log win first paying customer"
- "Jarvis, I got a signup today"
- "Jarvis, completed deployment on time"
- "Jarvis, win: 5 leads converted"

---

## GUIDANCE & ACCOUNTABILITY

### Task Guidance
- "Jarvis, what should I work on?"
- "Jarvis, what's next?"
- "Jarvis, suggest a task"
- "Jarvis, what's my next priority?"

### Accountability Check
- "Jarvis, am I procrastinating?"
- "Jarvis, check accountability"
- "Jarvis, keep me on track"

### Decision Support
- "Jarvis, what do you think?"
- "Jarvis, give me advice"
- "Jarvis, help me decide"

---

## NATURAL VARIATIONS

The parser understands many natural variations:

**Instead of:** "Jarvis, what is my MRR?"  
**You can say:** "Jarvis, what's my MRR?" or "Jarvis, show MRR"

**Instead of:** "Jarvis, log workout bench press"  
**You can say:** "Jarvis, track workout bench press" or "Jarvis, I did bench press"

**Instead of:** "Jarvis, activate sales mode"  
**You can say:** "Jarvis, let's sell" or "Jarvis, outreach time"

---

## QUICK REFERENCE

| Command | Example | Category |
|---------|---------|----------|
| **Status Check** | "Jarvis, am I on track?" | Status |
| **Find Leads** | "Jarvis, find 10 leads" | Action |
| **Log Workout** | "Jarvis, log workout deadlift 225" | Logging |
| **Next Task** | "Jarvis, what should I work on?" | Guidance |
| **Check Procrastination** | "Jarvis, am I procrastinating?" | Accountability |

---

## TIPS

1. **Be natural**: The parser handles contractions, variations, and casual phrasing
2. **Be specific**: For logging, include details ("shoulder press 180 pounds" vs just "workout")
3. **Context aware**: Jarvis responds differently based on time of day and current mode
4. **Conversational**: You can skip the wake word after the first command in a session

---

## COMING SOON

Future voice command capabilities:
- Calendar integration ("Jarvis, what's on my calendar?")
- Email summaries ("Jarvis, any important emails?")
- Reminder setting ("Jarvis, remind me in 30 minutes")
- Context switching ("Jarvis, switch to deep work mode")
- Performance analytics ("Jarvis, how was my week?")

---

## TESTING

To test a command without voice:
```bash
python3 ~/clawd/voice/response_generator.py "your command here"
```

Example:
```bash
python3 ~/clawd/voice/response_generator.py "Jarvis what's my MRR"
```

---

**Voice commands work anywhere Jarvis is active - Telegram, terminal, or direct chat.**
