# COST_STRATEGY.md - Smart Model Usage

**Goal:** Keep Sonnet quality, minimize waste, use the right tool for each job.

**Created:** February 8, 2026  
**Owner:** Jarvis + Ross

---

## 💰 Cost Reality Check

**Current Setup:**
- **Tier 1 (Local Daemon):** $0/day - Runs 24/7, handles background work
- **Tier 2 (Sonnet - Me):** ~$10-15/day - Conversations + orchestration
- **Tier 3 (Specialists):** $3-10/task - Only when ROI justifies

**Monthly estimate:** ~$300-450 depending on build volume

---

## 🎯 Smart Model Selection Matrix

### When to Use LOCAL (Daemon - $0)
✅ **Always use for:**
- Heartbeat health checks (every 5 min)
- System monitoring (disk, processes, services)
- Task queue generation (reads GOALS.md)
- Night shift automation (2am - research, NBA intel)
- Morning brief generation (file creation)
- Simple data extraction
- Pattern detection in logs
- Pre-filtering content (generate 10 options, filter to top 3)

❌ **Never use for:**
- Conversations with Ross
- Decisions requiring judgment
- Content that goes directly to users
- Complex multi-step reasoning

**Why:** It's FREE. Max out usage here. Quality is "good enough" for 80% of background work.

---

### When to Use SONNET (Me - $$)
✅ **Always use for:**
- All conversations with Ross
- Orchestration & decision-making
- Tool calling & automation
- Context management
- Personality & relationship building
- Quick builds (<30 min)
- Multi-step planning

