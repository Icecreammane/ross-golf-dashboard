# Productivity Stack for Shipping Machines

A 3-part system to turn builders into shippers: make decisions faster, prioritize revenue work, and actually launch things.

## The Problem

You build great things. But:
- You spend days deciding what to work on
- You're never sure if you're working on the RIGHT thing
- Projects sit "almost ready" for weeks
- $0 MRR despite having completed products

## The Solution

Three interconnected tools that work together:

### 1. Decision Framework Engine 🧠

**Kills overthinking in 2 minutes.**

Runs any decision through 7 proven frameworks:
- ⚡ Speed Test - Can results happen in <7 days?
- 🔍 Validation Test - Is there proof of demand?
- ⚠️ Risk Test - What's worst case?
- ⏰ Regret Test - Will you regret NOT doing it?
- 💰 Revenue Test - Does it lead to money?
- ⏱️ Time ROI - Hours vs potential return
- 🔥 Hell Yeah Test - Does it excite you?

**Usage:**
```bash
decide "Should I launch golf coaching tomorrow?"
```

**Output:**
```
DECISION: Should I launch golf coaching tomorrow?

✅ Speed Test: YES (revenue in 48 hours)
✅ Validation Test: YES (r/golf has demand)
✅ Risk Test: LOW (2 hours max lost)
✅ Regret Test: YES (will regret waiting)
✅ Revenue Test: YES (direct $)
⚠️  Time ROI: MEDIUM (2 hrs for potential $100)
✅ Hell Yeah: YES

SCORE: 6/7 ✅

RECOMMENDATION: LAUNCH IT. Stop overthinking.
```

### 2. Revenue Task Queue 💰

**Always know the highest-value task.**

Prioritizes tasks by: ($ per hour) × ease multiplier

**Usage:**
```bash
# Add tasks
revenue-queue add "Post on r/SideProject" --revenue 200 --time 1 --ease easy

# Show next task
nexttask

# List all tasks
tasks

# Suggest for available time
suggest 2  # "I have 2 hours"

# Complete and track
revenue-queue complete 1 --revenue 150
```

**Output:**
```
YOUR NEXT TASK:

#1 Post FitTrack on r/SideProject

💰 Revenue potential: $200
⏱️  Time required: 1h
🎯 Ease: easy
📊 Priority score: 400

$ per hour: $200

Ready to ship? 🚀
```

**Features:**
- Auto-calculates priority scores
- Suggests tasks based on available time
- Tracks actual vs expected revenue
- Weekly performance reports
- Learns which activities actually make money

### 3. Launch Accountability Bot 🚀

**Ships > Perfects.**

Tracks projects from "built" to "launched" and applies escalating pressure.

**Usage:**
```bash
# Add a project
launch-accountability add fittrack-pro "FitTrack Pro" --date 2026-02-05

# Check status
launch-status

# Apply pressure
pressure

# Mark as launched
launch-accountability launched fittrack-pro --revenue 100
```

**Output (Day 7):**
```
⚠️  UNCOMFORTABLE TRUTH

You've built for 7 days straight. LAUNCH SOMETHING.

🟠 FitTrack Pro: 7 days, $0 revenue
🟠 Golf Coaching: 7 days, $0 revenue

THE MATH:
Current MRR: $0
Target MRR: $3,000
Days remaining: 46
Required daily growth: $65.22/day
At current rate: You'll hit $0 by March 31
```

**Features:**
- Tracks days sitting unlaunched
- Escalating pressure messages
- Math tracker: MRR vs goal
- Celebrates launches
- Weekly accountability reports

## Quick Start

### 1. Setup Aliases

```bash
# Add to ~/.zshrc or ~/.bashrc
source ~/clawd/scripts/productivity_aliases.sh

# Reload shell
source ~/.zshrc
```

### 2. Seed Your Data

```bash
# Add your unlaunched projects
launch-accountability add fittrack-pro "FitTrack Pro"
launch-accountability add golf-coaching "Golf Coaching"

# Set your goal
launch-accountability goal 3000 2026-03-31

# Add revenue tasks
revenue-queue add "Post FitTrack on r/SideProject" --revenue 200 --time 1 --ease easy
revenue-queue add "Post golf offer on r/golf" --revenue 100 --time 2 --ease easy
revenue-queue add "Set up Stripe for FitTrack" --revenue 500 --time 1 --ease medium
```

### 3. Use Daily

```bash
# Morning: Check what to work on
nexttask

# When deciding: Run through framework
decide "Should I build feature X or launch now?"

# Evening: Face the truth
pressure
```

## Integration with Jarvis

Jarvis can proactively:

**When you're stuck:**
→ "Run it through 'decide' - kills overthinking in 2 min"

**When you ask "what should I work on?":**
→ Runs `nexttask` and shows priority task

**When projects sit >7 days:**
→ Runs `pressure` and shows uncomfortable truth

**Weekly:**
→ Performance report from revenue-queue
→ Accountability check from launch-accountability

See `PRODUCTIVITY_STACK_INTEGRATION.md` for full details.

## Files

```
clawd/
├── scripts/
│   ├── decision_framework.py        # 7 framework tests
│   ├── revenue_queue.py             # Task prioritization
│   ├── launch_accountability.py     # Launch pressure
│   └── productivity_aliases.sh      # Shell aliases
├── data/
│   ├── revenue-tasks.json           # Task queue
│   └── launch-accountability.json   # Project tracking
└── docs/
    ├── PRODUCTIVITY_STACK_README.md           # This file
    └── PRODUCTIVITY_STACK_INTEGRATION.md      # Jarvis integration
```

## Philosophy

This stack is built on three beliefs:

