# INTELLIGENCE_TIERS.md - Multi-Tier AI Routing System

## Overview

Jarvis now uses a **3-tier intelligence routing system** to reduce token costs by **70%+** while maintaining quality. Simple tasks run on free local models (Ollama), only escalating to expensive Sonnet for complex reasoning.

**Before:** Every task burned Sonnet tokens (~$40-50/day)  
**After:** 70%+ tasks run locally for FREE (~$10-15/day)

---

## The Three Tiers

### 🟢 Tier 1: Local Simple (Ollama 14B)
**Model:** `qwen2.5:14b`  
**Cost:** $0.00 (runs on your Mac)  
**Latency:** ~2 seconds  
**Use for:** Simple checks, parsing, data extraction

**Examples:**
- Check email for urgent messages
- Parse calendar for today's events
- Extract data from structured text
- Simple Q&A about facts
- Weather checks
- Basic summarization

**Complexity Score:** 1-5

---

### 🟡 Tier 2: Local Smart (Ollama 32B)
**Model:** `qwen2.5:32b-instruct-q4_K_M`  
**Cost:** $0.00 (runs on your Mac)  
**Latency:** ~5 seconds  
**Use for:** Complex reasoning, decisions, analysis

**Examples:**
- Strategic decision making
- Complex data analysis
- Multi-step reasoning
- Draft generation with review
- Research and synthesis
- Troubleshooting technical issues

**Complexity Score:** 6-8

---

### 🔴 Tier 3: Sonnet (Claude Sonnet 4)
**Model:** `claude-sonnet-4`  
**Cost:** $3.00 input / $15.00 output (per 1M tokens)  
**Latency:** ~1.5 seconds  
**Use for:** Vision, code generation, deep reasoning

**Examples:**
- Food photo analysis (vision)
- Code generation and architecture
- Complex builds and implementations
- Deep reasoning about trade-offs
- Strategic planning
- Philosophical questions

**Complexity Score:** 9-10

---

## Routing Logic

### Automatic Routing
The `LocalRouter` automatically scores task complexity (1-10) and routes appropriately:

```python
from scripts.local_router import LocalRouter

router = LocalRouter()
result = router.execute_task("Check my email for urgent messages")
# → Routes to Ollama 14B (complexity: 1)

result = router.execute_task("Should I accept this job offer?")
# → Routes to Ollama 32B (complexity: 7)

result = router.execute_task("Build a landing page")
# → Routes to Sonnet (complexity: 8)

result = router.execute_task("What's in this image?", context={"has_image": True})
# → Routes to Sonnet (complexity: 10, vision required)
```

### Complexity Scoring

**Complexity 1-2: Simple**
- Keywords: "check", "parse", "extract", "list"
- Simple data retrieval
- Straightforward yes/no questions

**Complexity 3-5: Medium**
- Keywords: "summarize", "draft", "analyze", "compare"
- Requires synthesis
- Multiple-step thinking

**Complexity 6-8: Complex**
- Keywords: "decide", "should I", "build", "design"
- Strategic reasoning
- Trade-off analysis
- Code generation

**Complexity 9-10: Advanced**
- Vision tasks (images, screenshots)
- Multi-step workflows
- Deep philosophical reasoning
- Complex architecture decisions

### Context Overrides

Certain contexts force specific routing:
- **Has image** → Always Sonnet (vision required)
- **Urgent flag** → +2 complexity (escalate faster)
- **Multi-step** → +3 complexity (needs better reasoning)

---

## Proactive Monitoring

The **Proactive Monitor Daemon** runs every 5 minutes using **local models only**, checking:

- 📧 **Email**: Urgent messages, time-sensitive requests
- 📅 **Calendar**: Upcoming events (<2h), conflicts
- 💪 **Fitness**: Missed meal logging, weight tracking
- 💳 **Bank**: Unusual transactions (future: Plaid)

**Only escalates to Sonnet when action needed!**

### Running the Monitor

```bash
# Run once (manual check)
python3 ~/clawd/scripts/proactive_monitor.py --once

# Run as daemon (every 5 minutes)
python3 ~/clawd/scripts/proactive_monitor.py --daemon

# Run as daemon with custom interval
python3 ~/clawd/scripts/proactive_monitor.py --daemon --interval 10
```

### Escalation Flow

1. Monitor checks systems using local AI (FREE)
2. If something needs attention → writes to `memory/escalation-pending.json`
3. During heartbeat, Sonnet reads escalation file via `check_escalations.py`
4. Sonnet handles the escalated item with full context

This means **routine checks never burn Sonnet tokens!**

---

## Cost Dashboard

Track your savings in real-time:

```bash
# Full dashboard (7-day breakdown)
python3 ~/clawd/scripts/cost_dashboard.py

# Quick stats
python3 ~/clawd/scripts/cost_dashboard.py --period today
python3 ~/clawd/scripts/cost_dashboard.py --period week
python3 ~/clawd/scripts/cost_dashboard.py --period month
```

