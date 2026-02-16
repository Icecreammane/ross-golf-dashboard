# Quick Start: Assistant Features

2 minute setup guide for both add-on features.

---

## 🎯 1. Smart Expense Categorizer + Tax Helper

### Start the Financial Dashboard:
```bash
cd ~/clawd/plaid-integration
python3 app_with_tax_helper.py
```

### Access:
- Dashboard: http://localhost:5002
- API docs: http://localhost:5002/api/tax/dashboard

### Test It:
```bash
# Categorize a transaction
curl -X POST http://localhost:5002/api/tax/categorize \
  -H "Content-Type: application/json" \
  -d '{"description": "Laptop for work", "amount": 1200, "merchant": "Apple Store"}'

# Check if deductible
curl -X POST http://localhost:5002/api/tax/deductions/check \
  -H "Content-Type: application/json" \
  -d '{"description": "Office chair", "category": "work", "amount": 300}'

# Get dashboard data
curl http://localhost:5002/api/tax/dashboard
```

### What You See:
- **YTD Deductions Widget** - Total potential tax savings
- **Monthly Deductions** - This month's deductible expenses
- **Top 3 Categories** - Highest deduction categories
- **Export Button** - One-click CSV export for tax time

---

## 📊 2. Performance Analytics Dashboard

### Already Integrated!
The Lean Fitness Tracker already has analytics.

### Access:
1. Start Lean Tracker (if not running):
   ```bash
   cd ~/clawd/fitness-tracker
   python3 app_pro.py
   ```

2. Go to: http://localhost:5001/analytics

### What You See:
- **Weight Loss Patterns** - "You lose most weight on weeks you lift 5+ times"
- **Best Workout Days** - Top 3 most consistent days
- **Goal Prediction** - "On pace to hit 200 lbs by May 19"
- **Weekly Comparison** - This week vs last week
- **Optimization Suggestions** - Actionable improvements
- **Charts** - Weight trend, workout frequency heatmap

---

## 🔗 Integration Notes

### For Mission Control Dashboard:
Add these widgets to main dashboard at `~/clawd/mission_control/`:

**Tax Helper Widget:**
```html
<div class="widget" onclick="window.location='/tax-helper'">
  <h3>💰 Tax Deductions YTD</h3>
  <div class="value" id="ytd-deductions">$0</div>
  <script>
    fetch('http://localhost:5002/api/tax/dashboard')
      .then(r => r.json())
      .then(d => {
        document.getElementById('ytd-deductions').textContent = 
          `$${d.ytd_total.toLocaleString()}`;
      });
  </script>
</div>
```

**Analytics Widget:**
```html
<div class="widget" onclick="window.location='http://localhost:5001/analytics'">
  <h3>📊 Goal Pace</h3>
  <div class="value" id="goal-status">Loading...</div>
  <script>
    fetch('http://localhost:5001/api/analytics')
      .then(r => r.json())
      .then(d => {
        const status = d.goal_prediction.on_pace ? 'On Track ✓' : 'Behind Pace';
        document.getElementById('goal-status').textContent = status;
      });
  </script>
</div>
```

### For Lean Tracker Dashboard:
Add analytics link button to `~/clawd/fitness-tracker/templates/dashboard.html`:

```html
<a href="/analytics" class="analytics-button" style="
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px 30px;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  margin-top: 20px;
">
  📊 View Performance Analytics
</a>
```

---

## 📝 Data Requirements

### Tax Helper:
Needs transactions in database with:
- `date` (ISO format)
- `name` (transaction description)
- `amount` (float)
- `merchant_name` (optional)
- `location` (optional, for smart rules)

### Performance Analytics:
Needs fitness data with:
- `weights`: Array of {date, weight}
- `workouts`: Array of {date, type, ...}
- `meals`: Array of {date, calories, protein, ...}

Both features work with existing data structures!

---

## 🐛 Troubleshooting

### Tax Helper not loading?
```bash
# Check if server is running
lsof -i :5002

# Check logs
tail -f ~/clawd/plaid-integration/server.log
```

### Analytics not showing data?
```bash
# Verify fitness_data.json exists
ls -la ~/clawd/fitness-tracker/fitness_data.json

# Test analytics engine
cd ~/clawd/fitness-tracker
python3 performance_analytics.py
```

### Import errors?
```bash
# Install dependencies
cd ~/clawd
pip3 install -r requirements-assistant-features.txt
```

---

## ✅ Success Checklist

After setup, you should be able to:

### Tax Helper:
- [ ] View YTD deductions total
- [ ] See top 3 deductible categories
- [ ] Export CSV with all deductions
- [ ] Auto-categorize new transactions

### Performance Analytics:
- [ ] See weight loss patterns
- [ ] View best workout days
- [ ] Get goal completion prediction
- [ ] Read optimization suggestions
- [ ] View weight trend chart
- [ ] View workout frequency heatmap

---

**Setup time: ~2 minutes**  
**Value delivered: Immediate**

🎉 Done! Start tracking and watch the insights appear.
