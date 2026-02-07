# JARVIS COMMANDS - Quick Reference

Your autonomous assistant has built-in tools. Here's how to use them.

## 🔧 Utility Scripts

All scripts are in `~/clawd/scripts/` and can be run with Python 3.

### System Status
```bash
# Quick system health check
bash ~/clawd/scripts/status-check.sh
```

Shows: Gateway status, fitness tracker status, disk space, memory, heartbeat config

### Backups
```bash
# Create backup now
python3 ~/clawd/scripts/backup.py

# List available backups
python3 ~/clawd/scripts/backup.py list
```

**What gets backed up:** TODO.md, CHANGELOG.md, memory/, projects/, scripts/, monitoring/, ross/

**Retention:** Last 7 backups kept automatically

### Food Logging
```bash
# Interactive mode
python3 ~/clawd/scripts/food-logger.py

# Quick log from database
python3 ~/clawd/scripts/food-logger.py "chicken breast" 1.5

# List common foods
python3 ~/clawd/scripts/food-logger.py

# Future: Analyze food photo (AI vision not yet configured)
python3 ~/clawd/scripts/food-logger.py photo.jpg
```

**Quick foods:** chicken, rice, broccoli, salmon, steak, eggs, oatmeal, banana, protein shake, peanut butter, bread, pasta, potato, sweet potato

### Morning Brief
```bash
# Generate morning summary
python3 ~/clawd/scripts/morning-brief.py
```

Shows: Overnight projects, today's priorities, system alerts

### Task Management
```bash
# List all tasks
python3 ~/clawd/scripts/task.py list

# Show high priority only
python3 ~/clawd/scripts/task.py priority

# Add new task
python3 ~/clawd/scripts/task.py add "Build something cool"

# Mark task complete
python3 ~/clawd/scripts/task.py done 3
```

## 📱 Telegram Commands

Just send me messages normally. I understand:

**Food logging:**
- Send photo + "log this" → I'll analyze and log
- "Log chicken and rice" → Quick manual entry

**Status checks:**
- "Status" or "How are things?" → System health
- "What did you build?" → Recent projects

**Task management:**
- "Add task: [description]" → New TODO item
- "What's on the list?" → Show priorities

**Help:**
- "What can you do?" → Capabilities overview
- "Show commands" → This guide

## 🚀 Fitness Tracker

**Start tracker:**
```bash
cd ~/clawd/projects/2026-02-01-fitness-dashboard-v2
python3 app.py
```

**Access:**
- Mac mini: http://localhost:3000
- iPhone/MacBook: http://10.0.0.18:3000
- Bookmark on iPhone for quick access

**Features:**
- Weight/calorie/lift progress charts
- Weekly summary stats
- Quick entry forms
- 7/30/90 day views

## 🤖 Autonomous Features

I work automatically every 30 minutes (7am-11pm):

**What I do:**
- System health monitoring
- Email checking (when configured)
- Task queue maintenance
- Opportunity scanning

**Nightly builds (11pm-7am):**
- Pick high-priority project
- Build & test
- Create handoff docs
- Morning brief at 7:30am

**You control it all via:**
- `TODO.md` - I work through this queue
- `IDEAS.md` - Project pipeline
- `AUTONOMOUS_WORK.md` - My operating manual

## 📊 Monitoring

**Logs:**
- `~/clawd/CHANGELOG.md` - What I've built
- `~/clawd/monitoring/health.log` - System alerts
- `~/clawd/monitoring/disconnects.log` - Downtime tracking
- `~/clawd/memory/YYYY-MM-DD.md` - Daily work logs

**Backups:**
- `~/clawd/backups/` - Last 7 days auto-retained

## 💡 Tips

1. **iPhone home screen:** Add fitness tracker for app-like access
2. **Morning routine:** Check morning brief before work
3. **Throughout day:** Send me food photos while at work
4. **End of day:** Review CHANGELOG.md to see what I built
5. **Test projects:** All new builds go to `projects/YYYY-MM-DD-name/`

## 🆘 Troubleshooting

**Fitness tracker won't start:**
```bash
# Kill any existing process
pkill -f "python3 app.py"

# Start fresh
cd ~/clawd/projects/2026-02-01-fitness-dashboard-v2
python3 app.py
```

**Can't access from iPhone:**
- Make sure Mac mini and iPhone are on same WiFi
- Try http://10.0.0.18:3000 (Mac mini's IP)
- Check if tracker is running: `curl http://localhost:3000`

**Jarvis not responding:**
- Check gateway: `ps aux | grep clawdbot-gateway`
- View logs: `tail -50 ~/.clawdbot/logs/gateway.log`
- Restart if needed (tell me: "restart gateway")

---

**Remember:** I'm always learning and improving. If you need something that's not here, just ask and I'll build it.
