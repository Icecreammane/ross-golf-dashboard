# Concert Mode Monitoring

Proactive monitoring system that watches important things while you're away and only alerts when something needs attention.

## What It Monitors

- **📧 Email**: Urgent messages via Himalaya CLI (VIP senders, urgent keywords)
- **⚙️ System Health**: Gateway status, disk usage, API costs, subagents
- **🔔 Smart Alerts**: Consolidated alerts sent only when genuinely urgent

## Files

```
monitoring/
├── monitor-email.py       # Email inbox checker
├── monitor-health.py      # System health checker
├── send-alerts.py         # Alert aggregator (calls other monitors)
├── monitoring.html        # Real-time dashboard
├── run-checks.sh          # Wrapper script for cron
├── setup-cron.sh          # Install cron job
├── state/                 # State tracking (auto-created)
├── logs/                  # Alert logs (auto-created)
└── README.md              # This file
```

## Quick Start

### 1. Test the Monitors

```bash
cd monitoring

# Test email monitor
python3 monitor-email.py

# Test health monitor
python3 monitor-health.py

# Test full alert pipeline
python3 send-alerts.py
```

### 2. Install Cron Job

```bash
cd monitoring
./setup-cron.sh
```

This installs a cron job that runs every hour from 7am-11pm, skipping 7pm-midnight (concert time).

### 3. View Dashboard

```bash
# Serve dashboard locally
cd monitoring
python3 -m http.server 8080

# Then open: http://localhost:8080/monitoring.html
```

## Configuration

### Email Monitor (`monitor-email.py`)

Edit the following variables to customize:

```python
# Urgent keywords that flag importance
URGENT_KEYWORDS = ['urgent', 'asap', 'emergency', ...]

# VIP senders (add emails of important people)
VIP_SENDERS = ['bigmeatyclawd@gmail.com', ...]

# Spam/newsletter indicators to ignore
IGNORE_KEYWORDS = ['unsubscribe', 'newsletter', ...]
```

### Health Monitor (`monitor-health.py`)

```python
COST_THRESHOLD = 10.0  # Alert if costs exceed $10/hour
DISK_THRESHOLD = 90    # Alert if disk usage >90%
DOWN_THRESHOLD = 300   # Alert if down >5 minutes
```

### Alert Timing

Edit `run-checks.sh` to change concert hours (default: 7pm-midnight):

```bash
if [ $HOUR -ge 19 ]; then  # Skip 19:00 (7pm) and later
```

## How It Works

### Conservative Alerting

- **Deduplication**: Won't alert twice for the same issue within 1 hour
- **Threshold**: Services must be down >5 minutes before alerting
- **Filtering**: Newsletters and spam automatically filtered out
- **Consolidation**: Multiple issues grouped into one message

### Alert Flow

1. **Cron runs** `run-checks.sh` every hour
2. **Script calls** `send-alerts.py`
3. **Aggregator runs** all individual monitors
4. **Monitors return** JSON with status and alerts
5. **Aggregator decides** if alerts are urgent and new
6. **If urgent**: Sends ONE consolidated message via Telegram
7. **Everything logged** to `logs/alerts.log`

### State Tracking

- `state/email-state.json`: Last check time, seen email IDs
- `state/health-state.json`: Service down times
- `state/alert-state.json`: Recent alerts (for deduplication)

## Manual Operations

### Force a Check (Ignore Concert Hours)

```bash
cd monitoring
./run-checks.sh --force
```

### View Recent Logs

```bash
tail -f monitoring/logs/alerts.log
```

### Remove Cron Job

```bash
crontab -l | grep -v run-checks.sh | crontab -
```

### Reset State (Fresh Start)

```bash
rm -rf monitoring/state/*.json
```

## Troubleshooting

### No alerts during testing?

- Check `logs/alerts.log` for what's happening
- Run monitors individually to see their output
- State files prevent duplicate alerts - delete them for fresh testing

### Himalaya not found?

The email monitor needs Himalaya CLI installed. If you don't have it:
```bash
brew install himalaya  # macOS
```

Or comment out email monitoring temporarily.

### Cron not running?

```bash
# View cron logs (macOS)
log show --predicate 'process == "cron"' --last 1h

# Or check system log
grep CRON /var/log/system.log
```

## Concert Day Checklist

Before you leave:

1. ✅ Test monitors: `python3 send-alerts.py`
2. ✅ Verify cron: `crontab -l`
3. ✅ Check dashboard: Open `monitoring.html`
4. ✅ Clear old state: `rm -rf monitoring/state/*.json`
5. ✅ Watch logs: `tail -f monitoring/logs/alerts.log` (verify first check runs)

## Cost Estimate

Running every hour for 16 hours (7am-11pm):
- 16 checks × minimal API usage
- Estimated: < $0.50/day
- Using Python (no LLM calls) keeps costs near zero

## Success Criteria

✅ Checks run automatically every hour  
✅ Alerts only when genuinely urgent  
✅ Clear, actionable messages  
✅ Dashboard shows real-time status  
✅ Zero false positives during testing  

## Support

If something breaks:
1. Check `logs/alerts.log`
2. Run monitors manually to see errors
3. Disable cron if needed: `crontab -l | grep -v run-checks.sh | crontab -`

Have a great concert! 🎵
