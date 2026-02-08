# Unified Dashboard - Quick Start

## 🚀 Get Started in 30 Seconds

```bash
cd ~/clawd/unified-dashboard
./start.sh
```

**That's it!** Open http://localhost:3000 in your browser.

---

## 🎯 What You Get

### Single Dashboard for Everything
- 💰 **Revenue** - MRR progress, sales tracking
- 💡 **Opportunities** - Business leads ranked
- 📰 **Morning Brief** - NBA DFS daily summary
- 💪 **Fitness** - Weight loss progress
- ⛳ **Golf** - Round stats & handicap
- 🏀 **NBA Slate** - Today's DFS rankings (when active)

### Fast & Beautiful
- ⚡ Loads in 3ms (yes, milliseconds!)
- 🎨 Modern, responsive design
- 📱 Works on mobile
- 🔄 Auto-updates every 30 seconds

---

## 📊 Quick Commands

```bash
# Start dashboard
./start.sh

# Run tests
python3 test_dashboard.py

# Check status
curl http://localhost:3000/api/health

# View logs
tail -f dashboard.log
```

---

## 🔧 Configuration

All automatic! But if you want to customize:

**Change data sources** → Edit `app.py`  
**Change refresh rate** → Edit `static/js/dashboard.js`  
**Change port** → Edit `app.py` (last line)

---

## 🆘 Troubleshooting

**Port 3000 in use?**
```bash
lsof -ti :3000 | xargs kill -9
./start.sh
```

**Data not showing?**
```bash
# Check if data files exist
ls -lh /Users/clawdbot/clawd/fitness-tracker/fitness_data.json
ls -lh /Users/clawdbot/clawd/data/golf-data.json
```

**Dashboard won't load?**
```bash
# Check logs
tail -30 dashboard.log
```

---

## 📚 More Info

- **Full documentation** → `README.md`
- **Deployment guide** → `DEPLOYMENT.md`
- **Build details** → `BUILD_COMPLETE.md`

---

**Built with ❤️ by Jarvis**
