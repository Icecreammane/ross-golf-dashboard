# Morning Brief - Quick Start

## What It Does
Sends you a daily morning brief at 7:30 AM CST with:
1. **What's most important today?** (tasks + weather + activities)
2. **What's about to become a problem?** (emails + revenue alerts)
3. **What did you do since last session?** (yesterday's highlights)

## Install (30 seconds)
```bash
cd ~/clawd/scripts
bash setup_morning_brief.sh
```

## Test Now
```bash
python3 ~/clawd/scripts/morning_brief.py
```
Check Telegram - you should receive a brief immediately!

## Commands

### View Latest Brief
```bash
cat ~/clawd/logs/morning-brief-latest.json | jq
```

### View Logs
```bash
tail -f ~/clawd/logs/morning-brief.log
```

### Check Status
```bash
launchctl list | grep morningbrief
```

### Force Run
```bash
launchctl start com.jarvis.morningbrief
```

### Uninstall
```bash
launchctl unload ~/Library/LaunchAgents/com.jarvis.morningbrief.plist
rm ~/Library/LaunchAgents/com.jarvis.morningbrief.plist
```

## Data Sources
- `data/task-queue.json` - Your top tasks
- `data/financial-tracking.json` - Revenue & goals
- `data/weather.json` - Weather & activity scores
- `email_scanner_state.json` - Flagged emails
- `memory/YYYY-MM-DD.md` - Yesterday's summary

## Output
Brief is sent to your Telegram and saved to:
- **Log:** `logs/morning-brief.log`
- **JSON:** `logs/morning-brief-latest.json`

## Example Output
```
🌅 Morning Brief
Saturday, February 08, 2026

1. What's most important today?
  📋 Build Stripe integration (Priority: 150)
  📋 Launch Notion Templates (Priority: 100)
  ☀️ Weather: 52°F, Cloudy
  🏃 Outdoor Workout: Excellent (100/100)

2. What's about to become a problem?
  📧 No flagged emails - inbox clear
  🏖️ Florida Fund: $18,500/$50,000 (37.0%) - $31,500 to go

3. What did you do since last session?
  • Built 15 systems last night
  • Shipped revenue tracker
  • Mission Control operational

─────────────────
📊 Quick Stats
• Active Tasks: 3
• MRR: $6,800
• Yesterday Revenue: $250
• Weather: 52°F, Cloudy
```

## Troubleshooting

**Not receiving briefs?**
```bash
# Check if service is loaded
launchctl list | grep morningbrief

# Check logs for errors
tail -20 ~/clawd/logs/morning-brief.log

# Test manually
python3 ~/clawd/scripts/morning_brief.py
```

**Want to change the time?**
Edit `~/Library/LaunchAgents/com.jarvis.morningbrief.plist` and change Hour/Minute, then:
```bash
launchctl unload ~/Library/LaunchAgents/com.jarvis.morningbrief.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.morningbrief.plist
```

## Full Documentation
See `MORNING_BRIEF.md` for complete docs, architecture, and advanced usage.
