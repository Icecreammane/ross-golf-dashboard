# Task Queue Auto-Generator - Build Documentation

**Status:** ✅ Production Ready  
**Built:** 2026-02-08  
**Location:** `/Users/clawdbot/clawd/scripts/task_queue_generator.py`

---

## 🎯 Purpose

Automatically generate priority-scored tasks from GOALS.md when the task queue runs low, ensuring Jarvis always has relevant work queued up.

---

## ⚙️ How It Works

### Automatic Generation
- **Runs hourly** via launchd (com.clawdbot.taskqueue)
- **Reads GOALS.md** to extract revenue, infrastructure, and personal goals
- **Generates 3-5 tasks** when queue drops below 3 items
- **Priority scoring:**
  - Revenue tasks: 100 pts (highest)
  - Infrastructure: 50 pts
  - Personal goals: 25 pts
  - Manual tasks: 200 pts (always top priority)

### Smart Merging
- **Preserves manual tasks** - never overwrites user-added items
- **Deduplicates** - won't add tasks with similar titles
- **Sorts by priority** - highest priority tasks bubble to top
- **Respects completions** - completed tasks don't trigger regeneration

---

## 📁 File Structure

```
/Users/clawdbot/clawd/
├── scripts/
│   ├── task_queue_generator.py   # Main auto-generator (runs hourly)
│   └── task_manager.py            # CLI for manual task management
├── data/
│   └── task-queue.json            # Task queue storage
├── logs/
│   └── task-generator.log         # Generation logs
└── Library/LaunchAgents/
    └── com.clawdbot.taskqueue.plist  # Hourly launchd job
```

---

## 🚀 Usage

### View Current Queue
```bash
python3 ~/clawd/scripts/task_manager.py list
```

### Add Manual Task
```bash
python3 ~/clawd/scripts/task_manager.py add "Task Title" "Task Description" [priority]
```

Example:
```bash
python3 ~/clawd/scripts/task_manager.py add \
  "Build Stripe Integration" \
  "Add payment processing to golf coaching site" \
  200
```

### Complete a Task
```bash
python3 ~/clawd/scripts/task_manager.py complete 3
```

### Remove a Task
```bash
python3 ~/clawd/scripts/task_manager.py remove 5
```

### Clear Completed Tasks
```bash
python3 ~/clawd/scripts/task_manager.py clear
```

### Force Regeneration
```bash
python3 ~/clawd/scripts/task_queue_generator.py
```

---

## 🔍 Task Queue Format

### JSON Structure
```json
{
  "last_updated": "2026-02-08T15:21:51.115823",
  "task_count": 6,
  "tasks": [
    {
      "id": "manual_20260208_152203",
      "title": "Ship Golf Coaching MVP",
      "description": "Build $29/mo golf coaching subscription",
      "priority": 100,
      "type": "revenue",
      "context": "Quick win product from GOALS",
      "created": "2026-02-08T15:21:51.115652",
      "source": "manual",
      "completed": false
    }
  ]
}
```

### Task Types
- **revenue** - Direct revenue-generating tasks
- **infrastructure** - Automation, tools, systems
- **personal** - Personal goals (fitness, learning, etc.)
- **manual** - User-added tasks (highest priority)

---

## 🎛️ Launchd Configuration

### Status Check
```bash
launchctl list | grep taskqueue
```

### View Logs
```bash
tail -f ~/clawd/logs/task-generator.log
```

### Reload Job
```bash
launchctl unload ~/Library/LaunchAgents/com.clawdbot.taskqueue.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.taskqueue.plist
```

### Disable Auto-Generation
```bash
launchctl unload ~/Library/LaunchAgents/com.clawdbot.taskqueue.plist
```

### Re-enable
```bash
launchctl load ~/Library/LaunchAgents/com.clawdbot.taskqueue.plist
```

---

## 🧪 Testing Results

### ✅ Test 1: Empty Queue Generation
- Started with 0 tasks
- Generated 5 tasks from GOALS.md
- Correctly prioritized by type
- **Status:** PASSED

### ✅ Test 2: Manual Task Preservation
- Added manual task
- Ran auto-generator
- Manual task preserved at top
- **Status:** PASSED

### ✅ Test 3: Regeneration Logic
- Reduced queue to 2 tasks (< 3 threshold)
- Auto-generator triggered
- Added 4 new tasks without duplicating
- Manual task remained at position 1
- **Status:** PASSED

