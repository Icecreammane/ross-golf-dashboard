# Jarvis Auto-Recovery System

**Making Jarvis self-healing and reliable.**

## Overview

The Auto-Recovery System continuously monitors Jarvis's health and automatically fixes common failures without bothering Ross. It consists of three main components:

1. **Health Monitor** - Detects problems
2. **Auto-Recovery** - Fixes problems automatically
3. **Alert System** - Notifies Ross when auto-fix fails

## What It Monitors

### Services
- **Gateway** (clawdbot-gateway) - Core communication service
- **Fitness Tracker** (port 3000) - Flask app for fitness data
- **Hub Dashboard** (port 8080) - Central dashboard server

### System Resources
- **Disk Space** - Must be >10% free
- **Memory Usage** - Alerts when >90% used
- **Log Files** - Flags files >100MB

### Check Frequency
- Every **5 minutes** (continuous loop, not cron-based)
- Results logged to `~/clawd/monitoring/health.log`

## What It Fixes Automatically

### Service Restarts

| Problem | Auto-Fix Action |
|---------|----------------|
| Gateway down | `clawdbot gateway restart` |
| Fitness tracker down | Kill old process → restart Flask app |
| Hub down | Kill old process → restart hub-api.py |

### Resource Cleanup

| Problem | Auto-Fix Action |
|---------|----------------|
| Disk >90% full | Delete logs older than 30 days |
| Memory >90% used | Log top 10 memory consumers (for review) |
| Log files >100MB | Rotate and archive large logs |

### Safety Features

- **Rate limiting**: Won't retry same fix within 5 minutes
- **Conservative approach**: Only fixes obvious, safe issues
- **Full logging**: Every action is timestamped and recorded
- **No data deletion**: Logs are rotated/archived, not deleted permanently

## When It Alerts Ross

The system will **NOT** spam Ross with notifications. Alerts are sent only when:

1. **Auto-recovery fails 3+ consecutive times** for the same service
2. **At least 1 hour** has passed since the last alert for that service
3. The problem persists despite multiple fix attempts

### Alert Format

```
🚨 System issue: [service_name]

Tried fixing [X] times, still failing.

Check logs:
/Users/clawdbot/clawd/monitoring/recovery.log

Service may need manual intervention.
```

Alerts are queued to `~/clawd/monitoring/alert-pending.json` for the main agent to send via Telegram.

## Log Files

All logs are in `~/clawd/monitoring/`:

- **health.log** - Health check results
- **recovery.log** - Recovery actions taken
- **alerts.log** - Alert history
- **health-state.json** - Current system state
- **recovery-state.json** - Recovery history and failure counts
- **alert-state.json** - Alert cooldown tracking
- **alert-pending.json** - Queued alerts for Ross

## How to Use

### Start the Health System

```bash
cd ~/clawd/automation
python3 health-system.py
```

### Run as Background Service (Recommended)

Create a LaunchAgent (macOS) to auto-start on login:

```bash
# Create the service file
cat > ~/Library/LaunchAgents/com.jarvis.health-system.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jarvis.health-system</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/clawdbot/clawd/automation/health-system.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/clawdbot/clawd</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/clawdbot/clawd/monitoring/health-system.out</string>
    <key>StandardErrorPath</key>
    <string>/Users/clawdbot/clawd/monitoring/health-system.err</string>
</dict>
</plist>
EOF

# Load and start the service
launchctl load ~/Library/LaunchAgents/com.jarvis.health-system.plist
launchctl start com.jarvis.health-system
```

### Check Status

```bash
# Check if running
launchctl list | grep jarvis.health

# View recent logs
tail -f ~/clawd/monitoring/health.log

# View recovery actions
tail -f ~/clawd/monitoring/recovery.log

# Check current state
cat ~/clawd/monitoring/health-state.json | python3 -m json.tool
```

### Manual Operations

```bash
# Run one check cycle (no loop)
python3 health-system.py --once

# Change check interval (in seconds)
python3 health-system.py --interval 180  # Check every 3 minutes

# Test individual components
python3 health-monitor.py  # Health checks only
python3 auto-recovery.py   # Recovery actions only
python3 alert.py           # Alert system only
```

## Recovery Dashboard

A web-based dashboard is available at:

```
file:///Users/clawdbot/clawd/dashboard/health.html
```

**Features:**
- Real-time system status (green/yellow/red indicators)
- Recent recovery actions history
- Quick action buttons:
  - 🔍 **Check Now** - Trigger immediate health check
  - 🔄 **Restart All** - Restart all monitored services
  - 🧹 **Clear Logs** - Delete old log files
  - 📋 **View Logs** - Open log files

The dashboard auto-refreshes every 30 seconds.

## How to Disable Auto-Recovery

If the system goes rogue or you need to disable it temporarily:

### Option 1: Stop the Service

```bash
# If running as LaunchAgent
launchctl stop com.jarvis.health-system

# Or kill the process
pkill -f health-system.py
```