✅ **Optimize by:**
- Keep context lean (don't load unnecessary files)
- Use cache-friendly prompts (reuse structure)
- Batch similar tasks together
- Let daemon handle prep work

❌ **Don't use for:**
- Deep technical builds (use Codex)
- Revenue content (use Opus)
- Background monitoring (use Local)

**Why:** You're conversational, fast with tools, and handle 90% of work well. Good value for money.

---

### When to Use CODEX ($$$)
✅ **Use for:**
- Full-stack feature development (fitness tracker, dashboards)
- Complex API integrations (OAuth, webhooks, Stripe)
- Performance optimization & debugging
- Large-scale refactoring
- Database design & migrations
- When technical depth > conversational skill

✅ **Prep before spawning:**
1. Sonnet gathers requirements from Ross
2. Sonnet writes detailed spec
3. Sonnet spawns Codex with complete context
4. Codex executes, Sonnet reviews

❌ **Don't use for:**
- Simple scripts (Sonnet can do it)
- Content writing (wrong tool)
- Exploratory work (too expensive)

**Cost:** ~$3-8/task  
**ROI Threshold:** Task should save 2+ hours of human work OR generate revenue

---

### When to Use OPUS ($$$$)
✅ **Use for (AUTONOMOUS_AGENT.md criteria):**
- Landing pages that convert
- Sales copy that drives revenue
- Course content (sell for $50-200+)
- Templates/tools people will pay for
- Strategic business documents
- High-stakes creative work

✅ **Prep before spawning:**
1. Sonnet validates ROI (per AUTONOMOUS_AGENT rules)
2. Sonnet gathers research & context
3. Sonnet writes creative brief
4. Sonnet spawns Opus with full context
5. Opus delivers, Ross approves before publish

❌ **Don't use for:**
- Anything that won't generate revenue
- Exploratory ideas (test with Sonnet first)
- Internal documentation
- Low-stakes content

**Cost:** ~$5-10/task  
**ROI Threshold:** Output should generate $200+ in revenue OR save 5+ hours

---

## 🧠 Decision Tree: Which Model?

```
Is it background monitoring/checks?
├─ YES → Local Daemon ($0)
└─ NO → Continue...

Is Ross involved in the conversation?
├─ YES → Sonnet (me)
└─ NO → Continue...

Is it a technical build >30min?
├─ YES → Codex ($$$)
│   └─ Does ROI justify cost? (2+ hours saved)
│       ├─ YES → Spawn Codex
│       └─ NO → Sonnet handles it
└─ NO → Continue...

Is it revenue-generating content?
├─ YES → Opus ($$$$)
│   └─ Will it generate $200+?
│       ├─ YES → Spawn Opus
│       └─ NO → Sonnet handles it
└─ NO → Sonnet handles it
```

---

## 💡 Cost Optimization Tactics

### 1. Batch Work
- Don't spawn Opus for one landing page → batch 3-5 pages
- Don't spawn Codex for one feature → bundle related features
- Saves spawn overhead + context loading

### 2. Let Daemon Do Prep
- Daemon generates task options (free)
- Sonnet filters to top 3 (cheap)
- Opus executes winner (expensive but focused)
- **Result:** 80% of work done free, 20% on premium model

### 3. Prototype First
- Test idea with Sonnet ($)
- Validate with Ross
- Then upgrade to specialist ($$$)
- Avoids expensive experiments

### 4. Use Context Efficiently
- Load only what's needed for each task
- Cache-friendly prompts (TTL: 1h)
- Don't repeat context across spawns

### 5. Escalate Strategically
- Sonnet tries first
- Escalate to specialist only when stuck OR when quality gap matters
- Example: "I can build this in 2h, or Codex can do it better in 30min + $5"

### 6. Track ROI
- Log every specialist spawn with expected ROI
- Review monthly: Did we get the value?
- Cut low-ROI patterns

---

## 📊 Budget Guardrails

### Daily Limits (Soft)
- **Local Daemon:** Unlimited (it's free)
- **Sonnet:** ~$15/day (conversational + orchestration)
- **Codex:** 1-2 spawns/day = $6-16
- **Opus:** 0-1 spawn/day = $0-10

**Total:** ~$20-40/day = $600-1200/month

### Monthly Targets
- **Baseline:** $300 (conversations + heartbeats)
- **Growth mode:** $600 (2-3 builds/week)
- **Launch mode:** $1200 (daily builds, revenue push)

### Alert Thresholds
- **Yellow flag:** >$50/day for 3 days
- **Red flag:** >$75/day or >$1500/month
- **Action:** Review logs, identify waste, adjust strategy

---

## 🎮 Execution Protocol

### Before Every Spawn:
**Sonnet asks:**
1. Can I handle this? (90% of the time: yes)
2. Is specialist worth the cost?
3. What's the ROI?
4. Have I prepped all context?

**If spawning specialist:**
1. Write detailed spec
2. Gather all research/context
3. Set clear success criteria
4. Estimate cost vs value
5. Get Ross's blessing if >$10

### After Every Spawn:
1. Log cost + outcome
2. Measure actual ROI
3. Update strategy if needed

---

## 📈 Success Metrics

**Cost efficiency:**
- Cost per revenue dollar generated
- Cost per hour of human time saved
- Specialist spawn success rate (did it deliver?)

**Model performance:**
- Local: Uptime, escalation accuracy
- Sonnet: Task completion rate, spawn decisions
- Codex: Build quality, time saved
- Opus: Revenue generated per spawn

**Monthly review:**
- Total spend
- ROI by model tier
- High-cost patterns to optimize
- Low-value work to cut

---

## 🚦 Traffic Light System

**🟢 GREEN - No permission needed:**
- Local daemon work (free)
- Sonnet conversational work (<$2)
- Quick builds/scripts (<15 min)

**🟡 YELLOW - Heads up:**
- Codex spawn ($3-8) - mention cost, execute
- Multi-hour builds - set expectations

**🔴 RED - Ask first:**
- Opus spawn ($5-10) - justify ROI
- Experimental/unproven ideas on premium models
- Anything >$10 in one go

---

## 🎯 Monthly Cost Goals by Phase

### Phase 1: Foundation (Current)
**Goal:** Build infrastructure, establish patterns  
**Budget:** $300-600/month  
**Focus:** Sonnet + occasional specialists  
**ROI:** Time saved, systems built

### Phase 2: Product Development (Q1 2026)
**Goal:** Ship first revenue products  
**Budget:** $600-900/month  
**Focus:** More Codex (builds), strategic Opus (landing pages)  
**ROI:** First dollars earned

### Phase 3: Scale (Q2 2026)
**Goal:** Multiple income streams  
**Budget:** $900-1500/month  
**Focus:** Opus for content, Codex for features  
**ROI:** $3-5 revenue per $1 AI spend

---

## 🧪 Optimization Experiments

### Test 1: Night Shift Efficiency
- Daemon pre-generates 10 content ideas (free)
- Sonnet filters to top 3 (cheap)
- Opus writes 1 winner (expensive but focused)
- **Hypothesis:** 70% cost reduction vs Opus generating from scratch

### Test 2: Build Batching
- Batch 3 features into one Codex spawn vs 3 separate spawns
- **Hypothesis:** 40% cost savings from shared context

### Test 3: Quality Threshold
- A/B test: Sonnet content vs Opus content
- **Hypothesis:** Find the quality gap, price the difference

---

## 📝 Quarterly Review Questions

1. What's our cost per $ earned ratio?
2. Which specialist spawns had best ROI?
3. What work can shift to cheaper tier?
4. Are we over-using or under-using specialists?
5. What patterns emerged? Optimize them.

---

## 🎬 TL;DR - The Strategy

1. **Max out free (Local)** - Background work, monitoring, prep
2. **Optimize middle (Sonnet)** - Conversations, orchestration, quick builds
3. **Be selective with premium (Codex/Opus)** - Only when ROI is clear
4. **Batch work** - Bundle tasks to reduce overhead
5. **Prototype cheap** - Test with Sonnet before upgrading
6. **Track ROI** - Every spawn should justify its cost
7. **Monthly review** - Adjust based on what actually works

**Philosophy:** Spend money to make money or save time. Everything else can run cheap or free.

---

*This is a living document. Update monthly based on actual costs and outcomes.*
