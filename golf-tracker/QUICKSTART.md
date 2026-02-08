# ⛳ Golf Tracker - Quick Start Guide

## Installation (30 seconds)

```bash
cd /Users/clawdbot/clawd/golf-tracker
bash start.sh
```

That's it! The script will:
1. Create a virtual environment
2. Install dependencies
3. Start the web server

## First Use

1. **Open your browser** to: http://localhost:5050
2. **Click "Log New Round"** to add your first round
3. Fill in the form and click "Save Round"
4. **View insights** on the dashboard

## Quick Commands

### Start Web UI
```bash
cd /Users/clawdbot/clawd/golf-tracker
bash start.sh
```

### CLI - Add a Round
```bash
cd /Users/clawdbot/clawd/golf-tracker
source venv/bin/activate
python golf_cli.py add
```

### CLI - View Insights
```bash
cd /Users/clawdbot/clawd/golf-tracker
source venv/bin/activate
python golf_cli.py insights
```

### CLI - List Rounds
```bash
cd /Users/clawdbot/clawd/golf-tracker
source venv/bin/activate
python golf_cli.py list
```

## Data Location

All your golf data is stored in:
```
/Users/clawdbot/clawd/data/golf-data.json
```

**Backup this file regularly!**

## Common Tasks

### Export Your Data
```bash
cd /Users/clawdbot/clawd/golf-tracker
source venv/bin/activate
python golf_cli.py export ~/my-golf-backup.json
```

### Run Tests
```bash
cd /Users/clawdbot/clawd/golf-tracker
source venv/bin/activate
python -m pytest tests/ -v
```

### Check Logs
```bash
tail -f /Users/clawdbot/clawd/golf-tracker/golf-tracker.log
```

## Sample Round Entry

Here's what a typical round entry looks like:

**Web Form:**
- Date: 2024-01-15
- Course: Pebble Beach
- Score: 87
- Par: 72
- Handicap: 15.2 (optional)
- Notes: "Windy conditions, great putting on back 9"

**CLI (quick add):**
```bash
python golf_cli.py add --date 2024-01-15 --course "Pebble Beach" --score 87 --par 72
```

## Tips

1. **Regular Updates**: Log rounds immediately after playing for best insights
2. **Add Notes**: Weather, highlights, or areas to improve help track patterns
3. **Set Goals**: Use the API to set goals like "break 80"
4. **Backup Data**: Export your data monthly to a backup file
5. **Check Insights**: Review the dashboard weekly to track improvement

## Troubleshooting

**Port already in use?**
```bash
# Edit app.py and change port 5050 to something else
nano app.py
# Then restart
bash start.sh
```

**Module not found errors?**
```bash
cd /Users/clawdbot/clawd/golf-tracker
source venv/bin/activate
pip install -r requirements.txt
```

**Can't find data file?**
```bash
mkdir -p /Users/clawdbot/clawd/data
# The app will create golf-data.json automatically
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API endpoints for integrations
- Customize the templates in `templates/` for your style
- Set up automatic backups with a cron job

---

**Need Help?** Check the logs at: `/Users/clawdbot/clawd/golf-tracker/golf-tracker.log`
