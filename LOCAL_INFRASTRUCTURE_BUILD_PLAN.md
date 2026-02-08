# Local Infrastructure Build Plan - Full Roadmap

**Goal:** Complete autonomous local infrastructure on Mac mini. Zero cloud dependency (except Sonnet for complex reasoning). All daemons + dashboards live and operational.

**Timeline:** This week (Feb 9-15, 2026)
**Cost:** $0/month (already running email daemon)
**ROI:** $150-250/month savings + 20-30 hours/week automation

---

## 🎯 Phase 1: Revenue-Enabling Infrastructure (Days 1-2)

**Critical path: Get to $500 MRR faster by removing distraction.**

### 1. Twitter Daemon (2 hours)
**What:** Monitor mentions, replies, DMs for revenue opportunities
**Why:** Catch golf coaching inquiries, product feedback, partnership pitches before they're lost
**Tech:** Twitter API polling (free tier) → local storage
**Output:** `/data/twitter-opportunities.json` + notifications
**Autonomous:** Every 15 min check mentions/DMs

### 2. Task Queue Auto-Generator (1.5 hours)
**What:** GOALS.md → auto-generate daily task list when queue is empty
**Why:** Never have an empty queue. Always know what to focus on.
**Tech:** Parse GOALS.md → priority scoring → generate 3-5 priority tasks
**Output:** `/data/task-queue.json` updated hourly
**Autonomous:** Every hour, regenerate if queue < 3 items

### 3. Revenue Dashboard (3 hours)
**What:** Central hub showing: golf coaching pipeline, template sales, daily revenue, stripe balance
**Why:** Single source of truth for $500 MRR progress
**Tech:** Flask API aggregating: Stripe webhook data + product landing page analytics
**Ports:** 3002 (revenue hub)
**Output:** http://mini:3002 → Real-time revenue visibility
**Autonomous:** Stripe webhooks auto-update on every sale/subscription

### 4. Social Post Scheduler (2.5 hours)
**What:** Generate + queue posts locally, publish automatically at 2am/6am/12pm/6pm
**Why:** Build audience while you sleep. Drive traffic to products.
**Tech:** Local LLM (Llama) generates variations → Twitter API posts
**Output:** `/data/social-posts-queue.json` + auto-posts to Twitter
**Autonomous:** Runs on schedule, no manual work

---

## 📊 Phase 2: Data Aggregation (Day 3)

### 5. Fitness Aggregator (1.5 hours)
**What:** Sync fitness tracker → daily/weekly summaries
**Why:** Morning brief context + data for fitness SaaS pitch
**Tech:** Call tracker API → analyze trends
**Output:** `/data/fitness-summary.json` (daily + weekly)
**Autonomous:** Every 6 hours, sync data

### 6. Golf Data Collector (1.5 hours)
**What:** Auto-score entry (simple form) → handicap calculation → trend analysis
**Why:** Track improvement + future golf coaching product data
**Tech:** Simple form submission → handicap algorithm
**Output:** `/data/golf-data.json` (scores + handicap trends)
**Autonomous:** When you score, auto-stores + recalculates

### 7. Email Daemon Enhancement (1 hour)
**What:** Already deployed. Add: extract action items + calendar event parsing
**Why:** More valuable summaries, auto-create tasks from emails
**Output:** Updated email-summary.json with action items + dates

---

## 🧠 Phase 3: Intelligence Layer (Days 4-5)

### 8. Morning Brief Generator (2 hours)
**What:** Automated 3-question brief from: tasks + email summary + calendar + fitness + golf + revenue
**Why:** Start every day with everything you need in one place
**Tech:** Aggregates data from all other daemons + formats into JSON
**Output:** `/data/reports/morning-brief-YYYY-MM-DD.json` + Telegram notification @ 7:30am
**Autonomous:** Every morning @ 7:30am

### 9. Opportunity Aggregator (1.5 hours)
**What:** Combine Twitter + Email + Calendar opportunities into priority list
**Why:** See all revenue opportunities in one place
**Output:** `/data/opportunities.json` (ranked by revenue potential)
**Autonomous:** Every 30 min

### 10. Weekly Report Generator (1.5 hours)
**What:** Compile: revenue snapshot, tasks completed, fitness progress, social reach, golf trends
**Why:** Track progress toward $500 MRR + personal goals
**Output:** `/data/reports/weekly-YYYY-WW.json` + pretty HTML
**Autonomous:** Every Sunday 6pm

---

## 🔌 Phase 4: Integration Layer (Day 6)

### 11. Central API Server (2 hours)
**What:** Single Flask API that all daemons + dashboards talk to
**Why:** Unified system, easier to maintain
**Tech:** REST endpoints for: tasks, opportunities, fitness, golf, social, revenue
**Port:** 3003 (internal API)

### 12. Dashboard Hub (2 hours)
**What:** Landing page showing: morning brief, tasks, opportunities, revenue, social stats
**Why:** Single dashboard for all automation
**Port:** 3002 (you open this every morning)
**Tech:** Real-time updates from central API

