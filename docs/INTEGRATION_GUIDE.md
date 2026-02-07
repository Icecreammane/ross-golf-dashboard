# Integration Guide

How the autonomous operation system connects to existing infrastructure.

## 🔌 System Connections

```
┌─────────────────────────────────────────────────┐
│           Autonomous Operations                 │
│                                                 │
│  ┌─────────────┐  ┌──────────────┐            │
│  │   Build     │  │  Overnight   │            │
│  │  Scheduler  │→│   Runner     │            │
│  └─────────────┘  └──────────────┘            │
│         ↓                 ↓                     │
│  ┌─────────────┐  ┌──────────────┐            │
│  │   Context   │  │   Problem    │            │
│  │  Scheduler  │  │  Predictor   │            │
│  └─────────────┘  └──────────────┘            │
│         ↓                 ↓                     │
│  ┌─────────────┐  ┌──────────────┐            │
│  │  Pattern    │  │    Self-     │            │
│  │  Learner    │  │  Improver    │            │
│  └─────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────┘
         ↓                 ↓                ↓
┌────────────────┐  ┌────────────┐  ┌──────────────┐
│   Heartbeat    │  │    Cron    │  │   Morning    │
│    System      │  │    Jobs    │  │    Brief     │
└────────────────┘  └────────────┘  └──────────────┘
         ↓                 ↓                ↓
┌────────────────────────────────────────────────────┐
│              Memory System & Logs                  │
└────────────────────────────────────────────────────┘
```

## 📅 Cron Integration

### Setup Cron Jobs

Edit crontab:
```bash
crontab -e
```

Add these entries:
```cron
# Overnight execution (11:00pm daily)
0 23 * * * cd /Users/clawdbot/clawd && /usr/bin/python3 autonomous/overnight_runner.py start >> /tmp/overnight.log 2>&1

# Morning report (6:30am daily)
30 6 * * * cd /Users/clawdbot/clawd && /usr/bin/python3 autonomous/overnight_runner.py report >> /tmp/overnight_report.log 2>&1

# Morning brief with autonomous section (7:00am daily)
0 7 * * * cd /Users/clawdbot/clawd && /usr/bin/python3 scripts/generate-morning-brief.py >> /tmp/morning_brief.log 2>&1

# Weekend planner (Friday 6pm)
0 18 * * 5 cd /Users/clawdbot/clawd && /usr/bin/python3 autonomous/weekend_planner.py suggest >> /tmp/weekend_planner.log 2>&1

# Problem scan (every 6 hours)
0 */6 * * * cd /Users/clawdbot/clawd && /usr/bin/python3 autonomous/problem_predictor.py scan >> /tmp/problem_scan.log 2>&1

# Auto-fix problems (daily at 11pm before overnight run)
55 22 * * * cd /Users/clawdbot/clawd && /usr/bin/python3 autonomous/problem_predictor.py fix >> /tmp/problem_fix.log 2>&1
```

### Verify Cron Jobs
```bash
# List current cron jobs
crontab -l

# Check cron logs
tail -f /tmp/overnight.log
tail -f /tmp/morning_brief.log
```

## 💓 Heartbeat Integration

### Update HEARTBEAT.md

Add to `HEARTBEAT.md`:
```markdown
# Heartbeat Tasks

## Build Queue Check (2x daily)
- Check morning (9am context)
- Check evening (7pm context)
- `cd autonomous && python3 build_scheduler.py next`
- Present available tasks if Ross is available

## Context Detection (every heartbeat)
- `cd autonomous && python3 context_scheduler.py detect`
- Adjust work based on context
- Log context transitions

## Pattern Learning (1x daily)
- Check for new patterns
- `cd autonomous && python3 pattern_learner.py suggest`
- Pre-build if confidence >0.8

## Problem Scan (2x daily)
- Morning and evening
- `cd autonomous && python3 problem_predictor.py scan`
- Auto-fix safe problems
- Escalate critical issues
```

### Heartbeat Workflow

```python
# In heartbeat handler
import subprocess
import json

def heartbeat_check():
    # 1. Detect context
    result = subprocess.run(
        ['python3', 'autonomous/context_scheduler.py', 'detect'],
        capture_output=True,
        text=True
    )
    
    # 2. Check for tasks if Ross available
    if context == "AVAILABLE":
        result = subprocess.run(
            ['python3', 'autonomous/build_scheduler.py', 'next'],
            capture_output=True,
            text=True
        )
        # Present quick wins
    
    # 3. Pattern suggestions
    if should_check_patterns():
        result = subprocess.run(
            ['python3', 'autonomous/pattern_learner.py', 'suggest'],
            capture_output=True,
            text=True
        )
        # Pre-build if high confidence
    
    return "HEARTBEAT_OK"
```

## 📝 Morning Brief Integration

### Update generate-morning-brief.py

Add autonomous section:

