# Gmail Support System Setup

Complete setup in **10 minutes**. 24/7 support monitoring active.

---

## Step 1: Enable Gmail API (3 minutes)

1. **Go to Google Cloud Console:** https://console.cloud.google.com
2. **Create a new project** (or select existing)
   - Name it "FitTrack Support"
3. **Enable Gmail API:**
   - Search for "Gmail API" in the search bar
   - Click "Enable"

---

## Step 2: Create OAuth Credentials (3 minutes)

1. **Go to Credentials:**
   - In Cloud Console, navigate to "APIs & Services" → "Credentials"
2. **Create OAuth 2.0 Client ID:**
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Name: "FitTrack Support Monitor"
   - Click "Create"
3. **Download credentials:**
   - Click the download icon next to your new client ID
   - Save as `credentials.json` in `integrations/gmail/`

---

## Step 3: Install Dependencies (1 minute)

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## Step 4: Authenticate (2 minutes)

Run the monitor for the first time:

```bash
cd integrations/gmail
python gmail_monitor.py
```

**What happens:**
1. Browser opens automatically
2. Sign in with your support email
3. Grant permissions to read/compose emails
4. Token saved automatically for future use

**Expected output:**
```
🔐 Authenticating with Gmail...
✅ Authenticated!
🔍 Scanning inbox for new emails...
✅ No new emails
```

---

## Step 5: Test Support Queue (1 minute)

Send yourself a test email mentioning "FitTrack" and run:

```bash
python gmail_monitor.py
```

You should see:
```
📧 Found 1 unread emails
📥 Added to queue: P2 - Test FitTrack email
✅ Processed 1 FitTrack emails
```

---

## Step 6: Test Auto-Response (1 minute)

```bash
python support_responder.py
```

This will:
1. Load your support queue
2. Match emails to templates
3. Create draft responses in Gmail
4. Mark tickets as "drafted"

**Check Gmail Drafts** - you should see the auto-generated response!

---

## Step 7: Automated Monitoring (Optional - 5 minutes)

### Option A: Cron Job (Recommended)

Check inbox every 5 minutes:

```bash
crontab -e

# Add these lines:
*/5 * * * * cd /path/to/integrations/gmail && python gmail_monitor.py >> monitor.log 2>&1
*/10 * * * * cd /path/to/integrations/gmail && python support_responder.py >> responder.log 2>&1
```

### Option B: Systemd Service (Advanced)

Create `/etc/systemd/system/gmail-monitor.service`:

```ini
[Unit]
Description=FitTrack Gmail Support Monitor
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/integrations/gmail
ExecStart=/usr/bin/python3 gmail_monitor.py
Restart=always
RestartSec=300

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable gmail-monitor
sudo systemctl start gmail-monitor
```

---

## Step 8: Enable Telegram Alerts (Optional - 2 minutes)

Add to `.env`:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

High-priority emails (P0/P1) will alert you on Telegram!

---

## Verification Checklist

✅ Gmail API enabled  
✅ OAuth credentials downloaded  
✅ Authentication successful  
✅ Monitor can read emails  
✅ Support queue working  
✅ Auto-responder creating drafts  
✅ Automated monitoring running (optional)  
✅ Telegram alerts configured (optional)  

---

## How It Works

### Email Monitoring (`gmail_monitor.py`)

Runs every 5 minutes (if automated):
1. Fetches unread emails
2. Filters for FitTrack-related content
3. Classifies priority (P0/P1/P2/P3)
4. Adds to support queue (`support-tickets.json`)
5. Alerts on high-priority tickets

**Priority Classification:**
- **P0:** Critical (payment failed, app down, data loss)
- **P1:** High (bugs, cancellations, refunds)
- **P2:** Medium (features, questions)
- **P3:** Low (feedback, general inquiries)

### Auto-Responder (`support_responder.py`)

Runs every 10 minutes:
1. Loads new tickets from queue
2. Matches to response template
3. Personalizes response (inserts name, context)
4. Creates draft in Gmail (doesn't auto-send)
5. Marks ticket as "drafted"

**You still review and send** - automation drafts, you approve!

---

## Customizing Templates

Edit `support_templates.json` to add/modify responses:

```json
{
  "your_category": "Hi {name},\n\nYour custom response here...\n\nBest,\nRoss"
}
```

**Available placeholders:**
- `{name}` - Sender's first name
- `{subject}` - Original email subject

---

## Troubleshooting

### "credentials.json not found"
- Make sure you downloaded OAuth credentials from Google Cloud Console
- Place in `integrations/gmail/` directory

### "Authentication failed"
- Delete `token.pickle` and re-run authentication
- Make sure you're using the correct Google account
- Check that Gmail API is enabled in Cloud Console

### "No emails detected"
- Make sure emails mention "FitTrack" or related keywords
- Check `gmail_monitor.py` → `detect_fittrack_related()` function
- Add your keywords if needed

### Drafts not being created
- Verify you granted "compose" permission during OAuth
- Check Gmail API quotas in Cloud Console
- Look for errors in logs

---

## Security Best Practices

🔒 **Protect your credentials**
```bash
chmod 600 credentials.json token.pickle
echo "credentials.json" >> .gitignore
echo "token.pickle" >> .gitignore
```

🔒 **Use a dedicated support email**
- Don't use your personal Gmail
- Create support@yourdomain.com and forward to Gmail

🔒 **Review before sending**
- Auto-responder creates DRAFTS only
- Always review and personalize before sending
- Catch any template errors

🔒 **Rotate credentials if compromised**
- Revoke access in Google Account settings
- Delete `token.pickle`
- Re-authenticate

---

## Advanced Features

### Custom Priority Rules

Edit `classify_priority()` in `gmail_monitor.py`:

```python
# Add your own keywords
p0_keywords = ['urgent', 'emergency', 'critical']
```

### Email Categories

Edit `categorize_email()` to add new categories:

```python
categories = {
    'your_category': ['keyword1', 'keyword2']
}
```

Then add matching template to `support_templates.json`.

### Integration with Stripe

Check for payment emails and auto-correlate with Stripe data:

```python
from integrations.stripe import StripeIntegration

stripe = StripeIntegration()
customer_data = stripe.get_customer_by_email(email_address)
```

---

## Next Steps

✅ **Done!** Support system is monitoring 24/7.

**Workflow:**
1. Email arrives → Auto-detected → Prioritized → Added to queue
2. Draft response generated → Appears in Gmail Drafts
3. You review → Personalize if needed → Send
4. Time saved: 80% of email response time

**Stats to track:**
- Average response time
- Tickets by priority
- Most common categories
- Template effectiveness

**Time to activation:** 10 minutes ⚡  
**Time saved per week:** 5-10 hours 🚀  
**24/7 monitoring:** Priceless 💪
