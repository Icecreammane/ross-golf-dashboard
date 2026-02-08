# Plaid Finance Dashboard - Setup Guide

## What You Have

A complete personal finance dashboard that:
- ✅ Links all your bank accounts via Plaid
- ✅ Shows real-time balances and transactions
- ✅ Tracks spending by category
- ✅ Calculates your net worth
- ✅ Displays spending trends

## Prerequisites

You need:
- Python 3.8+ (you have this)
- Plaid account credentials (you have these)

## Setup Steps

### Step 1: Install Dependencies (2 minutes)

```bash
cd ~/clawd/plaid-integration
pip install -r requirements.txt
```

### Step 2: Create the Database

```bash
python3
from app import app, db
with app.app_context():
    db.create_all()
exit()
```

Or simpler:
```bash
python3 app.py
# Wait 2 seconds, then press Ctrl+C
```

### Step 3: Start the Server

```bash
python3 app.py
```

You should see:
```
WARNING in app.runserver: This is a development server. Do not use it in production.
Running on http://127.0.0.1:3100
```

### Step 4: Open Dashboard

Open your browser: **http://localhost:3100**

### Step 5: Link Your Bank Accounts

1. Click **"+ Link Bank Account"** button
2. Search for your bank (Chase, Bank of America, Wells Fargo, etc.)
3. Enter your online banking credentials
4. Plaid securely authenticates (you stay in control)
5. Select which accounts to link
6. Done! Your accounts are now connected

### Step 6: View Your Data

- **Net Worth:** Total of all linked accounts
- **Accounts:** Real-time balances
- **Transactions:** Last 30 days (searchable, filterable)
- **Spending:** Breakdown by category

## How It Works

### Backend (Flask App)
- Authenticates with Plaid API
- Securely exchanges your credentials for access tokens
- Fetches accounts and transactions every time you click "Refresh"
- Stores data locally in SQLite database

### Frontend (Dashboard)
- Beautiful, responsive design
- Real-time balance updates
- Interactive spending charts
- Filter transactions by account and time period

## API Endpoints

**For Reference (you don't need to use these directly):**

- `POST /api/link-token` → Create Plaid Link token
- `POST /api/exchange-token` → Exchange public token for access
- `GET /api/accounts` → Get all linked accounts
- `GET /api/transactions` → Get transactions (filter by account/date)
- `GET /api/net-worth` → Calculate total net worth
- `GET /api/spending-summary` → Get spending by category
- `POST /api/refresh-accounts` → Manually refresh data

## Troubleshooting

### "ModuleNotFoundError: No module named 'plaid'"
Solution: Run `pip install -r requirements.txt`

### "Address already in use"
Solution: Port 3100 is taken. Change the port in app.py:
```python
if __name__ == '__main__':
    app.run(debug=True, port=3101)  # Use 3101 instead
```

### "No accounts showing"
Solution: Click "+ Link Bank Account" and complete the Plaid Link flow

### "Transactions not loading"
Solution: Click "🔄 Refresh Data" button

## Next Steps

### Integration with Jarvis (Advanced)
Once working, I can:
1. Auto-fetch your spending data periodically
2. Send you insights: "You're on track for your Florida Fund goal"
3. Alert on unusual spending
4. Recommend optimizations based on patterns

### Make It Production-Ready (Optional)
- Deploy to actual server (instead of local)
- Use production Plaid credentials
- Set up automatic daily refreshes
- Add email alerts

## File Structure

```
plaid-integration/
├── app.py                    # Flask backend
├── requirements.txt          # Python dependencies
├── finance.db               # SQLite database (created automatically)
├── templates/
│   └── dashboard.html       # Frontend dashboard
└── SETUP_GUIDE.md           # This file
```

## Your Plaid Credentials

**Keep these SECRET - never share them:**
- Client ID: 69b8b5dda8ab8881edc312
- Secret: 97d84d06a39cc134643c64268288f
- Environment: Sandbox (test mode)

These are stored in `app.py`. When you're ready for production, you'll switch to real credentials.

## Questions?

The dashboard is self-explanatory. Just:
1. Link accounts
2. Watch the data populate
3. Explore the filters and charts

That's it!

---

**Status:** Ready to run
**Time to Setup:** ~5 minutes
**Time to First Bank Link:** ~2 minutes