### ✅ Test 4: Healthy Queue Skip
- Queue has 6 tasks (> 3 threshold)
- Auto-generator skipped generation
- Logged "Queue healthy - no generation needed"
- **Status:** PASSED

### ✅ Test 5: Launchd Integration
- Job loaded successfully
- Appears in `launchctl list`
- Scheduled for hourly execution
- **Status:** PASSED

---

## 🔧 Customization

### Change Generation Threshold
Edit `task_queue_generator.py`:
```python
def should_generate_tasks(current_tasks):
    if len(active_tasks) < 3:  # Change this number
        return True
```

### Adjust Priority Weights
```python
PRIORITY_WEIGHTS = {
    "revenue": 100,        # Adjust these values
    "infrastructure": 50,
    "personal": 25,
    "manual": 200
}
```

### Change Run Interval
Edit `com.clawdbot.taskqueue.plist`:
```xml
<key>StartInterval</key>
<integer>3600</integer>  <!-- 3600 = 1 hour -->
```

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.clawdbot.taskqueue.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.taskqueue.plist
```

---

## 📊 Monitoring

### Check Last Generation
```bash
tail -20 ~/clawd/logs/task-generator.log
```

### View Current Queue Stats
```bash
cat ~/clawd/data/task-queue.json | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'Tasks: {d[\"task_count\"]} | Updated: {d[\"last_updated\"]}')"
```

### Task Breakdown by Type
```bash
cat ~/clawd/data/task-queue.json | python3 -c "
import sys, json
from collections import Counter
d = json.load(sys.stdin)
types = Counter(t['type'] for t in d['tasks'])
for typ, count in types.items():
    print(f'{typ}: {count}')
"
```

---

## 🐛 Troubleshooting

### Generator Not Running
```bash
# Check if job is loaded
launchctl list | grep taskqueue

# View logs for errors
tail -50 ~/clawd/logs/task-generator.log

# Manually run to see errors
python3 ~/clawd/scripts/task_queue_generator.py
```

### Tasks Not Generating
1. Check GOALS.md exists and has content
2. Verify queue is below threshold (< 3 active tasks)
3. Check logs for extraction errors

### Duplicate Tasks
- Generator uses title matching (case-insensitive)
- If duplicates appear, check title extraction logic
- Manual tasks with similar names are preserved

---

## 🔄 Integration Points

### For Jarvis
```python
# Check task queue in autonomous_check.py or heartbeat
import json

with open('/Users/clawdbot/clawd/data/task-queue.json') as f:
    queue = json.load(f)

top_task = queue['tasks'][0] if queue['tasks'] else None
if top_task and not top_task.get('completed'):
    # Start working on top task
    pass
```

### For Ross (Shortcuts/Alfred)
```bash
# Quick view
alias tasks='python3 ~/clawd/scripts/task_manager.py list'

# Quick add
function addtask() {
    python3 ~/clawd/scripts/task_manager.py add "$1" "$2" ${3:-200}
}
```

---

## 📝 Future Enhancements

### Potential Improvements
- [ ] Task dependencies (block tasks until prerequisite complete)
- [ ] Time estimates (task duration tracking)
- [ ] Deadline support (urgent tasks)
- [ ] Context switching cost (prefer batching similar tasks)
- [ ] Learning from completion patterns (boost successful task types)
- [ ] Integration with build tracker (link tasks to builds)

### Not Planned
- ❌ UI/web interface (CLI is sufficient)
- ❌ Multi-user support (single-user system)
- ❌ Complex scheduling (keep it simple)

---

## ✅ Production Checklist

- [x] Script created and tested
- [x] Logging implemented
- [x] Manual task preservation verified
- [x] Regeneration logic tested
- [x] Launchd job configured and loaded
- [x] CLI tool for manual management
- [x] Documentation complete
- [x] Priority scoring working
- [x] Deduplication working
- [x] Smart merging working

**Status:** 🚀 PRODUCTION READY

---

## 📞 Support

**Issues?** Check:
1. `/Users/clawdbot/clawd/logs/task-generator.log`
2. Manually run: `python3 ~/clawd/scripts/task_queue_generator.py`
3. Verify GOALS.md is readable
4. Check launchd job: `launchctl list | grep taskqueue`

**Questions?** Ask Jarvis or review this doc.

---

*Built by Jarvis for Ross - 2026-02-08*
