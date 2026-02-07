# Autonomous Operations System

**Transform 4 hours/day into 24 hours/day of productivity.**

This system enables Jarvis to work independently while Ross sleeps, works, hits the gym, or is otherwise unavailable.

## 🚀 Quick Start

```bash
# View the build queue
python3 build_scheduler.py list

# Add your first task
python3 autonomous_queue.py add \
  "Optimize database" \
  "Profile and optimize slow queries" \
  2.0 \
  "Performance optimization" \
  HIGH

# Check what's next
python3 build_scheduler.py next

# Start overnight session (or let cron do it at 11pm)
python3 overnight_runner.py start

# View morning report
python3 overnight_runner.py brief
```

## 📚 Documentation

Complete documentation in `docs/`:

- **[AUTONOMOUS_OPERATIONS.md](../docs/AUTONOMOUS_OPERATIONS.md)** — Complete system overview
- **[BUILD_QUEUE_GUIDE.md](../docs/BUILD_QUEUE_GUIDE.md)** — How to add and manage builds
- **[OVERNIGHT_EXECUTION.md](../docs/OVERNIGHT_EXECUTION.md)** — What runs when Ross sleeps
- **[DECISION_FRAMEWORK.md](../docs/DECISION_FRAMEWORK.md)** — What Jarvis can decide alone
- **[INTEGRATION_GUIDE.md](../docs/INTEGRATION_GUIDE.md)** — Connect to heartbeat/cron/memory

## 🎯 Core Components

| Script | Purpose | CLI |
|--------|---------|-----|
| `build_scheduler.py` | Time-based task scheduling | `list`, `schedule`, `stats`, `next` |
| `autonomous_queue.py` | Queue management & orchestration | `add`, `progress`, `report`, `schedule` |
| `context_scheduler.py` | Context-aware work selection | `detect`, `summary`, `upcoming` |
| `problem_predictor.py` | Proactive problem detection | `scan`, `fix`, `metrics`, `list` |
| `pattern_learner.py` | Learn routines & pre-build | `predict`, `suggest`, `list`, `stats` |
| `self_improver.py` | Identify & fix weaknesses | `suggest`, `stats` |
| `overnight_runner.py` | Overnight execution (11pm-7am) | `start`, `report`, `brief` |
| `weekend_planner.py` | Weekend project planning | `suggest`, `start`, `progress`, `summary` |

## ⏰ Time Windows

- **Quick Win (1-2 hrs):** Weeknight sessions (7pm-11pm)
- **Overnight (4-6 hrs):** Sleep window (11pm-7am) — **MAXIMUM PRODUCTIVITY**
- **Work Hours (8 hrs):** Office time (9am-5pm)
- **Weekend (8-12 hrs):** Saturday/Sunday

## 🔐 Auto-Approve Categories

These run without approval:
- ✅ Performance optimization
- ✅ Bug fixes
- ✅ Documentation
- ✅ Infrastructure (conservative)

These need approval:
- 🔒 New features
- 🔒 External actions
- 🔒 Config changes

## 📊 Directory Structure

```
autonomous/
├── README.md                      (this file)
├── build_scheduler.py             (time-based scheduling)
├── autonomous_queue.py            (queue orchestration)
├── context_scheduler.py           (context-aware work)
├── problem_predictor.py           (proactive monitoring)
├── pattern_learner.py             (routine learning)
├── self_improver.py               (weakness detection)
├── overnight_runner.py            (overnight execution)
├── weekend_planner.py             (weekend planning)
├── data/                          (state files)
│   ├── build_queue.json           (task queue)
│   ├── queue_state.json           (active agents)
│   ├── context_state.json         (current context)
│   ├── problems.json              (detected problems)
│   ├── patterns.json              (learned patterns)
│   ├── improvements.json          (self-improvements)
│   └── weekend_plan.json          (weekend project)
└── logs/                          (execution logs)
    ├── overnight_execution.log    (overnight sessions)
    ├── subagent_spawns.jsonl      (sub-agent launches)
    ├── queue_actions.log          (queue management)
    ├── auto_fixes.log             (auto-fixes)
    └── improvements.log           (self-improvements)
```

## 🎯 Daily Workflow

**7:00am** — Morning brief with overnight builds
```bash
python3 overnight_runner.py brief
```

**7:00pm** — Evening check-in, suggest quick wins
```bash
python3 build_scheduler.py next
```

**11:00pm** — Overnight session starts (cron)
```bash
python3 overnight_runner.py start
```

**Friday 6pm** — Weekend project options
```bash
python3 weekend_planner.py suggest
```

## 🔧 Setup

### 1. Install (Already Done)
Scripts are in place, ready to use.

### 2. Add Cron Jobs
```bash
crontab -e
```

Add:
```cron
# Overnight runner
0 23 * * * cd /Users/clawdbot/clawd && python3 autonomous/overnight_runner.py start

# Weekend planner
0 18 * * 5 cd /Users/clawdbot/clawd && python3 autonomous/weekend_planner.py suggest
```

### 3. Test
```bash
# Add test task
python3 autonomous_queue.py add "Test task" "Testing system" 1.0 "Documentation" MEDIUM

# Check queue
python3 build_scheduler.py list

# View stats
python3 build_scheduler.py stats
```

### 4. First Overnight Run
Queue some tasks before 11pm, let the overnight runner handle them.

## 📈 Success Metrics

**Daily Goals:**
- 2-3 builds completed overnight
- 6-8 hours of work shipped
- 1-2 problems auto-fixed

**Weekly Goals:**
- 14-21 builds completed
- 42-56 hours shipped
- 1-2 patterns learned

**Productivity Multiplier:**
- Ross: 4 hrs/day × 7 days = 28 hrs/week
- Jarvis autonomous: 18 hrs/day × 7 days = 126 hrs/week
- **Multiplier: 4.5x**

## 🎉 The Vision

**Tomorrow morning, Ross wakes up:**

> "🌅 Good morning! Here's what shipped overnight:
> 
> ✅ Optimized database queries (5x faster)
> ✅ Built analytics dashboard
> ✅ Documented REST API
> 
> Also auto-fixed 2 system issues.
> 
> Ready for more?"

**That's the goal. Every morning.**

## 🐛 Troubleshooting

**Queue not showing tasks?**
```bash
python3 build_scheduler.py list
# Should show all tasks with status
```

**Overnight runner not starting?**
```bash
# Check if it's overnight hours
python3 overnight_runner.py is-overnight

# Check logs
tail -f logs/overnight_execution.log
```

**Need help?**
Read the docs in `docs/` — everything is documented there.

## 🚀 Next Steps

1. **Add tasks** to the queue
2. **Run overnight** session tonight
3. **Review brief** tomorrow morning
4. **Iterate** and improve

**Let's build 24/7.**
