# Ross's Workspace Inventory
**Last Updated:** 2026-02-11 07:59 CST

*Everything you've built, where it lives, how to access it.*

---

## 🎯 Quick Access Commands

Ask me:
- **"Open dashboard"** → I'll give you the main command center URL
- **"Show me [project]"** → I'll pull up the specific tool
- **"What's running?"** → I'll list all active services
- **"Show inventory"** → I'll display this file with updates

---

## 🚀 Active Services (Running Now)

| Service | URL | Purpose | Status |
|---------|-----|---------|--------|
| Fitness Tracker | `http://localhost:3000` | Food/workout logging | ⏳ Building |
| Org Chart Dashboard | `http://localhost:8080` | System overview, builds, costs | ✅ Active |
| (Master Hub coming soon) | `http://localhost:5000` | Central command center | 🔨 Building |

**How to check status:** `bash ~/clawd/scripts/jarvis_quick.sh status`

---

## 📂 Projects & Tools

### NBA Rankings System
**Location:** `~/clawd/nba/`
**Status:** 🔨 Optimizing (Feb 20th deadline)

**Files:**
- `rankings.csv` — Latest rankings export
- `dawgbowl-rankings.csv` — DawgBowl-specific slate
- `rankings-report.md` — Human-readable analysis
- `nba_stats_integration.py` — Stats API connector
- `update_rankings.sh` — Regenerate rankings

**Quick commands:**
```bash
cd ~/clawd/nba && ./update_rankings.sh  # Refresh rankings
cat ~/clawd/nba/rankings-report.md      # View report
```

**Current optimization:** Professional-grade system (Drew Dinkmeyer level), fixing Underdog CSV export

---

### Fitness Tracker
**Location:** `~/clawd/fitness-dashboard/` (building now)
**Status:** 🔨 Building (ETA: 2-3 hours)

**What it will have:**
- Visual calorie tracking (goal: 2200/day)
- Workout calendar
- Weight trend graph
- Macro breakdown (protein goal: 200g)

**Access:** `http://localhost:3001` (when ready)

---

### GOALS & Decision Framework
**Location:** `~/clawd/GOALS.md`
**Purpose:** Your north star — what Jarvis builds autonomously

**Quick view:** `cat ~/clawd/GOALS.md`

---

### Memory Systems
**Location:** `~/clawd/memory/`

**Files:**
- `MEMORY.md` — Long-term curated memory (main session only)
- `jarvis-journal.md` — My learning log, patterns, insights
- `YYYY-MM-DD.md` — Daily logs (raw notes)
- `heartbeat-state.json` — Tracking periodic tasks
- `decision-log.json` — My autonomous decisions

**Purpose:** Continuity across sessions, learning over time

---

### Autonomous Build System
**How it works:**
1. I read `GOALS.md` on every startup
2. Every heartbeat (30 min), I check if builds are needed
3. I spawn sub-agents to build in parallel
4. Finished builds ping you via Telegram

**Files:**
- `BUILD_QUEUE.md` — Pending tasks
- `scripts/autonomous_check.py` — The brain
- `AUTONOMOUS_AGENT.md` — Protocol docs

**Monitor:** `bash ~/clawd/scripts/jarvis_quick.sh status`

---

### Cost Tracking
**Location:** `~/clawd/scripts/cost_tracker.py`

**Quick commands:**
```bash
python3 ~/clawd/scripts/cost_tracker.py daily   # Today's spend
python3 ~/clawd/scripts/cost_tracker.py week    # Last 7 days
python3 ~/clawd/scripts/cost_tracker.py month   # This month
```

**Budget:** $20/day, $250/week, $1000/month  
**Logs:** `~/clawd/memory/cost-log-YYYY-MM-DD.json`

---

### Dashboards & Reports
**Location:** `~/clawd/`

| File | Purpose |
|------|---------|
| `org-chart-dashboard.html` | System overview, build status, costs |
| `reports/weekly_progress.html` | Sunday 6pm weekly report |
| `monitoring/system-health.log` | Auto-recovery logs |

**Access:** Open in browser or ask me to pull them up

---

### Scripts & Automation
**Location:** `~/clawd/scripts/`

