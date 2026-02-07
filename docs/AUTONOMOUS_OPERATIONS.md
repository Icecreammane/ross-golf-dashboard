# Autonomous Operations System

Complete 24/7 productivity infrastructure that enables Jarvis to work independently while Ross is unavailable.

## 🎯 Mission

**Transform 4 hours/day into 24 hours/day of productivity.**

Ross has limited availability (4 hrs weeknights, some weekends). This system enables continuous progress during:
- Sleep (11pm-7am) — 8 hours
- Work (9am-5pm) — 8 hours  
- Gym (6-7:30am, 5-6:30pm) — 2-3 hours

**Total autonomous hours: 18-19 hours per day**

## 📦 Core Components

### 1. Build Scheduler (`build_scheduler.py`)
Time-based task categorization and queue management.

**Time Windows:**
- **Quick Win (1-2 hrs):** Weeknight sessions (7pm-11pm)
- **Overnight (4-6 hrs):** Sleep window (11pm-7am)
- **Work Hours (8 hrs):** Office time (9am-5pm)
- **Weekend (8-12 hrs):** Saturday/Sunday

**Features:**
- Priority scoring (impact × 1/effort)
- Dependency tracking
- Auto-scheduling by time window
- Queue statistics

**CLI:**
```bash
cd autonomous
python3 build_scheduler.py list      # Show queue
python3 build_scheduler.py schedule  # Show scheduled tasks
python3 build_scheduler.py stats     # Queue statistics
python3 build_scheduler.py next      # Next 3 tasks
```

### 2. Autonomous Queue (`autonomous_queue.py`)
Orchestrates build execution, spawns sub-agents, tracks progress.

**Functions:**
- `add_to_queue()` — Add tasks with priority and category
- `schedule_builds()` — Auto-schedule for current window
- `spawn_builder()` — Launch sub-agent for task
- `track_progress()` — Monitor active builds
- `generate_morning_report()` — Overnight completion report

**Categories:**
- Performance optimization (auto-approve)
- New features (needs approval)
- Bug fixes (auto-approve)
- Research/analysis
- Documentation (auto-approve)
- Infrastructure

**CLI:**
```bash
python3 autonomous_queue.py add "Task" "Description" 2.5 "Performance optimization" HIGH
python3 autonomous_queue.py progress    # Active builds
python3 autonomous_queue.py report      # Morning report
python3 autonomous_queue.py schedule    # Auto-schedule
```

### 3. Context Scheduler (`context_scheduler.py`)
Selects work based on Ross's activity/location.

**Contexts:**
- **GYM:** Fitness tools, workout analysis
- **WORK:** Productivity tools, revenue research, testing
- **SLEEPING:** Long builds, data processing, optimization (MAXIMUM PRODUCTIVITY)
- **AVAILABLE:** Quick iteration, stay responsive
- **UNKNOWN:** Conservative, low-risk only

**CLI:**
```bash
python3 context_scheduler.py detect     # Detect current context
python3 context_scheduler.py summary    # Full context summary
python3 context_scheduler.py upcoming   # Next 12 hours
python3 context_scheduler.py set sleeping  # Manual override
```

### 4. Problem Predictor (`problem_predictor.py`)
Monitors system health, predicts problems, auto-fixes when safe.

**Monitors:**
- Disk space (trend analysis)
- Log file growth
- Database sizes
- Memory usage

**Auto-Fixes:**
- Clean old logs (>30 days)
- Rotate large log files (>10MB)
- Optimize databases

**Escalates:**
- Critical issues
- Anything requiring human judgment

**CLI:**
```bash
python3 problem_predictor.py scan      # Scan for problems
python3 problem_predictor.py fix       # Auto-fix problems
python3 problem_predictor.py metrics   # System metrics
python3 problem_predictor.py list      # Active problems
```

### 5. Pattern Learner (`pattern_learner.py`)
Learns Ross's routines and pre-builds what he needs.

**Learns:**
- Day-of-week patterns (e.g., Thursday → NBA rankings)
- Time-of-day patterns (e.g., 6pm → workout log)
- Recurring requests

**Confidence Levels:**
- 0-0.5: Low (2-3 occurrences)
- 0.5-0.7: Medium (3-5 occurrences)
- 0.7+: High (5+ consistent occurrences)

**Auto-Execute:**
- Patterns with 0.8+ confidence can auto-execute
- Pre-builds 2-4 hours before predicted need

**CLI:**
```bash
python3 pattern_learner.py log "nba_rankings" '{"source": "manual"}'
python3 pattern_learner.py predict    # Current predictions
python3 pattern_learner.py suggest    # Pre-build suggestions
python3 pattern_learner.py list       # All patterns
python3 pattern_learner.py enable pattern_id  # Enable auto-execute
```

### 6. Self-Improver (`self_improver.py`)
Identifies weaknesses and builds fixes.

**Monitors:**
- Response latency (>5s = slow)
- API failures (3+ = reliability issue)
- User corrections (knowledge gaps)
- Repeated questions (missing automation)

**Auto-Improves:**
- Cache slow operations
- Add error handling
- Update documentation
- Build automation (with approval)

**CLI:**
```bash
python3 self_improver.py suggest         # Improvement suggestions
python3 self_improver.py stats           # Performance stats
python3 self_improver.py log-time "op" 2500    # Log operation time
python3 self_improver.py log-failure "api" "error"  # Log failure
```

### 7. Overnight Runner (`overnight_runner.py`)
Orchestrates 11pm-7am execution cycle.

