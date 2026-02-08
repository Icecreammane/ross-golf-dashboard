# Fitness Aggregator - Quick Reference

## 🚀 Quick Commands

```bash
# Manual run
python3 ~/clawd/scripts/fitness_aggregator.py

# Test
python3 ~/clawd/scripts/test_fitness_aggregator.py

# View latest insights
tail -20 ~/clawd/logs/fitness-aggregator.log | grep "•"

# View summary JSON
cat ~/clawd/data/fitness-summary.json | jq '.weekly_summaries[-1].insights'

# Check service status
launchctl list | grep fitness

# Restart service
launchctl unload ~/Library/LaunchAgents/com.clawdbot.fitness-aggregator.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.fitness-aggregator.plist
```

## 📊 What It Does

- **Pulls data** from FitTrack Pro API (localhost:3000)
- **Calculates** daily, weekly, monthly summaries
- **Identifies** best/worst days, patterns, trends
- **Generates** natural language insights
- **Stores** weekly summaries in JSON
- **Runs** daily at 11:00 PM automatically

## 📁 Key Files

| File | Path |
|------|------|
| Script | `~/clawd/scripts/fitness_aggregator.py` |
| Test | `~/clawd/scripts/test_fitness_aggregator.py` |
| Schedule | `~/Library/LaunchAgents/com.clawdbot.fitness-aggregator.plist` |
| Data | `~/clawd/data/fitness-summary.json` |
| Logs | `~/clawd/logs/fitness-aggregator.log` |

## 🔍 Example Insights

```
• You hit protein 5/7 days this week. 71% compliance. Up from 65% last week.
• Calorie compliance improved by 12% (86% vs 74%).
• Average daily protein up 15g (198g vs 183g).
• Mondays are your strongest (205g protein). Fridays need work (180g).
• Very consistent protein intake (±18g) - great job!
• 🔥 On fire! 3-day protein streak at 205g/day!
```

## ⚡ Troubleshooting

**Not running?**
```bash
launchctl list | grep fitness  # Should show the job
launchctl load ~/Library/LaunchAgents/com.clawdbot.fitness-aggregator.plist
```

**API errors?**
```bash
curl http://localhost:3000/api/stats  # Should return JSON
```

**No insights?**
- Need at least 7 days of data for comparisons
- Check logs: `tail ~/clawd/logs/fitness-aggregator.log`

## 📅 Schedule

- **When:** Daily at 11:00 PM
- **What:** Analyzes yesterday's data
- **Output:** Updates `fitness-summary.json` and logs insights

---

✅ **Status:** Production-ready and active  
📚 **Full Docs:** `FITNESS_AGGREGATOR.md`