### Option 2: Disable Specific Recoveries

Edit `~/clawd/automation/auto-recovery.py` and comment out recovery functions:

```python
# Disable gateway auto-restart
def recover_gateway(self, check_result):
    recovery_logger.info("Gateway recovery DISABLED")
    return False  # Don't attempt recovery
```

### Option 3: Emergency Kill Switch

```bash
# Unload the service completely
launchctl unload ~/Library/LaunchAgents/com.jarvis.health-system.plist

# Delete the service file
rm ~/Library/LaunchAgents/com.jarvis.health-system.plist
```

## Troubleshooting

### Problem: Health checks not running

**Check:**
```bash
ps aux | grep health-system.py
```

**Fix:**
```bash
launchctl start com.jarvis.health-system
```

### Problem: Recovery actions failing

**Check logs:**
```bash
tail -50 ~/clawd/monitoring/recovery.log
```

**Common issues:**
- Permission errors → Run as clawdbot user
- Missing dependencies → Install psutil: `pip3 install psutil`
- Port conflicts → Check if services are already running

### Problem: Too many alerts

**Adjust thresholds** in `~/clawd/automation/alert.py`:

```python
FAILURE_THRESHOLD = 5  # Default: 3
ALERT_COOLDOWN_HOURS = 2  # Default: 1
```

### Problem: Logs growing too large

**Manual cleanup:**
```bash
find ~/clawd/monitoring -name "*.log" -mtime +7 -delete
```

**Automated cleanup:**
The system automatically rotates logs >100MB.

### Problem: Health system consuming too many resources

**Increase check interval:**
```bash
# Edit LaunchAgent to add interval argument
python3 health-system.py --interval 600  # 10 minutes
```

Or edit the plist file and add `--interval` to ProgramArguments.

## Architecture

```
┌─────────────────────────────────────────────────┐
│         health-system.py (Main Daemon)          │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────┐│
│  │ Health       │→→│ Auto         │→→│ Alert  ││
│  │ Monitor      │  │ Recovery     │  │ System ││
│  └──────────────┘  └──────────────┘  └────────┘│
│         ↓                 ↓                ↓    │
│    health.log       recovery.log      alerts.log│
└─────────────────────────────────────────────────┘
         ↓                 ↓                ↓
    health-state.json  recovery-state.json  alert-pending.json
                                                   ↓
                                          Main Agent → Telegram
```

## Safety Constraints

The system is designed to be **conservative** and **safe**:

✅ **Will do:**
- Restart services that are clearly down
- Clean old logs (30+ days)
- Rotate large log files
- Log all actions for audit

❌ **Will NOT do:**
- Delete important files
- Restart during active builds (future enhancement)
- Spam Ross with alerts (rate limited)
- Make uncertain changes (logs and notifies instead)

## Testing

### Test Gateway Recovery

```bash
# Kill gateway
pkill -f clawdbot-gateway

# Wait for next check cycle (up to 5 minutes)
# Or trigger manual check:
python3 health-system.py --once

# Verify it restarted
ps aux | grep clawdbot-gateway
```

### Test Disk Cleanup

```bash
# Create old log files
touch -t 202301010000 ~/clawd/logs/old-test.log

# Trigger recovery
python3 health-system.py --once

# Verify cleanup
ls ~/clawd/logs/old-test.log  # Should not exist
```

### Test Alert System

```bash
# Simulate 3 failures
# (Manually edit recovery-state.json to set failure_counts)
cat > ~/clawd/monitoring/recovery-state.json << 'EOF'
{
  "failure_counts": {
    "gateway": 3
  }
}
EOF

# Check for pending alerts
cat ~/clawd/monitoring/alert-pending.json
```

## Integration with Main Agent

The main agent (Jarvis) can check for pending alerts during heartbeats:

```python
# In HEARTBEAT.md or heartbeat handler
import json
from pathlib import Path

alert_file = Path.home() / "clawd/monitoring/alert-pending.json"
if alert_file.exists():
    with open(alert_file) as f:
        alerts = json.load(f)
    
    for alert in alerts:
        # Send to Ross via Telegram
        send_message(alert['message'])
    
    # Clear pending alerts
    alert_file.unlink()
```

## Future Enhancements

- [ ] Detect active builds before restarting services
- [ ] Web API for dashboard actions
- [ ] Configurable recovery strategies per service
- [ ] Health metrics graphing
- [ ] Integration with external monitoring (Prometheus, etc.)
- [ ] Predictive failure detection (ML-based)
- [ ] Self-upgrade capability

## Support

If you encounter issues or have questions:

1. Check logs in `~/clawd/monitoring/`
2. Review this documentation
3. Ask Jarvis: "Check health system status"
4. Manually inspect: `python3 health-system.py --once`

---

**Built with ❤️ to keep Jarvis healthy and Ross happy.**
