# 💰 Revenue Dashboard

A production-ready Flask application that displays real-time revenue metrics, MRR tracking, and progress toward business goals.

## Features

✅ **Real-Time Revenue Tracking**
- Live Stripe integration for subscriptions and payments
- Daily revenue calculations
- Monthly Recurring Revenue (MRR) tracking
- Total revenue (30-day rolling window)

✅ **Goal Progress Visualization**
- Big, motivating UI with progress bars
- Visual progress toward $500/mo MRR goal
- Projected run rate calculations
- Days-to-goal estimates

✅ **Multi-Channel Revenue Tracking**
- Notion template sales (via Stripe)
- Golf coaching inquiries (email/Twitter parsing)
- Active subscription count
- Lead tracking

✅ **Real-Time Updates**
- Stripe webhooks for instant updates
- Auto-refresh every 5 minutes
- Manual refresh button
- Live status indicator

✅ **Production Features**
- Comprehensive logging
- Error handling and recovery
- JSON data persistence
- Health check endpoint
- Responsive design

## Quick Start

### 1. Installation

```bash
cd revenue_dashboard
bash setup.sh
```

### 2. Configuration

Edit `.env` and add your API keys:

```bash
# Stripe Configuration
STRIPE_API_KEY=sk_live_your_actual_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Flask Configuration
FLASK_SECRET_KEY=your-random-secret-key

# Optional: Email (for coaching inquiries)
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

### 3. Run

**Development:**
```bash
source venv/bin/activate
python app.py
```

**Production:**
```bash
source venv/bin/activate
gunicorn --bind 0.0.0.0:3002 --workers 2 --timeout 120 app:app
```

### 4. Access

Open your browser to: **http://localhost:3002**

## Architecture

### Backend (Flask)

**Main Routes:**
- `GET /` - Dashboard UI
- `GET /api/metrics` - Fetch current metrics (JSON)
- `POST /api/refresh` - Force data refresh
- `POST /api/webhook/stripe` - Stripe webhook endpoint
- `POST /api/coaching/inquiry` - Add coaching inquiry
- `GET /health` - Health check

**Data Flow:**
1. App fetches Stripe data on startup
2. Data stored in `data/revenue_data.json`
3. Frontend polls `/api/metrics` every 5 minutes
4. Webhooks trigger immediate updates
5. Manual refresh available via button

### Frontend (JavaScript + HTML/CSS)

**Components:**
- `dashboard.html` - Main UI structure
- `dashboard.css` - Clean, motivating design
- `dashboard.js` - Data fetching, auto-refresh, animations

**UI Features:**
- Animated number transitions
- Smooth progress bar
- Dynamic motivational messages
- Responsive grid layout
- Real-time status indicator

### Data Storage

**Files:**
- `data/revenue_data.json` - Main data store
- `data/coaching_inquiries.json` - Inquiry tracking
- `logs/revenue_dashboard.log` - Application logs

**Data Structure:**
```json
{
  "stripe_sales": [...],
  "subscriptions": [...],
  "coaching_inquiries": [...],
  "mrr": 0,
  "total_revenue": 0,
  "last_updated": "2024-01-01T00:00:00"
}
```

## Stripe Integration

### API Setup

1. Get your Stripe API key from: https://dashboard.stripe.com/apikeys
2. Add to `.env` as `STRIPE_API_KEY`

### Webhook Setup

1. Go to: https://dashboard.stripe.com/webhooks
2. Create endpoint: `https://your-domain.com/api/webhook/stripe`
3. Select events:
   - `charge.succeeded`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copy webhook secret to `.env` as `STRIPE_WEBHOOK_SECRET`

### Testing Webhooks Locally

Use Stripe CLI:
```bash
stripe listen --forward-to localhost:3002/api/webhook/stripe
```

## Email Integration (Optional)

For golf coaching inquiry tracking:

### Gmail Setup

1. Enable 2FA on your Google account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Add to `.env`:
```bash
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
```

### Run Email Parser

Manual check:
```bash
python email_parser.py
```

Automated (cron):
```bash
# Check every hour
0 * * * * cd /path/to/revenue_dashboard && venv/bin/python email_parser.py
```

## Metrics Explained

### Monthly Recurring Revenue (MRR)
- Sum of all active subscription values normalized to monthly
- Annual subscriptions divided by 12
- Primary goal: $500/month

### Daily Revenue
- Sum of successful charges today
- Includes one-time payments and subscription renewals

