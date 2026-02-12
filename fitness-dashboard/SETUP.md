# Fitness Dashboard - Setup Guide

## 🚀 Quick Start

### Step 1: Install Flask (if needed)
```bash
pip3 install Flask
```

### Step 2: Start the Dashboard
```bash
cd ~/clawd/fitness-dashboard
bash start.sh
```

Or manually:
```bash
cd ~/clawd/fitness-dashboard
python3 app.py
```

### Step 3: Open in Browser
Navigate to: **http://localhost:3001**

## ✨ Features Overview

### 📊 Stats Cards (Top of Dashboard)
- **Today's Calories** - Real-time tracking vs 2200 cal goal
- **Protein Today** - Tracking vs 200g goal
- **Current Weight** - Your latest weight entry
- **Workouts This Week** - Last 7 days of activity

### 📈 Charts
1. **Daily Calorie Tracking** - Bar chart showing last 7 days with goal line
2. **Weight Progress** - Line graph showing weight trend over time
3. **Workout Calendar** - Visual calendar of workout sessions

### ➕ Quick Log Section
Three easy-to-use forms at the bottom:

**Log Meal:**
- Enter calories and protein
- Add meal description
- Instantly updates charts

**Log Workout:**
- Choose from: Legs, Chest, Back, Arms, Shoulders, Cardio
- Add optional notes
- Updates calendar view

**Log Weight:**
- Enter current weight
- Tracks trend over time

## 📱 Mobile Friendly
The dashboard automatically adapts to phone screens - track on the go!

## 🔄 Auto-Refresh
Dashboard updates every 30 seconds automatically. No need to refresh manually.

## 📦 Pre-Populated Data

Your dashboard comes with sample data to show trends:

**Weight Entries:**
- 2/1: 227 lbs
- 2/5: 226 lbs
- 2/8: 225 lbs (current)

**Workouts:**
- 2/8: Legs
- 2/10: Legs
- 2/11: Chest

**Calories (Last 6 Days):**
- Sample data around 2100-2300 cal range

This helps visualize the charts immediately. Start logging your real data and it will blend in!

## 🗂️ Data Storage

All data stored in `data/` folder as JSON:
- `calories.json` - Meal logs with calories and descriptions
- `workouts.json` - Workout sessions with type and notes
- `weight.json` - Weight measurements over time
- `macros.json` - Protein and other macro tracking

You can edit these files directly if needed, or use the dashboard interface.

## 🔧 Customization

### Change Goals
Edit in `app.py`:
```python
"calorie_goal": 2200,  # Change to your target
"protein_goal": 200    # Change to your target
```

### Add Workout Types
Edit in `templates/index.html`, find the workout select:
```html
<option value="YourWorkout">Your Workout</option>
```

## 🚨 Troubleshooting

**Port already in use?**
Change port in `app.py`:
```python
app.run(host='0.0.0.0', port=3001, debug=True)  # Change 3001 to another port
```

**Flask not installed?**
```bash
pip3 install Flask
```

**Can't access from phone?**
Make sure you're on the same WiFi network, then use:
```
http://YOUR_MAC_IP:3001
```
Find your Mac's IP: System Settings → Network

## 💡 Tips

1. **Log as you go** - Quick entries keep data accurate
2. **Check trends** - Weekly view helps spot patterns
3. **Use notes** - Track how workouts felt, meal details, etc.
4. **Daily weigh-ins** - Best in morning for consistency
5. **Mobile bookmark** - Save dashboard to home screen for quick access

## 🎯 Daily Workflow

**Morning:**
- Log weight after waking up
- Check yesterday's summary

**Throughout Day:**
- Quick-log meals after eating
- Track protein intake

**After Workout:**
- Log workout type and notes

**Evening:**
- Review daily totals
- Check progress vs goals

## 📊 Understanding Your Data

**Calorie Bar Chart:**
- Green/purple bars = daily intake
- Red dashed line = 2200 cal goal
- Aim to stay consistent around goal

**Weight Line Graph:**
- Shows trend over time
- Week-to-week changes more important than daily
- Look for downward trend if cutting

**Workout Calendar:**
- Purple = workout completed
- Gray = rest day
- Aim for 3-5 sessions per week

## 🔐 Privacy
All data stays local on your Mac. Nothing is uploaded to cloud services.

## 🎨 Color Scheme
Purple gradient theme (`#667eea` to `#764ba2`) - can be customized in the HTML file's `<style>` section.

---

**Need help?** Check the main README.md or ask Jarvis!
