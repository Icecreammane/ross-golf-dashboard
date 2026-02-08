# Revenue Dashboard - Quick Start

## 🚀 Get Running in 3 Steps

### Step 1: Configure Stripe
```bash
nano .env
```

Add your Stripe API key:
```
STRIPE_API_KEY=sk_live_your_actual_key_here
```

### Step 2: Start Dashboard
```bash
bash start.sh
```

### Step 3: Open Browser
**Dashboard:** http://localhost:3002

---

## 🎯 What You'll See

### Main Metrics
- **MRR Progress** - Big progress bar showing path to $500/mo
- **Daily Revenue** - Today's earnings
- **Total Revenue** - Last 30 days
- **Subscriptions** - Active subscriber count
- **Coaching Inquiries** - Lead tracking

### Features
- ✅ Auto-refreshes every 5 minutes
- ✅ Manual refresh button
- ✅ Motivational messages
- ✅ Smooth animations
- ✅ Real-time status

---

## 🔧 Optional: Set Up Webhooks

For **instant updates** when new sales come in:

1. Go to: https://dashboard.stripe.com/webhooks
2. Add endpoint: `https://your-domain.com/api/webhook/stripe`
3. Select events:
   - `charge.succeeded`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copy webhook secret to `.env`:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_your_secret
   ```
5. Restart dashboard

---

## 🐛 Troubleshooting

**Port 3002 already in use?**
```bash
lsof -i :3002
kill -9 <PID>
```

**No data showing?**
- Check Stripe API key in `.env`
- Verify you have subscriptions/payments in Stripe
- Click "Refresh" button in dashboard

**Logs?**
```bash
tail -f logs/revenue_dashboard.log
```

**Health check:**
```bash
curl http://localhost:3002/health
```

---

## 📖 Full Documentation

See `README.md` for complete documentation including:
- Deployment options (systemd, Docker, Gunicorn)
- Email integration setup
- API reference
- Security configuration
- Production deployment guide

---

**That's it! You're tracking revenue! 💰**