1. **Decisions don't need days** - Run it through frameworks, get a score, move on
2. **Not all work is equal** - Prioritize by $/hour × ease
3. **Shipping > Perfecting** - Track days sitting, apply pressure, launch

The goal: **10x more shipping, 10x less overthinking**

## Workflow

### Daily Workflow

**Morning:**
```bash
launch-status  # Where am I?
nexttask       # What's most valuable?
```

**During work:**
```bash
decide "Should I X or Y?"  # When stuck
suggest 2                   # "I have 2 hours free"
```

**Evening:**
```bash
revenue-queue complete 1 --revenue 150  # Log what you did
pressure                                 # Face the truth
```

### Weekly Review

```bash
revenue-queue weekly           # What actually made money?
launch-accountability status   # Progress toward goal?
```

## Success Metrics

After 30 days, you should see:

- ✅ Decision time: Hours → Minutes
- ✅ "What should I work on?": Never ask again
- ✅ Launch rate: Monthly → Weekly
- ✅ MRR: $0 → Growing

## Commands Cheat Sheet

### Decision Framework
```bash
decide "Should I do X?"        # Interactive evaluation
decide --quick "X or Y?"       # Show frameworks only
```

### Revenue Queue
```bash
revenue-queue add "Task" --revenue 100 --time 2 --ease easy
revenue-queue list             # All tasks, sorted
revenue-queue next             # Top priority
revenue-queue suggest 2        # Fits in 2 hours
revenue-queue complete 1       # Mark done
revenue-queue weekly           # Performance report
```

### Launch Accountability
```bash
launch-accountability add project-id "Project Name"
launch-accountability status   # Dashboard
launch-accountability pressure # Truth bomb
launch-accountability launched project-id --revenue 100
launch-accountability revenue project-id 250
launch-accountability goal 3000 2026-03-31
```

### Aliases
```bash
decide          # Decision framework
nexttask        # Next revenue task
tasks           # List all tasks
suggest 2       # Suggest for 2 hours
pressure        # Accountability pressure
launch-status   # Full dashboard
```

## Examples

### Example 1: Morning Decision

Ross: "Should I add social login to FitTrack or launch with email-only?"

```bash
$ decide "Add social login or launch with email-only?"

⚡ Speed Test - Can you see results in < 7 days? (y/n): n
   Why/timeline: Social login = 2 days extra

🔍 Validation Test - Is there proof of demand? (y/n): n
   Evidence: No one asked for it yet

⚠️  Risk Test - What's the WORST that could happen?: Users want social, but email works
   Severity (low/medium/high): low

⏰ Regret Test - Will you regret NOT doing this in 1 year? (y/n): n
   Why: Can add later

💰 Revenue Test - Does this lead to money? (y/n): n
   How: Indirect at best

⏱️  Time ROI - Hours required: 16
   Potential return ($): 0

🔥 Hell Yeah Test - Does this excite you? (hell yeah/no): no

RESULTS:

❌ Speed Test: NO (Social login = 2 days extra)
❌ Validation Test: NO (No one asked for it yet)
✅ Risk Test: LOW (Users want social, but email works)
✅ Regret Test: NO (Can add later)
❌ Revenue Test: NO (Indirect at best)
❌ Time ROI: LOW (16hrs for $0 = $0/hr)
❌ Hell Yeah: NO

SCORE: 2/7 ❌

RECOMMENDATION: PAUSE. Too many red flags. Find something better.
```

**Decision made in 2 minutes: Launch with email, add social later if needed.**

### Example 2: Priority Confusion

Ross: "I have 2 hours. What should I work on?"

```bash
$ suggest 2

YOU HAVE 2h - HERE'S WHAT TO DO:

1. #1 Post FitTrack on r/SideProject
   💰 $200 in 1h (priority: 400)

2. #3 Set up Stripe for FitTrack
   💰 $500 in 1h (priority: 500)

3. #2 Post golf offer on r/golf
   💰 $100 in 2h (priority: 100)

Pick one and ship it. ⚡
```

**Clear priority. No more "hmm what should I do?"**

### Example 3: Launch Pressure

Day 10 of FitTrack sitting "almost ready":

```bash
$ pressure

⚠️  UNCOMFORTABLE TRUTH

10 days of building. Still $0 MRR. 43 days to deadline.

🔴 FitTrack Pro: 10 days, $0 revenue
🔴 Golf Coaching: 10 days, $0 revenue

THE MATH:
Current MRR: $0
Target MRR: $3,000
Days remaining: 43
Required daily growth: $69.77/day
At current rate: You'll hit $0 by March 31
```

**Uncomfortable? Good. That's the point. Ship something today.**

## Calibration

The system learns over time:

**Week 1:**
```
Reddit post: Expected $200, Actual $50
Email campaign: Expected $100, Actual $10
```

**Week 4:**
```
Reddit post: Expected $50 (learned), Actual $60 ✅
Email campaign: Expected $15 (learned), Actual $12 ✅
```

The more you track actual vs expected, the smarter the priority scores become.

## Anti-Patterns

**Don't:**
- ❌ Add tasks just to feel productive
- ❌ Ignore the pressure - that's the point
- ❌ Perfect the project before launching
- ❌ Skip tracking actual revenue (system needs to learn)

**Do:**
- ✅ Trust the priority scores
- ✅ Launch before you're ready
- ✅ Track actual outcomes
- ✅ Let uncomfortable truth drive action

## Support

Questions? Issues? Improvements?

- Check `PRODUCTIVITY_STACK_INTEGRATION.md` for Jarvis integration
- All scripts include `--help` flags
- Data files are human-readable JSON - edit directly if needed

---

**Built:** 2026-02-06  
**Purpose:** Turn Ross into a shipping machine  
**Status:** Ready to launch (practice what we preach)  
