# AI Optimization - Integration TODO

## ✅ Quick Wins (Done Now)

### 1. Helper Functions Created
**File:** `scripts/jarvis_helpers.py`
- `smart_route(task)` - Routes task to best model
- `log_cost(model, workflow, tokens_in, tokens_out)` - Logs costs

**Usage:**
```python
from jarvis_helpers import smart_route, log_cost

# Before AI call
model = smart_route("Generate daily tasks")

# After AI call
log_cost(model, "task-generation", 1000, 500)
```

### 2. Self-Optimizer Scheduled
**Cron:** Runs every day at 2:00 AM
- Reviews config files
- Suggests improvements
- Auto-applies safe changes
- Logs to `logs/self_optimization.log`

### 3. Dashboards Ready
- Cost dashboard: `dashboard/costs.html`
- Kanban board: `dashboard/kanban.html`

---

## ⏳ Heavy Lifting (Do Together Later)

### 1. Integrate Router into Sub-Agent Spawning
**File to modify:** Core Clawdbot session spawning logic

**Change:**
```python
# Before spawning sub-agent
from jarvis_helpers import smart_route
model = smart_route(task_description)

sessions_spawn(
    task=task,
    model=model  # Use routed model instead of default
)
```

**Impact:** Sub-agents use appropriate tier (big savings)

### 2. Wrap All AI API Calls with Cost Logging
**Files to modify:**
- `scripts/daily_task_generator.py`
- `scripts/instant_recall.py`
- `scripts/auto_memory.py`
- Any script that calls OpenAI/Anthropic

**Pattern:**
```python
response = client.chat.completions.create(...)

# Add this after every call:
from jarvis_helpers import log_cost
log_cost(
    model=response.model,
    workflow="task-generation",
    input_tokens=response.usage.prompt_tokens,
    output_tokens=response.usage.completion_tokens
)
```

**Impact:** Full cost visibility

### 3. Update Task Generator to Use Router
**File:** `scripts/daily_task_generator.py`

**Change:**
```python
from jarvis_helpers import smart_route

# Line 41: Instead of hardcoded model
model = smart_route(f"Generate 4-5 daily tasks from goals")

response = client.chat.completions.create(
    model=model,  # Use routed model
    messages=[...]
)
```

**Impact:** Free task generation (would route to local-smart)

### 4. Add Weekly Cost Reports
**New cron job:**
```bash
0 18 * * 0 python3 ~/clawd/scripts/cost_tracker_advanced.py report 7 | mail -s "Weekly AI Cost Report" ross@example.com
```

Or send via Telegram notification

**Impact:** Automatic spending awareness

### 5. Router Feedback Loop
**Track when routing fails:**
```python
# If task routed to local model but failed
# Auto-retry with next tier up
# Log the failure for router improvement
```

**Impact:** Router gets smarter over time

---

## 📊 Expected Timeline

**Now (Immediate):**
- ✅ Helper functions available
- ✅ Self-optimizer scheduled
- ✅ Dashboards ready

**Weekend (Light integration):**
- Update 2-3 high-use scripts with cost logging
- Test router with sub-agents manually

**Next Week (Full integration):**
- Systematic cost logging across all AI calls
- Router integrated into spawning logic
- Weekly reports automated

**Within Month:**
- 70-80% cost savings realized
- Full visibility into spending
- Self-optimization improvements visible

---

## 🎯 Priority Order

1. **Cost logging in task generator** (highest ROI)
2. **Router for sub-agent spawns** (big savings)
3. **Weekly cost reports** (awareness)
4. **Systematic logging everywhere** (completeness)
5. **Router feedback loop** (long-term improvement)

---

## 📝 Notes for Ross

**What Jarvis can do alone:**
- Use helper functions in new scripts
- Manually route tasks before spawning
- Generate reports from dashboards

**What needs Ross:**
- Core system integration (spawning logic)
- Systematic cost logging (wrap all AI calls)
- Cron job setup for reports

**Test anytime:**
```bash
# Check if routing works
python3 ~/clawd/scripts/jarvis_helpers.py

# Generate cost dashboard
python3 ~/clawd/scripts/cost_tracker_advanced.py dashboard
open ~/clawd/dashboard/costs.html
```
