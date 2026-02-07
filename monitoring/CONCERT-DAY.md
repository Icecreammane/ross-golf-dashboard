# 🎵 Concert Day Quick Reference

## Before You Leave (7:30 AM)

```bash
cd ~/clawd/monitoring

# 1. Quick status check
./status.sh

# 2. Install cron if not already done
./setup-cron.sh

# 3. Test the system
./test-system.sh

# 4. Clear old state for fresh start
rm -f state/*.json

# 5. Force one check to verify
./run-checks.sh --force
```

## While You're Away

The system will:
- ✅ Check every hour from 7am-11pm
- ✅ Skip checks during concert (7pm-midnight)
- ✅ Send Telegram alerts ONLY if urgent
- ✅ Log everything to `logs/alerts.log`

## What Gets Monitored

| Monitor | Checks | Alert When |
|---------|--------|------------|
| 📧 Email | Inbox via Himalaya | VIP sender or urgent keywords |
| ⚙️ Gateway | Service status | Down >5 minutes |
| 💾 Disk | Usage % | >90% full |
| 💰 Costs | API spend | >$10/hour |
| 🤖 Subagents | Session health | Stale sessions detected |

## Alert Examples

**What you WILL get:**
- "🚨 Urgent Email: 2 urgent email(s)"
- "🔴 Gateway down for 10 minutes"
- "⚠️ Disk usage at 92%"

**What you WON'T get:**
- Newsletters
- Regular notifications
- Non-urgent emails
- Status updates ("all good!")

## If You Need to Check In

```bash
# Quick status
cd ~/clawd/monitoring && ./status.sh

# View recent logs
tail -20 ~/clawd/monitoring/logs/alerts.log

# Force a check (even during concert hours)
cd ~/clawd/monitoring && ./run-checks.sh --force

# View dashboard
cd ~/clawd/monitoring && python3 -m http.server 8080
# Open: http://localhost:8080/monitoring.html
```

## Emergency: Disable Monitoring

```bash
# Remove cron job
crontab -l | grep -v run-checks.sh | crontab -

# Or just stop the next run
touch ~/clawd/monitoring/PAUSED
```

## When You're Back

```bash
# Review what happened
cat ~/clawd/monitoring/logs/alerts.log

# Check state files
ls -lh ~/clawd/monitoring/state/

# Optionally remove cron
crontab -l | grep -v run-checks.sh | crontab -
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No alerts received | Check `logs/alerts.log` - monitors may have errored |
| Too many alerts | Increase deduplication window in `send-alerts.py` |
| Email monitor failing | Himalaya not configured - see `monitor-email.py` |
| Cron not running | Check: `crontab -l` and system logs |

## Cost Estimate

Running 16 hours (7am-11pm):
- 16 checks × Python scripts (no LLM)
- Expected cost: **$0.00** (local scripts only)
- Alert sending uses existing Clawdbot (minimal)

---

**Have a great concert! The system's got your back.** 🎸