### 13. Stripe Webhook Handler (1 hour)
**What:** Listen for: new subscriptions, payments, refunds → auto-update dashboard
**Why:** Revenue dashboard updates in real-time
**Output:** Immediate notification when you make a sale

---

## 📁 Directory Structure (Final)

```
/Users/clawdbot/clawd/
├── daemons/
│   ├── email-daemon.py ✅ DONE
│   ├── twitter-daemon.py (NEXT)
│   ├── task-queue-generator.py (NEXT)
│   ├── fitness-aggregator.py
│   ├── golf-collector.py
│   ├── social-scheduler.py
│   ├── opportunity-aggregator.py
│   └── webhook-handler.py
│
├── processors/
│   ├── social-post-generator.py
│   ├── morning-brief-generator.py
│   ├── weekly-report-generator.py
│   └── email-summarizer.py (enhanced)
│
├── api-servers/
│   ├── central-api.py (port 3003)
│   ├── revenue-dashboard.py (port 3002)
│   ├── fitness-tracker/ (port 3000) ✅ DONE
│   └── golf-tracker.py (port 3001)
│
├── data/
│   ├── email-summary.json ✅ LIVE
│   ├── task-queue.json
│   ├── twitter-opportunities.json
│   ├── golf-data.json
│   ├── fitness-summary.json
│   ├── social-posts-queue.json
│   ├── revenue-tracking.json
│   └── reports/
│       ├── morning-brief-YYYY-MM-DD.json
│       └── weekly-YYYY-WW.json
│
├── launchd/
│   ├── com.jarvis.email-daemon.plist ✅ DONE
│   ├── com.jarvis.twitter-daemon.plist
│   ├── com.jarvis.task-generator.plist
│   ├── com.jarvis.fitness-aggregator.plist
│   ├── com.jarvis.golf-collector.plist
│   ├── com.jarvis.social-scheduler.plist
│   ├── com.jarvis.api-servers.plist
│   └── com.jarvis.webhook-handler.plist
│
└── logs/
    ├── email-daemon.log ✅ LIVE
    ├── twitter-daemon.log
    ├── api-server.log
    └── errors.log
```

---

## ⏱️ Build Schedule (Parallel Execution)

**Sunday Evening (Tonight):**
- ✅ Email daemon deployed
- 📝 You add Gmail password + deploy

**Monday (Day 1):**
- Spawn 4 builds in parallel:
  1. Twitter daemon (2h)
  2. Task queue generator (1.5h)
  3. Social scheduler (2.5h)
  4. Revenue dashboard (3h)

**Tuesday (Day 2):**
- Spawn 2 builds in parallel:
  1. Fitness aggregator (1.5h)
  2. Golf collector (1.5h)

**Wednesday (Day 3):**
- Spawn 3 builds in parallel:
  1. Morning brief generator (2h)
  2. Opportunity aggregator (1.5h)
  3. Weekly report generator (1.5h)

**Thursday (Day 4):**
- Spawn 3 builds in parallel:
  1. Central API (2h)
  2. Dashboard hub (2h)
  3. Webhook handler (1h)

**Friday (Day 5):**
- Integration testing
- Bug fixes + polish
- Launch all daemons on mini

**Total build time:** ~30 hours (parallel execution = done in 5 days)

---

## 💰 Cost Impact Summary

| System | Manual Cost | With Local | Savings |
|--------|------------|-----------|---------|
| Email monitoring | $0 (ignored) | $0 | $0 |
| Task management | $20/mo (Todoist) | $0 | $20 |
| Social posting | $50/mo (Buffer) | $0 | $50 |
| Analytics tracking | $30/mo | $0 | $30 |
| Fitness tracking | Ignored | $0 | $0 |
| Golf tracking | Ignored | $0 | $0 |
| Cloud processing (Sonnet) | ~$300/mo | ~$100/mo | $200 |
| **TOTAL** | **~$400/mo** | **~$100/mo** | **$300/mo savings** |

---

## 🎯 Success Criteria (End of Week)

- [ ] Email daemon running 24/7, fetching important emails every 30min
- [ ] Twitter daemon monitoring mentions/DMs, catching opportunities
- [ ] Task queue auto-generating when empty
- [ ] Morning brief lands at 7:30am every day (3 questions auto-generated)
- [ ] Revenue dashboard shows real-time: golf coaching inquiries, template sales, daily revenue
- [ ] Social posts scheduling + posting automatically
- [ ] Fitness data syncing + weekly summaries generated
- [ ] Golf scores logging + handicap calculating
- [ ] Weekly report generated every Sunday
- [ ] **All daemons running autonomously on Mac mini (zero manual work)**

---

## 🚀 The Win

By Friday: Your Mac mini is running your entire business.

- Email: Automated
- Tasks: Auto-generated
- Social: Scheduling itself
- Data: Aggregating itself
- Revenue: Visible in real-time
- You: Focus only on selling + shipping

**Everything else is automatic.** You wake up, check morning brief, see your revenue + tasks, work on high-leverage stuff.

That's the infrastructure.

---

## ✅ Approval Needed

**Do you approve this roadmap?** If yes, I'm spawning builds Monday morning (4 parallel builds). By Friday, the full system is live.

Any changes before we commit?
