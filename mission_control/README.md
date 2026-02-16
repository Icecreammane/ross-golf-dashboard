# Mission Control v3 - The Central Hub 🎯

**Your one-stop dashboard for all Jarvis operations**

![Version](https://img.shields.io/badge/version-3.0-blue)
![Status](https://img.shields.io/badge/status-live-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)

---

## What is Mission Control?

Mission Control is THE central dashboard Ross checks daily. It provides real-time visibility into what Jarvis is doing, shows all automated tasks, verifies memory persistence, and gives one-click access to every dashboard and tool.

**Think of it as your command center - everything Jarvis does, all in one place.**

---

## Features

### 🚀 Live Activity Feed
- **See what Jarvis is doing RIGHT NOW**
- 🔴 LIVE indicator pulses when actively working
- Shows last 20 actions with timestamps
- Smart icons for different action types
- Color-coded status (green=success, red=error, blue=in-progress)
- Cost tracking for each action
- Auto-refreshes every 5 seconds

### ⚙️ Daily Automations Status
- **All scheduled tasks in one place**
- Active: Morning Brief, Cost Tracking, Proactive Monitor, Memory Indexing
- Paused: Job Scanner, Flight Monitor
- Shows last run time, next run time, and results
- Status badges (Active/Paused/Stopped)
- Real-time daemon monitoring

### 🧠 Memory Health Widget
- **Verify persistence is working**
- Shows when SESSION_SUMMARY was last updated
- Displays files tracked, topics indexed, decision logs
- Health status indicator (Healthy/Degraded/Unhealthy)
- Proves memory system is functioning

### 🔗 Quick Access Links
- **One-click to everything**
- Daily Use: Lean Tracker, Tax Helper, Analytics, Jobs, Flights
- Production: Live deployments
- Admin: Settings, Memory Files, Logs, Cost Dashboard
- Live status indicators for local services

### 💰 Cost Dashboard
- Today's spend
- This week's total
- Projected monthly cost
- Top operations by cost
- Color-coded alerts

### 📊 System Health
- Disk space usage
- Memory usage
- Gateway status
- Visual health bars

---

## Quick Start

### Start Mission Control:
```bash
# Option 1: Use startup script
bash ~/clawd/scripts/start-mission-control.sh

# Option 2: Start manually
cd ~/clawd/mission_control
python3 app.py
```

### Access Dashboard:
**URL:** http://localhost:8081/mission-control

### Stop Mission Control:
```bash
# Find and kill process
cat ~/clawd/logs/mission-control.pid | xargs kill
```

---

## API Reference

### Live Activity Feed
```
GET /api/activity/live
Returns: {
  "actions": [...],
  "is_active": true/false,
  "timestamp": "2026-02-16T..."
}
```

### Automations Status
```
GET /api/automations
Returns: {
  "automations": [...],
  "timestamp": "2026-02-16T..."
}
```

### Memory Health
```
GET /api/memory/health
Returns: {
  "status": "healthy",
  "session_summary_updated": "Feb 15, 22:24",
  "files_tracked": 15,
  "topics_indexed": 284,
  "decision_logs": 47,
  ...
}
```

### Quick Links
```
GET /api/quick-links
Returns: {
  "daily_use": [...],
  "production": [...],
  "admin": [...]
}
```

### Complete Status (All-in-One)
```
GET /api/status
Returns: {
  "services": {...},
  "costs": {...},
  "health": {...},
  "memory": {...},
  "automations": [...],
  "activity": [...],
  "is_active": true/false,
  "timestamp": "2026-02-16T..."
}
```

---

## Integration

### Morning Brief
Mission Control link is automatically included in daily morning brief (7:30am):

```
🌅 Morning Brief - Feb 16, 2026
...
📊 [Open Mission Control](http://localhost:8081/mission-control)
Your central hub for all automations, live activity, and dashboards
```

### Action Tracking
All tool calls are logged to `logs/action-tracker.jsonl`:
```json
{
  "timestamp": "2026-02-16T10:30:00",
  "tool": "web_search",
  "action": "Search for Florida R&D jobs",
  "result": "success",
  "cost_estimate": 0.027
}
```

### Automation State
Heartbeat state tracked in `memory/heartbeat-state.json`:
```json
{
  "lastChecks": {
    "email": "2026-02-16T10:25:00",
    "calendar": "2026-02-16T10:20:00"
  },
  "morning_brief_sent": "2026-02-16T07:30:00"
}
```

---

## Architecture

**Stack:**
- Backend: Flask (Python)
- Frontend: Vanilla JavaScript + CSS
- Data: JSON files (no database)
- Refresh: REST API polling (5-30s intervals)

**Data Flow:**
```
Action Tracker (JSONL)  ──┐
Heartbeat State (JSON)  ──┤
Memory Index (JSON)     ──┼──> Flask API ──> Dashboard UI
Session Summary (MD)    ──┤
Cost Logs (JSON)        ──┘
```

**Performance:**
- Minimal CPU usage (polling-based)
- Fast response times (<50ms)
- Lightweight memory footprint
- No external dependencies

---

## Customization

### Add New Automation:
Edit `app.py` function `get_automations_status()`:
```python
{
    'name': 'My Automation',
    'icon': '🤖',
    'status': 'active',
    'last_run': timestamp,
    'next_run': 'Every hour',
    'result': 'Description',
    'enabled': True
}
```

### Add Quick Link:
Edit `app.py` function `get_quick_links()`:
```python
{
    'name': '🔧 My Tool',
    'url': 'http://localhost:9000',
    'status': check_port(9000)
}
```

### Customize Refresh Rate:
Edit `mission_control.html` at bottom:
```javascript
// Change from 5000 (5s) to desired milliseconds
setInterval(fetchData, 5000);
```

---

## Troubleshooting

### Dashboard won't load:
```bash
# Check if running
ps aux | grep "mission_control"

# Check logs
tail -f ~/clawd/logs/mission-control.log

# Restart
bash ~/clawd/scripts/start-mission-control.sh
```

### Port 8081 in use:
```bash
# Kill existing process
lsof -ti:8081 | xargs kill -9

# Or use different port
cd ~/clawd/mission_control
python3 app.py --port 8082
```

### Data not updating:
```bash
# Verify action tracker exists
ls -lh ~/clawd/logs/action-tracker.jsonl

# Check heartbeat state
cat ~/clawd/memory/heartbeat-state.json

# Verify memory index
ls -lh ~/clawd/memory/memory_index.json
```

### Live indicator always idle:
- Indicator activates when action logged in last 30 seconds
- Make sure action-tracker.jsonl is being written to
- Check system time is correct

---

## File Structure

```
mission_control/
├── app.py                          # Flask backend (all APIs)
├── templates/
│   └── mission_control.html        # Dashboard UI
├── README.md                       # This file
└── requirements.txt                # Python dependencies (Flask)

scripts/
└── start-mission-control.sh        # Startup script

logs/
├── action-tracker.jsonl            # All tool calls logged here
├── mission-control.log             # App logs
└── mission-control.pid             # Process ID

memory/
├── heartbeat-state.json            # Automation timestamps
├── memory_index.json               # Search index
└── cost-log-YYYY-MM-DD.json        # Daily costs
```

---

## Development

### Local Development:
```bash
cd ~/clawd/mission_control
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

### Add New Feature:
1. Add API endpoint in `app.py`
2. Add data fetching function
3. Add frontend component in `mission_control.html`
4. Wire up auto-refresh logic
5. Test and commit

### Debug Mode:
```python
# In app.py, change:
app.run(host='0.0.0.0', port=8081, debug=True)
```

---

## Version History

**v3.0 (2026-02-16):**
- ✨ Added live activity feed with 🔴 LIVE indicator
- ⚙️ Added daily automations status grid
- 🧠 Added memory health verification widget
- 🔗 Added quick access links navigation
- 📊 Integrated with morning brief
- 🎨 Full UI redesign with card-based layout
- ⚡ 5-second auto-refresh

**v2.0 (2026-02-15):**
- Original Mission Control launch
- Service status monitoring
- Cost dashboard
- System health metrics
- Confidence tracking

---

## Support

**Issues?** Check logs at `~/clawd/logs/mission-control.log`

**Questions?** Ask Jarvis: "Show me Mission Control logs"

**Feature requests?** Tell Ross what you want to see!

---

**Mission Control v3 - The one dashboard to rule them all.** 🎯
