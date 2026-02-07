# Installation Instructions

## Prerequisites

✅ **Already met** - Your system has:
- macOS (Darwin)
- Python 3
- Bash
- User crontab access
- Required scripts in place

## Installation (2 minutes)

### Step 1: Install the Cron Jobs

```bash
cd ~/clawd/automation
bash setup-cron.sh
```

You'll see:
- Verification of all scripts
- Backup of existing crontab
- Installation of 6 automated jobs
- Confirmation message

### Step 2: Verify Installation

```bash
python3 cron-manager.py list
```

Expected output:
```
Jarvis Automated Jobs
======================================================================
Job                  Schedule        Status     Description
----------------------------------------------------------------------
morning-brief        30 7 * * *      ✓ Enabled  Morning brief generation...
deal-flow-update     0 9 * * *       ✓ Enabled  Deal flow pipeline update
nba-update           0 10 * * *      ✓ Enabled  NBA rankings refresh
health-check         0 12 * * *      ✓ Enabled  System health diagnostics
evening-checkin      0 20 * * *      ✓ Enabled  Evening check-in trigger
overnight-research   0 23 * * *      ✓ Enabled  Overnight builds...
```

### Step 3: Test a Job (Optional)

```bash
python3 cron-manager.py test health-check
```

This runs a quick system health check to verify everything works.

## What Happens Next?

Tomorrow morning at 7:30am, your first automated job runs:
- Morning brief will be generated with voice
- You'll find the log at: `~/clawd/logs/cron/morning-brief-YYYY-MM-DD.log`

## Monitoring

### Check Job Status
```bash
python3 cron-manager.py status
```

### View Recent Logs
```bash
python3 cron-manager.py logs morning-brief
```

### List All Today's Logs
```bash
ls -lh ~/clawd/logs/cron/*-$(date +%Y-%m-%d).log
```

## Managing Jobs

### Disable a Job
```bash
python3 cron-manager.py disable nba-update
```

### Re-enable a Job
```bash
python3 cron-manager.py enable nba-update
```

### Test a Job Manually
```bash
python3 cron-manager.py test morning-brief
```

## Troubleshooting

### Jobs Not Running?

1. **Check if installed:**
   ```bash
   crontab -l | grep "Jarvis"
   ```

2. **Check System Preferences:**
   - Open System Preferences
   - Go to Security & Privacy
   - Privacy tab → Full Disk Access
   - Ensure `/usr/sbin/cron` has access

3. **Check logs:**
   ```bash
   python3 cron-manager.py logs <job-name>
   ```

### Need More Help?

- Read `CRON_SCHEDULE.md` for comprehensive guide
- Check `TEST_RESULTS.md` for test details
- Ask Jarvis: "Check cron status"

## Uninstalling

If you need to remove all automated jobs:

```bash
crontab -l | grep -v "# Jarvis Automation" | crontab -
```

Or use the manager:
```bash
for job in morning-brief deal-flow-update nba-update health-check evening-checkin overnight-research; do
    python3 cron-manager.py disable $job
done
```

## Backup & Recovery

Your original crontab is backed up automatically at:
```
~/clawd/automation/backups/crontab-backup-YYYYMMDD-HHMMSS.txt
```

To restore:
```bash
crontab ~/clawd/automation/backups/crontab-backup-YYYYMMDD-HHMMSS.txt
```

## Support

Questions? Ask Jarvis:
- "What cron jobs are running?"
- "Show me cron logs"
- "Test the morning brief job"
- "Disable NBA updates"

---

**Ready to install?** Run: `bash setup-cron.sh`
