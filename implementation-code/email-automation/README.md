# Email Automation System - Quick Start

Automated email sequences for product launches. From signup to activation in 30 days. **Deploy in 30 minutes.**

## 🚀 Quick Start (10 minutes to first email)

### 1. Install Dependencies
```bash
pip install schedule
```

### 2. Configure Gmail SMTP
You already have credentials at `~/.credentials/gmail-smtp.json`

Or set environment variable:
```bash
export SMTP_EMAIL="bigmeatyclawd@gmail.com"
export SMTP_PASSWORD="your-app-specific-password"
```

**Get App-Specific Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other"
3. Copy the 16-character password
4. Save to `~/.credentials/gmail-smtp.json`:
   ```json
   {
     "email": "bigmeatyclawd@gmail.com",
     "password": "abcd efgh ijkl mnop"
   }
   ```

### 3. Test Connection
```bash
python smtp-config.py
```

Should see: `✓ SMTP connection successful`

### 4. Add Your First Subscriber
```bash
python welcome-sequence.py add test@example.com "John"
```

This immediately sends the Day 0 welcome email!

### 5. Start the Scheduler
```bash
python scheduler.py
```

**Done!** Emails will be sent automatically based on the sequence schedule.

---

## 📋 The 7-Email Sequence

The welcome sequence is pre-built for you:

| Day | Email | Purpose | Key Action |
|-----|-------|---------|-----------|
| 0 | Welcome | First impression | Get started CTA |
| 1 | Tutorial | Teach basics | Watch 3-min video |
| 3 | Tips | Increase engagement | Try power features |
| 5 | Success Story | Inspire with social proof | See what's possible |
| 7 | Upgrade | Promote premium | Discount code offer |
| 14 | Feedback | Gather insights | Survey link |
| 30 | Re-engagement | Win back inactive | Come back or leave |

**All templates are in `email-templates.json`** - customize freely!

---

## 🎨 Customizing Email Templates

### Edit Content
Open `email-templates.json` and modify:

```json
{
  "id": "welcome_day0",
  "delay_days": 0,
  "subject": "Your custom subject line",
  "title": "Email Title",
  "content": "<h2>Your HTML content</h2><p>...</p>"
}
```

### Available Variables
Use `{{variable_name}}` in templates:

- `{{first_name}}` - Subscriber's first name
- `{{sender_name}}` - Your name (default: "Ross")
- `{{dashboard_url}}` - Link to dashboard
- `{{tutorial_url}}` - Link to tutorial
- `{{blog_url}}` - Link to blog
- `{{pricing_url}}` - Link to pricing
- `{{feedback_url}}` - Link to feedback form
- `{{unsubscribe_url}}` - Unsubscribe link

**To add new variables:**
Edit `welcome-sequence.py`, line ~130 in the `variables` dict.

### Change Timing
Modify `delay_days` in the JSON:

```json
{
  "id": "tutorial_day1",
  "delay_days": 1,  // ← Change this (0 = immediate, 1 = next day, etc.)
  ...
}
```

### Add New Emails
Add to the `emails` array in JSON:

```json
{
  "id": "custom_email_day10",
  "delay_days": 10,
  "subject": "Your subject",
  "title": "Title",
  "content": "<p>Content</p>"
}
```

### Change Email Design
Edit `smtp-config.py`, function `wrap_html_email()`:

```python
# Line 145 - modify colors, fonts, layout
--background-color: #5469d4;  # Header color
--button-color: #5469d4;      # CTA button
```

---

## 🔧 How It Works

### 1. Subscriber Added
```bash
python welcome-sequence.py add user@example.com "Jane"
```

- Creates subscriber in SQLite database
- Sends Day 0 email immediately
- Schedules future emails based on signup date

### 2. Scheduler Runs (Every 30 Min)
```bash
python scheduler.py
```

- Checks database for subscribers
- Calculates days since signup
- Sends any due emails
- Logs sent emails to prevent duplicates

