# Mission Control Dashboard

**Real-time visibility into Jarvis operations**

## Overview

Mission Control is your central hub for monitoring what Jarvis is doing, where money is going, and what's running. It solves the persistent memory problem and provides complete operational transparency.

## Quick Start

### Start Mission Control

```bash
cd /Users/clawdbot/clawd/mission_control
python3 app.py
```

Then visit: **http://localhost:8080/mission-control**

### What You'll See

- 🟢 **Live Services** - Status of all running services
- 💰 **Cost Dashboard** - Real-time spend tracking
- 🚀 **Active Builds** - What's being built right now
- 📊 **System Health** - Disk, memory, gateway status
- 💪 **Confidence Tracker** - Win streaks and patterns
- 🔗 **Quick Links** - Jump to important dashboards

## Features

### 1. Live Action Tracker

Every tool call Jarvis makes is logged with:
- **Tool used** (exec, read, write, web_fetch, etc.)
- **Action taken** (command, file read, web fetch URL)
- **Result** (success/error)
- **Cost estimate** (calculated per token)
- **Timestamp**

**Log file:** `/Users/clawdbot/clawd/logs/action-tracker.jsonl`

**Filters:**
- All actions
- High-cost operations (>$0.01)
- Errors only

### 2. Cost Tracking

Real-time cost visibility:
- **Today's spend** - Current daily total
- **This week** - 7-day rolling total
- **Projected monthly** - Based on daily average
- **Top operations** - Most expensive actions today
- **Daemon savings** - Money saved by automation

**Color coding:**
- 🟢 Green: <$10/day, <$50/week
- 🟡 Yellow: $10-40/day, $50-250/week
- 🔴 Red: >$40/day, >$250/week

### 3. Persistent Memory Fix

**The Problem:** Jarvis wakes up with amnesia every session.

**The Solution:** Auto-Context Loader

#### Auto-Context Loader

Runs automatically at session start (or manually):

```bash
python3 /Users/clawdbot/clawd/scripts/auto_context.py
```

**What it loads:**
1. `SESSION_SUMMARY.md` - Last session state
2. `memory/YYYY-MM-DD.md` - Today + yesterday
3. `MEMORY.md` - Long-term memory (main session only)
4. Memory index - Searchable topic map
5. Active builds - Recent BUILD_*.md files
6. Live services - What's running now

**Output:** Context summary showing what was loaded and key facts to remember

**Integration:** Add to AGENTS.md startup checklist or session init script

#### Memory Self-Audit

Track when Jarvis asks questions it should already know:

```python
from scripts.auto_context import AutoContextLoader
loader = AutoContextLoader()
loader.should_have_known("What's the Lean URL?", topic="lean")
```

Logs to: `/Users/clawdbot/clawd/logs/memory-audit.log`

### 4. Confidence Framework

Tracks wins, patterns, and confidence over time.

#### Running the Tracker

```bash
python3 /Users/clawdbot/clawd/scripts/confidence_tracker.py
```

#### What It Tracks

**Wins:**
- Completed builds (BUILD_*.md files)
- Git commits (shipped code)
- Deployments (live URLs)
- Manual wins (logged via API)

**Metrics:**
- **Confidence Score** - 1-10 based on recent activity
- **Stack Count** - Consecutive wins (resets after breaks)
- **Trend** - Week-over-week change
- **Last Win** - Most recent accomplishment

**Patterns:**
- Best day of week for shipping
- Most productive time of day
- Confidence peaks (when do wins cluster?)
- Activity correlation (building vs other activities)

#### Logging Wins

Manual logging:

```python
from scripts.confidence_tracker import ConfidenceTracker
tracker = ConfidenceTracker()
tracker.log_win("Deployed Lean to production", category="deployment")
```

**Auto-detection:** Tracker scans BUILD_*.md files, git commits, and SESSION_SUMMARY.md

#### Dashboard Widget

Shows:
- 🔥 Stack: X consecutive wins
- 💪 Confidence trend: ↑ Up 40% this week
- 🎯 Last big win: "Lean deployed publicly (2 hours ago)"

### 5. System Health

Real-time monitoring:
- **Disk space** - Usage percentage + GB used/total
- **Memory** - RAM usage percentage + GB used/total
- **Gateway status** - Clawdbot gateway up/down
- **Service status** - All services green/issues detected

**Health bars:**
- 🟢 Green: <80% usage
- 🟡 Yellow: 80-90% usage
- 🔴 Red: >90% usage

## API Endpoints

All endpoints return JSON.

### GET /api/status

Complete dashboard status in one call.

**Response:**
```json
{
  "services": [...],
  "costs": {...},
  "health": {...},
  "confidence": {...},
  "timestamp": "2026-02-15T20:00:00"
}
```

### GET /api/services

List of all services with status.

### GET /api/costs

Cost breakdown and projections.

### GET /api/actions

Recent action tracker entries.

**Query params:**
- `filter`: 'all', 'high-cost', 'errors'
- `limit`: Number of actions to return (default 20)