**Schedule:**
- 11:00pm — Scan for problems
- 11:05pm — Auto-fix problems
- 11:05pm — Check patterns and pre-build
- 11:10pm — Schedule and spawn builds (max 3 concurrent)
- Throughout night — Monitor progress
- 6:30am — Generate completion report
- 7:00am — Prepare morning brief

**Safety:**
- Max 3 concurrent sub-agents
- Cancel if system resources >80%
- Full logging to `autonomous/logs/overnight_execution.log`

**CLI:**
```bash
python3 overnight_runner.py start    # Start session (or run from cron)
python3 overnight_runner.py report   # Completion report
python3 overnight_runner.py brief    # Morning brief text
python3 overnight_runner.py is-overnight  # Check if overnight hours
```

### 8. Weekend Planner (`weekend_planner.py`)
Plans ambitious 8-12 hour weekend projects.

**Friday Evening:**
- Review queue for weekend-sized projects
- Present top 5 options with breakdowns
- Let Ross choose

**Saturday:**
- Start selected project
- Break into phases
- Build systematically

**Sunday Night:**
- Generate completion summary
- Ship complete system

**CLI:**
```bash
python3 weekend_planner.py suggest           # Friday suggestions
python3 weekend_planner.py select task_123   # Select project
python3 weekend_planner.py start             # Start execution
python3 weekend_planner.py progress          # Current progress
python3 weekend_planner.py complete "phase"  # Mark phase done
python3 weekend_planner.py summary           # Sunday summary
```

## 🔄 Daily Workflow

### Weekday Morning (7:00am)
1. Generate morning brief with overnight builds
2. Show what shipped, what's in progress
3. Report auto-fixed problems
4. Show pattern-based predictions

### Weekday Evening (7:00pm)
1. Quick check-in: "Ready for tonight's build session?"
2. Suggest 1-2 hour quick wins
3. Be responsive for collaboration

### Weekday Overnight (11:00pm)
1. Start overnight runner
2. Spawn 3 builds (4-6 hours each)
3. Monitor throughout night
4. Generate completion report

### Friday Evening (6:00pm)
1. Present weekend project options
2. Let Ross choose ambitious build

### Weekend
1. Execute weekend project in phases
2. Sunday night: ship complete system

## 📊 Data Files

All state stored in `autonomous/data/`:
- `build_queue.json` — Task queue
- `queue_state.json` — Active sub-agents
- `context_state.json` — Current context
- `problems.json` — Detected problems
- `metrics_history.json` — System metrics over time
- `patterns.json` — Learned patterns
- `improvements.json` — Self-improvements
- `weekend_plan.json` — Current weekend project

## 📝 Logs

All logs in `autonomous/logs/`:
- `overnight_execution.log` — Overnight sessions
- `subagent_spawns.jsonl` — Sub-agent launches
- `queue_actions.log` — Queue management
- `auto_fixes.log` — Auto-fix actions
- `improvements.log` — Self-improvements
- `overnight_report_YYYY-MM-DD.json` — Daily reports

## 🔐 Safety Features

1. **Resource Limits:**
   - Max 3 concurrent sub-agents
   - Cancel if disk >80%, memory high
   
2. **Auto-Approve Categories:**
   - Performance optimization
   - Bug fixes
   - Documentation
   - Infrastructure (conservative)

3. **Require Approval:**
   - New features
   - External actions
   - Config changes
   - User-facing changes

4. **Full Logging:**
   - Every action logged
   - Rollback capability
   - Audit trail

## 🎯 Success Metrics

**Daily:**
- Builds completed overnight: Target 2-3
- Hours shipped: Target 6-8 hours
- Problems auto-fixed: Target 1-2
- Patterns learned: 1+ per week

**Weekly:**
- Total autonomous hours: 18-19 hrs/day × 7 = 126-133 hours
- Ross's active hours: 4 hrs/day × 5 + 8 hrs/day × 2 = 36 hours
- **Productivity multiplier: 3.5x - 4x**

**Monthly:**
- Weekend projects completed: 2-4
- Self-improvements: 5-10
- Pattern confidence: 3-5 high-confidence patterns

## 🚀 Getting Started

1. **Review the queue:**
   ```bash
   cd autonomous
   python3 build_scheduler.py list
   ```

2. **Add your first task:**
   ```bash
   python3 autonomous_queue.py add \
     "Optimize database queries" \
     "Profile and optimize slow queries in fitness tracker" \
     2.0 \
     "Performance optimization" \
     HIGH
   ```

3. **Test overnight runner:**
   ```bash
   python3 overnight_runner.py start
   ```

4. **Check morning brief:**
   ```bash
   python3 overnight_runner.py brief
   ```

5. **Review weekend options:**
   ```bash
   python3 weekend_planner.py suggest
   ```

## 📚 See Also

- [BUILD_QUEUE_GUIDE.md](BUILD_QUEUE_GUIDE.md) — How to add and manage builds
- [OVERNIGHT_EXECUTION.md](OVERNIGHT_EXECUTION.md) — Overnight system details
- [DECISION_FRAMEWORK.md](DECISION_FRAMEWORK.md) — Autonomous decision rules
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) — Integration with heartbeat/cron/memory

## 🎉 The Vision

**Tomorrow morning, Ross wakes up and sees:**

> "🚀 What Shipped Overnight:
> - Autonomous Build Queue: Operational ✅
> - Database Optimization: 3x faster queries ✅
> - Pattern Learner: Detected your Thursday NBA routine ✅
> 
> Ready for more? Let's keep building."

**That's the goal. 24/7 productivity unlocked.**
