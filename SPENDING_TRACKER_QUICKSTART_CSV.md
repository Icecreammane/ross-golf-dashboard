# Spending Tracker - CSV Import (Works Now!)

**Plaid Issue:** Account needs email verification + risk questionnaire completion before API works.

**Solution:** CSV import works immediately while Plaid gets set up.

---

## Quick Start (5 Minutes)

### 1. Export CSV from Your Bank

**Chase:**
1. Login to chase.com
2. Account → Download transactions
3. Select last 30-90 days
4. Format: CSV
5. Save to ~/Downloads/chase_transactions.csv

**Most Banks:**
1. Login to your bank
2. Find "Export" or "Download transactions"
3. Select CSV format
4. Last 30-90 days
5. Save the file

### 2. Import Transactions

```bash
cd ~/clawd
python3 scripts/import_transactions_csv.py ~/Downloads/transactions.csv
```

**Output:**
```
📂 Importing: /Users/ross/Downloads/transactions.csv
Format detected: chase
📊 Parsed 247 transactions
🔄 247 new transactions (skipped 0 duplicates)
✅ Saved 247 transactions to /Users/ross/clawd/data/transactions.json

📈 Summary:
   Total transactions: 247
   Date range: 2025-11-17 to 2026-02-15

🏷️  New transactions by category:
   Dining Out: 89
   Groceries: 42
   Gas & Transportation: 28
   Shopping: 31
   Subscriptions: 12
   Other: 45
```

### 3. Launch Dashboard

```bash
bash scripts/start_spending_dashboard.sh
```

Dashboard: http://localhost:5002

---

## Supported CSV Formats

### Chase Format
```
Transaction Date,Post Date,Description,Category,Type,Amount,Memo
02/15/2026,02/16/2026,DOORDASH,Food & Drink,Sale,-35.42,
```

### Generic Format
```
Date,Description,Amount
02/15/2026,DoorDash,-35.42
02/14/2026,Publix,-87.23
```

### Custom Format
If your bank uses a different format, send me a sample and I'll add support.

---

## Update Your Data

**Daily/Weekly:**
1. Export new CSV from bank
2. Run import script again
3. Deduplication is automatic

```bash
python3 scripts/import_transactions_csv.py ~/Downloads/new_transactions.csv
```

Dashboard auto-refreshes every 5 minutes or refresh manually.

---

## Fixing Plaid (Later)

**To finish Plaid setup:**
1. Check email (rcaster624@gmail.com) for verification link
2. Click verification link
3. Login to dashboard.plaid.com
4. Complete "Risk diligence questionnaire" (takes 5-10 min)
5. Once complete, Plaid API will work
6. Then run: `python3 scripts/plaid_setup.py`

**Until then:** CSV import works perfectly!

---

## What You Get

✅ Real-time spending dashboard  
✅ Category breakdown (Dining, Gas, Groceries, etc.)  
✅ 30-day spending trends  
✅ Daily/weekly/monthly summaries  
✅ Transaction search  
✅ Works TODAY (no API wait)

**CSV import takes 30 seconds.** Plaid is nice-to-have, not need-to-have.

---

**Questions?** Just ask. This system works right now.