### GET /api/builds

Active spawned sessions + completed builds.

### GET /api/health

System health metrics.

### GET /api/confidence

Confidence tracking data.

## Action Tracker Integration

### In Code

```python
from scripts.action_tracker import log_action

# After any tool call
log_action('exec', 'ls -la', result='success')
log_action('web_fetch', 'https://example.com', result='success', tokens=3000)
log_action('read', 'MEMORY.md', result='success')  # Free operation
```

### Cost Estimation

**Free operations:**
- read, write, edit, heartbeat

**Estimated costs:**
- exec: ~$0.009 per call
- web_fetch: ~$0.027 per call
- web_search: ~$0.018 per call
- browser: ~$0.045 per call
- message: ~$0.0135 per call

Based on Claude Sonnet 4.5 pricing: $3/MTok input, $15/MTok output

### Daily Summary

```bash
python3 -c "from scripts.action_tracker import get_daily_summary; import json; print(json.dumps(get_daily_summary(), indent=2))"
```

## Usage Patterns

### Morning Briefing

1. Visit Mission Control dashboard
2. Check overnight costs
3. Review action tracker for daemon activity
4. Check confidence score

### During Development

1. Keep Mission Control open in browser tab
2. Auto-refreshes every 10 seconds
3. Monitor costs in real-time
4. Watch action tracker for tool calls

### Post-Ship

1. Log win in confidence tracker
2. Check updated confidence score
3. Review patterns (when do you ship most?)

### Debugging

1. Filter action tracker to "Errors"
2. Find failed operations
3. Check cost of retries
4. Identify expensive operations

## Troubleshooting

### Dashboard won't load

```bash
# Check if Flask is running
lsof -i :8080

# Restart
cd /Users/clawdbot/clawd/mission_control
python3 app.py
```

### No actions showing

Check if action tracker log exists:
```bash
ls -lh /Users/clawdbot/clawd/logs/action-tracker.jsonl
```

Start logging:
```python
from scripts.action_tracker import log_action
log_action('test', 'Testing action tracker', result='success')
```

### Memory not loading

Run auto-context manually:
```bash
python3 /Users/clawdbot/clawd/scripts/auto_context.py main
```

Check what was loaded:
```bash
tail -50 /Users/clawdbot/clawd/logs/context-loader.log
```

### Confidence score stuck at 0

Run full scan:
```bash
python3 /Users/clawdbot/clawd/scripts/confidence_tracker.py
```

Log a win manually:
```python
from scripts.confidence_tracker import ConfidenceTracker
tracker = ConfidenceTracker()
tracker.log_win("Manual test win", category="build")
print(tracker.get_summary())
```

## Configuration

### Auto-Refresh Interval

Edit `mission_control.html`, line with:
```javascript
setInterval(fetchData, 10000);  // 10 seconds
```

Change `10000` to desired milliseconds.

### Cost Thresholds

Edit `app.py`, functions:
- `get_cost_data()` - Daily/weekly/monthly calculations
- `estimate_cost()` in `action_tracker.py` - Token cost estimates

### Service Checks

Add new services in `app.py`:
```python
def check_my_service():
    # Your check logic
    return {'running': True, 'details': {...}}

services.append(get_service_status('My Service', check_my_service))
```

## Files

### Core Files

- `mission_control/app.py` - Flask backend
- `mission_control/templates/mission_control.html` - Dashboard UI
- `scripts/action_tracker.py` - Tool call logging
- `scripts/auto_context.py` - Memory loader
- `scripts/confidence_tracker.py` - Win tracking

### Data Files

- `logs/action-tracker.jsonl` - Action log (JSONL format)
- `logs/context-loader.log` - Context load history
- `logs/memory-audit.log` - Memory self-audit
- `memory/confidence_data.json` - Confidence metrics
- `memory/cost-log-YYYY-MM-DD.json` - Daily cost logs

## Maintenance

### Daily

- Auto-context loads at session start ✓
- Confidence tracker scans builds ✓
- Action tracker logs continuously ✓

### Weekly

- Review cost trends
- Check confidence patterns
- Archive old action logs (optional)

### Monthly

- Review memory audit log
- Clean up old confidence data (optional)
- Update service checks as needed

## Future Enhancements

- [ ] Email alerts for high costs
- [ ] Slack/Telegram notifications for wins
- [ ] Historical cost graphs
- [ ] Confidence trend charts
- [ ] Auto-retry for failed actions
- [ ] Cost optimization suggestions
- [ ] Predictive cost modeling
- [ ] Memory search API
- [ ] Voice summary of daily activity

## Support

**Issues?** Check logs:
```bash
# Mission Control
tail -f /Users/clawdbot/clawd/logs/action-tracker.jsonl

# Auto-Context
tail -f /Users/clawdbot/clawd/logs/context-loader.log

# Confidence
cat /Users/clawdbot/clawd/memory/confidence_data.json | python3 -m json.tool
```

**Questions?** Ask Jarvis: "Show me Mission Control status" or "What's my confidence score?"
