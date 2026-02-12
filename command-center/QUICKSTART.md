# 🚀 Command Center - Quick Start

Get your dashboard running in 2 minutes!

## Step 1: Install (30 seconds)

```bash
cd ~/clawd/command-center
pip3 install -r requirements.txt
chmod +x ~/clawd/scripts/start_command_center.sh
```

## Step 2: Start (10 seconds)

```bash
bash ~/clawd/scripts/start_command_center.sh start
```

## Step 3: Open (5 seconds)

**Open your browser to:** http://localhost:5000

---

## That's It! 🎉

You now have a single dashboard showing:
- ✅ All your services (running/down)
- 📊 Recent builds and activity
- 💰 Today's costs
- 📁 Quick access to all key files
- 🔍 Search everything instantly
- 🏥 System health alerts

---

## Bookmark This URL

Make `http://localhost:5000` your:
- Browser homepage
- Pinned tab
- Phone home screen shortcut

**One URL. Everything you need.**

---

## Common Commands

```bash
# Start
bash ~/clawd/scripts/start_command_center.sh start

# Stop
bash ~/clawd/scripts/start_command_center.sh stop

# Restart
bash ~/clawd/scripts/start_command_center.sh restart

# Check status
bash ~/clawd/scripts/start_command_center.sh status
```

---

## What You See

### Service Status Panel
Your services with live indicators:
- Fitness Tracker (port 3001) - ✅ running or ❌ down
- Org Chart Dashboard (port 8080) - ✅ running or ❌ down
- NBA Rankings - Shows last update time

### Quick Actions
One-click buttons for:
- Open dashboards
- View reports
- Check costs
- Access goals and build queue

### Recent Activity
Last 10 builds, today's costs, system alerts

### Key Files Browser
All important files with last-modified times

### Search Bar
Type anything → instant results

---

## Auto-Start on Boot (Optional)

Want it to start automatically when your Mac boots?

```bash
cp ~/clawd/command-center/com.clawd.commandcenter.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.clawd.commandcenter.plist
```

See `AUTOSTART_SETUP.md` for details.

---

## Troubleshooting

**Port 5000 already in use?**
```bash
lsof -i :5000
# Kill the process, then restart
```

**Command Center not showing?**
```bash
# Check logs
tail -f ~/clawd/logs/command_center.log
```

**Services showing as down?**
- Make sure they're actually running on their ports
- Check: `lsof -i :3001` (for fitness tracker)
- Check: `lsof -i :8080` (for org chart)

---

## Next Steps

1. **Customize**: Edit `app.py` to add your own services
2. **Bookmark**: Make this your browser homepage
3. **Mobile**: Add to your phone's home screen
4. **Auto-start**: Set up LaunchAgent for boot-time startup

See `README.md` for full documentation.

---

**Welcome to your Command Center! 🎯**

*One dashboard to rule them all.*
