# Stripe Integration Setup Guide

Complete setup in **5 minutes**. Real-time revenue tracking + alerts.

---

## Step 1: Get Stripe API Keys (2 minutes)

1. **Log into Stripe Dashboard:** https://dashboard.stripe.com
2. **Navigate to Developers → API Keys**
3. **Copy your keys:**
   - **Secret Key** (starts with `sk_live_` or `sk_test_`)
   - Save this - you'll need it in Step 2

---

## Step 2: Configure Environment (1 minute)

Add to your `.env` file (create if doesn't exist):

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Telegram Alerts (optional but recommended)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

**Where to find Telegram credentials:**
- Bot Token: Talk to @BotFather on Telegram, create new bot
- Chat ID: Message @userinfobot on Telegram

---

## Step 3: Install Dependencies (1 minute)

```bash
pip install stripe python-dotenv flask flask-cors requests
```

---

## Step 4: Test Integration (1 minute)

```bash
cd integrations/stripe
python stripe_integration.py
```

**Expected output:**
```
✅ Stripe configured!

💰 MRR: $47.00
📈 ARR: $564.00
👥 Active Customers: 3
```

---

## Step 5: Set Up Webhooks (Optional - 5 minutes)

Webhooks enable real-time alerts for subscription events.

### 5a. Install Stripe CLI

```bash
brew install stripe/stripe-cli/stripe
stripe login
```

### 5b. Forward Webhooks Locally (Development)

```bash
stripe listen --forward-to localhost:5001/webhook
```

Copy the webhook secret (starts with `whsec_`) and add to `.env`:
```bash
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
```

### 5c. Create Production Webhook

1. Go to Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. **Endpoint URL:** `https://your-domain.com/webhook`
4. **Events to send:**
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `charge.failed`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy webhook secret to `.env`

---

## Step 6: Start Revenue API (30 seconds)

```bash
cd integrations/stripe
python revenue_api.py
```

API now running at `http://localhost:5001`

**Test endpoints:**
- http://localhost:5001/api/revenue/mrr
- http://localhost:5001/api/revenue/customers
- http://localhost:5001/api/revenue/dashboard

---

## Step 7: Enable Alerts (30 seconds)

Test alert system:

```bash
python stripe_alerts.py
```

You'll receive a Telegram message with current revenue stats!

### Automated Daily Summary

Add to crontab (runs at 9 AM daily):

```bash
crontab -e

# Add this line:
0 9 * * * cd /path/to/integrations/stripe && python -c "from stripe_alerts import StripeAlerts; StripeAlerts().daily_summary()"
```

---

## Verification Checklist

✅ Stripe API key configured  
✅ MRR/ARR displaying correctly  
✅ Customer count accurate  
✅ Telegram alerts working  
✅ Revenue API responding  
✅ Webhooks receiving events (optional)  

---

## Troubleshooting

### "Stripe not configured" error
- Check `.env` file exists
- Verify `STRIPE_SECRET_KEY` is set correctly
- Make sure key starts with `sk_`

### MRR shows $0 but you have customers
- Check if subscriptions are in "active" status
- Verify prices are set correctly in Stripe
- Run `python stripe_integration.py` to see detailed output

### Telegram alerts not working
- Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are correct
- Test with `curl` to Telegram API directly
- Check bot has permission to message you

### Webhooks not receiving events
- Verify webhook secret is correct
- Check endpoint is publicly accessible
- Review Stripe Dashboard → Webhooks for failed deliveries

---

## Security Best Practices

🔒 **Never commit `.env` to git**
```bash
echo ".env" >> .gitignore
```

🔒 **Use test keys in development**
- Test keys start with `sk_test_`
- Live keys start with `sk_live_`

🔒 **Rotate keys if compromised**
- Generate new keys in Stripe Dashboard
- Update `.env` file
- Old keys stop working immediately

🔒 **Restrict API key permissions**
- Use restricted keys if possible
- Only grant necessary permissions

---

## Next Steps

✅ **Done!** Stripe integration is live.

**Now try:**
1. Open `revenue-dashboard.html` in browser
2. Set up automated alerts (see `stripe_alerts.py`)
3. Monitor webhooks for real-time events
4. Export data: `python -c "from stripe_integration import StripeIntegration; StripeIntegration().export_data()"`

**Time to activation:** 5 minutes ⚡  
**Time saved per week:** 2-3 hours 🚀
