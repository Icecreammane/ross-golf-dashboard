# Weekend Build Plan - Momentum Lock-In

**Goal:** Stop running in circles. Build systems that persist and compound.

**Deadline:** Sunday night, 2026-02-09

---

## ✅ DONE (Today)

### 1. Completion Registry
**File:** `DONE.md`  
**Purpose:** Everything we've shipped. Never rebuild, only improve forward.  
**Impact:** Visual proof of momentum, prevents circular work

### 2. Shortcuts Guide
**File:** `SHORTCUTS.md`  
**Purpose:** Fast commands to check status, prevent running in circles  
**Commands:** `/done`, `/status`, `/next`, `/wins`, `/blocked`, etc.  
**Impact:** 10x faster navigation, zero confusion

### 3. Trusted Actions
**Status:** Active  
**Scope:** Auto-commit memory, docs, build outputs  
**Impact:** Less friction, faster iteration

### 4. Hybrid Model Strategy
**Status:** Live  
**Logic:** Opus for revenue, Sonnet for everything else  
**Impact:** Better quality where it matters, cost-effective elsewhere

---

## 🔄 IN PROGRESS

### 5. Morning Momentum Brief
**Target:** Tomorrow morning (Feb 8, 7:30 AM)  
**Delivers:**
- Wins from overnight (what shipped while you slept)
- What's ready for you (builds complete, needs approval)
- What's blocked (needs your input)
- Today's plan (top 3 priorities)
- Quick stats (MRR, queue, health)

**Files to Create:**
- `scripts/morning_momentum.py` - Generator
- Integration with existing `morning-brief.html`

**Build Tonight:** Yes

---

### 6. Proactive Content Pipeline
**Target:** Tonight (Feb 7, overnight)  
**What:**
- Generate 7 tweet drafts overnight (side hustle journey, wins, lessons)
- Store in `content/tweets-pending/`
- Surface in morning brief with `/approve` commands
- Auto-post approved tweets at optimal times

**Files to Create:**
- `scripts/generate_tweets.py` - Content generator
- `content/tweets-pending/` - Staging folder
- `content/tweets-approved/` - Ready to post
- `scripts/post_tweet.py` - Publishing (manual for now, auto later)

**Build Tonight:** Yes

---

### 7. Smart Calendar Prep
**Target:** Tomorrow (Feb 8)  
**What:**
- Google Calendar API integration
- Check for events in next 24-48h
- Auto-generate context briefs:
  - Who are you meeting?
  - Why does it matter?
  - What should you prep?
- Deliver in morning brief

**Files to Create:**
- `calendar/google_calendar_integration.py` - API wrapper
- `calendar/event_brief_generator.py` - Context builder

**Build Tomorrow:** Yes

---

### 8. Automated Maintenance System
**Target:** Sunday (Feb 9)  
**What:**
- Dashboards auto-update (overnight cron)
- Content auto-generates (tweet drafts ready when you wake up)
- Builds auto-deploy (when completed, go live)
- Health auto-monitors (alert on failures)

**Files to Create:**
- `scripts/nightly_maintenance.sh` - Runner
- `scripts/update_all_dashboards.py` - Refresh all dashboards
- Cron job setup for overnight runs

**Build Sunday:** Yes

---

### 9. Weekly Velocity Report
**Target:** Sunday night (Feb 9, 6:00 PM)  
**What:**
- Every Sunday at 6pm, generate report:
  - This week: X shipped, Y hours saved, $Z generated
  - Last week: A/B/C
  - Trend: Up/Down/Flat
  - Momentum score (1-10)
  - What's working, what's not

**Files to Create:**
- `scripts/weekly_velocity.py` - Report generator
- `reports/weekly/` - Archive folder
- Integration with heartbeat for Sunday delivery

**Build Sunday:** Yes

---

## 📋 Implementation Order

**Tonight (Feb 7):**
1. Morning Momentum Brief script
2. Proactive Content Pipeline (tweet generator)
3. Test overnight run

**Tomorrow (Feb 8):**
1. Test morning brief delivery (7:30 AM)
2. Smart Calendar Prep (Google Calendar API)
3. Event brief generator

**Sunday (Feb 9):**
1. Automated Maintenance System
2. Weekly Velocity Report
3. Test full automation loop
4. Document everything

---

## 🎯 Success Criteria

**Monday morning (Feb 10), Ross wakes up to:**
- ✅ Morning brief with overnight wins
- ✅ 7 tweet drafts ready to approve
- ✅ Calendar prep for today's events
- ✅ Dashboard auto-updated with latest data
- ✅ Build queue refreshed with new tasks
- ✅ Weekly report from yesterday showing momentum

**Zero manual work. Just approve/reject/decide.**

---

## 🚫 Anti-Circle Checkpoints

**Before starting any build:**
1. Check `/done` - does this already exist?
2. Check `BUILD_QUEUE.md` - is it already queued?
3. Check `DONE.md` - can we extend instead of rebuild?

**If yes to any:** Don't rebuild. Optimize forward.

---

*This plan locks in momentum. No more waking up to nothing done.*
