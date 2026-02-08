# Financial Tracker - Quick Start Guide

## 🎯 What It Does
Tracks daily expenses, calculates spending patterns, projects when you'll hit:
- **Florida Fund Goal**: $50K 
- **Financial Independence**: $900K (4% rule for $3K/month)

## ⚡ Quick Commands

### Daily Entry (Interactive)
```bash
bash ~/clawd/scripts/finance_entry.sh
```
Enter today's expenses, revenue, and balances.

### View Report
```bash
bash ~/clawd/scripts/finance_report.sh
```
See current metrics, projections, and expense breakdown.

### View Logs
```bash
tail -f ~/clawd/logs/financial-daemon.log
```

### Check Data
```bash
cat ~/clawd/data/financial-tracking.json | python3 -m json.tool
```

## 🤖 Automation

**Runs automatically daily at 6:00 AM** via launchd.

### Verify daemon is loaded:
```bash
launchctl list | grep financial-tracker
```

### Manual trigger:
```bash
launchctl start com.jarvis.financial-tracker
```

### Stop daemon:
```bash
launchctl unload ~/Library/LaunchAgents/com.jarvis.financial-tracker.plist
```

### Restart daemon:
```bash
launchctl unload ~/Library/LaunchAgents/com.jarvis.financial-tracker.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.financial-tracker.plist
```

## 📊 What Gets Tracked

### Expenses (5 categories)
- **Food**: Groceries, dining out
- **Gym**: Membership, equipment
- **Living**: Rent, utilities, housing costs
- **Business**: Tools, services, investments
- **Other**: Everything else

### Metrics Calculated
- Daily/weekly/monthly expenses
- Revenue and net income
- Savings rate (%)
- Runway months
- Expense breakdown by category

### Goal Projections
- **Florida Fund**: Months/date to $50K
- **FI**: Months/date to $900K (14 year timeline at current pace)

## 📈 Sample Output

```
📊 LAST 30 DAYS:
  Daily Expenses:   $55.16
  Monthly Expenses: $1,654.84
  Monthly Revenue:  $6,653.23
  Monthly Net:      $4,998.39
  Savings Rate:     75.1%
  Runway:           7.3 months

🎯 GOAL PROJECTIONS:
  Florida Fund: 7.0 months → Sep 2026
  Financial Independence: 170.1 months (14.2 years) → Jan 2040
```

## 🧪 Testing

Run test suite to validate calculations:
```bash
python3 ~/clawd/scripts/test_financial_tracker.py
```

All tests should pass (7/7).

## 🔧 Troubleshooting

### No data file
Run manual entry first to initialize:
```bash
bash ~/clawd/scripts/finance_entry.sh
```

### Daemon not running
```bash
# Reload
launchctl load ~/Library/LaunchAgents/com.jarvis.financial-tracker.plist

# Check status
launchctl list | grep financial-tracker
```

### Wrong calculations
Run tests to identify issue:
```bash
python3 ~/clawd/scripts/test_financial_tracker.py
```

## 📁 File Locations

- **Data**: `~/clawd/data/financial-tracking.json`
- **Logs**: `~/clawd/logs/financial-daemon.log`
- **Scripts**: `~/clawd/scripts/financial_tracker.py`
- **Config**: `~/Library/LaunchAgents/com.jarvis.financial-tracker.plist`

## 💡 Tips

1. **Manual entry daily** for accurate tracking (takes 2 minutes)
2. **Review weekly** to spot spending patterns
3. **Export data** periodically for backup
4. **Adjust goals** in the script if targets change

## 📞 Help

Full documentation: `~/clawd/FINANCIAL_TRACKER.md`

Ask Jarvis for assistance!

---

**Status**: ✅ Production Ready  
**Last Updated**: 2026-02-08
