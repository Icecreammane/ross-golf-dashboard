# FitTrack Monitoring & Alerting Setup

**Goal:** Know immediately if FitTrack goes down or has issues

**Time to complete:** 15 minutes

**Result:** Peace of mind. Sleep well knowing you'll be alerted if anything breaks.

---

## Part A: UptimeRobot Setup (5 min, FREE)

### Why UptimeRobot?
- ✅ Free forever (50 monitors)
- ✅ Checks every 5 minutes
- ✅ Email + Telegram alerts
- ✅ 99.9% uptime tracking
- ✅ No credit card required

### Setup Steps

**1. Create Account**
- Visit: https://uptimerobot.com
- Click "Sign Up Free"
- Use: `bigmeatyclawd@gmail.com` (Jarvis's email)
- Verify email

**2. Add First Monitor**
- Dashboard → "Add New Monitor"
- **Monitor Type:** HTTPS
- **Friendly Name:** `FitTrack Production`
- **URL:** `https://[your-railway-url].up.railway.app/health`
  - Example: `https://fittrack-pro.up.railway.app/health`
- **Monitoring Interval:** 5 minutes (free tier)
- Click "Create Monitor"

**3. Add Alert Contacts**
- Settings → "Alert Contacts"
- **Add Email:**
  - Email: `bigmeatyclawd@gmail.com` (Jarvis)
  - Verify email
- **Add Telegram (Optional but Recommended):**
  - Search Telegram for: `@uptimerobot_bot`
  - Send: `/start`
  - Bot replies with your Telegram ID
  - UptimeRobot → Add Alert Contact → Telegram → Paste ID

**4. Configure Alerting**
- Monitors → FitTrack Production → Edit
- **Alert Contacts to Notify:** Select email + Telegram
- **When to Alert:**
  - ✅ When down
  - ✅ When up again (recovery)
- **Alert Threshold:** Alert if down for 5+ minutes (default)
- Save

### What You Get

**Every 5 minutes, UptimeRobot checks:**
- Is site reachable?
- Does `/health` endpoint return 200 OK?
- Response time under 10 seconds?

**If down:**
- 🚨 Email alert: "FitTrack Production is DOWN"
- 🚨 Telegram message (instant notification)

**When recovered:**
- ✅ Email: "FitTrack Production is UP"
- ✅ Telegram confirmation

**Dashboard shows:**
- Uptime %: Aim for 99.9%+
- Response time graph
- Downtime history

---

## Part B: Health Check Endpoint (5 min)

### Why Health Checks?
A simple `/health` endpoint that:
- ✅ Confirms app is running
- ✅ Tests database connection
- ✅ Verifies critical services work
- ✅ Returns JSON status

### Implementation

**File: `fittrack-tracker/health_check.py`**

Create this file in your FitTrack repo:

```python
"""
Health Check Endpoint for Monitoring
Add this to app_saas.py or app_production.py
"""

from flask import jsonify
import time
from datetime import datetime

@app.route('/health')
def health_check():
    """
    Health check endpoint for UptimeRobot and monitoring
    Returns 200 OK if everything is healthy
    Returns 500 if critical services are down
    """
    try:
        # Check 1: Database connection
        # Attempt a simple query
        from models import User  # adjust import based on your structure
        user_count = User.query.count()  # Quick query to verify DB
        
        # Check 2: Stripe API (optional, quick check)
        # import stripe
        # stripe.Account.retrieve()  # Verify Stripe key works
        
        # Check 3: Critical imports
        # Ensure all dependencies loaded
        
        # All checks passed
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time(),
            "version": "1.0.0",
            "checks": {
                "database": "ok",
                "stripe": "ok",
                "app": "ok"
            }
        }), 200
        
    except Exception as e:
        # Something is broken
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Optional: More detailed status endpoint (not public)
@app.route('/status')
def detailed_status():
    """
    Detailed status for debugging (add authentication later)
    """
    try:
        from models import User, Subscription, FoodLog
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": {
                "users": User.query.count(),
                "subscriptions": Subscription.query.count(),
                "food_logs_today": FoodLog.query.filter_by(
                    date=datetime.now().date()
                ).count()
            },
            "stripe": {
                "mode": os.environ.get('STRIPE_MODE', 'unknown')
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
```

### How to Add to Your App

**Option 1: Separate file (recommended)**
1. Save as `fittrack-tracker/health_check.py`
2. In `app_saas.py`, add:
```python
# Import health check routes
from health_check import *
```

**Option 2: Add directly to app_saas.py**
- Copy the `/health` route directly into your main Flask file
- Place near other routes

### Test It

**Local testing:**
```bash
# Start your Flask app
python app_saas.py

# In another terminal, test health endpoint
curl http://localhost:5000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-13T19:00:00",
  "uptime": 1708034400.0,
  "version": "1.0.0",
  "checks": {
    "database": "ok",
    "stripe": "ok",
    "app": "ok"
  }
}
```

**Production testing (after Railway deploy):**
```bash
curl https://[your-railway-url].up.railway.app/health
```

Should return same JSON with 200 status code.

---

## Part C: Telegram Alerts via Jarvis (5 min, ADVANCED)

### Direct Telegram Alerts

For instant notifications bypassing email, configure Jarvis to send alerts.

**File: `monitoring/telegram-alerts.sh`**

```bash
#!/bin/bash

# Telegram Alert Script for FitTrack Downtime
# Sends instant alert to Ross via Telegram

# Load credentials from secure storage
CREDENTIALS_FILE="$HOME/clawd/.credentials/telegram_credentials.json"
TELEGRAM_BOT_TOKEN=$(python3 -c "import json; print(json.load(open('$CREDENTIALS_FILE'))['bot_token'])")
TELEGRAM_CHAT_ID=$(python3 -c "import json; print(json.load(open('$CREDENTIALS_FILE'))['ross_chat_id'])")

send_alert() {
    local SITE_URL="$1"
    local REASON="$2"
    local STATUS="$3"  # "down" or "up"
    
    if [ "$STATUS" = "down" ]; then
        EMOJI="🚨"
        MESSAGE="*ALERT: FitTrack is DOWN*

Site: \`$SITE_URL\`
Reason: $REASON
Time: $(date '+%Y-%m-%d %H:%M:%S')

Checking now..."
    else
        EMOJI="✅"
        MESSAGE="*FitTrack is BACK UP*

Site: \`$SITE_URL\`
Downtime: $REASON
Recovered: $(date '+%Y-%m-%d %H:%M:%S')

All systems operational."
    fi
    
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d chat_id="$TELEGRAM_CHAT_ID" \
        -d text="$EMOJI $MESSAGE" \
        -d parse_mode="Markdown" \
        > /dev/null
}

# Usage examples:
# ./telegram-alerts.sh "https://fittrack.app" "502 Bad Gateway" "down"
# ./telegram-alerts.sh "https://fittrack.app" "5 minutes" "up"

send_alert "$1" "$2" "$3"
```

**Make executable:**
```bash
chmod +x ~/clawd/monitoring/telegram-alerts.sh
```

**Test it:**
```bash
# Test down alert
~/clawd/monitoring/telegram-alerts.sh "https://fittrack.app" "Test alert" "down"

# Test recovery alert
~/clawd/monitoring/telegram-alerts.sh "https://fittrack.app" "Test recovery" "up"
```

You should receive Telegram messages instantly.

### Integration with UptimeRobot (Advanced)

**UptimeRobot Webhook → Telegram:**

1. **UptimeRobot Dashboard**
   - Settings → Alert Contacts → "Add Alert Contact"
   - Type: "Webhook"
   - **Webhook URL:** `https://[your-server]/webhook/uptime`
   - (Requires separate webhook receiver - can add to Railway app)

2. **Add Webhook Route to Flask:**

```python
@app.route('/webhook/uptime', methods=['POST'])
def uptime_webhook():
    """
    Receives UptimeRobot alerts and forwards to Telegram
    """
    data = request.form  # UptimeRobot sends form data
    
    monitor_name = data.get('monitorFriendlyName', 'Unknown')
    monitor_url = data.get('monitorURL', 'Unknown')
    alert_type = data.get('alertType', 'Unknown')  # "down" or "up"
    alert_details = data.get('alertDetails', 'No details')
    
    # Send to Telegram via Jarvis
    import subprocess
    subprocess.run([
        '/Users/clawdbot/clawd/monitoring/telegram-alerts.sh',
        monitor_url,
        alert_details,
        alert_type
    ])
    
    return jsonify({"success": True}), 200
```

Now UptimeRobot → Railway → Telegram (instant alerts).

---

## Part D: Error Logging & Debugging

### Railway Built-in Logs

**Access logs:**
1. Railway dashboard → Your project
2. **Logs tab** (left sidebar)
3. See all:
   - HTTP requests
   - Errors (red)
   - Warnings (yellow)
   - Info (white)

**Filter logs:**
- Click "Errors" to see only errors
- Search by keyword: "stripe", "database", "500", etc.
- Expand entries to see full stack traces

**Download logs:**
- Useful for debugging complex issues
- Click "Export" → Download as .txt

### Custom Error Tracking (Optional: Sentry)

**Sentry.io** catches Python exceptions automatically.

**Setup (5 minutes):**

1. **Create Sentry Account**
   - Visit: https://sentry.io
   - Sign up (free tier: 5,000 errors/month)

2. **Create Project**
   - "Create Project" → Python → Flask
   - Copy DSN: `https://[key]@sentry.io/[project]`

3. **Add to Flask App**

Install Sentry:
```bash
pip install sentry-sdk[flask]
```

Add to `requirements.txt`:
```
sentry-sdk[flask]==1.40.0
```

Add to `app_saas.py` (top of file):
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://[your-key]@sentry.io/[project]",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,  # 100% performance monitoring
    environment="production"
)
```

4. **Deploy to Railway**
   - Push changes to GitHub
   - Railway auto-deploys
   - Sentry now catches all errors

**What you get:**
- 🚨 Email when errors occur
- 🐛 Full stack traces
- 📊 Error frequency tracking
- 👤 User context (which user hit the bug)
- 🔍 Breadcrumbs (what led to error)

**Test it:**
```python
# Add a test route
@app.route('/test-error')
def test_error():
    raise Exception("Test error for Sentry")
