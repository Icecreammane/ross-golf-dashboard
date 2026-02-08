# Task Queue - Quick Reference

## 🚀 Quick Commands

### View Tasks
```bash
python3 ~/clawd/scripts/task_manager.py list
```

### Add Task
```bash
python3 ~/clawd/scripts/task_manager.py add "Title" "Description" [priority]
```

### Complete Task
```bash
python3 ~/clawd/scripts/task_manager.py complete 1
```

### Clear Completed
```bash
python3 ~/clawd/scripts/task_manager.py clear
```

---

## 💡 What You Need to Know

1. **Auto-generates tasks hourly** from GOALS.md when queue drops below 3
2. **Your manual tasks** always stay at top (priority 200)
3. **Smart merging** - won't duplicate or overwrite your tasks
4. **Priority order:** Manual (200) > Revenue (100) > Infrastructure (50) > Personal (25)

---

## 🎯 Typical Workflow

```bash
# Morning: Check what's queued
python3 ~/clawd/scripts/task_manager.py list

# Add urgent task
python3 ~/clawd/scripts/task_manager.py add \
  "Fix production bug" \
  "Dashboard showing wrong data" \
  200

# Later: Mark complete
python3 ~/clawd/scripts/task_manager.py complete 1

# Weekly: Clear done items
python3 ~/clawd/scripts/task_manager.py clear
```

---

## 📁 Files

- **Queue:** `/Users/clawdbot/clawd/data/task-queue.json`
- **Logs:** `/Users/clawdbot/clawd/logs/task-generator.log`
- **Full docs:** `/Users/clawdbot/clawd/BUILD_TASK_QUEUE.md`

---

## 🛠️ Control the Service

```bash
# Check status
launchctl list | grep taskqueue

# View logs
tail -f ~/clawd/logs/task-generator.log

# Disable auto-generation
launchctl unload ~/Library/LaunchAgents/com.clawdbot.taskqueue.plist

# Re-enable
launchctl load ~/Library/LaunchAgents/com.clawdbot.taskqueue.plist
```

---

That's it! Let Jarvis handle the task generation, you just add/complete as needed.
