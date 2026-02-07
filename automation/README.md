# 🏥 Jarvis Auto-Recovery System

**Self-healing infrastructure for Jarvis - auto-detect and fix failures without bothering Ross.**

## Quick Start

### Check Status
```bash
~/clawd/automation/manage-health.sh status
```

### View Dashboard
```bash
open ~/clawd/dashboard/health.html
```
Or visit: `file:///Users/clawdbot/clawd/dashboard/health.html`

### View Logs
```bash
~/clawd/automation/manage-health.sh logs
```

## What It Does

**Monitors (every 5 minutes):**
- ✅ Gateway process (clawdbot-gateway)
- ✅ Fitness tracker (port 3000)
- ✅ Hub dashboard (port 8080)
- ✅ Disk space (>10% free)
- ✅ Memory usage (<90%)
- ✅ Log files (<100MB)

**Auto-Fixes:**
- 🔄 Restarts crashed services
- 🧹 Cleans old logs when disk full
- 📝 Rotates large log files
- 🚨 Alerts Ross only after 3+ failures

## Common Commands

```bash
# Management
~/clawd/automation/manage-health.sh start      # Start daemon
~/clawd/automation/manage-health.sh stop       # Stop daemon
~/clawd/automation/manage-health.sh restart    # Restart daemon
~/clawd/automation/manage-health.sh status     # Check status
~/clawd/automation/manage-health.sh logs       # View logs

# Testing
~/clawd/automation/test-recovery.sh            # Run tests
python3 health-system.py --once                # Manual check

# Logs
tail -f ~/clawd/monitoring/health.log          # Watch health checks
tail -f ~/clawd/monitoring/recovery.log        # Watch recovery actions
tail -f ~/clawd/monitoring/alerts.log          # Watch alerts
```

## Files

| File | Purpose |
|------|---------|
| `health_monitor.py` | Health check daemon |
| `auto_recovery.py` | Recovery actions |
| `alert.py` | Alert system |
| `health-system.py` | Main orchestrator |
| `manage-health.sh` | Management script |
| `test-recovery.sh` | Test suite |
| `ERROR_RECOVERY.md` | Full documentation |

## Logs & State

All in `~/clawd/monitoring/`:
- `health.log` - Health check results
- `recovery.log` - Recovery actions
- `alerts.log` - Alert history
- `health-state.json` - Current state
- `recovery-state.json` - Recovery history
- `alert-state.json` - Alert cooldowns
- `alert-pending.json` - Pending alerts for Ross

## Safety Features

- 🔒 Rate limited (5 min between attempts)
- 🔢 Failure counting (3 strikes rule)
- ⏰ Alert cooldown (1 hour per service)
- 📝 Full audit logging
- 🛡️ Conservative recovery (only safe fixes)
- 🔄 PID tracking for safe restarts

## Alert Policy

**When alerts are sent:**
- ❌ Service fails 3+ times consecutively
- ⏰ At least 1 hour since last alert
- 🔧 Auto-recovery couldn't fix it

**When alerts are NOT sent:**
- ✅ Auto-recovery successfully fixed the issue
- 🕐 Within cooldown period
- 🔢 Less than 3 failures

## Integration with Main Agent

Add to `HEARTBEAT.md`:

```python
# Check for pending recovery alerts
import json
from pathlib import Path

alert_file = Path.home() / "clawd/monitoring/alert-pending.json"
if alert_file.exists():
    with open(alert_file) as f:
        alerts = json.load(f)
    
    for alert in alerts:
        # Send to Ross via Telegram
        send_message(alert['message'])
    
    # Clear after sending
    alert_file.unlink()
```

## Troubleshooting

**Service not running?**
```bash
launchctl load ~/Library/LaunchAgents/com.jarvis.health-system.plist
launchctl start com.jarvis.health-system
```

**Want to disable it?**
```bash
~/clawd/automation/manage-health.sh stop
# Or uninstall completely:
~/clawd/automation/manage-health.sh uninstall
```

**Check what went wrong?**
```bash
cat ~/clawd/monitoring/health-system.err
~/clawd/automation/manage-health.sh logs
```

## Full Documentation

See `ERROR_RECOVERY.md` for complete documentation including:
- Detailed recovery strategies
- Configuration options
- Testing procedures
- Future enhancements

---

**Built to keep Jarvis healthy and Ross happy! 🏥**
