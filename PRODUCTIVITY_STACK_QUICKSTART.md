# Productivity Stack - Quick Start

Your 3-part system to ship 10x more is ready. Here's how to use it in 60 seconds.

## 1. Activate Aliases (One-Time Setup)

```bash
# Add to your shell config
echo 'source ~/clawd/scripts/productivity_aliases.sh' >> ~/.zshrc

# Reload
source ~/.zshrc
```

Now you have:
- `decide` - Decision framework
- `nexttask` - Next revenue task
- `tasks` - List all tasks
- `suggest` - Suggest for available time
- `pressure` - Accountability pressure
- `launch-status` - Full dashboard

## 2. Try It Right Now

### When deciding anything:
```bash
decide "Should I launch FitTrack today or wait?"
# Walks you through 7 frameworks in 2 minutes
# Gives you a score and recommendation
```

### When you don't know what to work on:
```bash
nexttask
# Shows highest-priority revenue task
# With $ potential, time required, priority score
```

### When you want to see the full queue:
```bash
tasks
# All tasks sorted by ($/hr × ease)
```

### When you have limited time:
```bash
suggest 2
# "I have 2 hours - what should I do?"
# Shows tasks that fit in that time
```

### When you need uncomfortable truth:
```bash
pressure
# Shows days sitting unlaunched
# Shows MRR vs goal
# Applies escalating pressure
```

### When you want the full picture:
```bash
launch-status
# All unlaunched projects
# Goal tracking
# Days remaining
```

## 3. Daily Workflow

**Morning:**
```bash
nexttask          # What's most valuable?
launch-status     # Where am I?
```

**During work:**
```bash
decide "X or Y?"  # When stuck
```

**After completing a task:**
```bash
revenue-queue complete 1 --revenue 150
# Tracks actual vs expected
```

**Evening:**
```bash
pressure          # Face the truth
```

## 4. When You Launch Something

```bash
launch-accountability launched fittrack-pro --revenue 100
# Celebrates launch
# Updates MRR
# Resets pressure
```

## 5. Add Your Own Tasks

```bash
revenue-queue add "Your task description" --revenue 200 --time 2 --ease easy
```

Ease levels:
- `easy` - 2x multiplier (you know exactly how)
- `medium` - 1x multiplier (might need to figure some things out)
- `hard` - 0.5x multiplier (significant complexity)

## Pre-Seeded Data

You already have:

**Revenue tasks (4):**
1. Set up Stripe for FitTrack ($500, 1h) ← **Highest priority**
2. Post FitTrack on r/SideProject ($200, 1h)
3. Launch golf landing page ($300, 3h)
4. Post golf offer on r/golf ($100, 2h)

**Unlaunched projects (2):**
1. FitTrack Pro (built 2026-02-05)
2. Golf Coaching (built 2026-02-05)

**Goal:**
- Target: $3,000 MRR
- Deadline: 2026-03-31
- Days remaining: 53
- Required daily growth: $56.60/day

## The Philosophy

Three simple principles:

1. **Decisions in minutes, not days** - Run through frameworks, get a score, move on
2. **Always know what to work on** - Highest ($/hr × ease) wins
3. **Ship > Perfect** - Track days sitting, feel uncomfortable, launch

## Documentation

- **Full guide:** `docs/PRODUCTIVITY_STACK_README.md`
- **Jarvis integration:** `docs/PRODUCTIVITY_STACK_INTEGRATION.md`
- **Deployment details:** `docs/PRODUCTIVITY_STACK_DEPLOYMENT.md`

## Most Important Command

```bash
nexttask
```

This one command eliminates "what should I work on?" forever.

---

**Now go ship something.** 🚀
