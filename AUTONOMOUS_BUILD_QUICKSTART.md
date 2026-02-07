# 🚀 Autonomous Build System - Quick Start

**Status:** ✅ OPERATIONAL  
**Date:** 2026-02-06

---

## 🎯 What Is This?

**PROBLEM:** When Ross says "build X" and leaves, builds don't start automatically.

**SOLUTION:** This system auto-spawns sub-agents to build things while Ross is away.

**RESULT:** Ross says "build X" at 9am → comes back at 5pm → thing is done and ready to review.

---

## ⚡ Quick Commands

### Add a Build Task
```bash
# Quick add
python3 ~/clawd/scripts/add_build_task.py \
  --name "Your Task Name" \
  --desc "What to build" \
  --priority high

# With all options
python3 ~/clawd/scripts/add_build_task.py \
  --name "Spotify Integration" \
  --desc "OAuth + playlist automation" \
  --priority high \
  --time "4 hours" \
  --tech "Python, Spotipy"
```

### Check Status
```bash
# Full status
python3 ~/clawd/scripts/build_status.py

# Quick checks
python3 ~/clawd/scripts/build_status.py --queue      # What's queued
python3 ~/clawd/scripts/build_status.py --active     # What's building
python3 ~/clawd/scripts/build_status.py --completed  # What's done
```

### Force Build Start (Don't Wait for Heartbeat)
```bash
python3 ~/clawd/scripts/auto_build_manager.py
```

### View Status Files
```bash
# Real-time status
cat ~/clawd/BUILD_STATUS.md

# Full queue
cat ~/clawd/BUILD_QUEUE.md

# Open visual dashboard
open ~/clawd/progress.html
```

---

## 📋 How to Use

### 1. Add Task to Queue

**Option A: Using script (recommended)**
```bash
python3 ~/clawd/scripts/add_build_task.py \
  --name "My New Feature" \
  --desc "Detailed description here" \
  --priority high
```

**Option B: Edit BUILD_QUEUE.md manually**
1. Open `~/clawd/BUILD_QUEUE.md`
2. Add under "Active Queue" section:
   ```markdown
   - [ ] My New Feature - Added: 2026-02-06 15:00 - Priority: High
   ```
3. Add details under "Task Details" section

### 2. Wait for Auto-Start (or Force)

**Auto-start:**
- High priority: Starts within 30 min (next heartbeat)
- Medium priority: Starts overnight (10pm-6am)
- Low priority: Needs manual approval

**Force start now:**
```bash
python3 ~/clawd/scripts/auto_build_manager.py
```

### 3. Monitor Progress

**Check status anytime:**
```bash
python3 ~/clawd/scripts/build_status.py
```

**Or ask Jarvis:**
> "How's the build going?"

### 4. Review Completion

When done, Jarvis notifies you with:
- ✅ Completion message
- 🔗 Links to deliverables
- 📝 Summary of what was built

---

## 🎛️ Priority Levels

| Priority | When Starts | Use For |
|----------|-------------|---------|
| **High** | Within 30min | Direct requests, urgent work |
| **Medium** | Overnight (10pm-6am) | Improvements, nice-to-haves |
| **Low** | Manual only | Far-future ideas |

---

## 📊 File Locations

| File | Purpose |
|------|---------|
| `~/clawd/BUILD_QUEUE.md` | Task list (source of truth) |
| `~/clawd/BUILD_STATUS.md` | Real-time status |
| `~/clawd/scripts/auto_build_manager.py` | Core orchestrator |
| `~/clawd/scripts/add_build_task.py` | Helper: add tasks |
| `~/clawd/scripts/build_status.py` | Helper: check status |
| `~/clawd/subagents/active.json` | Build tracking database |

---

## 🔧 Troubleshooting

### Build Not Starting?

1. **Check if something else is building:**
   ```bash
   python3 ~/clawd/scripts/build_status.py --active
   ```

2. **Check priority:**
   - High priority? Should start within 30min
   - Medium priority? Only starts overnight
   - Low priority? Needs manual approval

3. **Force start:**
   ```bash
   python3 ~/clawd/scripts/auto_build_manager.py
   ```

### Check What's Happening

```bash
# See everything
python3 ~/clawd/scripts/build_status.py

# Just the queue
python3 ~/clawd/scripts/build_status.py --queue

# Active builds
python3 ~/clawd/scripts/build_status.py --active
```

---

## 🎓 Examples

### Example 1: Simple Build Request

Ross: "Build a script that backs up my fitness data daily"

Jarvis adds to queue:
```bash
python3 ~/clawd/scripts/add_build_task.py \
  --name "Fitness Data Backup" \
  --desc "Daily cron job to backup fitness tracker data to cloud storage" \
  --priority high \
  --time "2 hours"
```

Within 30 minutes → sub-agent spawns → builds it → notifies Ross when done

### Example 2: Overnight Build

Ross: "Would be cool to have NBA stats in the dashboard"

Jarvis adds to queue:
```bash
python3 ~/clawd/scripts/add_build_task.py \
  --name "NBA Stats Widget" \
  --desc "Add live NBA stats widget to dashboard with team rankings and scores" \
  --priority medium \
  --time "3 hours"
```

Added at 8pm → builds overnight → Ross wakes up to working widget

### Example 3: Batch Tasks

Ross: "I want these three things by tomorrow"

Add all three:
```bash
python3 ~/clawd/scripts/add_build_task.py --name "Task 1" --desc "..." --priority high
python3 ~/clawd/scripts/add_build_task.py --name "Task 2" --desc "..." --priority high  
python3 ~/clawd/scripts/add_build_task.py --name "Task 3" --desc "..." --priority high
```

System builds them sequentially overnight → all done by morning

---

## ✅ Success Checklist

System is working when:
- [x] Can add tasks via script
- [x] Can check status via script
- [x] BUILD_STATUS.md updates automatically
- [x] Heartbeat checks queue every 30min
- [x] High priority tasks auto-start
- [ ] Test task completed (pending next heartbeat)

---

## 📖 Full Documentation

For complete details, see: `~/clawd/AUTONOMOUS_BUILDS.md`

---

**Built:** 2026-02-06  
**Version:** 2.0  
**Status:** ✅ READY FOR USE

**THE SYSTEM IS LIVE. ADD TASKS AND WATCH THEM BUILD AUTOMATICALLY.** 🚀
