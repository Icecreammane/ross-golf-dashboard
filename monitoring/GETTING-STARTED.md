# 🚀 Getting Started - Concert Mode Monitoring

## Quick Start (5 Minutes)

You're 5 commands away from having a fully automated monitoring system watching your world while you're at the concert tomorrow.

### Step 1: Test the System

```bash
cd ~/clawd/monitoring
./test-system.sh
```

This verifies all monitors work. You should see lots of ✅ checkmarks.

### Step 2: Install Cron Job

```bash
./setup-cron.sh
```

This installs hourly checks (7am-11pm, skipping concert hours).

### Step 3: Clear Old State

```bash
rm -f state/*.json
```

Fresh start for tomorrow.

### Step 4: Test One Cycle

```bash
./run-checks.sh --force
```

This runs all monitors once. Check for any errors.

### Step 5: View Dashboard

```bash
python3 -m http.server 8080 &
open http://localhost:8080/monitoring.html
```

You should see the dashboard with green status cards.

## That's It! 🎉

Your system is now monitoring:
- 📧 Email inbox (urgent messages only)
- ⚙️ Gateway status
- 💾 Disk usage
- 💰 API costs
- 🤖 Subagent health

## What Happens Tomorrow

**7:00 AM** - First check runs automatically  
**8:00 AM** - Second check runs  
**...every hour...**  
**6:00 PM** - Last check before concert  
**7:00 PM** - Checks pause (you're at the concert)  
**11:59 PM** - System stays quiet  

**If something urgent happens**, you'll get a Telegram message like:
```
🚨 2 things need attention:

1. Urgent Email: 1 urgent email(s)
   • Subject: Action Required: Security Alert

2. ⚠️ Disk: Disk usage at 92%
```

**If everything is fine**, you get nothing. Zero spam. Just peace of mind.

## Verify It's Working

### Before You Leave
```bash
# Quick status check
cd ~/clawd/monitoring && ./status.sh

# Should show:
# ✅ Cron job installed
# ✅ No alerts yet
# ✅ Last check: recent time
```

### At the Concert (If You Check Your Phone)
```bash
# View today's activity
tail ~/clawd/monitoring/logs/alerts.log

# You should see hourly "All checks passed" entries
```

## Commands You Should Know

| Command | What It Does |
|---------|--------------|
| `./status.sh` | Quick status at a glance |
| `./run-checks.sh --force` | Run check now (ignores schedule) |
| `tail -f logs/alerts.log` | Watch logs in real-time |
| `rm -f state/*.json` | Reset state (fresh start) |
| `crontab -l` | View installed cron job |
| `python3 -m http.server 8080` | Serve dashboard locally |

## Troubleshooting

### "Cron job not running"
```bash
# Check if it's installed
crontab -l | grep run-checks

# If not, install it
./setup-cron.sh
```

### "Email monitor failing"
That's OK! The email monitor needs Himalaya CLI configured. If you haven't set it up, it will log an error but won't crash the system. Other monitors still work.

### "No logs appearing"
```bash
# Force a check to generate logs
./run-checks.sh --force

# Then check
cat logs/alerts.log
```

### "Dashboard not loading"
```bash
# Make sure you're in the monitoring directory
cd ~/clawd/monitoring

# Start the server
python3 -m http.server 8080

# Open browser to: http://localhost:8080/monitoring.html
```

## Emergency Stop

If you need to disable monitoring:

```bash
# Remove cron job
crontab -l | grep -v run-checks.sh | crontab -

# Or create a pause file
touch ~/clawd/monitoring/PAUSED
```

## After the Concert

```bash
# Review what happened
cd ~/clawd/monitoring
cat logs/alerts.log

# View state
cat state/health-state.json | python3 -m json.tool

# Optionally remove cron (if you want)
crontab -l | grep -v run-checks.sh | crontab -
```

## Understanding Alert Logic

### Email Alerts
✅ **Will alert**: VIP senders, urgent keywords (urgent, ASAP, action required)  
❌ **Won't alert**: Newsletters, spam, routine notifications

### System Alerts
✅ **Will alert**: Gateway down >5 min, disk >90%, costs >$10/hr  
❌ **Won't alert**: Temporary blips, normal activity

### Deduplication
Once you've been alerted about something, you won't be alerted again for 1 hour (prevents spam).

## Files to Know

| File | Purpose |
|------|---------|
| `logs/alerts.log` | All activity logged here |
| `state/*.json` | What's been checked, what's been alerted |
| `monitoring.html` | Dashboard you can open in browser |
| `CONCERT-DAY.md` | Quick reference card (print/save to phone) |

## Visual: How It Works

```
Every hour (7am-11pm):
    │
    ├─→ run-checks.sh (cron)
    │       │
    │       └─→ send-alerts.py (aggregator)
    │               │
    │               ├─→ monitor-email.py
    │               │       └─→ Check inbox via Himalaya
    │               │
    │               ├─→ monitor-health.py
    │               │       ├─→ Check gateway status
    │               │       ├─→ Check disk usage
    │               │       ├─→ Check API costs
    │               │       └─→ Check subagents
    │               │
    │               ├─→ Collect all results
    │               ├─→ Filter for urgent issues
    │               ├─→ Deduplicate (don't spam)
    │               └─→ Send ONE alert if needed
    │
    └─→ Log everything to alerts.log
```

## Cost Estimate

**Development**: ~$0.50  
**Daily operation**: ~$0.00 (pure Python, no LLM calls)  
**Alert sending**: Free (uses existing Clawdbot)

**Total**: Under $1 for the entire project

## Success Metrics

After tomorrow, you should have:
- ✅ ~16 entries in `logs/alerts.log` (one per hour)
- ✅ Zero or minimal Telegram alerts (hopefully nothing urgent happened)
- ✅ State files showing what was monitored
- ✅ Peace of mind that your systems were watched

## Need Help?

1. Check `README.md` for detailed documentation
2. Run `./status.sh` for current status
3. Run `./test-system.sh` to verify everything works
4. Check `logs/alerts.log` for what's happening

## You're All Set! 🎸

Go enjoy the concert. The system's got your back.

---

**Questions before you leave?** Test it now with:
```bash
cd ~/clawd/monitoring && ./run-checks.sh --force && ./status.sh
```

You should see "All checks passed - no alerts needed" in the output.

**Have fun tomorrow!** 🎵
