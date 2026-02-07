# Model Strategy - Hybrid Opus/Sonnet

**Philosophy:** Use the right tool for the job. Opus for revenue, Sonnet for everything else.

## Model Selection Rules

### 🚀 Opus (Claude Opus 4-5)
**Use for:**
- Stripe/payment integration
- Landing pages & conversion funnels
- Checkout flows
- Subscription systems
- Revenue-generating features
- High-stakes builds where quality = money

**Why:** First-try accuracy matters. Better UX, fewer bugs, ships faster.

**Cost:** ~$3-5 per build (worth it for revenue impact)

### ⚡ Sonnet (Claude Sonnet 4-5)
**Use for:**
- Content generation (tweets, posts, drafts)
- Dashboards & reporting
- Automation scripts
- Documentation
- Research & analysis
- Internal tools

**Why:** Fast, cost-effective, good enough for non-revenue work.

**Cost:** ~$0.50-1 per build

## Implementation

**autonomous_check.py** auto-detects revenue builds by keywords:
- "stripe", "payment", "landing page", "checkout", "subscription", "conversion"
- Or explicit `category: "revenue"` in BUILD_QUEUE.md

**Main chat (Jarvis):** Stays on Sonnet by default

**Override:** Can manually specify model in spawn signal or BUILD_QUEUE.md task

## The Math

**Scenario:** Landing page build
- Sonnet: $1 × 3 attempts = $3 + 2 hours of your time
- Opus: $5 × 1 attempt = $5 + 30 min of your time

**Winner:** Opus (saves time, ships better product)

---

*Updated: 2026-02-07*
