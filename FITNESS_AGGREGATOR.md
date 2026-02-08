# Fitness Aggregator

**Status:** ✅ Production-ready and active  
**Version:** 1.0.0  
**Last Updated:** 2026-02-08

## Overview

The Fitness Aggregator is an automated system that pulls data from the FitTrack Pro API, analyzes nutrition and fitness metrics, and generates actionable insights.

**What it does:**
- Pulls daily nutrition data from FitTrack Pro (running on port 3000)
- Calculates daily, weekly, and monthly summaries
- Identifies patterns (best/worst days, day-of-week trends)
- Generates natural language insights comparing week-over-week performance
- Stores weekly summaries in `/Users/clawdbot/clawd/data/fitness-summary.json`
- Runs automatically every day at 11:00 PM via launchd

## Quick Start

### Manual Run
```bash
# Run aggregator manually
python3 ~/clawd/scripts/fitness_aggregator.py

# Run test suite
python3 ~/clawd/scripts/test_fitness_aggregator.py

# View latest summary
cat ~/clawd/data/fitness-summary.json | jq
```

### Check Service Status
```bash
# Check if launchd job is loaded
launchctl list | grep fitness-aggregator

# View recent logs
tail -50 ~/clawd/logs/fitness-aggregator.log

# View stdout/stderr
tail ~/clawd/logs/fitness-aggregator-stdout.log
tail ~/clawd/logs/fitness-aggregator-stderr.log
```

### Manage Service
```bash
# Reload launchd job (after editing plist)
launchctl unload ~/Library/LaunchAgents/com.clawdbot.fitness-aggregator.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.fitness-aggregator.plist

# Manually trigger job (for testing)
launchctl start com.clawdbot.fitness-aggregator

# Disable automatic runs
launchctl unload ~/Library/LaunchAgents/com.clawdbot.fitness-aggregator.plist

# Re-enable automatic runs
launchctl load ~/Library/LaunchAgents/com.clawdbot.fitness-aggregator.plist
```

## Architecture

### Components

1. **fitness_aggregator.py** - Main aggregator script
   - Location: `/Users/clawdbot/clawd/scripts/fitness_aggregator.py`
   - Functions:
     - `fetch_data()` - Pulls from API
     - `calculate_daily_summary()` - Daily metrics
     - `calculate_weekly_summary()` - Weekly comparison
     - `calculate_monthly_summary()` - 30-day trends
     - `identify_patterns()` - Pattern detection
     - `generate_insights()` - Natural language insights
     - `save_summary()` - Persist to JSON

2. **test_fitness_aggregator.py** - Test suite
   - Location: `/Users/clawdbot/clawd/scripts/test_fitness_aggregator.py`
   - Validates all functions
   - Runs full integration test

3. **com.clawdbot.fitness-aggregator.plist** - launchd configuration
   - Location: `/Users/clawdbot/Library/LaunchAgents/`
   - Runs daily at 11:00 PM
   - Logs to `~/clawd/logs/`

### Data Flow

```
FitTrack Pro API (port 3000)
         ↓
   fetch_data()
         ↓
Calculate summaries:
  - Daily (yesterday)
  - Weekly (this week vs last week)
  - Monthly (last 30 days)
         ↓
  Pattern analysis
         ↓
  Insight generation
         ↓
Save to fitness-summary.json
         ↓
   Log results
```

## Data Structures

### Input (from API)
```json
{
  "goals": {
    "calories": 2200,
    "protein": 200,
    "carbs": 250,
    "fat": 70
  },
  "history": [
    {
      "date": "2026-02-08",
      "calories": 2150,
      "protein": 198,
      "carbs": 185,
      "fat": 68,
      "weight": 224.5
    }
  ],
  "today": { ... },
  "current_weight": 224.5
}
```