### Total Revenue
- Sum of all successful charges in last 30 days
- Rolling window

### Days to Goal
- Calculated from recent growth rate
- Estimates when you'll hit $500 MRR
- Based on last 30 payments

### Projected Run Rate
- Current MRR + (average daily growth × 30)
- Forward-looking estimate

## Production Deployment

### Option 1: Systemd Service

```bash
bash setup.sh --systemd
sudo cp revenue-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable revenue-dashboard
sudo systemctl start revenue-dashboard
```

Check status:
```bash
sudo systemctl status revenue-dashboard
```

View logs:
```bash
sudo journalctl -u revenue-dashboard -f
```

### Option 2: Docker (Manual)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 3002
CMD ["gunicorn", "--bind", "0.0.0.0:3002", "--workers", "2", "app:app"]
```

Build and run:
```bash
docker build -t revenue-dashboard .
docker run -d -p 3002:3002 --env-file .env revenue-dashboard
```

### Option 3: Reverse Proxy (Nginx)

Add to nginx config:
```nginx
server {
    listen 80;
    server_name revenue.yourdomain.com;

    location / {
        proxy_pass http://localhost:3002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring

### Health Check

```bash
curl http://localhost:3002/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "stripe_configured": true
}
```

### Logs

View live logs:
```bash
tail -f logs/revenue_dashboard.log
```

Search for errors:
```bash
grep ERROR logs/revenue_dashboard.log
```

## Customization

### Change MRR Goal

Edit `app.py`:
```python
MRR_GOAL = 1000  # Change to your goal
```

### Adjust Auto-Refresh Interval

Edit `static/js/dashboard.js`:
```javascript
this.refreshInterval = 10 * 60 * 1000; // 10 minutes
```

### Modify Coaching Keywords

Edit `email_parser.py`:
```python
self.coaching_keywords = [
    'your',
    'custom',
    'keywords'
]
```

## Troubleshooting

### "No Stripe API key found"
- Check `.env` file exists
- Verify `STRIPE_API_KEY` is set
- Restart the application

### Webhooks not working
- Verify webhook secret in `.env`
- Check Stripe dashboard for failed deliveries
- Ensure endpoint is publicly accessible
- Test with Stripe CLI

### Email parser fails
- Verify Gmail App Password (not regular password)
- Check 2FA is enabled on Google account
- Ensure IMAP is enabled in Gmail settings

### Port 3002 already in use
```bash
# Find process using port
lsof -i :3002

# Kill process
kill -9 <PID>

# Or use different port
python app.py --port 3003
```

## Security Notes

🔒 **Never commit `.env` to git**
- Add `.env` to `.gitignore`
- Use environment variables in production

🔒 **Webhook signature verification**
- Always verify Stripe webhook signatures
- Prevents unauthorized data injection

🔒 **HTTPS in production**
- Stripe webhooks require HTTPS
- Use Let's Encrypt or Cloudflare

## API Reference

### GET /api/metrics

Returns current dashboard metrics.

**Response:**
```json
{
  "mrr": 125.50,
  "daily_revenue": 15.00,
  "total_revenue": 450.00,
  "days_to_goal": 45,
  "projected_run_rate": 200.00,
  "progress_percent": 25.1,
  "coaching_inquiries_count": 3,
  "subscription_count": 5,
  "last_updated": "2024-01-01T12:00:00"
}
```

### POST /api/refresh

Forces immediate data refresh from Stripe.

**Response:**
```json
{
  "mrr": 125.50,
  "daily_revenue": 15.00,
  ...
}
```

### POST /api/coaching/inquiry

Manually add a coaching inquiry.

**Request:**
```json
{
  "source": "twitter",
  "contact": "@username",
  "message": "Interested in lessons"
}
```

**Response:**
```json
{
  "status": "success",
  "inquiry": { ... }
}
```

## Tech Stack

- **Backend:** Flask 3.0
- **API:** Stripe Python SDK
- **Frontend:** Vanilla JavaScript (no frameworks)
- **Styling:** Custom CSS with gradients and animations
- **Data:** JSON file storage
- **Production:** Gunicorn WSGI server

## License

MIT - Feel free to use and modify for your own revenue tracking!

## Support

Questions? Check the logs first:
```bash
tail -n 100 logs/revenue_dashboard.log
```

Common issues are documented in the Troubleshooting section above.

---

**Built with 💪 for tracking revenue growth and staying motivated!**