**Key scripts:**
- `autonomous_check.py` — Autonomous build system
- `cost_tracker.py` — Cost monitoring
- `jarvis_quick.sh` — Quick commands (status, spawn, etc.)
- `current_context.py` — Current date/time/context
- `check_escalations.py` — Daemon → Sonnet escalations
- `orchestrator.py` — Tier 1 automation (Twitter, email, health checks)

**Run shortcuts:** `bash ~/clawd/scripts/jarvis_quick.sh <command>`

---

### Calendar Integration
**Location:** `~/clawd/calendar/`
**Status:** ✅ Active (Google Calendar synced)

**Quick commands:**
```bash
cd ~/clawd/calendar && python3 google_calendar.py today      # Today's events
cd ~/clawd/calendar && python3 google_calendar.py upcoming 24 # Next 24 hours
```

**Upcoming:** Hannah visiting March 3-6

---

### Security & Logs
**Location:** `~/clawd/security-logs/`

**Purpose:** Track all sensitive actions, external API calls, credential access

**Weekly audit:** Runs Sunday 9am CST automatically

**Emergency kill switch:** Tell me `/lockdown` to revoke all credentials immediately

---

## 🏗️ Builds In Progress

| Build | Started | ETA | Purpose |
|-------|---------|-----|---------|
| NBA Rankings Optimization | 2026-02-11 07:56 | 9 hrs | Professional-grade system, Underdog CSV fix |
| Fitness Progress Dashboard | 2026-02-11 07:57 | 2-3 hrs | Visual calorie/workout/weight tracking |

**Track progress:** Ask me "How's the build going?" or check `org-chart-dashboard.html`

---

## 🗂️ File Organization

```
~/clawd/
├── GOALS.md                    # Your north star
├── AGENTS.md                   # My operating instructions
├── SOUL.md                     # My personality/style
├── USER.md                     # About you
├── TOOLS.md                    # Tool-specific notes
├── HEARTBEAT.md                # Periodic task schedule
├── WORKSPACE_INVENTORY.md      # This file!
│
├── memory/                     # Continuity & learning
│   ├── MEMORY.md               # Long-term memory
│   ├── jarvis-journal.md       # My learning log
│   ├── 2026-02-*.md            # Daily logs
│   └── *.json                  # State tracking
│
├── scripts/                    # Automation & tools
│   ├── autonomous_check.py
│   ├── cost_tracker.py
│   ├── jarvis_quick.sh
│   └── ...
│
├── nba/                        # NBA rankings system
│   ├── rankings.csv
│   ├── rankings-report.md
│   └── ...
│
├── fitness-dashboard/          # Fitness tracking (building)
│   └── (in progress)
│
├── calendar/                   # Google Calendar integration
│   └── google_calendar.py
│
├── reports/                    # Generated reports
│   └── weekly_progress.html
│
├── security-logs/              # Security audit logs
│   └── audit-*.md
│
└── monitoring/                 # System health logs
    └── system-health.log
```

---

## 📱 Easy Access Strategy

**Option 1: Just Ask Me**
- "Open NBA rankings"
- "Show me fitness dashboard"
- "Pull up the org chart"
- I'll give you the direct link or file path

**Option 2: Bookmarks** (Coming Soon)
- I'll create a bookmarks HTML page with all your dashboards
- Bookmark it in Safari: instant access to everything

**Option 3: Alfred/Spotlight** (Coming Soon)
- Quick shortcuts for common tasks
- `cmd+space` → "Jarvis dashboard" → opens hub

---

## 🎯 What's Next

**Building now:**
1. ✅ This inventory (done!)
2. 🔨 Master Command Center — single dashboard to rule them all
3. 🔨 NBA rankings optimization
4. 🔨 Fitness progress dashboard

**Coming soon:**
- Bookmark page (all dashboards in one HTML page)
- Mobile-friendly access
- Quick command palette (type "jarvis [command]")

---

## 💡 Pro Tips

1. **Lost a dashboard?** Ask me "What's running?" or "Show inventory"
2. **Need to see something specific?** Just ask — I'll pull it up
3. **Want to check costs?** `python3 ~/clawd/scripts/cost_tracker.py daily`
4. **Weekly overview?** Check `reports/weekly_progress.html` (Sunday 6pm)
5. **System issues?** `bash ~/clawd/scripts/jarvis_quick.sh status`

---

**Bottom line:** You shouldn't have to remember URLs or hunt for files. Just ask me. I'll get you there.

---

*This inventory updates automatically. Ask me "refresh inventory" anytime.*