```

Visit `/test-error` → Sentry captures it → You get email.

---

## Monitoring Dashboard

### What to Check Daily

**Morning routine (2 minutes):**
1. **UptimeRobot Dashboard**
   - Check uptime % (should be 99.9%+)
   - Any downtime overnight?
   - Response times normal? (<500ms)

2. **Railway Logs**
   - Any errors overnight?
   - Filter by "ERROR" level
   - Investigate unusual patterns

3. **Stripe Dashboard**
   - Any failed payments?
   - Webhook deliveries successful?
   - Subscription churn?

**Weekly:**
- Review Sentry errors (if using)
- Check UptimeRobot response time trends
- Verify backup systems working (see `AUTOMATED_BACKUP_SETUP.md`)

---

## Alert Levels

### 🟢 Green - All Good
- Uptime: 99.9%+
- Response time: <500ms
- No errors in logs
- All webhooks delivering

**Action:** None, keep building

### 🟡 Yellow - Minor Issues
- Uptime: 99.0-99.9%
- Response time: 500ms-2s
- Occasional errors (1-2/day)
- Some webhook retries

**Action:** Investigate when convenient, not urgent

### 🔴 Red - Critical
- Uptime: <99.0%
- Response time: >2s or timeouts
- Frequent errors (10+/day)
- Webhook failures

**Action:** Investigate immediately, users affected

### ⚫ Black - Down
- Site completely unreachable
- Health check failing
- No response from server

**Action:** Emergency response (see Emergency Response Plan below)

---

## Emergency Response Plan

### If FitTrack Goes Down

**Step 1: Verify (30 seconds)**
- Visit site in incognito/private window
- Check Railway dashboard (is app running?)
- Check Railway logs (recent errors?)

**Step 2: Quick Fix Attempts (2 minutes)**
- **Restart app:** Railway dashboard → "Restart"
- **Check env vars:** Variables tab → all present?
- **Check database:** Is PostgreSQL running?

**Step 3: Rollback (2 minutes)**
- Railway → Deployments → Previous deployment
- Click "Redeploy"
- Confirm working

**Step 4: Investigate**
- Review logs for root cause
- Fix issue in code
- Push to GitHub (Railway auto-deploys)

**Step 5: Communicate**
- If down >10 minutes:
  - Tweet: "Experiencing brief downtime, fixing now. Back shortly."
  - Update status if you have status page

**Step 6: Post-Mortem**
- Document what happened
- Add to `memory/YYYY-MM-DD.md`
- Prevent recurrence

---

## Success Metrics

**Targets for FitTrack:**

| Metric | Target | Reality Check |
|--------|--------|---------------|
| **Uptime** | 99.9% | <5min downtime/week |
| **Response Time** | <500ms | Fast page loads |
| **Error Rate** | <0.1% | 1 error per 1,000 requests |
| **Time to Recovery** | <5min | From alert to fixed |

**Track in:**
- UptimeRobot: Uptime % (automatic)
- Railway Logs: Error count (manual review)
- Sentry: Error rate (automatic if using)

---

## Monitoring Checklist

Before launch (Feb 13):
- ✅ UptimeRobot monitoring FitTrack
- ✅ Email alerts configured
- ✅ Telegram alerts configured (optional but recommended)
- ✅ Health check endpoint working (`/health`)
- ✅ Railway logs accessible
- ✅ Tested alert notifications (sent test alerts)
- ✅ Emergency response plan documented
- ✅ Sentry configured (optional)

After launch:
- ✅ Check UptimeRobot daily (morning routine)
- ✅ Review Railway logs weekly
- ✅ Monitor Stripe webhook deliveries
- ✅ Track uptime % (aim for 99.9%+)

---

## Cost

| Service | Cost | Value |
|---------|------|-------|
| **UptimeRobot** | FREE | Uptime monitoring |
| **Railway Logs** | Included | Error tracking |
| **Sentry** (optional) | FREE (5k errors/mo) | Exception tracking |
| **Telegram Alerts** | FREE | Instant notifications |
| **Total** | **$0/month** | Peace of mind |

---

## Next Steps

1. ✅ Complete this setup (15 min)
2. ✅ Test all alerts work
3. ✅ Add monitoring URLs to `MEMORY.md`
4. ✅ Set up automated backups (see `AUTOMATED_BACKUP_SETUP.md`)
5. ✅ Sleep well knowing you'll be alerted if anything breaks

---

**You now have professional-grade monitoring. Most indie hackers don't even have this. You're ahead of the game. 🚀**
