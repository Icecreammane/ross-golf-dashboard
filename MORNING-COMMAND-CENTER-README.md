# 🌅 Morning Command Center

**The anti-doomscroll weapon. The one dashboard to rule them all.**

Replace your phone-scrolling dopamine spiral with directed, intentional motivation.

## 🚀 Quick Start

1. **Open the dashboard:**
   - Direct: `open morning-command-center.html`
   - Or visit: `http://localhost:PORT/morning-command-center.html`

2. **Make it your home page:** Set this as your browser's startup page

3. **Add to phone home screen:** Open in Safari → Share → Add to Home Screen

## 📁 Files

| File | Purpose |
|------|---------|
| `morning-command-center.html` | Main dashboard (self-contained) |
| `morning-config.json` | Your settings, goals, priorities |
| `freedom-config.json` | Florida Freedom financial data |
| `memory/daily-wins.json` | Your logged wins |
| `fitness-tracker/fitness_data.json` | Workout & nutrition data |

## ⚙️ Configuration

Edit `morning-config.json` to customize:

### Set Your Priorities
```json
"priorities": {
  "today": [
    "Your #1 priority",
    "Your #2 priority", 
    "Your #3 priority"
  ]
}
```

### Track Your Streaks
```json
"streaks": {
  "workout_days": 3,
  "wins_logged": 5,
  "productive_days": 7,
  "no_scroll_days": 2
}
```

### Define Your Goals
```json
"goals": [
  { "name": "Launch FitTrack MVP", "progress": 60, "deadline": "2026-02-15" },
  { "name": "First Paying Customer", "progress": 20, "deadline": "2026-02-28" }
]
```

### Revenue Sources
```json
"revenue_sources": [
  { "name": "FitTrack AI", "mrr": 0, "icon": "💪" },
  { "name": "Golf Coaching", "mrr": 99, "icon": "⛳" }
]
```

### Your Why
```json
"florida_freedom": {
  "why": "Beach volleyball at sunset. Waking up without an alarm. Building something that's MINE."
}
```

### Custom Quotes
```json
"quotes": [
  "The best time to plant a tree was 20 years ago. The second best time is now.",
  "Every day you work on this is a day closer to Clearwater."
]
```

## 🔗 Data Integration

### Weather
Uses wttr.in API (no key needed). Change location:
```json
"weather": {
  "location": "Nashville",
  "enabled": true
}
```

### Fitness Data
Automatically pulls from `fitness-tracker/fitness_data.json`:
- Today's macros (calories, protein, carbs, fat)
- Last workout details
- Macro targets

### Financial Data
Pulls from `freedom-config.json`:
- Current MRR
- Target MRR
- Florida Fund progress
- Target date countdown

### Daily Wins
Pulls from `memory/daily-wins.json`:
- Recent wins displayed in dashboard
- Add wins via Quick Actions

## 📱 Mobile Setup

### iPhone/iPad
1. Open in Safari
2. Tap Share button
3. "Add to Home Screen"
4. Name it "Command Center"
5. Now it opens like a native app!

### Android
1. Open in Chrome
2. Menu → "Add to Home Screen"
3. Or "Install App" if prompted

## 🎨 Features

### Dark/Light Mode
- Click 🌙/☀️ in top right
- Preference saved automatically

### Anti-Scroll Timer
- Warning after 5 minutes on page
- Reminder to get moving
- Configure in `morning-config.json`:
```json
"anti_scroll": {
  "warning_after_minutes": 5,
  "enabled": true
}
```

### Social Media Shame Toggle
- Track if you've doomscrolled today
- Visual shame counter
- Break your streak = reset your progress

### Keyboard Shortcuts
- `Escape` - Close modal
- `Enter` - Submit modal

## 🔄 Auto-Refresh

Dashboard auto-updates every 60 seconds:
- Weather
- Financial data
- Fitness data
- Wins

## 📊 Sections Explained

1. **Hero Stats** - Days to Florida, MRR, Weather (the big numbers)
2. **Today's Mission** - Your top 3 priorities (tap to complete)
3. **Momentum Tracker** - Streaks and consistency metrics
4. **Recent Wins** - Your logged victories
5. **Goal Progress** - Visual progress bars
6. **Revenue Sources** - Your empire at a glance
7. **Today's Fuel** - Macros and last workout
8. **Focus Shield** - Anti-distraction tools
9. **Motivation** - Quote + Your Why
10. **Quick Actions** - One-tap tasks

## 🛠️ Advanced: Calendar Integration

To add calendar events, you'd need a backend service. Options:
1. Use Google Calendar API with a simple proxy
2. Manual entry in config
3. Apple Calendar via AppleScript (local only)

For now, manage priorities manually in `morning-config.json`.

## 💡 Tips

1. **Morning Routine:** Open this FIRST, before any other app
2. **Set 3 priorities** the night before
3. **Log wins daily** - builds momentum
4. **Update streaks** weekly to stay honest
5. **Customize quotes** with what resonates with YOU

## 🎯 Success Metrics

You're using this right if:
- ✅ First thing you open each morning
- ✅ Replaces 20+ min of phone scrolling
- ✅ You know your MRR without checking
- ✅ You can recite your top 3 priorities
- ✅ Florida countdown motivates you daily

---

**This is your anti-doomscroll weapon. Use it daily. Crush it. Get to Florida.** 🌴
