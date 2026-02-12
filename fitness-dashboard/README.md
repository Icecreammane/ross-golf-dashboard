# Fitness Progress Dashboard

A beautiful, mobile-friendly dashboard for tracking Ross's fitness journey.

## Features

✅ **Calorie Tracking**
- Daily calorie intake vs 2200 cal goal
- Visual bar chart showing last 7 days
- Progress bar showing today's progress

✅ **Workout Logging**
- Calendar view of workouts
- Quick-log interface for different workout types
- Weekly workout count

✅ **Weight Tracking**
- Trend line graph showing weight over time
- Easy weight entry

✅ **Macro Breakdown**
- Protein tracking (200g daily goal)
- Progress visualization

✅ **Auto-Refresh**
- Dashboard updates every 30 seconds
- Always current data

## Installation

```bash
cd ~/clawd/fitness-dashboard
pip3 install -r requirements.txt
```

## Running

```bash
python3 app.py
```

Then open: **http://localhost:3001**

## Quick Start

The dashboard comes pre-populated with:
- Weight: 225 lbs (2/8)
- Workout: Legs (2/10)
- Workout: Chest (2/11)

Just start logging your meals and workouts!

## Data Storage

All data is stored in JSON files in the `data/` directory:
- `calories.json` - Meal logs
- `workouts.json` - Workout sessions
- `weight.json` - Weight measurements
- `macros.json` - Protein and other macros

Easy to migrate to a database later if needed.

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Charts:** Chart.js
- **Storage:** JSON files
- **Port:** 3001

## Usage

### Log a Meal
1. Enter calories and protein
2. Add meal description (optional)
3. Click "Log Meal"

### Log a Workout
1. Select workout type from dropdown
2. Add notes (optional)
3. Click "Log Workout"

### Log Weight
1. Enter current weight in lbs
2. Click "Log Weight"

All changes update the dashboard immediately!
