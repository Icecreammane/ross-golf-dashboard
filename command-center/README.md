# 🎯 Master Command Center

**Ross's Single Dashboard Hub** - One URL to rule them all.

Your central command center that shows all active services, dashboards, files, and activity in one unified interface at `http://localhost:5000`.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd ~/clawd/command-center
pip3 install -r requirements.txt
```

### 2. Start the Command Center

```bash
# Using the auto-start script (recommended)
bash ~/clawd/scripts/start_command_center.sh start

# Or run directly
python3 ~/clawd/command-center/app.py
```

### 3. Access Dashboard

Open your browser to: **http://localhost:5000**

---

## 📊 Features

### 🖥️ Service Status Panel
Real-time monitoring of all your services:
- **Fitness Tracker** (localhost:3001) - ✅ running / ❌ down
- **Org Chart Dashboard** (localhost:8080) - ✅ running / ❌ down  
- **Command Center** (localhost:5000) - ✅ running / ❌ down
- **NBA Rankings** (file-based) - Shows last update time

### ⚡ Quick Actions
One-click access to:
- 💪 Fitness Tracker dashboard
- 🏢 Org Chart dashboard
- 🏀 NBA Rankings report
- 💰 Cost Summary
- 🎯 Goals document
- 🔨 Build Queue

### 📈 Recent Activity Feed
Last 10 activities including:
- Builds completed
- Daily cost summary
- Calendar events (when integrated)
- System updates

### 📁 Key Files Browser
Quick access to important files with metadata:
- GOALS.md
- MEMORY.md
- BUILD_QUEUE.md
- WEEKEND_BUILD.md
- NBA Rankings
- Cost Summary
- And more...

### 🔖 Bookmarks
Organized shortcuts to:
- All dashboards
- Documentation files
- Utility scripts

### 🏥 System Health
Real-time system alerts:
- Disk space warnings
- Service status notifications
- Build failures
- Cost alerts

### 🔍 Smart Search
Instant search across:
- Services and dashboards
- Key files and documents
- Scripts and utilities

Type "NBA rankings" → instant link to report
Type "fitness" → jump to Fitness Tracker

### 📱 Mobile-Friendly
Fully responsive design - check your command center on any device.

### 🔄 Auto-Refresh
Dashboard auto-refreshes every 10 seconds to keep data current.

---

## 🛠️ Management Commands

### Start Command Center
```bash
bash ~/clawd/scripts/start_command_center.sh start
```

### Stop Command Center
```bash
bash ~/clawd/scripts/start_command_center.sh stop
```

### Restart Command Center
```bash
bash ~/clawd/scripts/start_command_center.sh restart
```

### Check Status
```bash
bash ~/clawd/scripts/start_command_center.sh status
```

---

## 🔧 Configuration

### Adding New Services

Edit `~/clawd/command-center/app.py` and add to the `SERVICES` list:

```python
SERVICES = [
    {'name': 'My New Service', 'port': 8888, 'url': 'http://localhost:8888'},
    # ... existing services
]
```

### Adding Key Files

Add to the `KEY_FILES` list:

```python
KEY_FILES = [
    {'name': 'My File', 'path': CLAWD_PATH / 'myfile.md', 'category': 'Category'},
    # ... existing files
]
```

### Customizing Auto-Refresh

Edit `static/js/dashboard.js`:

```javascript
const REFRESH_INTERVAL = 10000; // Change to your preference (milliseconds)
```

---

## 📁 Project Structure

```
command-center/
├── app.py                      # Flask backend
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── templates/
│   └── dashboard.html          # Main dashboard template
└── static/
    ├── css/
    │   └── style.css          # Dashboard styles
    └── js/
        └── dashboard.js        # Dashboard logic
```

---

## 🔗 API Endpoints

The Command Center exposes several JSON API endpoints:

### GET `/api/status`
Returns status of all services:
```json
[
  {
    "name": "Fitness Tracker",
    "url": "http://localhost:3001",
    "status": "running",
    "type": "service"
  }
]
```

### GET `/api/files`
Returns key files with metadata:
```json
[
  {
    "name": "GOALS.md",
    "category": "Planning",
    "path": "/Users/clawdbot/clawd/GOALS.md",
    "exists": true,
    "modified": "2024-01-15 14:30",
    "time_ago": "2h ago"
  }
]
```

### GET `/api/activity`
Returns recent activity:
```json
{
  "builds": [...],
  "costs": {"today": 12.50, "breakdown": {...}},
  "calendar": [...],
  "alerts": [...]
}
```

### GET `/api/search?q=query`
Search for services and files:
```json
[
  {
    "type": "service",
    "name": "Fitness Tracker",
    "url": "http://localhost:3001"
  }
]
```

---

## 🎨 Customization

### Theme Colors
Edit `static/css/style.css` CSS variables:

```css
:root {
    --primary: #2563eb;      /* Primary color */
    --success: #10b981;      /* Success indicators */
    --warning: #f59e0b;      /* Warning indicators */
    --danger: #ef4444;       /* Error indicators */
    --bg-dark: #0f172a;      /* Background */
    --bg-card: #1e293b;      /* Card background */
}
```

### Dashboard Layout
Modify `templates/dashboard.html` to add/remove sections or change layout.

---

## 🚨 Troubleshooting

### Command Center won't start
1. Check if port 5000 is already in use:
   ```bash
   lsof -i :5000
   ```
2. Check logs:
   ```bash
   tail -f ~/clawd/logs/command_center.log
   ```
3. Ensure Python 3 is installed:
   ```bash
   python3 --version
   ```

### Services show as "down" but are running
- Check firewall settings
- Verify services are bound to `0.0.0.0` or `localhost`
- Test port manually: `curl http://localhost:PORT`

### Files not showing
- Verify file paths in `app.py` match your actual file locations
- Check file permissions

---

## 🔐 Security Notes

- Command Center runs on localhost only (not exposed to internet)
- No authentication required (local access only)
- For production use, add authentication middleware
- Consider using HTTPS in production environments

---

## 📝 Future Enhancements

Potential features to add:

- [ ] Google Calendar integration
- [ ] Email inbox monitoring
- [ ] GitHub commit activity
- [ ] System resource monitoring (CPU, RAM)
- [ ] Build queue management UI
- [ ] File editor integration
- [ ] Notification system
- [ ] Dark/light theme toggle
- [ ] Customizable dashboard layout
- [ ] Widget system

---

## 🎯 Usage Tips

1. **Bookmark it**: Make `http://localhost:5000` your browser homepage
2. **Pin it**: Keep the tab pinned for instant access
3. **Mobile shortcut**: Add to home screen on mobile devices
4. **Auto-start**: Add to system startup for always-on access
5. **Second monitor**: Perfect for a dedicated status monitor

---

## 📞 Support

For issues or feature requests, document them in:
- `~/clawd/GOALS.md` for new features
- `~/clawd/memory/YYYY-MM-DD.md` for bugs/issues

---

## ✨ The Vision

**One URL. One Dashboard. Everything.**

No more juggling multiple tabs, remembering ports, or searching for files. The Command Center is your mission control - the single source of truth for everything Ross needs to see, access, and manage.

---

**Built with ❤️ by Jarvis**
*Your AI assistant, making life simpler one dashboard at a time.*
