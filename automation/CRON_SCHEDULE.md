# Jarvis Automation - Cron Schedule

**Last Updated:** 2026-01-30  
**Status:** Production Ready

## Overview

This system automates Jarvis's recurring tasks using cron jobs. All jobs run on Ross's Mac mini under the user crontab (not system crontab).

## Installation

```bash
cd ~/clawd/automation
bash setup-cron.sh
```

The setup script is **idempotent** — safe to run multiple times. It will:
- Backup your existing crontab
- Remove old Jarvis automation entries
- Install all jobs
- Verify the installation

## Schedule

| Time    | Job                  | Description                          | Timeout |
|---------|----------------------|--------------------------------------|---------|
| 7:30am  | morning-brief        | Generates morning brief with voice   | 5 min   |
| 9:00am  | deal-flow-update     | Updates deal flow pipeline           | 10 min  |
| 10:00am | nba-update           | Refreshes NBA Top 50 rankings        | 5 min   |
| 12:00pm | health-check         | System health diagnostics            | 1 min   |
| 8:00pm  | evening-checkin      | Triggers evening check-in            | 1 min   |
| 11:00pm | overnight-research   | Overnight builds & maintenance       | 30 min  |

## Job Details

### Morning Brief (7:30am)
**Script:** `~/clawd/scripts/generate-morning-brief-voice.py`  
**Purpose:** Generates daily morning brief with voice narration  
**Output:** Morning brief audio file  
**Log:** `~/clawd/logs/cron/morning-brief-YYYY-MM-DD.log`

This kicks off Ross's day with a comprehensive briefing including:
- Weather and calendar
- NBA updates
- Deal flow status
- Important notifications

### Deal Flow Update (9:00am)
**Script:** `~/clawd/revenue/deal-flow/scraper.py`  
**Purpose:** Scrapes and updates deal flow pipeline data  
**Output:** Updated deal flow database  
**Log:** `~/clawd/logs/cron/deal-flow-update-YYYY-MM-DD.log`

Refreshes the entire deal flow pipeline with latest data from sources.

### NBA Update (10:00am)
**Script:** `~/clawd/nba/update_top_50.sh`  
**Purpose:** Updates NBA Top 50 player rankings  
**Output:** Updated NBA rankings file  
**Log:** `~/clawd/logs/cron/nba-update-YYYY-MM-DD.log`

Note: This runs daily but only processes data on game days.

### Health Check (12:00pm)
**Script:** `~/clawd/automation/jobs/health-check.sh`  
**Purpose:** System diagnostics and log cleanup  
**Checks:**
- Disk space
- Memory usage
- Load average
- Clawdbot process status
- Log directory size

**Actions:**
- Cleans logs older than 30 days
- Reports any issues

**Log:** `~/clawd/logs/cron/health-check-YYYY-MM-DD.log`

### Evening Check-in (8:00pm)
**Script:** `~/clawd/automation/jobs/evening-checkin.sh`  
**Purpose:** Creates flag for main agent to process during heartbeat  
**Output:** Flag file at `~/clawd/tmp/evening-checkin-pending`  
**Log:** `~/clawd/logs/cron/evening-checkin-YYYY-MM-DD.log`

The main agent checks for this flag during heartbeats and performs evening tasks.

### Overnight Research (11:00pm)
**Script:** `~/clawd/automation/jobs/overnight-research.sh`  
**Purpose:** Maintenance and background research  
**Actions:**
- Git status check
- Pull latest changes
- Clean temp files
- Archive old memory files (>90 days)
- Creates flag for research tasks

**Log:** `~/clawd/logs/cron/overnight-research-YYYY-MM-DD.log`

**Note:** No notifications during sleep hours (11pm-7am per QUALITY STANDARDS).

## Management Commands

All management is done via `cron-manager.py`:

```bash
# List all jobs
python3 ~/clawd/automation/cron-manager.py list

# Show detailed status
python3 ~/clawd/automation/cron-manager.py status

# View logs for a job
python3 ~/clawd/automation/cron-manager.py logs morning-brief
python3 ~/clawd/automation/cron-manager.py logs morning-brief -n 100  # Last 100 lines

# Test a job manually
python3 ~/clawd/automation/cron-manager.py test health-check

# Enable a job
python3 ~/clawd/automation/cron-manager.py enable morning-brief

# Disable a job
python3 ~/clawd/automation/cron-manager.py disable nba-update
```

## Modifying the Schedule

### Option 1: Use cron-manager.py (Recommended)
The manager preserves manual edits and provides safe enable/disable.

### Option 2: Edit Crontab Directly
```bash
crontab -e
```

Find lines with `# Jarvis Automation` comment and modify the schedule.