### 3. Subscriber Receives Email
- Opens email in inbox
- Clicks CTA button
- Gets next email in X days

---

## 📊 Managing Subscribers

### Add Subscriber
```bash
python welcome-sequence.py add email@example.com "First Name"
```

### List Subscribers
```bash
# Active subscribers
python welcome-sequence.py list

# Unsubscribed
python welcome-sequence.py list unsubscribed

# All
python welcome-sequence.py list all
```

### View Stats
```bash
python welcome-sequence.py stats
```

Output:
```
📊 Sequence Statistics
==================================================
Total subscribers: 127
Active: 89
Unsubscribed: 38
Emails sent: 453

Emails by type:
  welcome_day0: 127
  tutorial_day1: 98
  tips_day3: 76
  ...
```

### Unsubscribe User
```bash
python welcome-sequence.py unsubscribe email@example.com
```

### Process Emails Manually
```bash
python welcome-sequence.py process
```

---

## 🚀 Deployment

### Option 1: Background Process (Simple)
```bash
# Start scheduler
nohup python scheduler.py > email-scheduler.log 2>&1 &

# Check status
tail -f email-scheduler.log

# Stop
pkill -f scheduler.py
```

### Option 2: systemd Service (Recommended)
Create `/etc/systemd/system/email-scheduler.service`:

```ini
[Unit]
Description=Email Automation Scheduler
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/email-automation
ExecStart=/usr/bin/python3 scheduler.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable email-scheduler
sudo systemctl start email-scheduler
sudo systemctl status email-scheduler
```

### Option 3: Cron Job (Lightweight)
```bash
# Edit crontab
crontab -e

# Add line (runs every 30 minutes)
*/30 * * * * cd /path/to/email-automation && python3 scheduler.py once >> /var/log/email-scheduler.log 2>&1
```

---

## 🔌 Integration with Your App

### Flask Integration
```python
from welcome_sequence import WelcomeSequence

sequence = WelcomeSequence()

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data['email']
    first_name = data.get('first_name', '')
    
    # Add to email sequence
    sequence.add_subscriber(email, first_name)
    
    return jsonify({'success': True})

@app.route('/unsubscribe')
def unsubscribe():
    email = request.args.get('email')
    sequence.unsubscribe(email)
    return "You've been unsubscribed."
```

### Express (Node.js) Integration
```javascript
const { exec } = require('child_process');

app.post('/api/signup', (req, res) => {
    const { email, firstName } = req.body;
    
    // Call Python script
    exec(`python3 welcome-sequence.py add "${email}" "${firstName}"`, 
         (error, stdout, stderr) => {
        if (error) {
            console.error(error);
            return res.status(500).json({ error: 'Failed to add subscriber' });
        }
        res.json({ success: true });
    });
});
```

---

## 📧 Email Best Practices

### Subject Lines
- **Keep short:** 6-10 words max
- **Be specific:** "3 tips to X" > "Some tips"
- **Create curiosity:** "You're missing this feature"
- **Test emojis:** Use 1-2 max, test performance
- **Avoid spam words:** FREE, $$$ , URGENT

### Email Content
- **Scannable:** Short paragraphs, bullet points, bold key words
- **One CTA:** Don't give 5 links. Pick the most important action.
- **Personal:** Write like you're emailing a friend
- **Value-first:** Teach before you sell
- **Stories:** Real examples > abstract benefits

### Timing
- **Day 0:** Welcome + quick win
- **Day 1-7:** Education, build trust
- **Day 7+:** Upsell, premium features
- **Day 14+:** Engagement check
- **Day 30+:** Re-engagement or goodbye

### Testing
- **Send to yourself first:** Catch typos, broken links
- **Check spam score:** Use mail-tester.com
- **Test on mobile:** 50%+ opens are mobile
- **A/B test subject lines:** Track open rates

---