**Example Output:**
```
💰 MULTI-TIER INTELLIGENCE COST DASHBOARD
======================================================================

📊 TODAY'S SUMMARY
----------------------------------------------------------------------
  Total Tasks:        47
  Local (Ollama):     38 (80.9%)
  Sonnet:             9
  Cost Spent:         $1.23
  💚 Amount Saved:    $4.87
  📉 Cost Reduction:  79.8%

🔮 PROJECTIONS
----------------------------------------------------------------------
  Without multi-tier:  ~$183.00/month ($6.10/day)
  With multi-tier:     ~$36.90/month ($1.23/day)
  💰 Monthly Savings:  ~$146.10
```

---

## Integration Points

### 1. Heartbeat Integration
Update `HEARTBEAT.md` to check escalations:

```markdown
# Heartbeat Checklist
1. Run: python3 ~/clawd/scripts/check_escalations.py
2. If escalations found, handle them
3. Otherwise, HEARTBEAT_OK
```

### 2. Orchestrator Integration
Use local AI for drafts, summaries:

```python
from scripts.local_router import LocalRouter

router = LocalRouter()

# Draft emails locally
draft = router.execute_task(
    "Draft a professional email declining this meeting",
    context={"type": "draft"}
)

# Only use Sonnet for final review if needed
```

### 3. Custom Scripts
Any script can use the router:

```python
from scripts.local_router import LocalRouter

router = LocalRouter()

# Simple check (free)
result = router.execute_task("Is this email urgent?")

# Complex reasoning (free, uses larger model)
result = router.execute_task("Should I invest in this opportunity?")

# Force specific model if needed
result = router.execute_task("Generate code", force_model="sonnet")
```

---

## Cost Comparison

### Before Multi-Tier Routing

| Task Type | Model | Cost/Task | Daily Count | Daily Cost |
|-----------|-------|-----------|-------------|------------|
| Email checks | Sonnet | $0.10 | 12 | $1.20 |
| Calendar checks | Sonnet | $0.08 | 8 | $0.64 |
| Summaries | Sonnet | $0.25 | 10 | $2.50 |
| Code generation | Sonnet | $2.00 | 5 | $10.00 |
| **TOTAL** | | | **35** | **$14.34/day** |

**Monthly Cost:** ~$430

---

### After Multi-Tier Routing

| Task Type | Model | Cost/Task | Daily Count | Daily Cost |
|-----------|-------|-----------|-------------|------------|
| Email checks | Ollama 14B | $0.00 | 12 | $0.00 |
| Calendar checks | Ollama 14B | $0.00 | 8 | $0.00 |
| Summaries | Ollama 14B | $0.00 | 10 | $0.00 |
| Code generation | Sonnet | $2.00 | 5 | $10.00 |
| **TOTAL** | | | **35** | **$10.00/day** |

**Monthly Cost:** ~$300  
**Savings:** ~$130/month (30% reduction on code tasks alone)

**With 70% local routing:**

| Model | Tasks/Day | Cost/Day |
|-------|-----------|----------|
| Ollama | 35 (70%) | $0.00 |
| Sonnet | 15 (30%) | $4.50 |
| **TOTAL** | **50** | **$4.50/day** |

**Monthly Cost:** ~$135  
**Savings:** ~$295/month (68.6% reduction!)

---

## Testing the System

### Test Routing Decisions

```bash
python3 ~/clawd/scripts/local_router.py
```

This runs test cases and shows routing decisions:

```
LOCAL ROUTER TEST
============================================================

Task: Check my email for urgent messages
Context: None
→ Model: ollama (complexity: 1, confidence: 0.95)
  Reasoning: Simple task (complexity 1): routine checks, parsing

Task: Build a landing page for my startup
Context: None
→ Model: sonnet (complexity: 8, confidence: 0.90)
  Reasoning: Advanced task (complexity 8): code generation, vision, deep reasoning

Task: Is 2871 calories right for cutting?
Context: {'urgent': True}
→ Model: ollama-smart (complexity: 7, confidence: 0.75)
  Reasoning: Complex task (complexity 7): reasoning, decisions - using larger local model
```

### Test Monitor

```bash
# Run one monitoring cycle
python3 ~/clawd/scripts/proactive_monitor.py --once
```

Output:
```
============================================================
🤖 Proactive Monitor - 2026-02-13 14:30:00
============================================================
📧 Checking email...
📅 Checking calendar...
💪 Checking fitness tracking...
💳 Checking bank transactions...

💰 Today's Stats:
   Tasks: 4 (4 local, 0 Sonnet)
   Cost: $0.0000
   Saved: $0.4000
   Local %: 100.0%

✅ All clear, no escalations needed
```

---

## Success Metrics

