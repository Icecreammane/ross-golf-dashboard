# Morning Brief Generator

**Status:** ✅ Production Ready  
**Version:** 1.0  
**Created:** 2026-02-08

## Overview

Automated morning brief system that aggregates data from multiple sources and delivers a concise 3-question summary to Ross via Telegram at 7:30 AM CST daily.

## Features

### Data Sources
- **Task Queue** (`data/task-queue.json`) - Top 3 priority tasks
- **Email Scanner** (`email_scanner_state.json`) - Flagged emails summary
- **Financial Tracking** (`data/financial-tracking.json`) - MRR, daily revenue, Florida Fund progress
- **Weather Daemon** (`data/weather.json`) - Current conditions + activity scores
- **Memory Files** (`memory/YYYY-MM-DD.md`) - Yesterday's activity summary

### The 3 Questions

#### 1. What's most important today?
**Sources:** Task queue + Weather conditions + Activity scores

**Output:**
- Top 3 priority tasks with priority scores
- Current weather (temp, conditions)
- Best activity recommendation with score

#### 2. What's about to become a problem?
**Sources:** Emails + Revenue data + Financial goals

**Output:**
- Flagged emails requiring attention
- Revenue trends (daily/monthly)
- Florida Fund progress (% to goal)
- Alerts for zero revenue days

#### 3. What did you do since last session?
**Sources:** Yesterday's memory file

**Output:**
- Key headlines from yesterday's activity
- Major accomplishments
- Systems built/shipped

### Fallback Behavior

All data sources have graceful fallbacks:
- Missing files → Default messages
- Parse errors → Error messages logged, brief still generated
- Empty data → Friendly "all clear" messages

## Files

```
scripts/
  morning_brief.py                    # Main generator script
  com.jarvis.morningbrief.plist      # launchd configuration
  setup_morning_brief.sh              # Installation script

logs/
  morning-brief.log                   # Execution log
  morning-brief-latest.json           # Latest brief JSON output
```

## Installation

### Quick Setup
```bash
cd ~/clawd/scripts
bash setup_morning_brief.sh
```

This will:
1. Make scripts executable
2. Copy launchd plist to `~/Library/LaunchAgents/`
3. Load the service
4. Schedule daily execution at 7:30 AM

### Manual Setup
```bash
# Make executable
chmod +x ~/clawd/scripts/morning_brief.py

# Copy plist
cp ~/clawd/scripts/com.jarvis.morningbrief.plist ~/Library/LaunchAgents/

# Load service
launchctl load ~/Library/LaunchAgents/com.jarvis.morningbrief.plist
```

## Usage

### Test Immediately
```bash
python3 ~/clawd/scripts/morning_brief.py
```

### Check Status
```bash
launchctl list | grep morningbrief
```

### View Logs
```bash
# Live tail
tail -f ~/clawd/logs/morning-brief.log

# Latest brief JSON
cat ~/clawd/logs/morning-brief-latest.json | jq
```

### View Latest Brief
```bash
cat ~/clawd/logs/morning-brief-latest.json | jq
```

## Schedule

**Execution Time:** 7:30 AM CST (13:30 UTC during standard time)  
**Frequency:** Daily  
**Delivery:** Telegram direct message to Ross

## Output Format

### JSON Structure
```json
{
  "timestamp": "2026-02-08T07:30:00.000000",
  "date": "Saturday, February 08, 2026",
  "questions": [
    {
      "question": "What's most important today?",
      "answer": [
        "📋 Task 1 (Priority: 100)",
        "📋 Task 2 (Priority: 90)",
        "☀️ Weather: 52°F, Cloudy",
        "🏃 Outdoor Workout: Excellent (100/100)"
      ]
    },
    {
      "question": "What's about to become a problem?",
      "answer": [
        "📧 3 flagged emails requiring attention",
        "🏖️ Florida Fund: $18,500/$50,000 (37.0%) - $31,500 to go"
      ]
    },
    {
      "question": "What did you do since last session?",
      "answer": "• Built 15 systems\n• Shipped revenue tracker\n• Completed autonomous builds"
    }
  ],
  "stats": {
    "active_tasks": 3,
    "mrr": 6800,
    "daily_revenue": 250.0,
    "weather_temp": 52.8,
    "weather_conditions": "Cloudy"
  }
}
```