```python
#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime

def generate_morning_brief():
    brief = []
    
    # Date and greeting
    brief.append(f"🌅 **Good Morning!**")
    brief.append(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}\n")
    
    # Autonomous section (NEW!)
    brief.append("## 🚀 Overnight Builds\n")
    
    try:
        # Get overnight report
        result = subprocess.run(
            ['python3', 'autonomous/overnight_runner.py', 'brief'],
            capture_output=True,
            text=True,
            cwd='/Users/clawdbot/clawd'
        )
        
        if result.returncode == 0:
            brief.append(result.stdout)
        else:
            brief.append("_No overnight builds (run overnight_runner.py manually)_\n")
    except Exception as e:
        brief.append(f"_Error loading overnight report: {e}_\n")
    
    # Build queue status
    brief.append("\n## 📋 Build Queue\n")
    
    try:
        result = subprocess.run(
            ['python3', 'autonomous/build_scheduler.py', 'stats'],
            capture_output=True,
            text=True,
            cwd='/Users/clawdbot/clawd'
        )
        brief.append(result.stdout)
    except Exception as e:
        brief.append(f"_Error loading queue stats: {e}_\n")
    
    # Pattern predictions
    brief.append("\n## 🔮 Today's Predictions\n")
    
    try:
        result = subprocess.run(
            ['python3', 'autonomous/pattern_learner.py', 'predict'],
            capture_output=True,
            text=True,
            cwd='/Users/clawdbot/clawd'
        )
        
        if result.stdout.strip():
            brief.append(result.stdout)
        else:
            brief.append("_No predictions for today_\n")
    except Exception as e:
        brief.append(f"_Error loading predictions: {e}_\n")
    
    # ... rest of morning brief (weather, calendar, etc.)
    
    return "\n".join(brief)

if __name__ == "__main__":
    print(generate_morning_brief())
```

## 🧠 Memory Integration

### Daily Memory Files

Log autonomous actions to `memory/YYYY-MM-DD.md`:

```python
def log_to_memory(action: str, details: str):
    """Log autonomous action to daily memory"""
    from datetime import datetime
    import os
    
    date = datetime.now().strftime('%Y-%m-%d')
    memory_file = f'memory/{date}.md'
    
    # Ensure memory directory exists
    os.makedirs('memory', exist_ok=True)
    
    # Append to daily log
    with open(memory_file, 'a') as f:
        timestamp = datetime.now().strftime('%H:%M')
        f.write(f"\n## [{timestamp}] Autonomous: {action}\n")
        f.write(f"{details}\n")
```

### Example Memory Entries

```markdown
## [23:15] Autonomous: Overnight Session Started
- Context: SLEEPING
- Tasks queued: 3
- Max concurrent: 3

## [03:45] Autonomous: Build Completed
- Task: Optimize database queries
- Runtime: 3.8 hours
- Result: 5x speedup achieved
- Tests: All passing

## [06:30] Autonomous: Morning Report Generated
- Tasks completed: 2
- Hours shipped: 6.3
- Problems fixed: 2
```

## 🔄 Sub-Agent Spawning

### Clawdbot API Integration

When spawning sub-agents, use clawdbot spawn API:

```python
def spawn_subagent(task: BuildTask) -> Optional[SubAgent]:
    """Spawn a sub-agent via clawdbot API"""
    
    # Build prompt
    prompt = f"""You are a sub-agent spawned to complete: {task.title}

Description: {task.description}
Category: {task.category}
Estimated: {task.estimated_hours} hours

Complete this task autonomously. Test thoroughly and document."""
    
    # In actual implementation, would call clawdbot spawn API
    # For now, log the intent
    
    agent = SubAgent(task.id)
    log_subagent_spawn(task, agent, prompt)
    
    return agent
```

## 📊 Progress Tracking

### Status Dashboard (Future)

Create `autonomous/dashboard.py` for real-time status:

```python
#!/usr/bin/env python3
"""Real-time autonomous operations dashboard"""

def generate_dashboard():
    queue = AutonomousQueue()
    scheduler = BuildScheduler()
    context = ContextScheduler()
    
    print("=" * 60)
    print("AUTONOMOUS OPERATIONS DASHBOARD")
    print("=" * 60)
    
    # Current context
    ctx = context.detect_context()
    print(f"\n📍 Context: {ctx.value}")
    print(f"⚡ Work Intensity: {context.get_work_intensity()}")
    print(f"🔨 Max Concurrent: {context.get_max_concurrent_builds()}")
    
    # Active builds
    progress = queue.track_progress()
    print(f"\n🏗️  Active Builds: {len(progress)}")
    for p in progress:
        print(f"  • {p['title']} ({p['progress_percent']:.0f}%)")
    
    # Queue stats
    stats = scheduler.get_stats()
    print(f"\n📊 Queue Stats:")
    print(f"  Total: {stats['total']}")
    print(f"  Queued: {stats['queued']}")
    print(f"  Completed: {stats['completed']}")
    print(f"  Rate: {stats['completion_rate']:.0%}")
    
    # Next tasks
    next_tasks = scheduler.get_next_scheduled_tasks(3)
    print(f"\n🎯 Next Tasks:")
    for task in next_tasks:
        print(f"  • {task.title} ({task.estimated_hours}h)")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    generate_dashboard()
```

