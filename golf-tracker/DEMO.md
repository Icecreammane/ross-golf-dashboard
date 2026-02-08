# ⛳ Golf Tracker - Interactive Demo

This guide walks you through using the Golf Tracker for the first time.

## Setup (30 seconds)

```bash
cd /Users/clawdbot/clawd/golf-tracker
bash start.sh
```

Wait for the server to start, then open: **http://localhost:5050**

---

## Demo Scenario: Track Your Golf Season

### Step 1: Add Your First Round

**Via Web UI:**
1. Click **"Log New Round"** button
2. Fill in the form:
   - **Date:** Select today's date
   - **Course Name:** "Pebble Beach"
   - **Your Score:** 87
   - **Course Par:** 72
   - **Notes:** "First round of the season!"
3. Click **"Save Round"**

You'll be redirected to the dashboard showing your new round.

**Via CLI (alternative):**
```bash
cd /Users/clawdbot/clawd/golf-tracker
source venv/bin/activate
python golf_cli.py add --date 2024-01-15 --course "Pebble Beach" --score 87 --par 72 --notes "First round of the season"
```

### Step 2: Add More Rounds

Let's add a few more rounds to see the insights develop:

```bash
# Round 2: Improved score
python golf_cli.py add --date 2024-01-22 --course "Torrey Pines" --score 84 --par 72 --notes "Great putting today"

# Round 3: Different course
python golf_cli.py add --date 2024-01-28 --course "Augusta National" --score 92 --par 72 --notes "Tough course!"

# Round 4: Back to Pebble Beach
python golf_cli.py add --date 2024-02-05 --course "Pebble Beach" --score 82 --par 72 --notes "Personal best on this course!"

# Round 5: Consistent performance
python golf_cli.py add --date 2024-02-12 --course "Torrey Pines" --score 83 --par 72 --notes "Windy conditions"
```

### Step 3: View Your Dashboard

Refresh the web UI (http://localhost:5050) to see:

📊 **Insight Cards:**
- 5-Round Average
- This Month's Performance
- Best Score
- Total Rounds

📈 **Performance Insights:**
- "Your 5-round average is improving..."
- Best/worst course statistics
- Improvement trends

🏌️ **Course Statistics:**
- Each course you've played
- Average, best, and worst scores
- Rounds played per course

📝 **Recent Rounds Table:**
- Color-coded scores (excellent/good/average/poor)
- Date, course, score, differential
- Notes for each round

### Step 4: View Insights via CLI

```bash
python golf_cli.py insights
```

**Sample Output:**
```
📊 Performance Insights
==================================================

5-Round Average: 85.6
This Month Average: 83.5 (3 rounds)
Last Month Average: 87.7

🎉 Great progress! You've improved by 4.2 strokes!

Best Score: 82
Worst Score: 92
Total Rounds: 5

Best Course: Pebble Beach (avg: 84.5)
Most Challenging: Augusta National (avg: 92.0)
```

### Step 5: Check Course Statistics

```bash
python golf_cli.py courses
```

**Sample Output:**
```
🏌️ Course Statistics
================================================================================
Course                         Rounds     Average    Best       Worst     
--------------------------------------------------------------------------------
Pebble Beach                   2          84.5       82         87        
Torrey Pines                   2          83.5       83         84        
Augusta National               1          92.0       92         92
```

### Step 6: List All Rounds

```bash
python golf_cli.py list
```

**Sample Output:**
```
⛳ Recent Rounds (last 5)
================================================================================
Date         Course                    Score    Par    Diff    
--------------------------------------------------------------------------------
2024-02-12   Torrey Pines              83       72     +11     
2024-02-05   Pebble Beach              82       72     +10     
2024-01-28   Augusta National          92       72     +20     
2024-01-22   Torrey Pines              84       72     +12     
2024-01-15   Pebble Beach              87       72     +15
```

---

## Advanced Features

### Export Your Data

```bash
python golf_cli.py export ~/my-golf-backup.json
```

This creates a complete backup of all your golf data.

### Quick Add (Non-Interactive)

Perfect for scripts or quick logging:

```bash
python golf_cli.py add \
  --date 2024-02-20 \
  --course "St. Andrews" \
  --score 79 \
  --par 72 \
  --handicap 8.5 \
  --notes "Broke 80!"
```

### API Usage

You can also use the REST API directly:

```bash
# Add a round via API
curl -X POST http://localhost:5050/api/add_round \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-02-20",
    "course": "Bethpage Black",
    "score": 86,
    "par": 71
  }'

# Get all rounds
curl http://localhost:5050/api/rounds

# Get insights
curl http://localhost:5050/api/insights
```

---

## Sample Data for Testing

Want to try the system with realistic data? Run:

```bash
python add_sample_data.py
```

This will add 25 sample rounds from the past 3 months with:
- Various courses
- Improving trend over time
- Realistic scores and notes
- Goals to track

Then view the populated dashboard!

---

## Common Workflows

### Weekly Check-In
```bash
# After your Sunday round
python golf_cli.py add  # Interactive mode
python golf_cli.py insights  # See how you're doing
```

### Monthly Review
```bash
# First of the month
python golf_cli.py list --count 20  # Review last month
python golf_cli.py courses  # See which courses you played
python golf_cli.py export ~/golf-backups/$(date +%Y-%m).json  # Backup
```

### Goal Tracking

Track a goal via API:

```bash
# Add a goal
curl -X POST http://localhost:5050/api/add_goal \
  -H "Content-Type: application/json" \
  -d '{
    "type": "break_score",
    "target": 80,
    "description": "Break 80 by summer"
  }'
```

The system will automatically detect when you achieve your goal and display a congratulations message!

---

## Tips for Best Results

1. **Log rounds immediately** - While details are fresh
2. **Add meaningful notes** - Weather, what worked, what didn't
3. **Be consistent** - Regular logging shows better trends
4. **Review monthly** - Check insights to track improvement
5. **Backup regularly** - Export your data monthly
6. **Set goals** - Having targets motivates improvement

---

## Troubleshooting Demo

**Issue: Web UI won't load**
```bash
# Check if server is running
lsof -i :5050

# If nothing shown, restart
bash start.sh
```

**Issue: CLI command not found**
```bash
# Make sure you're in the right directory
cd /Users/clawdbot/clawd/golf-tracker

# Activate virtual environment
source venv/bin/activate

# Then run commands
python golf_cli.py --help
```

**Issue: Want to start fresh**
```bash
# Backup current data
python golf_cli.py export ~/golf-backup.json

# Delete data file
rm /Users/clawdbot/clawd/data/golf-data.json

# Restart app (will create new empty file)
bash start.sh
```

---

## Next Steps

Now that you've seen how it works:

1. **Add your real rounds** - Start logging your actual golf data
2. **Customize templates** - Edit `templates/*.html` to match your style
3. **Set up backups** - Create a cron job for automatic backups
4. **Share with friends** - Show them the insights feature
5. **Track improvement** - Use monthly to monitor progress toward goals

---

## Demo Complete! 🎉

You now know how to:
- ✅ Add rounds via web UI
- ✅ Add rounds via CLI
- ✅ View insights and statistics
- ✅ Export data
- ✅ Use the API
- ✅ Track goals
- ✅ Review performance trends

**Happy golfing!** ⛳

---

*Questions? Check [README.md](README.md) for detailed documentation or [QUICKSTART.md](QUICKSTART.md) for command reference.*
