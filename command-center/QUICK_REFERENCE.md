# 🎯 Command Center - Quick Reference Card

## 📍 Essential Info

**URL**: http://localhost:5000  
**Location**: `~/clawd/command-center/`  
**Script**: `~/clawd/scripts/start_command_center.sh`  
**Logs**: `~/clawd/logs/command_center.log`  

---

## ⚡ Quick Commands

```bash
# Start
bash ~/clawd/scripts/start_command_center.sh start

# Stop
bash ~/clawd/scripts/start_command_center.sh stop

# Restart
bash ~/clawd/scripts/start_command_center.sh restart

# Check Status
bash ~/clawd/scripts/start_command_center.sh status

# View Logs
tail -f ~/clawd/logs/command_center.log

# Verify Installation
bash ~/clawd/command-center/verify_install.sh
```

---

## 🔧 First-Time Setup

```bash
cd ~/clawd/command-center
pip3 install -r requirements.txt
chmod +x ~/clawd/scripts/start_command_center.sh
bash ~/clawd/scripts/start_command_center.sh start
open http://localhost:5000
```

---

## 🚀 What It Shows

✅ **Service Status** - Fitness (3001), Org Chart (8080), NBA Rankings  
✅ **Quick Actions** - One-click dashboard access  
✅ **Recent Activity** - Builds, costs, calendar  
✅ **Key Files** - GOALS, MEMORY, BUILD_QUEUE, reports  
✅ **Search** - Find anything instantly  
✅ **System Health** - Disk space, service alerts  
✅ **Bookmarks** - All important links  

---

## 🎯 Pro Tips

1. **Bookmark** http://localhost:5000 as homepage
2. **Pin tab** in browser for always-on access
3. **Mobile shortcut** - Add to phone home screen
4. **Auto-refresh** - Updates every 10 seconds automatically
5. **Search** - Type anything to find it fast

---

## 🔧 Customization

**Add Services**: Edit `app.py` → `SERVICES` list  
**Add Files**: Edit `app.py` → `KEY_FILES` list  
**Change Theme**: Edit `static/css/style.css` → `:root` variables  
**Change Refresh**: Edit `static/js/dashboard.js` → `REFRESH_INTERVAL`  

---

## 🐛 Troubleshooting

**Port 5000 in use?**
```bash
lsof -i :5000
kill -9 <PID>
```

**Won't start?**
```bash
tail -f ~/clawd/logs/command_center.log
```

**Services show down?**
- Check if actually running: `lsof -i :3001`
- Restart service, then refresh dashboard

**Missing dependencies?**
```bash
pip3 install -r ~/clawd/command-center/requirements.txt
```

---

## 📚 Documentation

- `README.md` - Complete docs
- `QUICKSTART.md` - 2-min setup
- `FEATURES.md` - Feature list
- `BUILD_REPORT.md` - Build summary
- `AUTOSTART_SETUP.md` - Auto-boot

---

## 🎯 Remember

**One URL: http://localhost:5000**  
**One command: `bash ~/clawd/scripts/start_command_center.sh start`**  
**One dashboard: Everything you need**  

---

*Print this and keep it handy!*