### Telegram Format
```
🌅 *Morning Brief*
_Saturday, February 08, 2026_

*1. What's most important today?*
  📋 Build Stripe integration (Priority: 150)
  📋 Launch Notion Templates (Priority: 100)
  ☀️ Weather: 52°F, Cloudy
  🏃 Outdoor Workout: Excellent (100/100)

*2. What's about to become a problem?*
  📧 No flagged emails - inbox clear
  🏖️ Florida Fund: $18,500/$50,000 (37.0%) - $31,500 to go

*3. What did you do since last session?*
  • Built 15 systems
  • Shipped revenue tracker
  • Completed autonomous builds

──────────────────────────────
📊 *Quick Stats*
• Active Tasks: 3
• MRR: $6,800
• Yesterday Revenue: $250
• Weather: 52°F, Cloudy
```

## Maintenance

### Update Schedule
```bash
# Edit the plist file
nano ~/Library/LaunchAgents/com.jarvis.morningbrief.plist

# Reload service
launchctl unload ~/Library/LaunchAgents/com.jarvis.morningbrief.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.morningbrief.plist
```

### Uninstall
```bash
# Unload service
launchctl unload ~/Library/LaunchAgents/com.jarvis.morningbrief.plist

# Remove plist
rm ~/Library/LaunchAgents/com.jarvis.morningbrief.plist
```

### Debugging

**Check if service is loaded:**
```bash
launchctl list | grep morningbrief
```

**Manual test with verbose output:**
```bash
python3 ~/clawd/scripts/morning_brief.py
```

**Check logs:**
```bash
tail -20 ~/clawd/logs/morning-brief.log
```

**Force run (bypass schedule):**
```bash
launchctl start com.jarvis.morningbrief
```

## Error Handling

### Missing Data Files
- Script continues with default messages
- Logs warning to `morning-brief.log`
- Brief still generated and sent

### Failed JSON Parse
- Error logged
- Default value used
- Brief generation continues

### Telegram Send Failure
- Error logged
- Brief saved to JSON file
- Returns exit code 1

### Complete Failure
- Full traceback logged
- Exit code 1
- Can review logs for debugging

## Testing

### Test Checklist
- [x] Script executes without errors
- [x] Reads all data sources correctly
- [x] Handles missing files gracefully
- [x] Generates valid JSON output
- [x] Formats Telegram message correctly
- [x] Sends to Telegram successfully
- [x] Logs to file correctly
- [x] launchd plist valid
- [x] Setup script works

### Test Results (2026-02-08 16:13)
```
✅ All data sources loaded
✅ 3 questions generated
✅ JSON output valid
✅ Telegram message sent
✅ Log file created
✅ End-to-end test passed
```

## Future Enhancements

### Potential Additions
- [ ] Add calendar events (next 24h)
- [ ] Include win streaks status
- [ ] Add social media mentions/opportunities
- [ ] Weather forecast (3-day outlook)
- [ ] Habit tracking summary
- [ ] Weekly review option (Sundays)
- [ ] Voice version (TTS)
- [ ] Email delivery option

### Intelligence Upgrades
- [ ] Personalized recommendations based on day of week
- [ ] Priority scoring based on deadlines
- [ ] Trend analysis (week-over-week)
- [ ] Predictive alerts (problems before they happen)

## Architecture

### Design Principles
1. **Fail gracefully** - Never crash, always deliver something
2. **Log everything** - Full audit trail
3. **Zero dependencies** - Only Python stdlib + existing data
4. **Portable** - Works anywhere with access to data files
5. **Testable** - Can run manually anytime

### Data Flow
```
Data Sources → Aggregation → Brief Generation → JSON Export → Telegram Send
     ↓              ↓              ↓                 ↓             ↓
  (fallback)   (validation)   (formatting)       (save)      (log result)
```

## Support

**Log Location:** `~/clawd/logs/morning-brief.log`  
**JSON Output:** `~/clawd/logs/morning-brief-latest.json`  
**Script:** `~/clawd/scripts/morning_brief.py`  
**Config:** `~/Library/LaunchAgents/com.jarvis.morningbrief.plist`

**Maintainer:** Jarvis (bigmeatyclawd@gmail.com)  
**Owner:** Ross  
**Built:** 2026-02-08 by subagent
