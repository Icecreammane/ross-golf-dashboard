# 📊 Analytics System - Quick Start Guide

## Installation Complete ✅

The analytics system has been installed and tested successfully!

---

## What's Working Right Now

✅ **Analytics Tracker** - Tracks opportunities and conversions  
✅ **Insights Generator** - Produces actionable recommendations  
✅ **Weekly Reports** - Auto-generates HTML + text reports  
✅ **Dashboard Integration** - Displays metrics on revenue dashboard  
✅ **Data Sync** - Pulls from opportunities.json and social posts  
✅ **Tests** - All 6 tests passing  

---

## Quick Commands

### Run Analytics Once
```bash
# Full analytics cycle (sync + insights + dashboard)
python3 ~/clawd/scripts/analytics_runner.py
```

### View Current Analytics
```bash
# See analytics data
cat ~/clawd/data/analytics.json | python3 -m json.tool

# See latest insights
cat ~/clawd/data/analytics-insights.json | python3 -m json.tool

# View latest report
open ~/clawd/reports/analytics_report_latest.html
```

### Test Everything
```bash
# Run test suite
python3 ~/clawd/scripts/test_analytics.py
```

---

## Setting Up Continuous Mode

### Option 1: Run in Background (Simple)
```bash
# Start continuous analytics (checks every 15 min)
nohup python3 ~/clawd/scripts/analytics_runner.py --continuous > ~/clawd/logs/analytics_bg.log 2>&1 &

# Check it's running
ps aux | grep analytics_runner

# View logs
tail -f ~/clawd/logs/analytics_bg.log

# Stop it
pkill -f analytics_runner.py
```

### Option 2: Cron Jobs (Recommended)
```bash
# Edit crontab
crontab -e

# Add these lines:
*/15 * * * * cd ~/clawd && python3 scripts/analytics_runner.py >> logs/analytics_cron.log 2>&1
0 18 * * 0 cd ~/clawd && python3 scripts/analytics_weekly_report.py >> logs/analytics_weekly.log 2>&1

# Save and exit
# Cron will now run analytics every 15 minutes + weekly report on Sundays @ 6pm
```

### Option 3: LaunchAgent (Mac Native)
```bash
# Create launchd plist (already created below)
# Load it:
launchctl load ~/Library/LaunchAgents/com.clawd.analytics.plist

# Check status:
launchctl list | grep analytics

# Unload:
launchctl unload ~/Library/LaunchAgents/com.clawd.analytics.plist
```

---

## Integration with Revenue Dashboard

The analytics widget is automatically embedded in your revenue dashboard.

**To update dashboard:**
```bash
python3 ~/clawd/scripts/analytics_dashboard.py
```

Then refresh the dashboard in your browser: `http://10.0.0.18:8080/revenue/dashboard.html`

---

## Weekly Reports

Reports are auto-generated **Sundays @ 6pm**.

**Manual generation:**
```bash
python3 ~/clawd/scripts/analytics_weekly_report.py
```

**View latest report:**
```bash
# HTML version
open ~/clawd/reports/analytics_report_latest.html

# Text version
cat ~/clawd/reports/analytics_report_latest.txt
```

---

## Tracking New Data

### Mark Opportunity Conversion
```python
from scripts.analytics_tracker import AnalyticsTracker

tracker = AnalyticsTracker()
tracker.mark_conversion(
    tracking_id='email_2026-02-08T10:00:00Z_john@example.com',
    revenue=500.0,
    notes='Paid for coaching package'
)
```

### Track Social Post Engagement
```python
tracker.track_social_post({
    'id': 'tweet_123456',
    'posted_at': '2026-02-08T06:00:00Z',
    'likes': 45,
    'retweets': 12,
    'replies': 3
})
```

### Add Manual Opportunity
```python
tracker.track_opportunity({
    'source': 'email',
    'type': 'golf_coaching',
    'score': 95,
    'revenue_potential': '$500',
    'timestamp': '2026-02-08T10:00:00Z',
    'sender': 'john@example.com',
    'content': 'Inquiry about coaching'
})
```

---

## Monitoring

### Check Logs
```bash
# Tracker logs
tail -50 ~/clawd/logs/analytics_tracker.log

# Insights logs
tail -50 ~/clawd/logs/analytics_insights.log

# Runner logs
tail -50 ~/clawd/logs/analytics_runner.log

# All analytics logs
tail -50 ~/clawd/logs/analytics*.log
```

### Check System Status
```bash
# See runner state
cat ~/clawd/data/analytics-state.json | python3 -m json.tool

# Count opportunities tracked
cat ~/clawd/data/analytics.json | python3 -c "import json, sys; print(len(json.load(sys.stdin)['opportunities']))"

# Check conversion rate
python3 -c "
from scripts.analytics_tracker import AnalyticsTracker
tracker = AnalyticsTracker()
print(f'Overall conversion rate: {tracker.get_conversion_rate():.1f}%')
"
```

---

## Dashboard Access

Once integrated, view analytics at:

**Revenue Dashboard:** `http://10.0.0.18:8080/revenue/dashboard.html`  
**Analytics Report:** `http://10.0.0.18:8080/reports/analytics_report_latest.html`  
**Analytics Widget:** Embedded in revenue dashboard (scrolldown)

---

## Troubleshooting

### "No data appearing"
```bash
# Sync data manually
python3 ~/clawd/scripts/analytics_tracker.py

# Check source files exist
ls -lh ~/clawd/data/opportunities.json
ls -lh ~/clawd/data/social-posts-queue.json
```

### "Insights not generating"
```bash
# Generate manually
python3 ~/clawd/scripts/analytics_insights.py

# Check for errors
tail -20 ~/clawd/logs/analytics_insights.log
```

### "Runner not working"
```bash
# Check if running
ps aux | grep analytics_runner

# Check last run time
cat ~/clawd/data/analytics-state.json | grep last_sync

# Run manually
python3 ~/clawd/scripts/analytics_runner.py
```

---

## Next Steps

1. ✅ System is installed and tested
2. **Choose deployment method** (background, cron, or launchd)
3. **Start the runner** (see "Setting Up Continuous Mode" above)
4. **Monitor for 24 hours** to ensure data collection works
5. **Wait for first weekly report** (next Sunday @ 6pm)
6. **Review and adjust** insights based on your data

---

## Production Checklist

- [x] All tests passing (6/6)
- [x] Analytics data file created
- [x] Insights generator working
- [x] Weekly report generator working
- [x] Dashboard integration working
- [x] Logging configured
- [x] Documentation complete
- [ ] Continuous runner deployed (choose method above)
- [ ] First weekly report generated
- [ ] Dashboard displaying analytics

---

**Status:** Production-ready ✅  
**Deployed:** 2026-02-08 @ 4:30 PM  
**Version:** 1.0

For full documentation, see `ANALYTICS.md`
