# Spending Accountability System - Plaid Integration

**Real-time financial visibility + automatic categorization + coaching insights**

Ross's problem: A month behind on manual expense tracking, no real-time visibility.  
The solution: Automated spending tracker that pulls from bank/credit cards/Venmo via Plaid.

---

## 🚀 Quick Start

### 1. Get Plaid API Keys

**Sandbox (for testing):**
1. Go to https://dashboard.plaid.com/signup
2. Create free account
3. Get your `client_id` and `secret` from the dashboard
4. Start with sandbox environment

**Production (for real data):**
1. Apply for Plaid Production access
2. Complete verification
3. Get production keys

### 2. Configure Credentials

```bash
cp ~/.clawdbot/credentials/plaid.json.template ~/.clawdbot/credentials/plaid.json
```

Edit `~/.clawdbot/credentials/plaid.json`:
```json
{
  "client_id": "YOUR_CLIENT_ID",
  "secret": "YOUR_SECRET",
  "environment": "sandbox"
}
```

**Security:**
- File is gitignored
- Permissions set to 600 (owner read/write only)
- Never commit credentials

### 3. Connect Accounts

```bash
cd ~/clawd
python3 scripts/plaid_setup.py
```

**Sandbox mode:**
- Browser opens with Plaid Link
- Select "First Platypus Bank" (or any test institution)
- Username: `user_good`
- Password: `pass_good`
- Complete flow and paste public token

**Production mode:**
- Connect real bank accounts
- Connect credit cards
- Connect Venmo

Repeat for each account you want to track.

### 4. Initial Sync

Pull last 30 days of transactions:

```bash
python3 scripts/sync_transactions.py --initial
```

### 5. Start Dashboard

```bash
# Terminal 1: Start API
python3 scripts/spending_api.py

# Terminal 2: Open dashboard
open dashboard/spending.html
```

Dashboard: http://localhost:5002

---

## 📊 Features

### Real-Time Dashboard
- **Today's spending** - Live total + breakdown
- **This week** - Total + comparison to last week
- **This month** - Total + daily average + projection
- **Category charts** - Visual breakdown (dining, groceries, gas, etc.)
- **Spending trends** - 30-day line chart
- **Recent transactions** - Last 20 purchases

### Automatic Categorization
Plaid categories mapped to Ross-relevant buckets:
- **Dining Out** - Restaurants, DoorDash, fast food
- **Groceries** - Supermarkets, grocery stores
- **Gas & Transportation** - Gas stations, Uber, public transit
- **Subscriptions** - Netflix, Spotify, gyms
- **Shopping** - Amazon, Target, retail
- **Entertainment** - Bars, events, recreation
- **Other** - Everything else

### Spending Alerts
```bash
# Daily summary
python3 scripts/spending_alerts.py daily

# Evening check-in (full summary)
python3 scripts/spending_alerts.py evening

# Morning brief (yesterday's spending)
python3 scripts/spending_alerts.py morning

# Weekly alerts
python3 scripts/spending_alerts.py weekly

# Financial insights
python3 scripts/spending_alerts.py insights
```

**Alert types:**
- ⚠️ Spending up >20% vs last week
- ✅ Spending down >20% (positive reinforcement!)
- 💳 Large transactions (>$100)
- 💡 Optimization opportunities (dining vs groceries)
- 📱 Subscription audits

### Coaching Insights
- **Dining optimization:** Compare dining out vs groceries, suggest meal prep savings
- **Subscription audit:** Flag monthly subscription costs
- **Top merchants:** Show where money actually goes
- **Averages:** Daily/weekly/monthly spending patterns
- **Annual projections:** "$400/mo on DoorDash = $4,800/year"

---

## 🤖 Automation

### Daily Transaction Sync (2am)

Automatically pulls new transactions every night:

```bash
bash scripts/setup_spending_cron.sh
```

Then add to crontab:
```
0 2 * * * cd ~/clawd && python3 scripts/sync_transactions.py >> logs/spending_sync.log 2>&1
```

### Evening Summary (8pm)

Integrate with evening check-in:

```python
# In your evening check-in script
import subprocess
result = subprocess.run(
    ['python3', 'scripts/spending_alerts.py', 'evening'],
    capture_output=True,
    text=True,
    cwd=os.path.expanduser('~/clawd')
)
spending_summary = result.stdout
# Include in evening message
```

### Morning Brief

Yesterday's spending for morning brief:

```python
result = subprocess.run(
    ['python3', 'scripts/spending_alerts.py', 'morning'],
    capture_output=True,
    text=True,
    cwd=os.path.expanduser('~/clawd')
)
# Include in morning brief
```

---

## 🗂️ File Structure

```
~/clawd/
├── scripts/
│   ├── plaid_setup.py           # Account connection
│   ├── sync_transactions.py     # Transaction sync
│   ├── spending_api.py          # Flask API
│   ├── spending_alerts.py       # Alerts & insights
│   └── setup_spending_cron.sh   # Cron setup helper
├── dashboard/
│   └── spending.html            # Web dashboard
├── data/
│   ├── transactions.json        # All transactions (append-only)
│   ├── transaction_sync_state.json  # Last sync metadata
│   └── spending_alerts.json     # Alert history
└── .credentials/
    ├── plaid.json               # API credentials
    └── plaid_tokens.json        # Access tokens (per account)
```