### Output (fitness-summary.json)
```json
{
  "weekly_summaries": [
    {
      "generated_at": "2026-02-08T23:00:00",
      "yesterday": {
        "date": "2026-02-07",
        "calories": 2150,
        "protein": 198,
        "compliance": {
          "calories": 97.7,
          "protein": 99.0
        },
        "goals_met": {
          "calories": true,
          "protein": true
        }
      },
      "this_week": {
        "start_date": "2026-02-02",
        "end_date": "2026-02-08",
        "days_logged": 7,
        "averages": {
          "calories": 2050.5,
          "protein": 198.2
        },
        "goal_hits": {
          "protein": 5,
          "calories": 6
        },
        "compliance_percentage": 85.7
      },
      "monthly": {
        "period": "2026-01-10 to 2026-02-08",
        "days_logged": 30,
        "averages": { ... },
        "consistency": {
          "calorie_stdev": 250.5,
          "protein_stdev": 22.3
        }
      },
      "patterns": {
        "best_days": { ... },
        "worst_days": { ... },
        "day_of_week_performance": {
          "Monday": {
            "avg_calories": 2100,
            "avg_protein": 205
          }
        }
      },
      "insights": [
        "You hit protein 5/7 days this week. 71% compliance. Up from 65% last week.",
        "Calorie compliance improved by 15% (86% vs 71%).",
        "Mondays are your strongest (205g protein). Fridays need work (180g)."
      ]
    }
  ],
  "last_updated": "2026-02-08T23:00:00"
}
```

## Insights Generated

The aggregator generates several types of insights:

1. **Weekly Protein Compliance**
   - Example: "You hit protein 5/7 days this week. 71% compliance. Up from 65% last week."
   - Compares current week to previous week
   - Shows trend direction (Up/Down/Steady)

2. **Calorie Compliance Changes**
   - Example: "Calorie compliance improved by 15% (86% vs 71%)."
   - Only shown if change >= 10%

3. **Average Protein Changes**
   - Example: "Average daily protein up 12g (198g vs 186g)."
   - Only shown if change >= 10g

4. **Day-of-Week Patterns**
   - Example: "Mondays are your strongest (205g protein). Fridays need work (180g)."
   - Identifies best and worst days of the week

5. **Consistency Feedback**
   - Example: "Very consistent protein intake (±18g) - great job!"
   - Or: "Protein intake varies widely (±45g) - try to be more consistent."

6. **Recent Trend Alerts**
   - Example: "🔥 On fire! 3-day protein streak at 205g/day!"
   - Or: "⚠️ Below target last 3 days (175g/day). Time to refocus!"

## Metrics Tracked

### Daily
- Calories consumed
- Macros: protein, carbs, fat
- Compliance percentage for each metric
- Goals met (boolean for each)

### Weekly
- Days logged
- Average macros
- Goal hit count (protein, calories)
- Overall compliance percentage

### Monthly
- 30-day averages
- Consistency (standard deviation)
- Protein goal hit rate

### Patterns
- Best/worst days for calories and protein
- Day-of-week performance averages
- Trends and correlations

## Configuration

### API Endpoint
Change in `fitness_aggregator.py`:
```python
API_URL = "http://localhost:3000/api/stats"
```

### Storage Location
Change in `fitness_aggregator.py`:
```python
DATA_DIR = Path("/Users/clawdbot/clawd/data")
SUMMARY_FILE = DATA_DIR / "fitness-summary.json"
```

### Schedule
Edit `com.clawdbot.fitness-aggregator.plist`:
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>23</integer>  <!-- 11 PM -->
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.clawdbot.fitness-aggregator.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.fitness-aggregator.plist
```

## Logging

### Log Files
- **Main log:** `/Users/clawdbot/clawd/logs/fitness-aggregator.log`
  - Application-level logging
  - Includes insights and summaries
  - Rotates naturally (append-only)

- **Stdout:** `/Users/clawdbot/clawd/logs/fitness-aggregator-stdout.log`
  - Standard output from script execution

- **Stderr:** `/Users/clawdbot/clawd/logs/fitness-aggregator-stderr.log`
  - Error output and stack traces

### Log Format
```
2026-02-08 23:00:15,123 - INFO - Starting daily fitness summary
2026-02-08 23:00:15,456 - INFO - Data fetched successfully
2026-02-08 23:00:15,789 - INFO - 
📊 FITNESS INSIGHTS:
2026-02-08 23:00:15,790 - INFO -   • You hit protein 5/7 days this week...
```

## Troubleshooting

### Job not running at 11 PM
```bash
# Check if job is loaded
launchctl list | grep fitness-aggregator