Run dashboard:
```bash
cd autonomous
python3 dashboard.py
```

## 🔗 External Integrations

### Telegram/Discord Notifications

Send overnight completion to Telegram:

```python
def send_completion_notification():
    """Send overnight report to Telegram"""
    report = queue.generate_morning_report()
    
    message = f"""🌅 Overnight Build Report

✅ Completed: {len(report['completed_overnight'])} tasks
⏱️ Hours shipped: {report['total_hours_shipped']:.1f}h
🔧 Problems fixed: {len(report['problems_fixed'])}

Check full report: /autonomous-report"""
    
    # Send via message tool
    # message(action="send", target="ross", message=message)
```

### Calendar Integration

Block "building time" on calendar:

```python
def block_building_time():
    """Add overnight building session to calendar"""
    from datetime import datetime, timedelta
    
    # Create calendar event: "Jarvis Building (Autonomous)"
    # Time: 11pm-7am
    # Recurrence: Daily
    # Description: "Autonomous build session - do not disturb"
```

## 🧪 Testing Integration

### Test Autonomous System

```bash
cd autonomous

# Test each component
python3 build_scheduler.py stats
python3 autonomous_queue.py progress
python3 context_scheduler.py detect
python3 problem_predictor.py scan
python3 pattern_learner.py list
python3 self_improver.py stats

# Test overnight workflow (without actually spawning)
python3 overnight_runner.py start

# Test weekend planner
python3 weekend_planner.py suggest

# Test morning brief
python3 overnight_runner.py brief
```

### Integration Test Script

Create `autonomous/test_integration.sh`:

```bash
#!/bin/bash
# Integration test for autonomous system

echo "Testing Autonomous Operations System..."

cd autonomous

echo "1. Testing build scheduler..."
python3 build_scheduler.py stats || exit 1

echo "2. Testing queue manager..."
python3 autonomous_queue.py progress || exit 1

echo "3. Testing context detection..."
python3 context_scheduler.py detect || exit 1

echo "4. Testing problem predictor..."
python3 problem_predictor.py metrics || exit 1

echo "5. Testing pattern learner..."
python3 pattern_learner.py stats || exit 1

echo "6. Testing self-improver..."
python3 self_improver.py stats || exit 1

echo "7. Testing overnight runner..."
python3 overnight_runner.py is-overnight || echo "Not overnight (OK)"

echo "8. Testing weekend planner..."
python3 weekend_planner.py progress || echo "No weekend project (OK)"

echo ""
echo "✅ All integration tests passed!"
```

Run tests:
```bash
chmod +x autonomous/test_integration.sh
./autonomous/test_integration.sh
```

## 📚 Complete Setup Checklist

### Initial Setup
- [ ] Create `autonomous/` directory structure
- [ ] Copy all Python scripts
- [ ] Create `docs/` with all documentation
- [ ] Test each script individually

### Cron Setup
- [ ] Add cron jobs (see above)
- [ ] Verify cron is running: `crontab -l`
- [ ] Check cron logs: `tail -f /tmp/overnight.log`

### Heartbeat Setup
- [ ] Update `HEARTBEAT.md` with autonomous checks
- [ ] Test heartbeat integration
- [ ] Verify context detection works

### Morning Brief Setup
- [ ] Update `generate-morning-brief.py`
- [ ] Test morning brief generation
- [ ] Verify autonomous section appears

### Memory Setup
- [ ] Create `memory/` directory if needed
- [ ] Test logging to daily files
- [ ] Verify memory entries appear

### Testing
- [ ] Run integration test script
- [ ] Add test task to queue
- [ ] Verify overnight runner works
- [ ] Check morning brief includes overnight work

### Production Launch
- [ ] Queue first real tasks
- [ ] Run overnight session
- [ ] Review morning brief next day
- [ ] Iterate and improve

## 🎯 Success Criteria

System is fully integrated when:

✅ Overnight runner executes automatically (cron)
✅ Morning brief includes overnight builds
✅ Heartbeat checks build queue
✅ Context detection adjusts work
✅ Patterns are learned and predicted
✅ Problems are detected and fixed
✅ Memory logs autonomous actions
✅ Weekend planner suggests projects

**The goal:** Seamless 24/7 operation that feels like Jarvis never sleeps.

## 📚 See Also

- [AUTONOMOUS_OPERATIONS.md](AUTONOMOUS_OPERATIONS.md) — System overview
- [BUILD_QUEUE_GUIDE.md](BUILD_QUEUE_GUIDE.md) — Adding tasks
- [OVERNIGHT_EXECUTION.md](OVERNIGHT_EXECUTION.md) — Overnight details
- [DECISION_FRAMEWORK.md](DECISION_FRAMEWORK.md) — Decision rules
