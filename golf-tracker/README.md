# ⛳ Golf Tracker

A production-ready golf data collector for Mac mini with both web UI and CLI interface. Track your golf rounds, analyze performance trends, and work toward your goals.

## Features

- 📊 **Simple Data Entry**: Web form or CLI for logging rounds
- 📈 **Auto-Calculations**: Handicap trends, improvement over time, best/worst courses
- 💾 **Local Storage**: All data stored in `/Users/clawdbot/clawd/data/golf-data.json`
- 🎯 **Insights Generation**: Automatic performance analysis and trends
- 🏆 **Goal Tracking**: Set and track goals (e.g., "break 80")
- 🌐 **Works Offline**: No internet required
- ✅ **Validated Input**: Comprehensive validation and error handling
- 🧪 **Fully Tested**: Complete test suite with 25+ tests
- 📝 **Well Documented**: This guide plus inline code documentation

## Quick Start

### Installation

```bash
cd /Users/clawdbot/clawd/golf-tracker

# Install dependencies
pip3 install -r requirements.txt
```

### Web Interface (Recommended)

```bash
# Start the web server
python3 app.py
```

Then open your browser to: **http://localhost:5050**

The web UI provides:
- Beautiful dashboard with performance insights
- Easy-to-use round entry form
- Course statistics and trends
- Visual score badges (excellent/good/average/poor)

### CLI Interface

```bash
# Interactive mode - add a round
python3 golf_cli.py add

# Quick add (non-interactive)
python3 golf_cli.py add --date 2024-01-15 --course "Pebble Beach" --score 87 --par 72

# List recent rounds
python3 golf_cli.py list

# Show performance insights
python3 golf_cli.py insights

# Show course statistics
python3 golf_cli.py courses

# Export all data to JSON
python3 golf_cli.py export backup.json
```

## Usage Guide

### Logging a Round

**Web UI:**
1. Click "Log New Round" on the dashboard
2. Fill in the form:
   - **Date**: When you played (defaults to today)
   - **Course Name**: Name of the golf course
   - **Your Score**: Total strokes for the round
   - **Course Par**: Standard par (usually 72)
   - **Handicap Estimate**: (Optional) Your current handicap
   - **Notes**: (Optional) Weather, highlights, etc.
3. Click "Save Round"

**CLI:**
```bash
python3 golf_cli.py add
```
Follow the interactive prompts.

### Viewing Insights

**Web UI:**
- Visit the dashboard (homepage) to see:
  - 5-round average
  - This month's performance
  - Best/worst scores
  - Course statistics
  - Performance trends with insights

**CLI:**
```bash
python3 golf_cli.py insights
```

Example output:
```
📊 Performance Insights
==================================================

5-Round Average: 84.2
This Month Average: 84.0 (6 rounds)
Last Month Average: 87.5

🎉 Great progress! You've improved by 3.5 strokes!

Best Score: 78
Worst Score: 95
Total Rounds: 24

Best Course: Pebble Beach (avg: 82.3)
Most Challenging: Augusta National (avg: 91.2)
```

### Data Storage

All data is stored in a single JSON file:
```
/Users/clawdbot/clawd/data/golf-data.json
```

The file contains:
- **rounds**: Array of all golf rounds with full details
- **courses**: Course statistics (best/worst/average scores)
- **goals**: Your golf goals and achievement status

### Data Format

Each round is stored with:
```json
{
  "id": 1,
  "date": "2024-01-15",
  "course": "Pebble Beach",
  "score": 87,
  "par": 72,
  "differential": 15,
  "handicap_estimate": 15.2,
  "notes": "Windy conditions",
  "timestamp": "2024-01-15T14:30:00"
}
```

## Auto-Calculations

### Handicap Trend
The system calculates a simplified handicap trend based on your recent rounds using the formula:
```
Handicap = Average(last 5 differentials) × 0.96
```
(USGA handicap uses a similar approach but with more complex weighting)

### Course Statistics
For each course, the system tracks:
- **Rounds Played**: Total times you've played
- **Average Score**: Mean score across all rounds
- **Best Score**: Your lowest score on that course
- **Worst Score**: Your highest score on that course

### Performance Insights
The system automatically generates insights like:
- "Your 5-round average is improving. Last month avg: 87. This month avg: 84."
- "Great progress! You've improved by 3 strokes!"
- "Best course: Pebble Beach (avg: 82.3)"

## Validation

Input validation ensures data quality:

- **Date**: Must be YYYY-MM-DD format
- **Score**: Must be between 50 and 200
- **Par**: Must be between 60 and 80
- **Handicap**: Optional, must be a number

Invalid input triggers clear error messages.

