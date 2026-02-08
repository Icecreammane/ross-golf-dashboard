# 💰 Revenue Dashboard

**Single source of truth for tracking your path to $500 MRR**

---

## 🚀 Quick Start

### Open the Dashboard

**Option 1: Double-click** (macOS/Windows)
```
Double-click `index.html` in Finder
```

**Option 2: Terminal**
```bash
cd ~/clawd/revenue-dashboard
open index.html  # macOS
# or
xdg-open index.html  # Linux
# or
start index.html  # Windows
```

**Option 3: Simple HTTP Server** (recommended)
```bash
cd ~/clawd/revenue-dashboard
python3 -m http.server 8000
# Then open: http://localhost:8000
```

---

## 📊 What's Inside

### 8 Dashboard Widgets:

1. **🎯 MRR Tracker** - Current MRR vs $500 goal with progress bar
2. **💳 Income Streams** - Visual breakdown of all revenue sources
3. **📊 This Week** - Recent performance metrics
4. **🗺️ Path to $500** - Three scenarios to hit your goal
5. **🌴 Florida Fund** - Long-term savings goal ($50k)
6. **⚡ Quick Actions** - Launch, create, analyze, optimize
7. **📝 Recent Activity** - Last 10 revenue events
8. **🎯 Next Milestones** - Key goals and timelines

---

## ✏️ How to Update Data

### Manual Update (Current Method)

1. **Open data.json** in any text editor
2. **Update values:**
   ```json
   {
     "mrr": {
       "current": 50,  // ← Update this
       "goal": 500
     }
   }
   ```
3. **Save the file**
4. **Refresh browser** (⌘R / Ctrl+R)

### What to Update:

**When you get a new customer:**
```json
"incomeStreams": [
  {
    "id": "fitness-tracker",
    "mrr": 30,        // ← Add $10 per customer
    "users": 3        // ← Increment
  }
]
```

**When you launch a product:**
```json
{
  "status": "live",              // ← Change from "not_launched"
  "launchDate": "2026-02-08"     // ← Add launch date
}
```

**Weekly stats:**
```json
"thisWeek": {
  "revenue": 30,           // ← Total revenue this week
  "newCustomers": 3,       // ← New signups
  "conversionRate": 5.2,   // ← Conversion %
  "traffic": 58            // ← Visitors
}
```

**New activity:**
```json
"recentActivity": [
  {
    "date": "2026-02-08",
    "type": "revenue",           // or "milestone", "customer"
    "description": "First customer! John signed up",
    "amount": 10
  },
  // ... existing items
]
```

---

## 🔮 Future Integrations

**Coming soon:** Automatic data updates via APIs

### Stripe Integration
- Auto-update MRR when customers subscribe
- Track churn, upgrades, downgrades
- Real-time revenue tracking

### Gumroad Integration
- Auto-log template sales
- Track conversion rates
- Revenue notifications

### Plaid Integration
- Connect bank account
- Track Florida Fund savings
- Automatic progress updates

### Google Analytics Integration
- Real-time traffic stats
- Conversion tracking
- Funnel analysis

**For now:** Manual updates = full control, no API complexity

---

## 🎨 Features

✅ **Clean, Stripe-inspired design**  
✅ **Mobile responsive**  
✅ **Print-friendly** (share progress)  
✅ **Fast** (static HTML, no server needed)  
✅ **Motivating** (visual progress = psychological win)  
✅ **Flexible** (easy to customize)  

---

## 🛠️ Customization

### Change Colors

Edit `styles.css`:
```css
:root {
    --primary-blue: #635bff;  /* ← Your brand color */
    --purple: #8b5cf6;
    --green: #10b981;
}
```

### Add Income Stream

Edit `data.json`:
```json
{
  "id": "new-product",
  "name": "Your Product Name",
  "type": "recurring",  // or "one-time"
  "mrr": 0,
  "users": 0,
  "pricePerMonth": 20,
  "status": "planned",
  "color": "#f59e0b"  // Any hex color
}
```

### Change Goals

```json
"mrr": {
  "current": 0,
  "goal": 1000  // ← Adjust your target
}
```

---

## 📈 Tips for Success

### Update Weekly
- Every Sunday night, update your stats
- Track trends (are you growing?)
- Celebrate small wins

### Be Honest
- Don't fudge numbers
- Track failures too (they're data)
- Realistic projections > optimistic fantasies

### Use It Daily
- Open it every morning
- Let it guide decisions
- Stay focused on the goal

### Share Progress
- Screenshot milestones
- Post wins on Twitter
- Build in public

---

## 🐛 Troubleshooting

**Dashboard not loading?**
- Make sure all 4 files are in the same folder
- Check browser console for errors (F12)
- Try using a simple HTTP server

**Chart not showing?**
- Check if Chart.js CDN is accessible
- View source, make sure script tag loads

**Data not updating?**
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
- Check `data.json` syntax (use JSONLint.com)

---

## 📁 File Structure

```
revenue-dashboard/
├── index.html       # Main dashboard page
├── dashboard.js     # Data loading + rendering logic
├── styles.css       # Clean, Stripe-inspired design
├── data.json        # Your revenue data (update this!)
└── README.md        # This file
```

---

## 🎯 Your Mission

**From $0 → $500 MRR → Florida Move**

This dashboard is your mission control. Use it every day. Track every dollar. Celebrate every win.

You got this. 🚀

---

**Built by Jarvis** | Sunday, Feb 8, 2026
