# 🔐 Plaid Integration Setup Guide

## What is Plaid?

Plaid is the industry-standard API for connecting bank accounts securely. It's used by:
- Venmo (for bank transfers)
- Cash App
- Robinhood
- Mint
- Most fintech apps

**Security:** You login on YOUR BANK'S website, not ours. Plaid never sees your password.

---

## Setup Steps

### 1. Create Plaid Account (Monday)

**Sign up:** https://dashboard.plaid.com/signup

**Account Type:** Development (free for testing, then $1-5/month for production)

**You'll get:**
- `client_id` (public identifier)
- `secret` (private key - NEVER share)
- `public_key` (for frontend)

### 2. Configure Plaid

**Products to enable:**
- ✅ Transactions (read transaction history)
- ✅ Auth (verify accounts)
- ✅ Identity (get account holder info)

**Institutions to enable:**
- ✅ PNC Bank
- ✅ Chase
- ✅ Venmo
- ✅ Cash App

### 3. Store Credentials Securely

**Create:** `~/clawd/finance/.env`

```bash
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_here
PLAID_ENV=development  # or 'production' when ready
```

**Important:** This file is in `.gitignore` - never committed to GitHub

### 4. Test Connection

Run:
```bash
python3 ~/clawd/finance/plaid_connector.py test
```

This verifies your credentials work.

### 5. Link Your Accounts

Run:
```bash
python3 ~/clawd/finance/plaid_connector.py link
```

This opens a secure OAuth flow where you:
1. Select your bank (PNC, Chase, etc.)
2. Login on the bank's website
3. Approve read-only access
4. Done!

### 6. Sync Transactions

After linking, run:
```bash
python3 ~/clawd/finance/plaid_connector.py sync
```

This pulls your transaction history and updates the dashboard.

---

## Security Notes

### What Plaid CAN Do:
- ✅ Read transaction history
- ✅ Get account balances
- ✅ Verify account ownership

### What Plaid CANNOT Do:
- ❌ Move money
- ❌ Change account settings
- ❌ Access your login credentials
- ❌ Make purchases or transfers

### Revoking Access

You can revoke Plaid's access anytime:
1. Login to your bank
2. Go to "Connected Apps" or "Third-Party Access"
3. Remove "Plaid"

Or revoke via Plaid dashboard: https://my.plaid.com/

---

## Troubleshooting

### "Institution not found"
- Some banks require manual approval
- Check Plaid's institution list: https://plaid.com/docs/institutions/

### "Invalid credentials"
- Plaid keys incorrect
- Check `.env` file
- Regenerate keys in Plaid dashboard

### "Access denied"
- Bank declined OAuth request
- Try again or contact bank
- Some banks require phone verification

---

## Cost

**Development (Testing):**
- Free for first 100 items
- Perfect for personal use

**Production (Real Use):**
- $1-5/month depending on volume
- Worth it for automation

---

## Next Steps (Monday)

1. Sign up at Plaid (5 min)
2. Get credentials (instant)
3. Add to `.env` file (1 min)
4. Run test connection (1 min)
5. Link accounts (5 min - one at a time)
6. First sync (automatic)

**Total time: ~15 minutes Monday morning**

Then you never touch it again - updates daily automatically.

---

## Alternative: Stay with CSV

If Plaid feels like too much setup:
- Export CSVs weekly (5 min)
- Same dashboard, 95% as good
- Zero API costs
- You control everything

Your choice! Both work great.
