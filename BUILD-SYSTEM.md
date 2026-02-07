# 🔨 Autonomous Build System

**Created:** 2026-02-05
**Status:** ✅ OPERATIONAL

---

## Overview

This is Jarvis's autonomous build system - the infrastructure that allows continuous development while maintaining responsiveness. It enables parallel builds, tracks progress, and generates nightly reports.

## Components

### 1. Build Queue (`build-queue.md`)
**Purpose:** Single source of truth for what needs to be built

**Features:**
- Priority-ordered task list (High/Medium/Low)
- Status tracking (TODO/IN PROGRESS/COMPLETED)
- Template for adding new items
- Integration with subagent system

**Usage:**
- Main agent checks queue during heartbeats
- Spawns builders for high-priority items when time available
- Updates status as builds progress

### 2. Progress Dashboard (`progress.html`)
**Purpose:** Live view of active builds and completed work

**Features:**
- Real-time status of active builds
- Progress bars and completion percentages
- Links to code, demos, and logs
- Auto-refreshes every 30 seconds
- Beautiful gradient UI with animations

**Access:** Open `~/clawd/progress.html` in any browser

### 3. Nightly Build Reporter (`scripts/generate-build-report.py`)
**Purpose:** Auto-generate summaries of daily work

**Features:**
- Aggregates completed builds from active.json
- Extracts queue completions
- Includes progress log updates
- Email/Telegram ready formatting
- Saves to build-reports/ directory

**Usage:**
```bash
# Manual run
python3 ~/clawd/scripts/generate-build-report.py

# Add to cron for nightly reports (11pm)
crontab -e
# Add: 0 23 * * * python3 ~/clawd/scripts/generate-build-report.py
```

### 4. Decision Framework (in `SUBAGENT-FRAMEWORK.md`)
**Purpose:** Guidelines for when to build autonomously vs escalate

**Includes:**
- Build vs Escalate decision criteria
- Risk assessment checklist
- Decision matrix with examples
- Clear escalation patterns

**Key Rule:** When in doubt, escalate. Better to ask than build wrong thing.

### 5. Active Builds Tracker (`subagents/active.json`)
**Purpose:** JSON database of current and completed builds

**Structure:**
```json
{
  "active": [
    {
      "label": "agent-name",
      "sessionKey": "agent:main:subagent:xxx",
      "started": "ISO-8601 timestamp",
      "status": "in-progress|pending|blocked",
      "lastUpdate": "ISO-8601 timestamp",
      "tasks": [
        {"name": "task", "status": "todo|in-progress|done"}
      ],
      "links": [
        {"label": "Demo", "url": "file://..."}
      ]
    }
  ],
  "completed": [...]
}
```

**Updated by:**
- Main agent when spawning builds
- Subagents reporting progress
- Main agent when builds complete

---

## Workflow

### 1. Adding Work to Queue
Ross says: "Build [X]" or "I want to see [X] tomorrow"

Main agent:
1. Adds item to build-queue.md (HIGH priority)
2. Fills in template with details
3. Decides: build now or queue for later

### 2. Starting a Build
Main agent checks heartbeat or Ross's request:
1. Reviews build-queue.md HIGH priority items
2. Checks if requirements clear + risk low (decision framework)
3. Spawns subagent with specific task brief
4. Updates build-queue.md (TODO → IN PROGRESS)
5. Creates entry in active.json
6. Announces to Ross

### 3. During Build
Subagent:
- Works on tasks systematically
- Updates progress log every 2 hours
- Updates active.json task status
- Logs blockers if stuck

Main agent:
- Checks progress during heartbeats
- Reports status when Ross asks
- Unblocks or escalates issues

### 4. Completing Build
Subagent:
1. Marks all tasks done in active.json
2. Creates completion report
3. Final progress log update

Main agent:
1. Moves build to completed in active.json
2. Updates build-queue.md (IN PROGRESS → COMPLETED)
3. Announces to Ross with deliverable links
4. Includes in next nightly report

### 5. Nightly Report
Runs at 11pm (or manual):
1. Generates summary of day's work
2. Lists completed builds + deliverables
3. Shows active builds + progress
4. Saves to build-reports/YYYY-MM-DD.md
5. Available for email/Telegram delivery

---

## Integration Points

### With Heartbeats
Main agent heartbeat routine includes:
- Check build-queue.md for HIGH priority items
- Check active.json for stuck builds (no update >4h)
- Decide if time to spawn new builder
- Update Ross on progress if builds active

### With Memory System
- Daily logs (memory/YYYY-MM-DD.md) capture build context
- Progress logs provide detailed build history
- Build reports summarize for long-term memory

### With SUBAGENT-FRAMEWORK.md
- Decision framework guides spawn decisions
- Risk checklist prevents autonomous mistakes
- Role definitions ensure proper agent selection

---

## File Locations

```
~/clawd/
├── build-queue.md              # Priority task list
├── progress.html               # Dashboard
├── BUILD-SYSTEM.md            # This file
├── SUBAGENT-FRAMEWORK.md      # Includes decision framework
├── scripts/
│   └── generate-build-report.py  # Report generator
├── subagents/
│   ├── active.json            # Active/completed builds
│   └── *-progress.md          # Individual progress logs
└── build-reports/
    └── YYYY-MM-DD.md          # Daily reports
```

---

## Success Metrics

**Before Build System:**
- "I haven't started yet"
- Single-threaded work
- No visibility into progress
- Manual status updates

**After Build System:**
- Multiple builds in parallel
- Always responsive main agent
- Real-time progress dashboard
- Automated nightly reports
- Clear decision framework
- Structured task queue

---

## Usage Examples

### Example 1: Ross Requests New Feature
Ross: "Build a Spotify integration by tomorrow"

Jarvis:
1. Adds to build-queue.md (HIGH priority)
2. Checks decision framework (clear requirements, low risk)
3. Spawns spotify-integration-agent
4. "✅ Spawning builder for Spotify integration. I'll stay responsive and check progress every 2 hours."
5. Updates active.json
6. Checks in periodically
7. Announces when done

### Example 2: Proactive Build
Heartbeat at 10pm, Ross likely sleeping:

Jarvis:
1. Checks build-queue.md
2. Sees MEDIUM priority item ready to build
3. Risk assessment passes
4. Spawns agent for overnight build
5. Logs decision to memory/YYYY-MM-DD.md
6. Continues normal heartbeat routine

Ross wakes up to:
- Nightly build report in email
- Progress dashboard showing completion
- Working demo ready to test

### Example 3: Progress Check
Ross: "How's the build going?"

Jarvis:
1. Reads active.json
2. Checks builder-progress.md
3. "🔨 Builder agent is 60% done with AI Concierge:
   - ✅ Research completed
   - ✅ Database schema designed
   - 🔨 API implementation in progress
   - ⏳ Frontend pending
   
   Latest update 30 minutes ago. On track for completion by midnight."

---

## Maintenance

### Daily
- Build reports auto-generate at 11pm
- Progress logs update every 2 hours
- active.json updates in real-time

### Weekly
- Review build-queue.md priorities
- Archive old completed items
- Clean up old progress logs (>30 days)

### Monthly
- Review decision framework effectiveness
- Update templates based on learnings
- Optimize dashboard and reporting

---

## Future Enhancements

**Potential additions:**
- Slack/Discord notifications for build completions
- Automated testing in build pipeline
- Build success/failure analytics
- Integration with GitHub for commit tracking
- Estimated completion times based on historical data
- Resource usage tracking

---

**This system enables true autonomous building while maintaining safety and visibility.**

*Built by: build-system-agent*
*Completion: 2026-02-05 21:30 CST*