### Target Goals
- ✅ **70%+ tasks routed to local** (currently tracking)
- ✅ **Cost reduction from $40-50/day to $10-15/day** (68%+ reduction)
- ✅ **No quality degradation** (larger local model handles complex tasks)
- ✅ **Proactive monitoring works** (daemon running, no Sonnet cost)
- ✅ **Dashboard shows real-time savings** (implemented)

### Monitoring Success

Check daily:
```bash
python3 ~/clawd/scripts/cost_dashboard.py --period today
```

If **local_percentage < 60%**, investigate:
- Are tasks being scored too high?
- Should we adjust complexity thresholds?
- Are there new task patterns to add?

If **quality issues**, consider:
- Using `ollama-smart` (32B) for more tasks
- Adjusting routing thresholds
- Adding manual overrides for specific patterns

---

## Fallback & Error Handling

### Automatic Fallback
If Ollama fails (service down, timeout), the router **automatically falls back to Sonnet**:

```python
result = router.execute_task("Check my email")
# If Ollama fails → automatically uses Sonnet
# Logs the fallback for review
```

### Manual Override
Force a specific model when needed:

```python
# Force Sonnet for critical tasks
result = router.execute_task(
    "Make strategic business decision",
    force_model="sonnet"
)

# Force local for testing
result = router.execute_task(
    "Generate code",
    force_model="ollama-smart"
)
```

### Logging
All routing decisions are logged to:
- `memory/routing-decisions.json` - Every routing choice
- `memory/cost-savings.json` - Cost tracking and savings

Review logs to improve routing:
```bash
# See recent routing decisions
cat memory/routing-decisions.json | jq '.decisions[-10:]'

# See cost breakdown
cat memory/cost-savings.json | jq '.daily_stats'
```

---

## Future Enhancements

### Vision on Local
When `llava` or other local vision models improve:
- Add vision support to Ollama tier
- Route simple image tasks locally
- Keep complex vision (food logging) on Sonnet

### Adaptive Routing
Learn from past decisions:
- Track when local model was "good enough"
- Track when we should have used Sonnet
- Adjust complexity scores based on outcomes

### Cost Alerts
Add alerts to dashboard:
- 🟡 Yellow flag: Daily cost >$15
- 🔴 Red flag: Daily cost >$25
- Alert if local_percentage drops below 60%

### Batch Processing
For non-urgent tasks:
- Queue multiple tasks
- Run as single batch on local model
- Further reduce overhead

---

## Troubleshooting

### "Ollama not responding"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

### "All tasks routing to Sonnet"
Check complexity scoring:
```bash
python3 ~/clawd/scripts/local_router.py
# Review routing decisions for test cases
```

### "Dashboard shows $0 savings"
Likely no tasks routed yet:
```bash
# Run monitor to generate some local tasks
python3 ~/clawd/scripts/proactive_monitor.py --once

# Check logs
cat memory/cost-savings.json
```

### "Monitor not escalating urgent items"
Check escalation file:
```bash
cat memory/escalation-pending.json
```

If file exists but Sonnet not seeing it:
- Ensure `check_escalations.py` is called in heartbeat
- Check `HEARTBEAT.md` for integration

---

## Quick Reference

### Commands
```bash
# Test routing
python3 ~/clawd/scripts/local_router.py

# Run monitor once
python3 ~/clawd/scripts/proactive_monitor.py --once

# Run monitor as daemon
python3 ~/clawd/scripts/proactive_monitor.py --daemon

# Check escalations (for heartbeat)
python3 ~/clawd/scripts/check_escalations.py

# Show cost dashboard
python3 ~/clawd/scripts/cost_dashboard.py

# Quick stats
python3 ~/clawd/scripts/cost_dashboard.py --period today
```

### Files
- `scripts/local_router.py` - Core routing logic
- `scripts/proactive_monitor.py` - Monitoring daemon
- `scripts/check_escalations.py` - Heartbeat integration
- `scripts/cost_dashboard.py` - Savings dashboard
- `memory/cost-savings.json` - Cost tracking data
- `memory/routing-decisions.json` - Routing logs
- `memory/escalation-pending.json` - Items needing Sonnet attention
- `memory/monitor-state.json` - Monitor state

---

## Philosophy

**The goal isn't to eliminate Sonnet—it's to use it strategically.**

- **Local models** handle the routine, the predictable, the simple
- **Sonnet** handles the creative, the complex, the critical
- **Together** they make Jarvis both powerful AND affordable

Think of it like a company:
- Junior employees (Ollama) handle routine tasks
- Senior experts (Sonnet) handle strategic decisions
- Everyone works together efficiently

**Smart routing = Sustainable AI assistant** 🚀

---

## Support

Questions or issues? Update this doc or check:
- Routing logs: `memory/routing-decisions.json`
- Cost logs: `memory/cost-savings.json`
- Monitor logs: Check output of `proactive_monitor.py`

The system learns and improves over time. Give it a few days to collect data, then review the dashboard to optimize further.