## 🔐 Security & Compliance

### GDPR Compliance
- [ ] Clear opt-in (checkbox, not pre-checked)
- [ ] Privacy policy linked
- [ ] Unsubscribe link in every email
- [ ] Delete data on request

### CAN-SPAM Compliance (US)
- [ ] Real "From" address
- [ ] Accurate subject lines
- [ ] Physical address in footer
- [ ] Unsubscribe link works within 10 days
- [ ] Honor unsubscribe immediately

### Email Security
- [ ] Use app-specific passwords (not main Gmail password)
- [ ] Don't commit passwords to git
- [ ] Rotate credentials quarterly
- [ ] Log email sending for audit trail

---

## 📈 Tracking Performance

### Key Metrics to Track
1. **Open rate** - % who open emails (avg: 15-25%)
2. **Click rate** - % who click links (avg: 2-5%)
3. **Conversion rate** - % who take desired action
4. **Unsubscribe rate** - Keep below 0.5%
5. **Spam complaints** - Keep below 0.1%

### Adding Open Tracking
Add to HTML:
```html
<img src="https://yoursite.com/track/open/{{subscriber_id}}/{{email_id}}" width="1" height="1" />
```

Track in Flask:
```python
@app.route('/track/open/<sub_id>/<email_id>')
def track_open(sub_id, email_id):
    # Log open event
    db.execute("UPDATE email_log SET opened_at = ? WHERE subscriber_id = ? AND email_id = ?",
               datetime.now(), sub_id, email_id)
    
    # Return 1x1 transparent pixel
    return send_file('pixel.png', mimetype='image/png')
```

### Adding Click Tracking
Wrap links:
```html
<a href="https://yoursite.com/track/click?url={{encoded_url}}&sub={{subscriber_id}}&email={{email_id}}">
    Click here
</a>
```

---

## 🧪 Testing

### Test the Full Flow
```bash
# Test SMTP connection
python smtp-config.py

# Add test subscriber
python welcome-sequence.py add test+1@yourdomain.com "Test User"

# Check email was sent (Day 0)
# Check your inbox

# Manually trigger Day 1 email (for testing)
# Edit database to set signed_up_at to 1 day ago, then:
python welcome-sequence.py process

# View stats
python welcome-sequence.py stats
```

### Test Script
```bash
bash test-emails.sh
```

This will:
1. Test SMTP connection
2. Send test email
3. Add test subscriber
4. Verify database entries

---

## 🐛 Troubleshooting

### "SMTP Authentication Error"
- Check app-specific password is correct
- Verify 2FA is enabled on Gmail account
- Generate new app password at myaccount.google.com/apppasswords

### "Connection Timed Out"
- Check internet connection
- Verify firewall allows port 587
- Try port 465 (SSL) instead of 587 (TLS)

### Emails Not Sending
```bash
# Check scheduler is running
ps aux | grep scheduler

# Check logs
tail -f email-scheduler.log

# Manually process emails to see errors
python welcome-sequence.py process
```

### Emails Going to Spam
- **Warm up your domain:** Start with 50 emails/day, increase gradually
- **Set up SPF/DKIM:** Add DNS records
- **Good content:** Avoid spam trigger words
- **Low complaint rate:** Honor unsubscribes
- **Test spam score:** mail-tester.com

### Database Locked Error
- Only run one scheduler instance
- Close database connections properly
- Use `PRAGMA journal_mode=WAL` in SQLite

---

## 🎯 Next Steps

1. **Customize templates** - Replace placeholder content
2. **Add more sequences** - Create abandoned cart, trial ending, etc.
3. **Set up tracking** - Implement open/click tracking
4. **A/B test** - Test subject lines and send times
5. **Segment users** - Send different sequences based on behavior
6. **Add webhooks** - Trigger emails from Stripe, Zapier, etc.

---

**Time to ship:** ~30 minutes from here to automated emails 🚀
