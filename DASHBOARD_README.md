# 🎯 Jarvis Command Center Dashboard

Real-time organization chart showing Jarvis's sub-agent structure and build queue.

## Quick Start

### Start the Dashboard Server

```bash
bash ~/clawd/scripts/dashboard_start.sh
```

Then open in your browser:
```
http://10.0.0.16:8080/org-chart-dashboard.html
```

### Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

## Features

- **Live Org Chart** - Visual hierarchy of Jarvis and all active sub-agents
- **Real-time Updates** - Auto-refreshes every 10 seconds
- **Build Queue** - Shows what's coming up next
- **Statistics** - Daily stats on builds and success rate
- **Click for Details** - Click any agent node to see full details

## Status Colors

- 🟢 **Green** - Completed
- 🔵 **Blue** - Currently Building
- 🔴 **Red** - Failed
- ⚪ **Gray** - Queued
- ⚡ **Purple** - Active (Main Agent)

## Manual Data Refresh

If you want to manually update the dashboard data:

```bash
python3 ~/clawd/scripts/update_dashboard_data.py
```

## Files

- **Dashboard**: `/Users/clawdbot/clawd/org-chart-dashboard.html`
- **Data Source**: `/Users/clawdbot/clawd/dashboard-data.json`
- **Updater Script**: `/Users/clawdbot/clawd/scripts/update_dashboard_data.py`
- **Server Script**: `/Users/clawdbot/clawd/scripts/dashboard_server.sh`

## Data Sources

The dashboard pulls data from:
- `clawdbot sessions` - Active agents and sessions
- `BUILD_STATUS.md` - Current build status
- `BUILD_QUEUE.md` - Queued builds

## Customization

Edit `org-chart-dashboard.html` to customize:
- Colors and theme
- Refresh interval (default: 10s)
- Layout and styling
- Add new panels or features

## Troubleshooting

**Dashboard shows "No active agents":**
- Wait a few seconds for data to generate
- Check if `dashboard-data.json` exists
- Manually run the updater script

**Port 8080 already in use:**
- Check what's running: `lsof -i :8080`
- Kill existing process: `kill <PID>`
- Or use a different port in `dashboard_server.sh`

**Data not updating:**
- Check if updater process is running: `ps aux | grep update_dashboard_data`
- Check for errors: `python3 ~/clawd/scripts/update_dashboard_data.py`

## Mobile Access

The dashboard is fully responsive! Access from any device on your network at:
```
http://10.0.0.16:8080/org-chart-dashboard.html
```

---

Built with ❤️ by Jarvis