# Check launchd errors
cat ~/clawd/logs/fitness-aggregator-stderr.log

# Manually trigger to test
launchctl start com.clawdbot.fitness-aggregator
```

### API connection errors
```bash
# Verify FitTrack Pro is running
curl http://localhost:3000/api/stats

# Check the error log
tail ~/clawd/logs/fitness-aggregator.log
```

### No insights generated
- Need at least 7 days of data for weekly comparison
- Need at least 5 days for pattern analysis
- Check that API returns non-zero data

### Summary file not updating
```bash
# Check permissions
ls -l ~/clawd/data/fitness-summary.json

# Verify data directory exists
mkdir -p ~/clawd/data

# Run manually to see errors
python3 ~/clawd/scripts/fitness_aggregator.py
```

## Testing

### Run Full Test Suite
```bash
cd ~/clawd
python3 scripts/test_fitness_aggregator.py
```

Tests include:
1. API data fetching
2. Daily summary calculation
3. Weekly summary calculation
4. Monthly summary calculation
5. Pattern identification
6. Insight generation
7. Full summary generation and saving

### Manual Testing Checklist
- [ ] API endpoint is accessible
- [ ] Script runs without errors
- [ ] Summary file is created/updated
- [ ] Insights are generated
- [ ] Logs are written correctly
- [ ] launchd job is loaded
- [ ] Permissions are correct

## Dependencies

### Python Packages
```bash
pip3 install requests
# (Already installed - comes with Python 3)
```

### System Requirements
- macOS with launchd
- Python 3.7+
- FitTrack Pro running on port 3000
- Network access to localhost:3000

## Future Enhancements

Potential improvements:
- Email/notification delivery of insights
- Integration with other health apps
- Predictive analytics (trend forecasting)
- Custom goal threshold configuration
- Weekly/monthly report generation
- Charts and visualizations
- Correlation analysis with other metrics (sleep, exercise, etc.)

## Support

### Quick Commands Reference
```bash
# Status check
launchctl list | grep fitness-aggregator

# Manual run
python3 ~/clawd/scripts/fitness_aggregator.py

# View logs
tail -f ~/clawd/logs/fitness-aggregator.log

# View summary
cat ~/clawd/data/fitness-summary.json | jq '.weekly_summaries[-1]'

# Test
python3 ~/clawd/scripts/test_fitness_aggregator.py

# Restart service
launchctl unload ~/Library/LaunchAgents/com.clawdbot.fitness-aggregator.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.fitness-aggregator.plist
```

### Files and Locations
| File | Location |
|------|----------|
| Main script | `/Users/clawdbot/clawd/scripts/fitness_aggregator.py` |
| Test script | `/Users/clawdbot/clawd/scripts/test_fitness_aggregator.py` |
| launchd plist | `/Users/clawdbot/Library/LaunchAgents/com.clawdbot.fitness-aggregator.plist` |
| Summary data | `/Users/clawdbot/clawd/data/fitness-summary.json` |
| Main log | `/Users/clawdbot/clawd/logs/fitness-aggregator.log` |
| Stdout log | `/Users/clawdbot/clawd/logs/fitness-aggregator-stdout.log` |
| Stderr log | `/Users/clawdbot/clawd/logs/fitness-aggregator-stderr.log` |

---

**Built:** 2026-02-08  
**Status:** Production-ready ✅  
**Tested:** Yes ✅  
**Scheduled:** Daily at 11:00 PM ✅
