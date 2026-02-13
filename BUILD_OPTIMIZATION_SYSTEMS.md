# AI Optimization Systems - SHIPPED ✅

**Inspired by:** Advanced AI automation video (Q7r--i9lLck)

## What Got Built

### 1. Advanced Cost Tracker 💰
**Script:** `scripts/cost_tracker_advanced.py`

**Features:**
- Tracks every API call (model, tokens, cost)
- Per-workflow cost breakdown
- Per-model spending analysis
- Daily/weekly/monthly reports
- Visual dashboard with charts
- High spending alerts

**Pricing database:**
- Local models: $0 (Arnold, Batman, LD)
- Haiku: $0.25/M input, $1.25/M output
- Sonnet: $3/M input, $15/M output
- Opus: $15/M input, $75/M output
- GPT-4o: $2.50/M input, $10/M output

**Usage:**
```bash
# Log an API call
python3 cost_tracker_advanced.py log sonnet "task-generation" 1000 500

# Weekly report
python3 cost_tracker_advanced.py report 7

# Generate dashboard
python3 cost_tracker_advanced.py dashboard
```

**Dashboard:** `~/clawd/dashboard/costs.html`

**Impact:** Full visibility into AI spending by workflow and model

---

### 2. Tiered Model Router 🎯
**Script:** `scripts/tiered_model_router.py`

**How it works:**
Analyzes task complexity and routes to cheapest capable model:

**Tier 1 - TRIVIAL** ($0)
- Local models (Batman/LD/Arnold)
- Tasks: list files, simple parsing, quick checks
- Cost: FREE

**Tier 2 - SIMPLE** ($0.25/M)
- Haiku or local-smart
- Tasks: basic summarization, classification
- Cost: ~$0.001 per task

**Tier 3 - MEDIUM** ($3/M)
- Sonnet or GPT-4o
- Tasks: complex analysis, code generation
- Cost: ~$0.01 per task

**Tier 4 - COMPLEX** ($3-5/M)
- Sonnet or GPT-5
- Tasks: strategic planning, architecture
- Cost: ~$0.02 per task

**Tier 5 - CRITICAL** ($15/M)
- Opus or GPT-5
- Tasks: production decisions, customer-facing
- Cost: ~$0.06 per task

**Automatic classification:**
```python
# Example routing
route_task("Summarize this article")  
→ local-smart (FREE)

route_task("Generate product launch strategy")  
→ claude-sonnet-4-5 ($0.01)

route_task("Critical production bug review")  
→ claude-opus-4-5 ($0.06)
```

**Estimated savings:** 70-80% on API costs by routing appropriately

---

### 3. Self-Optimization System 🔄
**Script:** `scripts/self_optimizer.py`

**What it does:**
- Reviews its own configuration files nightly
- Uses GPT-4o to analyze AGENTS.md, SOUL.md, etc.
- Compares against AI best practices
- Suggests improvements
- Auto-applies safe changes

**Files reviewed:**
- AGENTS.md (operating procedures)
- SOUL.md (personality/communication)
- TOOLS.md (tool usage patterns)
- HEARTBEAT.md (proactive behaviors)
- DECISION_PROTOCOL.md (decision making)
- daily_task_generator.py (task quality)

**Analysis output:**
- Score: 0-100 (quality rating)
- Issues: Problems found (high/medium/low severity)
- Improvements: Suggested changes with rationale
- Auto-apply: Safe changes that can be applied immediately

**Usage:**
```bash
# Run optimization
python3 self_optimizer.py

# View report
python3 self_optimizer.py report
```

**Scheduled:** Runs nightly at 2:00 AM (cron job pending)

**Impact:** System continuously improves itself based on latest best practices

---

## Integration Plan

### Cost Tracker Integration
**Hook into all AI calls:**
```python
# After every AI API call
from cost_tracker_advanced import log_api_call

response = client.chat.completions.create(...)
log_api_call(
    model='claude-sonnet-4-5',
    workflow='task-generation',
    input_tokens=response.usage.prompt_tokens,
    output_tokens=response.usage.completion_tokens
)
```

**Weekly cost review:** Auto-generate report every Sunday

---

### Tiered Router Integration
**Replace direct model calls:**
```python
# OLD: Always use Sonnet
model = 'claude-sonnet-4-5'

# NEW: Route based on task
from tiered_model_router import route_task

result = route_task("Generate daily tasks from goals")
model = result['model']  # Might be local-smart (free!)
```

**Fallback logic:** If local model fails, auto-retry with next tier

---

### Self-Optimizer Integration
**Cron job:**
```
0 2 * * * cd /Users/clawdbot/clawd && python3 scripts/self_optimizer.py >> logs/self_optimization.log 2>&1
```

**Morning notification:** 
"🔧 Self-optimization complete: 3 improvements applied, score: 87/100"

---

## Expected Impact

### Cost Savings
**Current:** ~$100-300/month (everything on Sonnet)

**With tiered routing:**
- 50% of tasks → local models (FREE)
- 30% of tasks → Haiku ($0.25/M)
- 15% of tasks → Sonnet ($3/M)
- 5% of tasks → Opus ($15/M)

**New cost:** ~$30-80/month

**Savings:** 70-80% reduction

---

### Quality Improvements
**Self-optimization results:**
- Better prompts (clearer, more specific)
- Fewer edge cases missed
- More consistent behavior
- Stays current with best practices

**Example improvements:**
- "Add timeout handling to all API calls"
- "Clarify when to use exec vs browser tool"
- "Add fallback behavior for rate limits"

---

### Visibility
**Before:** No idea what costs what

**After:**
- Know exactly where money is spent
- Identify expensive workflows
- Optimize highest-cost areas first
- Track savings from optimization

---

## Files Created

- `scripts/cost_tracker_advanced.py` (400 lines)
- `scripts/tiered_model_router.py` (200 lines)
- `scripts/self_optimizer.py` (300 lines)
- `dashboard/costs.html` (cost visualization)
- `data/api_costs.json` (cost log)
- `data/optimizations.json` (improvement log)

---

## Next Steps

1. **Hook cost tracker into all AI calls**
   - Wrap OpenAI/Anthropic clients
   - Auto-log every API interaction
   
2. **Replace model selection with router**
   - Update task_generator, memory scripts
   - Use tiered routing everywhere

3. **Schedule self-optimizer**
   - Add cron job for 2am daily
   - Morning notification of improvements

4. **Build cost alerting**
   - Slack/Telegram notification if spending spikes
   - Weekly cost reports

5. **Train router with feedback**
   - Log when routing fails
   - Improve classification over time

---

## Status
✅ All systems built and tested  
⏳ Integration pending  
📊 Dashboards ready  
🚀 Ready for deployment

**Test:**
```bash
# Cost tracker
python3 ~/clawd/scripts/cost_tracker_advanced.py dashboard

# Tiered router
python3 ~/clawd/scripts/tiered_model_router.py "your task here"

# Self-optimizer
python3 ~/clawd/scripts/self_optimizer.py
```