**Cron Schedule Format:**
```
* * * * *
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, 0=Sunday)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

**Examples:**
- `30 7 * * *` = 7:30am every day
- `0 9 * * 1-5` = 9:00am Monday-Friday
- `*/30 * * * *` = Every 30 minutes
- `0 */2 * * *` = Every 2 hours

### Option 3: Re-run Setup
Modify `setup-cron.sh` and run it again. It will remove old entries and install fresh.

## Logging

All jobs log to: `~/clawd/logs/cron/<job-name>-YYYY-MM-DD.log`

**Log Format:**
```
[YYYY-MM-DD HH:MM:SS] Message
```

**Log Retention:**
- Logs are kept for 30 days
- Cleaned automatically by health-check job
- Manual cleanup: `find ~/clawd/logs/cron -name "*.log" -mtime +30 -delete`

**View Logs:**
```bash
# Tail live log
tail -f ~/clawd/logs/cron/morning-brief-2026-01-30.log

# View today's logs for all jobs
ls -lh ~/clawd/logs/cron/*-$(date +%Y-%m-%d).log

# Search logs
grep ERROR ~/clawd/logs/cron/*.log
```

## Troubleshooting

### Job Not Running
1. Check if cron is enabled:
   ```bash
   crontab -l | grep "Jarvis Automation"
   ```

2. Check System Preferences → Security & Privacy → Full Disk Access
   - Ensure `/usr/sbin/cron` has access

3. View system logs:
   ```bash
   log show --predicate 'process == "cron"' --last 1h
   ```

### Job Running But Failing
1. Check the job's log file
2. Test manually:
   ```bash
   python3 ~/clawd/automation/cron-manager.py test <job-name>
   ```

3. Verify script paths and permissions:
   ```bash
   ls -lh ~/clawd/automation/jobs/
   ```

### Environment Issues
Cron runs with minimal environment. Jobs set:
- `PATH` includes common bin directories
- `HOME` is set correctly
- Working directory changes to script location when needed

If a job needs additional env vars, add them to the wrapper script.

### Time Zone Issues
Cron uses system time zone. Verify:
```bash
date
# Should show: America/Chicago
```

### Timeout Issues
If a job times out:
1. Check the log for timeout message
2. Increase timeout in the wrapper script
3. Optimize the underlying script

## Testing

Before relying on automation, test each job:

```bash
# Test all jobs
for job in morning-brief deal-flow-update nba-update health-check evening-checkin overnight-research; do
    echo "Testing $job..."
    python3 ~/clawd/automation/cron-manager.py test $job
    echo ""
done
```

## Backup & Recovery

### Backup Crontab
```bash
crontab -l > ~/clawd/automation/backups/crontab-backup-$(date +%Y%m%d).txt
```

### Restore Crontab
```bash
crontab ~/clawd/automation/backups/crontab-backup-YYYYMMDD.txt
```

### Backups Location
`~/clawd/automation/backups/`

Setup script creates automatic backups before making changes.

## Uninstall

Remove all Jarvis automation jobs:

```bash
crontab -l | grep -v "# Jarvis Automation" | crontab -
```

Or disable individual jobs:
```bash
python3 ~/clawd/automation/cron-manager.py disable <job-name>
```

## Security Notes

- All jobs run as the `clawdbot` user
- No external network access required (except deal-flow-update)
- Logs may contain sensitive info — stored locally only
- Scripts use `set -euo pipefail` for safety
- Timeout protection on all long-running jobs

## Integration with Main Agent

The automation system integrates with Jarvis's main agent via:

1. **Flag Files:**
   - Evening check-in creates: `~/clawd/tmp/evening-checkin-pending`
   - Overnight research creates: `~/clawd/tmp/overnight-research-pending`
   - Main agent checks these during heartbeats

2. **Logs:**
   - Main agent can read logs to report status
   - Use `cron-manager.py logs` command

3. **Manual Triggers:**
   - Main agent can use `cron-manager.py test` to run jobs on-demand

## Performance

- Each job wrapper adds ~10ms overhead
- Total daily cron time: ~20-25 minutes across all jobs
- CPU impact: Negligible (jobs are I/O bound)
- Disk usage: ~50MB logs per month

## Future Enhancements

Potential additions:
- [ ] Slack/email notifications on failures
- [ ] Job dependency chains
- [ ] Conditional execution (e.g., NBA only on game days)
- [ ] Web dashboard for monitoring
- [ ] Metrics collection (execution time, success rate)

## Support

Questions or issues:
1. Check this documentation
2. Test manually with `cron-manager.py test <job>`
3. Review logs in `~/clawd/logs/cron/`
4. Ask Ross or main Jarvis agent

---

**Maintained by:** Jarvis (automated system)  
**Repository:** `~/clawd/automation/`
