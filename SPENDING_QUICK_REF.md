# 💰 Spending Tracker Quick Reference

## 🚀 Setup (5 Minutes)

```bash
# 1. Get Plaid keys: https://dashboard.plaid.com/signup

# 2. Configure
cat > ~/.clawdbot/credentials/plaid.json <<EOF
{
  "client_id": "YOUR_CLIENT_ID",
  "secret": "YOUR_SECRET",
  "environment": "sandbox"
}
EOF

# 3. Connect account
python3 scripts/plaid_setup.py

# 4. Sync transactions
python3 scripts/sync_transactions.py --initial

# 5. Launch
bash scripts/start_spending_dashboard.sh
```

---

## 📊 Daily Commands

```bash
# Today's spending
python3 scripts/spending_alerts.py daily

# Evening summary
python3 scripts/spending_alerts.py evening

# Insights
python3 scripts/spending_alerts.py insights

# Dashboard
open dashboard/spending.html

# Sync
python3 scripts/sync_transactions.py
```

---

## 🤖 Automation

```bash
# Add to crontab (crontab -e)
0 2 * * * cd ~/clawd && python3 scripts/sync_transactions.py >> logs/spending_sync.log 2>&1
```

---

## 📍 Files

```
scripts/plaid_setup.py        # Connect accounts
scripts/sync_transactions.py  # Pull transactions
scripts/spending_api.py       # API backend
scripts/spending_alerts.py    # Alerts & insights
dashboard/spending.html       # Web dashboard
data/transactions.json        # Your data
```

---

## 🔧 Troubleshooting

**Dashboard shows $0?**  
→ `python3 scripts/sync_transactions.py --initial`

**No accounts connected?**  
→ `python3 scripts/plaid_setup.py`

**API won't start?**  
→ Check port: `lsof -i :5002`

---

## 📚 Full Docs

- `docs/SPENDING_QUICKSTART.md`
- `docs/SPENDING_TRACKER.md`
- `SPENDING_TRACKER_COMPLETE.md`

---

**Dashboard:** http://localhost:5002  
**Status:** ✅ Ready to use
