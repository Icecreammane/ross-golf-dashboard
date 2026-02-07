# 🌴 Florida Freedom Dashboard

**Your escape countdown and motivation center.**

A beautiful, full-screen dashboard that visualizes your journey from corporate Tennessee to beach life Florida.

---

## 🚀 Quick Start

### Option 1: Open Directly in Browser
```bash
open ~/clawd/florida-freedom-dashboard.html
```

### Option 2: Serve Locally (Recommended)
```bash
cd ~/clawd
python3 -m http.server 8000
```
Then open: **http://localhost:8000/florida-freedom-dashboard.html**

---

## 📊 Features

### ⏰ Countdown Timer
- Real-time countdown to your freedom date (June 15, 2026)
- Shows days, hours, and minutes remaining
- Updates every second

### 🏢 Corporate Prison Sentence
- Calculates remaining **workdays** (Monday-Friday only)
- Progress bar showing how much of the sentence is complete
- Visual motivation to see the cage shrinking

### 💰 Financial Trackers

**MRR Tracker (Escape Velocity)**
- Current Monthly Recurring Revenue vs. $3,000 target
- Color-coded progress bars:
  - 🔴 Red: <30%
  - 🟡 Yellow: 30-70%
  - 🟢 Green: >70%

**Florida Fund (Move Money)**
- Savings progress toward $50,000 move goal
- Same color-coded system

### 📊 Freedom Date Projection
- Calculates when you'll be financially free based on current MRR growth
- Assumes 50% of MRR can be saved toward the fund
- Shows months needed and amount remaining

### 🌡️ Weather Comparison
- Live weather: **Nolensville, TN** vs. **Clearwater, FL**
- Pulled from wttr.in API (updates every 60 seconds)
- Visual reminder of paradise waiting for you

### 🛫 Runway Calculator
- Projects Florida Fund growth over 12 months
- Visual Chart.js graph showing trajectory to goal
- Compares current fund vs. target line

### 🏖️ Live Beach Webcam
- Embedded 24/7 live stream from Clearwater Beach
- Your future view
- Muted autoplay for ambient motivation

### 🏐 Beach Volleyball Map
- Google Maps embed showing volleyball courts in Tampa/St. Pete area
- Your future playground mapped out

### 💪 Daily Fire
- Rotating motivational quotes about freedom, risk, and escaping 9-5
- Changes every refresh

### ✅ Recent Wins
- Displays your last 5 achievements from `memory/daily-wins.json`
- Visual reminder of progress

---

## ⚙️ Configuration

### Edit Your Data: `freedom-config.json`

```json
{
  "target_date": "2026-06-15",
  "current_mrr": 0,
  "target_mrr": 3000,
  "florida_fund": 0,
  "florida_fund_goal": 50000,
  "current_location": "Nolensville, TN",
  "target_location": "Clearwater, FL",
  "monthly_expenses": 500
}
```

**Update these values as you make progress:**
- `current_mrr`: Your actual monthly recurring revenue
- `florida_fund`: Current amount saved toward move
- `target_date`: Change if your freedom date shifts
- `monthly_expenses`: Your average monthly spending (for runway calc)

**The dashboard auto-refreshes every 60 seconds** to pick up changes.

---

## 🏆 Logging Wins

Create or edit `memory/daily-wins.json`:

```json
{
  "wins": [
    "Built fitness tracker",
    "Launched golf page",
    "First paying customer",
    "Hit $500 MRR",
    "Closed a freelance deal"
  ]
}
```

Add your wins to the `wins` array. The dashboard shows the **last 5** in reverse order (newest first).

---

## 🎨 Design Features

- **Dark theme** with beach/ocean aesthetic
- **Sunrise/sunset gradient background**
- **Teal, blue, and sandy beige** color palette
- **Glassmorphism effects** (backdrop blur, transparency)
- **Hover animations** on cards
- **Mobile responsive** - looks great on phone, tablet, desktop
- **Zero dependencies** except Chart.js (CDN)

---

## 🔧 Technical Details

- **Self-contained HTML** file
- **Inline CSS and JavaScript**
- **Chart.js** for runway visualization (loaded via CDN)
- **wttr.in API** for weather data
- **No backend required** - runs entirely in the browser
- **Auto-refresh** every 60 seconds
- **Live countdown** updates every second

---

## 📱 Mobile Use

The dashboard is fully responsive. Add it to your phone's home screen:

**iOS Safari:**
1. Open dashboard in Safari
2. Tap Share button
3. Tap "Add to Home Screen"
4. Name it "Florida Freedom"

**Android Chrome:**
1. Open dashboard in Chrome
2. Tap menu (⋮)
3. Tap "Add to Home screen"

Now you have a dedicated app icon!

---

## 🎯 Daily Ritual

**Make this your morning routine:**

1. Open the dashboard (or check your phone home screen shortcut)
2. See the countdown shrink
3. Update your MRR and fund in `freedom-config.json`
4. Add yesterday's wins to `daily-wins.json`
5. Watch the progress bars grow
6. Look at the beach cam
7. Read the motivational quote

**Every day closer. Every build matters.**

---

## 🛠️ Customization Ideas

- Change the target date in config
- Add more motivational quotes in the HTML (`quotes` array)
- Swap the beach webcam URL (find other live cams on YouTube)
- Adjust the map location (change Google Maps embed URL)
- Modify colors in CSS (search for color codes like `#00bcd4`)
- Change the refresh interval (default: 60 seconds)

---

## 🐛 Troubleshooting

**Weather not loading?**
- Check internet connection
- wttr.in might be temporarily down (it's free and sometimes slow)
- Refresh the page

**Dashboard not updating?**
- Make sure you saved `freedom-config.json`
- Check browser console for errors (F12 → Console)
- Wait 60 seconds for auto-refresh (or refresh manually)

**Webcam not playing?**
- Some browsers block autoplay - click to play manually
- YouTube embed might require interaction first

**Chart not showing?**
- Make sure Chart.js CDN is accessible
- Check browser console for errors

---

## 📂 Files

- `florida-freedom-dashboard.html` - Main dashboard (open this)
- `freedom-config.json` - Your editable data
- `memory/daily-wins.json` - Your achievements log
- `FLORIDA_FREEDOM_README.md` - This file

---

## 💭 Philosophy

This dashboard is more than numbers. It's a daily reminder that:

- **Your current situation is temporary**
- **Every small win compounds**
- **Freedom is a choice, not a dream**
- **The beach is waiting**

Look at it every morning. Update it every day. **Feel the Florida dream getting closer.**

127 days until freedom. Let's make them count.

🌊 **See you on the beach, brother.** 🏐

---

## 📸 Screenshot

*(Open the dashboard to see it in action!)*

---

**Built with determination and beach dreams.**  
**For Ross - From Tennessee to Clearwater.**  
**Every day closer. Every build matters.**
