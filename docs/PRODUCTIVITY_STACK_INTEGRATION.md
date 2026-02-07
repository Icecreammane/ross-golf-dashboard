# Productivity Stack Integration Guide

This guide shows how to integrate the 3-part productivity stack with Jarvis.

## Components

1. **Decision Framework Engine** - Kill overthinking with 7 proven frameworks
2. **Revenue Task Queue** - Always know the highest-value task to work on
3. **Launch Accountability Bot** - Ship more, build less

## Installation

### 1. Load Aliases

Add to your shell config (`~/.zshrc` or `~/.bashrc`):

```bash
source ~/clawd/scripts/productivity_aliases.sh
```

Then reload:
```bash
source ~/.zshrc
```

### 2. Quick Access Commands

After loading aliases, you can use:

- `decide "Should I launch X?"` - Run decision through frameworks
- `nexttask` - Show your highest priority revenue task
- `tasks` - List all revenue tasks sorted by priority
- `suggest 2` - Suggest tasks that fit in 2 hours
- `pressure` - Show uncomfortable truth about unlaunched projects
- `launch-status` - Full accountability dashboard

## Jarvis Integration

### HEARTBEAT.md Integration

Add this to `HEARTBEAT.md` for proactive accountability:

```markdown
## Daily Accountability Checks

### Morning (first heartbeat after 8am)
- Run `launch-accountability status` silently
- If projects sitting >3 days: mention casually
- If projects sitting >7 days: apply pressure

### Afternoon (around 2pm)
- Run `revenue-queue next` silently
- If Ross seems idle/indecisive: suggest the top task
- Keep it light: "Got 2 hours? nexttask says: [task]"

### Evening (last heartbeat before 10pm)
- Run `launch-accountability pressure` silently
- If days_sitting increased: gentle reminder
- Don't nag every day - rotate checks
```

### Autonomous Agent Integration

Add to `autonomous_check.py`:

```python
# Check launch accountability
result = subprocess.run(['python3', 'scripts/launch_accountability.py', 'status'], 
                       capture_output=True, text=True)
# Parse and act on unlaunched projects

# Suggest revenue tasks
result = subprocess.run(['python3', 'scripts/revenue_queue.py', 'next'],
                       capture_output=True, text=True)
# Surface high-priority tasks
```

### Telegram Integration

Make these available via Telegram commands:

- `/decide [question]` - Run decision framework
- `/nexttask` - Show next revenue task
- `/pressure` - Show accountability pressure
- `/tasks` - List revenue queue
- `/launch [project]` - Mark project as launched

## Usage Examples

### Decision Framework

```bash
# Interactive mode - asks questions
decide "Should I launch golf coaching tomorrow?"

# Quick mode - just shows frameworks
decide --quick "Build feature X or launch now?"
```

### Revenue Queue

```bash
# Add a task
revenue-queue add "Post on r/SideProject" --revenue 200 --time 1 --ease easy

# List all tasks (sorted by priority)
revenue-queue list

# Show next task
revenue-queue next

# Suggest tasks for available time
revenue-queue suggest 2  # "I have 2 hours, what should I do?"

# Complete a task
revenue-queue complete 1 --revenue 150  # actual revenue earned

# Weekly report
revenue-queue weekly
```

### Launch Accountability

```bash
# Add a project
launch-accountability add my-project "My Project Name" --date 2026-02-01

# Check status
launch-accountability status

# Apply pressure
launch-accountability pressure

# Mark as launched
launch-accountability launched my-project --revenue 100

# Update revenue
launch-accountability revenue my-project 250

# Set goal
launch-accountability goal 3000 2026-03-31
```

## Jarvis Behaviors

### When Ross is stuck deciding

**Instead of:** "What do you want to do?"
**Say:** "Run it through 'decide' - takes 2 minutes, kills overthinking."

### When Ross asks "what should I work on?"

**Instead of:** General suggestions
**Say:** Run `nexttask` and surface the result:
```
Your next task: Post FitTrack on r/SideProject
💰 $200 potential in 1hr (priority: 400)
```

### When projects sit too long

**Day 3:** "FitTrack has been ready for 3 days. Launch when you're ready."
**Day 7:** "7 days. Still $0 MRR. Type 'pressure' when you're ready for the truth."
**Day 14:** Don't ask. Just run `pressure` and show the output.

### Weekly Check-in

Every Monday morning:
1. Run `revenue-queue weekly` - show performance
2. Run `launch-accountability status` - show progress toward goal
3. Celebrate wins, apply pressure where needed

## Calibration Over Time

The revenue queue learns:
- Track actual vs expected revenue
- Learn which activities generate real money
- Adjust priority scores based on historical performance

Example:
```
Reddit posts: Expected $100, Actual avg $50 (50% accuracy)
Email campaigns: Expected $50, Actual avg $10 (20% accuracy)

→ Adjust future estimates accordingly
```

## Integration with Life OS

Add to Morning Command Center:
```markdown
## Revenue Focus
[Auto-populated from revenue-queue next]

## Launch Accountability
[Auto-populated from launch-accountability status]
```

## Success Metrics

Track these over 30 days:

1. **Decision Speed**
   - Before: Hours to decide
   - After: Minutes to decide

2. **Launch Rate**
   - Before: 1 launch per month
   - After: 1 launch per week

3. **Revenue Focus**
   - Before: "What should I work on?"
   - After: Always know the next high-value task

4. **Shipping Bias**
   - Before: Build → Perfect → Maybe Launch
   - After: Build → Launch → Iterate

## Philosophy

This stack exists to solve three problems:

1. **Analysis paralysis** → Decision framework
2. **Priority confusion** → Revenue queue
3. **Perpetual building** → Launch accountability

The goal isn't perfection. It's shipping.

---

Built: 2026-02-06
Last Updated: 2026-02-06