## Testing

Run the comprehensive test suite:

```bash
# Run all tests with verbose output
python3 -m pytest tests/test_golf_tracker.py -v

# Run specific test class
python3 -m pytest tests/test_golf_tracker.py::TestGolfDataManager -v

# Run with coverage report
python3 -m pytest tests/test_golf_tracker.py --cov=app
```

The test suite includes:
- ✅ 25+ comprehensive tests
- ✅ Input validation tests
- ✅ Data persistence tests
- ✅ Calculation accuracy tests
- ✅ Edge case handling
- ✅ API endpoint tests
- ✅ Multi-course tracking tests

## API Reference

The web app exposes RESTful API endpoints:

### GET /api/rounds
Get all rounds (newest first).

**Response:**
```json
[
  {
    "id": 1,
    "date": "2024-01-15",
    "course": "Pebble Beach",
    "score": 87,
    "par": 72,
    ...
  }
]
```

### GET /api/insights
Get performance insights.

**Response:**
```json
{
  "recent_average": 84.2,
  "this_month_avg": 84.0,
  "last_month_avg": 87.5,
  "improvement": 3.5,
  "trend": "improving",
  "best_score": 78,
  "worst_score": 95,
  "total_rounds": 24,
  "best_course": {
    "name": "Pebble Beach",
    "avg_score": 82.3
  }
}
```

### POST /api/add_round
Add a new round.

**Request:**
```json
{
  "date": "2024-01-15",
  "course": "Pebble Beach",
  "score": 87,
  "par": 72,
  "handicap_estimate": 15.2,
  "notes": "Great weather"
}
```

**Response:**
```json
{
  "success": true,
  "round": {
    "id": 1,
    "date": "2024-01-15",
    ...
  }
}
```

### POST /api/add_goal
Add a new goal.

**Request:**
```json
{
  "type": "break_score",
  "target": 80,
  "description": "Break 80 by end of year"
}
```

## Logging

All operations are logged to:
```
/Users/clawdbot/clawd/golf-tracker/golf-tracker.log
```

Log entries include:
- Round additions
- Data file operations
- Errors and validation failures
- API requests

Example log entry:
```
2024-01-15 14:30:00 - app - INFO - Added round: Pebble Beach on 2024-01-15, score: 87
```

## Security & Privacy

- ✅ All data stored locally (no cloud sync)
- ✅ No external API calls
- ✅ No user accounts or authentication needed
- ✅ File permissions respect Mac system security
- ✅ Works completely offline

## Troubleshooting

### Web UI won't start
```bash
# Check if port 5050 is in use
lsof -i :5050

# Use a different port
python3 app.py  # Edit app.py to change port
```

### Data file not found
The data file is automatically created on first run. If issues persist:
```bash
# Manually create the directory
mkdir -p /Users/clawdbot/clawd/data

# Restart the application
python3 app.py
```

### Import errors
```bash
# Ensure all dependencies are installed
pip3 install -r requirements.txt
```

## Architecture

### Project Structure
```
golf-tracker/
├── app.py                  # Flask web application
├── golf_cli.py            # Command-line interface
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   ├── base.html        # Base template with styling
│   ├── index.html       # Dashboard page
│   └── add.html         # Round entry form
├── tests/
│   └── test_golf_tracker.py  # Comprehensive test suite
└── golf-tracker.log      # Application logs
```

### Data Flow
```
User Input (Web/CLI)
    ↓
Input Validation
    ↓
GolfDataManager
    ↓
JSON File Storage (/Users/clawdbot/clawd/data/golf-data.json)
    ↓
Calculations (handicap, averages, insights)
    ↓
Display (Web UI / CLI output)
```

### Key Classes

**GolfDataManager**
- Manages all data operations
- Handles file I/O
- Performs calculations
- Generates insights

**Flask App**
- Web routes (/, /add)
- API endpoints (/api/*)
- Template rendering

## Future Enhancements

Potential features for future versions:
- 📊 Chart visualizations (score over time)
- 🏌️ Hole-by-hole scoring
- 📸 Course photos
- 📤 Export to PDF/CSV
- 🌍 GPS course location tracking
- 👥 Multi-player tracking
- 🏆 Achievement badges
- 📱 Mobile-responsive design improvements

## License

This is a custom-built tool for personal use. Feel free to modify and extend as needed.

## Support

For issues or questions:
1. Check the logs: `/Users/clawdbot/clawd/golf-tracker/golf-tracker.log`
2. Run tests to verify functionality: `python3 -m pytest tests/ -v`
3. Review this documentation

---

**Version:** 1.0.0  
**Created:** 2024  
**Platform:** macOS (Mac mini)