---

## 🔒 Security & Privacy

### Local-Only Storage
- All data stays on Ross's machine
- No cloud storage
- No external API calls (except Plaid)

### Read-Only Access
- Plaid integration is view-only
- Cannot move money
- Cannot make payments
- Can only fetch transaction history

### Credential Protection
- Stored in `~/.clawdbot/credentials/` (gitignored)
- File permissions: 600 (owner only)
- Never logged or exposed
- Encrypted at rest by macOS FileVault

### Access Tokens
- One per connected institution
- Revocable via Plaid dashboard
- Can disconnect accounts anytime

---

## 📈 API Endpoints

**Base URL:** http://localhost:5002/api

### GET /health
Health check

### GET /today
Today's spending summary
```json
{
  "date": "2026-02-16",
  "total_spent": 67.45,
  "transaction_count": 5,
  "by_category": {"Dining Out": 35.00, "Gas & Transportation": 32.45},
  "recent_transactions": [...]
}
```

### GET /week
This week's summary + comparison to last week

### GET /month
This month's summary + daily average + projection

### GET /categories
Category breakdown (last 30 days) with percentages

### GET /trends
Daily spending over last 30 days (for charts)

### GET /merchants
Top merchants by spending

### GET /transactions/recent?limit=20
Recent transactions

### GET /stats
Overall statistics (lifetime data)

---

## 🔧 Maintenance

### Add New Account
```bash
python3 scripts/plaid_setup.py
```

### List Connected Accounts
```bash
python3 scripts/plaid_setup.py list
```

### Manual Sync
```bash
# Incremental (new transactions only)
python3 scripts/sync_transactions.py

# Full resync (last 30 days)
python3 scripts/sync_transactions.py --initial
```

### View Logs
```bash
tail -f logs/spending_sync.log
tail -f logs/spending_alerts.log
```

### Backup Transactions
```bash
cp data/transactions.json data/transactions_backup_$(date +%Y%m%d).json
```

---

## 🎯 Success Criteria

✅ Plaid connected to:
- Bank account
- Credit cards
- Venmo

✅ Transactions sync daily (automated)

✅ Dashboard shows real-time spending

✅ Categories make sense (dining, gas, groceries, etc.)

✅ Alerts fire when overspending detected

✅ Ross can check anytime: "Show me my spending"

✅ Financial awareness = better decisions

---

## 🐛 Troubleshooting

### "No accounts connected"
Run `python3 scripts/plaid_setup.py` to connect accounts.

### "Error fetching transactions"
Check:
1. Credentials in `~/.clawdbot/credentials/plaid.json`
2. Environment (sandbox vs production)
3. Access tokens in `plaid_tokens.json`
4. Plaid account status

### Dashboard shows $0
1. Run `python3 scripts/sync_transactions.py --initial`
2. Check `data/transactions.json` exists and has data
3. Restart API: `python3 scripts/spending_api.py`
4. Refresh dashboard

### Categories wrong
Edit category mappings in `scripts/sync_transactions.py`:
```python
CATEGORY_MAP = {
    'Your Category': ['Plaid, Category, Pattern'],
    ...
}
```

Re-sync to update categories.

---

## 🚀 Next Steps

### Phase 2 Ideas
1. **Budget alerts** - Set category budgets, alert when exceeded
2. **SMS alerts** - Real-time notifications for large purchases
3. **Recurring transaction detection** - Flag subscriptions automatically
4. **Merchant analysis** - "You visit Starbucks 23x/month"
5. **Weekly reports** - Email summary every Friday
6. **Goal tracking** - "Save $500/mo for Florida fund"
7. **Comparison mode** - "Your dining: $400/mo vs avg: $250/mo"

### Production Migration
When ready for real data:
1. Apply for Plaid Production access
2. Update `environment` to `production` in credentials
3. Re-run `plaid_setup.py` to connect real accounts
4. Sync historical data (up to 2 years depending on institution)

---

## 💡 Pro Tips

### Daily Check-In
Pull up dashboard every evening: "Where did my money go today?"

### Weekly Review
Friday: Review weekly alert + identify optimization opportunities.

### Monthly Analysis
End of month: Compare actual vs projected. Adjust habits for next month.

### Category Customization
Customize categories to match YOUR spending patterns:
- Add "Golf" category if you track that separately
- Split "Entertainment" into "Bars" and "Events"
- Create "Side Hustle Expenses" for business costs

### Integration with Florida Fund
Use insights to find money for Florida:
- "DoorDash costs $400/mo → meal prep saves $250 → Florida fund gets $250"

---

## 📞 Support

**Check connection status:**
```bash
python3 scripts/plaid_setup.py list
```

**Test API:**
```bash
curl http://localhost:5002/api/health
curl http://localhost:5002/api/today
```

**Clear and resync:**
```bash
rm data/transactions.json
rm data/transaction_sync_state.json
python3 scripts/sync_transactions.py --initial
```

---

**The Unlock:**

Ross is never "a month behind" on finances again. Real-time visibility = conscious spending = more money toward Florida.

Financial awareness is the first step to financial freedom. 🎯
