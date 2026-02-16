# 💰 Spending Accountability System

**Real-time financial visibility powered by Plaid**

---

## What This Does

- ✅ Connects to banks, credit cards, Venmo via Plaid
- ✅ Automatically syncs transactions daily
- ✅ Categorizes spending (dining, groceries, gas, etc.)
- ✅ Real-time dashboard with charts and insights
- ✅ Smart alerts when overspending
- ✅ Financial coaching insights
- ✅ Local storage (no cloud, fully private)

---

## Quick Start

**Full guide:** [`docs/SPENDING_QUICKSTART.md`](../docs/SPENDING_QUICKSTART.md)

```bash
# 1. Configure Plaid credentials
cp ~/.clawdbot/credentials/plaid.json.template ~/.clawdbot/credentials/plaid.json
# Edit plaid.json with your API keys

# 2. Connect accounts
python3 ../scripts/plaid_setup.py

# 3. Sync transactions
python3 ../scripts/sync_transactions.py --initial

# 4. Start dashboard
bash ../scripts/start_spending_dashboard.sh
```

---

## Components

### Scripts (`../scripts/`)
- **plaid_setup.py** - Connect bank accounts
- **sync_transactions.py** - Pull transaction data
- **spending_api.py** - Flask API backend
- **spending_alerts.py** - Alerts and insights
- **start_spending_dashboard.sh** - Launch everything

### Dashboard (`../dashboard/`)
- **spending.html** - Interactive web dashboard

### Data (`../data/`)
- **transactions.json** - All transactions
- **transaction_sync_state.json** - Sync metadata
- **spending_alerts.json** - Alert history

---

## Daily Commands

```bash
# Check today's spending
python3 ../scripts/spending_alerts.py daily

# Evening summary
python3 ../scripts/spending_alerts.py evening

# Insights
python3 ../scripts/spending_alerts.py insights

# Manual sync
python3 ../scripts/sync_transactions.py

# View dashboard
open ../dashboard/spending.html
```

---

## Automation

### Cron Setup

```bash
# Add to crontab (crontab -e)

# Daily sync at 2am
0 2 * * * cd ~/clawd && python3 scripts/sync_transactions.py >> logs/spending_sync.log 2>&1
```

### Integration

See [`docs/SPENDING_INTEGRATION_EXAMPLE.md`](../docs/SPENDING_INTEGRATION_EXAMPLE.md) for:
- Evening check-in integration
- Morning brief integration
- Voice command support
- Telegram bot commands
- API usage examples

---

## API Endpoints

**Base:** http://localhost:5002/api

- `GET /health` - Health check
- `GET /today` - Today's spending
- `GET /week` - This week's summary
- `GET /month` - This month's summary
- `GET /categories` - Category breakdown
- `GET /trends` - Daily trends (30 days)
- `GET /merchants` - Top merchants
- `GET /transactions/recent` - Recent transactions
- `GET /stats` - Overall statistics

---

## Security

- 🔒 All data local (no cloud)
- 🔒 Read-only Plaid access
- 🔒 Credentials encrypted at rest
- 🔒 File permissions: 600
- 🔒 Gitignored sensitive files

---

## Troubleshooting

**Dashboard shows $0**  
→ `python3 ../scripts/sync_transactions.py --initial`

**No accounts connected**  
→ `python3 ../scripts/plaid_setup.py`

**API not responding**  
→ `python3 ../scripts/spending_api.py`

---

## Documentation

- **Full Guide:** [`docs/SPENDING_TRACKER.md`](../docs/SPENDING_TRACKER.md)
- **Quick Start:** [`docs/SPENDING_QUICKSTART.md`](../docs/SPENDING_QUICKSTART.md)
- **Integration:** [`docs/SPENDING_INTEGRATION_EXAMPLE.md`](../docs/SPENDING_INTEGRATION_EXAMPLE.md)

---

**The Goal:** Real-time financial visibility → conscious spending → more money toward Florida 🎯
