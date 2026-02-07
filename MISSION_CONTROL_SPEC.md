# Mission Control V2 - Design Specification

**Purpose:** The single source of truth for the $500 MRR mission.

**Philosophy:** Not an org chart. A real command center showing what's happening RIGHT NOW and what needs to happen NEXT.

---

## Layout (Single Page, Mobile-First)

### 🎯 Header: The Mission
```
┌─────────────────────────────────────────────┐
│  🚀 MISSION: $500 MRR by March 31, 2026    │
│                                             │
│  Current MRR: $0        Days Left: 52       │
│  Progress: ▓░░░░░░░░░░ 0%                  │
│  On Track: ⚠️ NEED REVENUE                  │
└─────────────────────────────────────────────┘
```

**Data Sources:**
- MRR: Stripe API (when live), manual tracker file for now
- Days left: Auto-calculated from deadline
- Progress: MRR / 500 * 100
- Status: Green (>pace) / Yellow (on pace) / Red (<pace)

---

### 📊 Key Metrics (3-Column Grid)
```
┌─────────┬─────────┬─────────┐
│ Revenue │ Builds  │  Cost   │
│  $0     │  2/5    │  $12    │
│ This Mo │ Active  │ This Mo │
└─────────┴─────────┴─────────┘
```

**Revenue:** Total this month (all sources)
**Builds:** Active/Queued (e.g., "2 building, 5 queued")
**Cost:** API spend this month (Opus + Sonnet)

---

### 🏗️ Active Builds (Live Status)
```
┌─────────────────────────────────────────────┐
│ 🔨 BUILDING NOW                             │
├─────────────────────────────────────────────┤
│ Mission Control V2                          │
│ ▓▓▓▓▓░░░░░ 50% • 1h 15m left                │
│ Model: Opus • Cost: ~$3.50                  │
│                                             │
│ Tweet Content Pipeline                      │
│ ▓▓░░░░░░░░ 20% • 2h 30m left                │
│ Model: Sonnet • Cost: ~$0.80                │
└─────────────────────────────────────────────┘
```

**Shows:**
- What's building right now
- Progress bar + ETA
- Model being used
- Estimated cost

**Data Source:** BUILD_STATUS.md + session status

---

### 📋 Task Queue (Next 5 Tasks)
```
┌─────────────────────────────────────────────┐
│ 📝 QUEUE (Next 5)                           │
├─────────────────────────────────────────────┤
│ 1. [HIGH] Stripe Integration • 45min • $5   │
│    └─ Click to spawn → [SPAWN]              │
│                                             │
│ 2. [HIGH] Landing Page - Golf • 30min • $3  │
│    └─ Click to spawn → [SPAWN]              │
│                                             │
│ 3. [MED] Tweet Generator • 20min • $1       │
│    └─ Click to spawn → [SPAWN]              │
└─────────────────────────────────────────────┘
```

**Shows:**
- Priority, task name, ETA, cost estimate
- One-click spawn button
- Auto-prioritizes by: revenue > automation > content

**Data Source:** BUILD_QUEUE.md

---

### ✅ Recent Wins (Last 7 Days)
```
┌─────────────────────────────────────────────┐
│ 🏆 WINS (Last 7 Days)                       │
├─────────────────────────────────────────────┤
│ • Hybrid Model Strategy (Today)             │
│ • Autonomous Build System Fixed (Today)     │
│ • Florida Freedom Dashboard (Yesterday)     │
│ • Calendar Integration (Feb 2-3)            │
│                                             │
│ Velocity: 4 builds/week ↗️                   │
└─────────────────────────────────────────────┘
```

**Shows:**
- What shipped recently
- Proof of momentum
- Velocity trend (up/down/flat)

**Data Source:** DONE.md

---

### 🚨 Alerts & Blockers
```
┌─────────────────────────────────────────────┐
│ ⚠️ NEEDS ATTENTION                          │
├─────────────────────────────────────────────┤
│ • Fitness tracker down (port 3000)          │
│ • Stripe integration blocked (need API key) │
│ • Tweet approval needed (7 drafts pending)  │
└─────────────────────────────────────────────┘
```

**Shows:**
- What's broken or blocked
- What needs your decision
- What's waiting on you

**Data Source:** Health checks, BUILD_QUEUE.md blockers, pending approvals

---

### ⚡ Quick Actions (Buttons)
```
┌────────────────────────────────────────┐
│ [🚀 Spawn Next Build]                  │
│ [📊 View Full Queue]                   │
│ [✅ Approve Content]                   │
│ [📈 Weekly Report]                     │
│ [⏸️ Pause Autonomy]                    │
└────────────────────────────────────────┘
```

**One-click actions:**
- Spawn Next Build: Spawns highest priority task
- View Full Queue: Opens BUILD_QUEUE.md
- Approve Content: Opens tweets-pending/ folder
- Weekly Report: Generates velocity report
- Pause Autonomy: Stops auto-spawning

---

### 🤖 Agent Status (Collapsed by Default)
```
┌─────────────────────────────────────────────┐
│ 🤖 AGENTS                            [▼]    │
├─────────────────────────────────────────────┤
│ Jarvis (Main)        Active    Sonnet       │
│ Build Agent #1       Building  Opus         │
│ Build Agent #2       Building  Sonnet       │
│ Research Agent       Idle      GLM-4.7      │
└─────────────────────────────────────────────┘
```

**Shows:**
- Which agents are running
- What they're doing
- What model they're using

---

## Technical Implementation

### Frontend
- **Single HTML file** (self-contained, works offline)
- **Auto-refresh** every 30 seconds (live updates)
- **Mobile-first** responsive design
- **Dark mode** by default
- **No backend needed** (reads markdown files directly via fetch)

### Data Sources
- `BUILD_STATUS.md` → Active builds
- `BUILD_QUEUE.md` → Task queue
- `DONE.md` → Recent wins
- `dashboard-data.json` → Metrics (MRR, revenue, costs)
- `memory/heartbeat-state.json` → System health

### Visualizations
- **Chart.js** for progress bars and trend lines
- **Gradient progress bars** for builds
- **Color coding:** Green (good), Yellow (warning), Red (alert)

### Actions
- **Spawn Build:** Writes to `memory/spawn-signal.json`
- **Pause Autonomy:** Touches `.pause_autonomy` file
- **Approve Content:** Opens file browser to `content/tweets-pending/`

---

## User Experience

### On Desktop
- Large, immersive dashboard
- All sections visible at once
- Keyboard shortcuts (S = spawn, P = pause, Q = queue)

### On Mobile
- Stacked vertical layout
- Swipe between sections
- Quick actions at top (most important)
- Collapsed sections (tap to expand)

### Auto-Refresh
- Polls every 30 seconds for changes
- Shows "last updated" timestamp
- Visual indicator when refreshing

---

## Success Criteria

**Ross should be able to:**
1. Open Mission Control and know instantly: "What's happening?"
2. See if he's on track to hit $500 MRR
3. Know what's building and when it'll be done
4. Spawn the next build with one click
5. See blockers/alerts without digging through logs
6. Check on his phone in 5 seconds

**Mission Control becomes:**
- The first thing Ross opens every morning
- The single source of truth during work sessions
- The momentum tracker he checks before bed

---

## Future Enhancements (V3+)

- Voice control ("Mission Control, spawn next build")
- Push notifications for completed builds
- Integrations: Stripe, GitHub, social media
- Historical trends (MRR over time, velocity chart)
- Team view (if others join the mission)
- API endpoint (query via CLI)

---

**Build This First.** Everything else flows from this command center.

*Spec written: 2026-02-07 10:15 CST*
