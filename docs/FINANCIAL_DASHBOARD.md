# Financial Dashboard

**AI-powered financial tracking with Plaid integration**

## Features

- 💰 **Real-time balance tracking** across all accounts
- 📊 **Automatic spending categorization** (Food, Transportation, Shopping, etc.)
- 📈 **Visual spending charts** with Chart.js
- ⚠️ **Budget alerts** when you're over budget
- 📅 **Weekly spending summary**
- 🔄 **Daily automatic sync** via daemon

## Quick Start

### 1. Install Dependencies

```bash
pip3 install plaid-python flask requests beautifulsoup4
```

### 2. Get Plaid API Credentials

1. Sign up at https://dashboard.plaid.com/signup
2. Get your **Client ID** and **Secret** (sandbox mode is free)
3. Export credentials:

```bash
export PLAID_CLIENT_ID="your_client_id"
export PLAID_SECRET="your_secret"
export PLAID_ENV="sandbox"
```

### 3. Start Dashboard

```bash
python3 ~/clawd/scripts/financial_dashboard.py
```

Visit: **http://localhost:8082/finances**

### 4. Connect Bank Account

1. Click "Connect Bank Account"
2. Select your bank (in sandbox, use test credentials)
3. Dashboard will auto-sync!

### 5. Setup Daily Sync

Add to crontab:

```bash
# Daily financial sync at 6am
0 6 * * * python3 ~/clawd/scripts/financial_sync_daemon.py >> ~/clawd/logs/financial-sync.log 2>&1
```

## Usage

### View Dashboard

```bash
# Start server
python3 ~/clawd/scripts/financial_dashboard.py

# Open in browser
open http://localhost:8082/finances
```

### Manual Sync

```bash
python3 ~/clawd/scripts/financial_sync_daemon.py
```

### Check Budget Status

The dashboard shows budget status for each category:
- 🟢 **On Track**: <80% of budget spent
- 🟡 **Warning**: 80-100% of budget spent
- 🔴 **Over Budget**: >100% spent

### Customize Budgets

Edit `data/financial_data.json`:

```json
{
  "budgets": {
    "Food and Drink": 500,
    "Transportation": 200,
    "Shopping": 300,
    "Entertainment": 100
  }
}
```

## Data Storage

All data stored in `data/financial_data.json`:
- Access tokens (encrypted)
- Account balances
- Transaction history (90 days)
- Budget configuration
- Spending categories

## Plaid Sandbox Testing

Use these test credentials in sandbox mode:

**Username:** `user_good`  
**Password:** `pass_good`

Plaid will generate realistic test transactions!

## Production Setup

1. **Upgrade to Plaid Development** (still free for <100 users)
2. **Set production credentials:**
   ```bash
   export PLAID_ENV="development"
   export PLAID_CLIENT_ID="your_dev_client_id"
   export PLAID_SECRET="your_dev_secret"
   ```
3. **Restart dashboard**

## API Endpoints

- `GET /` - Dashboard UI
- `POST /api/create_link_token` - Create Plaid Link token
- `POST /api/exchange_public_token` - Exchange token for access token
- `GET /api/accounts` - Get account balances
- `GET /api/transactions` - Get transaction history
- `GET /api/spending_summary` - Get spending by category
- `GET /api/budget_status` - Get budget status
- `POST /api/sync` - Manual sync trigger

## Troubleshooting

### "No access token found"
**Solution:** Connect a bank account through the dashboard first

### "Plaid API error"
**Solution:** Check your credentials are correct:
```bash
echo $PLAID_CLIENT_ID
echo $PLAID_SECRET
```

### Transactions not showing
**Solution:** Run manual sync:
```bash
python3 ~/clawd/scripts/financial_sync_daemon.py
```

## The Pitch

> "I wake up, check my dashboard, and know exactly where I stand financially. No logging into 3 bank accounts. No spreadsheets. My AI tracks everything."

Show your friends:
- Real-time balance across all accounts
- Automatic spending categorization
- Budget tracking that actually works
- Beautiful visualizations

**This is the future of personal finance.**
