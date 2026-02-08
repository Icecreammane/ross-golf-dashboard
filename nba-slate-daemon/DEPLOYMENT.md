# NBA Slate Rankings Daemon - Deployment Guide

## Pre-Deployment Checklist

### Before February 9, 2026:

1. **Configure Data Sources** (if real APIs available)
   - Update `scrapers/underdog_scraper.py` with actual Underdog API credentials
   - Add RotoWire scraping if needed (currently ESPN only)
   - Configure OddsAPI for real Vegas lines

2. **Test Scheduler**
   ```bash
   ./venv/bin/python3 -c "
   from apscheduler.schedulers.background import BackgroundScheduler
   from apscheduler.triggers.cron import CronTrigger
   import pytz
   
   scheduler = BackgroundScheduler()
   central = pytz.timezone('America/Chicago')
   
   # Test job scheduling
   scheduler.add_job(
       func=lambda: print('Test job fired!'),
       trigger=CronTrigger(hour=7, minute=30, timezone=central),
       id='test_job'
   )
   
   print('Jobs scheduled:')
   for job in scheduler.get_jobs():
       print(f'  {job.id}: {job.next_run_time}')
   "
   ```

3. **Verify System Time**
   ```bash
   # Ensure system is set to Central Time (America/Chicago)
   date
   python3 -c "import datetime, pytz; print(datetime.datetime.now(pytz.timezone('America/Chicago')))"
   ```

## Deployment on February 9, 2026

### Morning Setup (before 7:30 AM CT)

```bash
cd /Users/clawdbot/clawd/nba-slate-daemon

# Start the daemon
./start_daemon.sh

# Verify it's running
curl http://localhost:5051/api/status

# Check logs
tail -f daemon.log
```

### Monitoring Throughout the Day

```bash
# Check daemon status
curl http://localhost:5051/api/status | python3 -m json.tool

# View recent injuries
curl http://localhost:5051/api/injuries | python3 -m json.tool

# Get recommendations
curl http://localhost:5051/api/recommendations | python3 -m json.tool | head -50

# Manual refresh
curl http://localhost:5051/api/refresh

# Check data file
cat /Users/clawdbot/clawd/data/nba-slate-2026-02-09.json | python3 -m json.tool | head -100
```

### View Dashboard

Open browser to: **http://localhost:5051**

Or if accessing remotely: **http://[Mac-IP]:5051**

### Morning Brief (Auto-generated at 7:30 AM)

```bash
# View morning brief
cat /Users/clawdbot/clawd/data/nba-morning-brief-2026-02-09.md

# Or generate manually
./venv/bin/python3 test_morning_brief.py
```

## Schedule Verification

The daemon runs these jobs automatically:

| Time | Action | What it does |
|------|--------|--------------|
| 00:00 - 23:00 | Hourly updates | Scrapes injuries, updates rankings |
| 07:30 AM | Morning brief | Generates markdown summary |
| 23:59 PM | Final lock | Locks rankings, no more updates |

### Check Scheduled Jobs

```bash
./venv/bin/python3 -c "
import requests
import json
from datetime import datetime

status = requests.get('http://localhost:5051/api/status').json()
print(f'Status: {json.dumps(status, indent=2)}')
print(f'Current time: {datetime.now()}')
"
```

## Emergency Procedures

### Daemon Won't Start

```bash
# Kill any hanging processes
lsof -ti:5051 | xargs kill -9

# Check logs for errors
cat daemon.log

# Restart with fresh virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./start_daemon.sh
```

### Missing Data

```bash
# Manual data refresh
curl http://localhost:5051/api/refresh

# Verify data file exists
ls -lh /Users/clawdbot/clawd/data/nba-slate-2026-02-09.json

# Re-run ranking algorithm
./venv/bin/python3 -c "
from scrapers.underdog_scraper import UnderdogScraper
from ranking_engine import RankingEngine

scraper = UnderdogScraper()
players = scraper.fetch_slate_players()
engine = RankingEngine()
df = engine.rank_players(players)
df = engine.assign_tiers(df)
print(f'✅ {len(df)} players ranked')
"
```

### Scheduler Not Working

Check scheduler jobs:
```bash
./venv/bin/python3 -c "
from app import setup_scheduler
import time

scheduler = setup_scheduler()
print('Active jobs:')
for job in scheduler.get_jobs():
    print(f'  {job.id}: Next run at {job.next_run_time}')

# Let it run for 10 seconds
time.sleep(10)
scheduler.shutdown()
"
```

## Production Recommendations

1. **Use a process manager** (PM2, systemd, supervisord)
   ```bash
   # Example with PM2
   npm install -g pm2
   pm2 start ./venv/bin/python3 --name nba-daemon -- app.py
   pm2 logs nba-daemon
   pm2 stop nba-daemon
   ```

2. **Use a production WSGI server** (Gunicorn, uWSGI)
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5051 app:app
   ```

3. **Set up log rotation**
   ```bash
   # Add to logrotate
   /Users/clawdbot/clawd/nba-slate-daemon/daemon.log {
       daily
       rotate 7
       compress
       missingok
       notifempty
   }
   ```

4. **Monitor system resources**
   ```bash
   # Check memory usage
   ps aux | grep 'python3 app.py'
   
   # Check disk space
   df -h /Users/clawdbot/clawd/data/
   ```

## Post-Contest

After 11:59 PM on Feb 9, 2026:

```bash
# Stop the daemon
./stop_daemon.sh

# Archive results
mkdir -p ~/clawd/nba-archives/2026-02-09
cp -r /Users/clawdbot/clawd/data/nba-* ~/clawd/nba-archives/2026-02-09/
cp daemon.log ~/clawd/nba-archives/2026-02-09/

# Cleanup (optional)
# rm -rf venv
# rm daemon.log
```

## Troubleshooting

**Port already in use:**
```bash
lsof -ti:5051 | xargs kill -9
```

**Module not found:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**JSON serialization errors:**
- Already fixed with `NumpyEncoder` in `app.py`
- If issues persist, check `ranking_engine.py` for numpy type conversions

**Scheduler not firing:**
- Check system time and timezone
- Verify cron trigger syntax
- Review `daemon.log` for scheduler errors

---

**Support**: Check logs first (`daemon.log`), then review this guide.
**Dashboard**: http://localhost:5051
**Data**: `/Users/clawdbot/clawd/data/`
