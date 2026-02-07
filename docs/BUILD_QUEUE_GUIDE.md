# Build Queue Guide

How to add, manage, and prioritize builds in the autonomous queue system.

## 🎯 Quick Start

Add a task:
```bash
cd autonomous
python3 autonomous_queue.py add \
  "Task title" \
  "Detailed description of what to build" \
  2.5 \
  "Category" \
  PRIORITY
```

**Priority levels:** CRITICAL, HIGH, MEDIUM, LOW, BACKLOG

**Categories:**
- Performance optimization
- New features
- Bug fixes
- Research/analysis
- Documentation
- Infrastructure

## 📝 Adding Tasks

### Performance Optimization (Auto-Approve)
```bash
python3 autonomous_queue.py add \
  "Optimize nutrition logging" \
  "Profile nutrition.py, cache frequent queries, optimize database access" \
  1.5 \
  "Performance optimization" \
  HIGH
```

**Auto-approved** — Will run automatically during overnight/work hours.

### New Feature (Requires Approval)
```bash
python3 autonomous_queue.py add \
  "Add meal suggestions" \
  "Build AI-powered meal suggestion system based on nutrition goals and preferences" \
  4.0 \
  "New features" \
  MEDIUM
```

**Needs approval** — Will be queued but won't auto-spawn until approved.

### Bug Fix (Auto-Approve)
```bash
python3 autonomous_queue.py add \
  "Fix workout logging crash" \
  "Handle edge case when workout has no exercises" \
  0.5 \
  "Bug fixes" \
  CRITICAL
```

**Auto-approved** — Critical/High priority bugs run immediately.

### Research/Analysis
```bash
python3 autonomous_queue.py add \
  "Research revenue opportunities" \
  "Analyze market for fitness SaaS, pricing models, competition analysis" \
  6.0 \
  "Research/analysis" \
  HIGH
```

**Context-aware** — Best during work hours (9am-5pm) when deep thinking appropriate.

### Documentation
```bash
python3 autonomous_queue.py add \
  "Document API endpoints" \
  "Write comprehensive API documentation for all fitness tracker endpoints" \
  2.0 \
  "Documentation" \
  MEDIUM
```

**Auto-approved** — Documentation improvements always safe.

### Infrastructure
```bash
python3 autonomous_queue.py add \
  "Set up CI/CD pipeline" \
  "Build automated testing and deployment pipeline for fitness tracker" \
  8.0 \
  "Infrastructure" \
  HIGH
```

**Weekend candidate** — Long builds best for weekends.

## ⏰ Time Windows

Tasks auto-schedule based on estimated hours:

| Estimated Hours | Time Window | When It Runs |
|----------------|-------------|--------------|
| 1-2 hours | Quick Win | Weeknights (7pm-11pm) |
| 4-6 hours | Overnight | Sleep (11pm-7am) |
| 8 hours | Work Hours | Office time (9am-5pm) |
| 8-12 hours | Weekend | Saturday/Sunday |

The scheduler automatically matches tasks to appropriate windows.

## 🎯 Priority Scoring

Tasks ranked by: **Priority × (1 / Effort)**

**Why?** This favors high-impact, low-effort work.

Examples:
- HIGH priority, 1 hour → Score: 4.0
- HIGH priority, 4 hours → Score: 1.0
- MEDIUM priority, 0.5 hours → Score: 6.0 (quick win!)

Quick wins often run first, even at lower priority.

## 🔗 Dependencies

Tasks can depend on others:

```bash
# First task
python3 autonomous_queue.py add \
  "Build user authentication" \
  "..." \
  3.0 \
  "New features" \
  HIGH

# Dependent task (won't run until first completes)
python3 autonomous_queue.py add \
  "Add user preferences" \
  "..." \
  2.0 \
  "New features" \
  MEDIUM \
  --depends task_123
```

Dependency tracking ensures correct build order.

## 📊 Queue Management

### View Queue
```bash
python3 build_scheduler.py list
```

Shows all tasks with status:
- ⏳ Queued
- ✅ Completed
- ❌ Failed
- 🔨 In Progress

### Check Stats
```bash
python3 build_scheduler.py stats
```

Outputs:
```
Total tasks: 15
Queued: 8
Completed: 6
Failed: 1
Completion rate: 85.7%
```

