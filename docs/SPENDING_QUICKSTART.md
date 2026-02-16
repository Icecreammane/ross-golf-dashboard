# Spending Tracker - Quick Start

**Get up and running in 5 minutes**

## 1. Get Plaid Keys (2 min)

**Sandbox (testing):**
1. Go to https://dashboard.plaid.com/signup
2. Sign up (free)
3. Copy `client_id` and `secret`

## 2. Configure (30 sec)

```bash
cd ~/clawd
cat > ~/.clawdbot/credentials/plaid.json <<EOF
{
  "client_id": "YOUR_CLIENT_ID_HERE",
  "secret": "YOUR_SECRET_HERE",
  "environment": "sandbox"
}
EOF
chmod 600 ~/.clawdbot/credentials/plaid.json
```

## 3. Connect Accounts (1 min)

```bash
python3 scripts/plaid_setup.py
```

**Sandbox credentials:**
- Institution: "First Platypus Bank"
- Username: `user_good`
- Password: `pass_good`

Repeat for multiple accounts.

## 4. Sync Transactions (30 sec)

```bash
python3 scripts/sync_transactions.py --initial
```

## 5. Launch Dashboard (30 sec)

```bash
# Terminal 1
python3 scripts/spending_api.py

# Terminal 2
open dashboard/spending.html
```

Visit: http://localhost:5002

---

## Daily Commands

```bash
# Check today's spending
python3 scripts/spending_alerts.py daily

# Evening summary
python3 scripts/spending_alerts.py evening

# View dashboard
open dashboard/spending.html

# Manual sync
python3 scripts/sync_transactions.py
```

---

## Evening Check-In Integration

Add to your evening check-in script:

```python
# scripts/evening_checkin.py

import subprocess
import os

# ... your existing code ...

# Add spending summary
try:
    result = subprocess.run(
        ['python3', 'scripts/spending_alerts.py', 'evening'],
        capture_output=True,
        text=True,
        cwd=os.path.expanduser('~/clawd'),
        timeout=10
    )
    
    if result.returncode == 0:
        spending_summary = result.stdout
        # Add to your evening message
        message += f"\n\n{spending_summary}"
except Exception as e:
    print(f"Spending summary unavailable: {e}")
```

---

## Automation Setup

```bash
# Add to crontab
crontab -e

# Add this line (2am daily sync):
0 2 * * * cd ~/clawd && python3 scripts/sync_transactions.py >> logs/spending_sync.log 2>&1
```

---

## Troubleshooting

**Dashboard shows $0**
→ Run `python3 scripts/sync_transactions.py --initial`

**"No accounts connected"**
→ Run `python3 scripts/plaid_setup.py`

**API not responding**
→ Start API: `python3 scripts/spending_api.py`

---

**Done!** You now have real-time spending visibility.

Full docs: `docs/SPENDING_TRACKER.md`
