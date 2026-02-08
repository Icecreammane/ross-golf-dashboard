# Opportunity Aggregator - Quick Reference

## 🎯 What It Does

Aggregates opportunities from Twitter, Email, and Revenue Dashboard → Scores them 0-100 → Ranks by revenue potential

## 📊 View Opportunities

```bash
# Quick view (top 10)
python3 ~/clawd/scripts/view_opportunities.py

# View top 5
python3 ~/clawd/scripts/view_opportunities.py --top 5

# View all
python3 ~/clawd/scripts/view_opportunities.py --all

# Just summary
python3 ~/clawd/scripts/view_opportunities.py --summary-only
```

## 🔍 Filter Options

```bash
# By type
python3 ~/clawd/scripts/view_opportunities.py --type golf_coaching
python3 ~/clawd/scripts/view_opportunities.py --type partnership

# By source
python3 ~/clawd/scripts/view_opportunities.py --source twitter
python3 ~/clawd/scripts/view_opportunities.py --source email

# By score
python3 ~/clawd/scripts/view_opportunities.py --min-score 80

# Combine filters
python3 ~/clawd/scripts/view_opportunities.py --type golf_coaching --min-score 90
```

## 🎨 Priority Levels

- 🔥 **HIGH (80-100):** Act immediately - high revenue potential
- ⚡ **MED (50-79):** Review within 24-48h
- 💡 **LOW (<50):** Low priority or informational

## 🔄 Daemon Control

```bash
# Check status
launchctl list | grep opportunity-aggregator

# Reload daemon
launchctl unload ~/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist

# Run manually
python3 ~/clawd/scripts/opportunity_aggregator.py
```

## 📝 Check Logs

```bash
# Live logs
tail -f ~/clawd/logs/opportunity-aggregator.log

# Last 50 lines
tail -n 50 ~/clawd/logs/opportunity-aggregator.log

# Errors only
grep ERROR ~/clawd/logs/opportunity-aggregator.log
```

## 🧪 Verify System

```bash
bash ~/clawd/scripts/verify_opportunity_system.sh
```

## 📚 Full Docs

```bash
# Read documentation
cat ~/clawd/OPPORTUNITY_AGGREGATOR.md

# Build summary
cat ~/clawd/BUILD_OPPORTUNITY_AGGREGATOR.md
```

## 📂 Key Files

**Output:** `/Users/clawdbot/clawd/data/opportunities.json`  
**Logs:** `/Users/clawdbot/clawd/logs/opportunity-aggregator.log`  
**Config:** `~/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist`

## ⏰ Schedule

Runs automatically every **30 minutes**

## 🆘 Troubleshooting

**Daemon not running?**
```bash
launchctl load ~/Library/LaunchAgents/com.jarvis.opportunity-aggregator.plist
```

**No opportunities?**
```bash
ls -lh ~/clawd/data/{twitter-opportunities,email-summary,revenue-tasks}.json
```

**Errors?**
```bash
tail -n 100 ~/clawd/logs/opportunity-aggregator.log | grep ERROR
```

---

**Tip:** Add this alias to your `.zshrc` or `.bashrc` for quick access:

```bash
alias opportunities='python3 ~/clawd/scripts/view_opportunities.py'
alias opps='python3 ~/clawd/scripts/view_opportunities.py --top 5'
```

Then just type `opportunities` or `opps` to view!