### Next Tasks
```bash
python3 build_scheduler.py next
```

Shows next 3 tasks for current time window.

### Active Builds
```bash
python3 autonomous_queue.py progress
```

Shows currently running builds with progress.

## 🤖 Auto-Approve Categories

These categories **auto-run** without approval:
- ✅ Performance optimization
- ✅ Bug fixes
- ✅ Documentation
- ✅ Infrastructure (conservative changes)

These categories **need approval:**
- 🔒 New features
- 🔒 External actions
- 🔒 Config changes
- 🔒 API integrations

## 🎯 Best Practices

### 1. Break Down Big Tasks
Instead of:
```
"Build entire fitness dashboard" (20 hours)
```

Do:
```
"Build workout history chart" (3 hours)
"Build nutrition trends chart" (3 hours)
"Build goals tracker" (2 hours)
```

**Why?** Smaller tasks:
- Fit in time windows better
- Show incremental progress
- Easier to debug

### 2. Use Descriptive Titles
Bad: "Fix bug"
Good: "Fix workout logging crash on empty exercises"

**Why?** You'll thank yourself later.

### 3. Set Realistic Hours
Under-promise, over-deliver.

- Add 50% buffer for unknowns
- 2 hours estimated? Say 3 hours
- Better to finish early than run over

### 4. Prioritize Ruthlessly
- CRITICAL: System broken, blocking work
- HIGH: Important, high impact
- MEDIUM: Useful, moderate impact
- LOW: Nice to have
- BACKLOG: Someday/maybe

**Don't make everything HIGH.** Priority inflation kills the system.

### 5. Add Context in Description
Include:
- What to build
- Why it matters
- How to test
- Where to document

Example:
```
"Optimize database queries in nutrition.py

Profile with cProfile, identify slow queries.
Focus on daily_stats() and weekly_summary().
Target: 3x speedup.

Test: Run benchmarks before/after.
Document: Update PERFORMANCE.md with results."
```

## 🚀 Workflow Examples

### Morning Review
```bash
# Check overnight builds
python3 autonomous_queue.py report

# See what's queued
python3 build_scheduler.py list

# Add quick win for tonight
python3 autonomous_queue.py add \
  "Add input validation" \
  "..." \
  1.0 \
  "Bug fixes" \
  HIGH
```

### Evening Session
```bash
# What's next for tonight?
python3 build_scheduler.py next

# Manually trigger a build if desired
# (or let overnight runner handle it)
```

### Friday Planning
```bash
# Weekend options
python3 weekend_planner.py suggest

# Add weekend project
python3 autonomous_queue.py add \
  "Build social sharing feature" \
  "Complete social media integration with image generation" \
  10.0 \
  "New features" \
  HIGH
```

## 📈 Monitoring

### Daily
- Check morning report
- Review overnight builds
- Adjust priorities if needed

### Weekly
- Review completion rate
- Archive old tasks
- Plan next week's builds

### Monthly
- Analyze patterns
- Optimize scheduling
- Review self-improvements

## 🔧 Troubleshooting

### Task not running?
Check:
1. Status queued? (not completed/failed)
2. Dependencies met?
3. Category auto-approved?
4. Current time window matches?

### Build taking too long?
- Check progress logs
- Might need to break into smaller tasks
- Adjust time estimates for future

### Too many queued tasks?
- Prioritize ruthlessly
- Archive low-priority backlog
- Focus on high-impact work

## 🎉 Success Story

**Before autonomous queue:**
- Ross manually tracks what to build
- Work only happens when Ross available
- Ideas get forgotten
- Progress is sporadic

**After autonomous queue:**
- Ideas captured immediately
- Builds run 24/7
- Progress is continuous
- Ross wakes up to completed work

**The goal:** When Ross says "I wish we had X," reply "Already building it, ships tomorrow."

## 📚 See Also

- [AUTONOMOUS_OPERATIONS.md](AUTONOMOUS_OPERATIONS.md) — Full system overview
- [OVERNIGHT_EXECUTION.md](OVERNIGHT_EXECUTION.md) — Overnight details
- [DECISION_FRAMEWORK.md](DECISION_FRAMEWORK.md) — What auto-approves
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) — Connect to existing systems
