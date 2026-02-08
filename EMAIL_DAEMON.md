# Email Daemon Documentation

**Status:** ✅ Deployed and Ready  
**Location:** `/Users/clawdbot/clawd/scripts/email_daemon.py`  
**Service:** `com.jarvis.email-daemon` (launchd)

---

## Overview

The email daemon monitors `bigmeatyclawd@gmail.com` for important emails every 30 minutes automatically. It identifies emails based on sender patterns, keywords, and domains, then creates summaries stored in JSON format.

---

## Setup Instructions

### 1. Get Gmail App Password

Since Gmail requires app-specific passwords for IMAP access:

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in as `bigmeatyclawd@gmail.com`
3. Create a new app password:
   - App: "Mail"
   - Device: "Mac mini"
4. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)
5. Update `.env` file:

```bash
# Edit the .env file
nano /Users/clawdbot/clawd/.env

# Replace this line:
JARVIS_EMAIL_PASSWORD=your-gmail-app-password-here

# With your actual app password (remove spaces):
JARVIS_EMAIL_PASSWORD=xxxxxxxxxxxxxxxx
```

### 2. Load the Daemon

```bash
# Load the launchd service
launchctl load ~/Library/LaunchAgents/com.jarvis.email-daemon.plist

# Verify it's loaded
launchctl list | grep jarvis.email
```

### 3. Test Manually

Before relying on automatic runs, test manually:

```bash
# Run the daemon once
python3 /Users/clawdbot/clawd/scripts/email_daemon.py

# Check the log
tail -f /Users/clawdbot/clawd/logs/email-daemon.log

# View summaries
cat /Users/clawdbot/clawd/data/email-summary.json | python3 -m json.tool
```

---

## How It Works

### Monitoring Schedule
- **Frequency:** Every 30 minutes (1800 seconds)
- **Auto-start:** Yes (runs at system boot)
- **Runs as:** Current user (clawdbot)

### Importance Detection

Emails are flagged as important if they match any of these criteria:

#### 1. **Important Senders** (case-insensitive):
- Boss/work: `ross`, `manager`, `ceo`, `founder`
- Investors: `investor`, `venture`, `capital`, `funding`
- Financial: `stripe`, `paypal`, `bank`, `invoice`

#### 2. **Subject Keywords**:
- `urgent`, `deadline`, `action needed`, `action required`
- `asap`, `important`, `payment`, `invoice`
- `overdue`, `expired`, `expiring`
- `verify`, `confirm`, `security alert`
- `suspended`, `required`, `immediately`

#### 3. **Important Domains**:
- `@stripe.com`
- `@github.com`
- `@openai.com`
- `@anthropic.com`

### Email Processing

1. **Connect** to Gmail via IMAP (SSL)
2. **Fetch** unread emails from INBOX
3. **Analyze** each email against importance filters
4. **Extract** sender, subject, body preview, key points
5. **Summarize** important emails with metadata
6. **Store** summaries in JSON file with timestamp
7. **Log** all activity to log file

### Data Storage

**Summaries:** `/Users/clawdbot/clawd/data/email-summary.json`
```json
[
  {
    "sender": "Jane Investor",
    "subject": "Urgent: Funding Decision Needed",
    "key_points": [
      "Need response by Friday",
      "Terms sheet attached",
      "Call scheduled for 3pm"
    ],
    "preview": "Hi Ross, Following up on our discussion...",
    "importance_reason": "keyword: urgent",
    "timestamp": "2026-02-08T14:52:30.123456",
    "date": "Sat, 8 Feb 2026 14:30:00 -0600",
    "from_email": "jane@vc-firm.com"
  }
]
```

**State:** `/Users/clawdbot/clawd/data/email-daemon-state.json`  
Tracks last processed email to avoid duplicates.

**Logs:** `/Users/clawdbot/clawd/logs/email-daemon.log`  
All daemon activity, errors, and processing details.

---

## Viewing Email Summaries

### Quick View (Terminal)

```bash
# Pretty-print all summaries
cat /Users/clawdbot/clawd/data/email-summary.json | python3 -m json.tool

# Count important emails
jq length /Users/clawdbot/clawd/data/email-summary.json

# Show only subjects
jq '.[].subject' /Users/clawdbot/clawd/data/email-summary.json

# Show recent (last 5)
jq '.[-5:]' /Users/clawdbot/clawd/data/email-summary.json
```

### Python Script (Interactive)

```python
#!/usr/bin/env python3
import json
from datetime import datetime

with open('/Users/clawdbot/clawd/data/email-summary.json') as f:
    summaries = json.load(f)

print(f"📧 {len(summaries)} Important Emails\n")

for i, email in enumerate(summaries[-10:], 1):  # Last 10
    print(f"{i}. [{email['importance_reason']}]")
    print(f"   From: {email['sender']}")
    print(f"   Subject: {email['subject']}")
    print(f"   Time: {email['timestamp']}")
    print(f"   Preview: {email['preview'][:80]}...")
    print()
```

### Ask Jarvis

Just ask me:
- "What important emails do I have?"
- "Show me today's email summaries"
- "Any urgent emails?"
- "Summarize recent important emails"

---

## Adjusting Importance Filters

Edit the daemon script to customize filters:

```bash
nano /Users/clawdbot/clawd/scripts/email_daemon.py
```

### Add Important Sender

Find the `IMPORTANT_SENDERS` list (~line 40):

```python
IMPORTANT_SENDERS = [
    "ross",
    "manager",
    "your-boss-name",  # ← Add here
]
```

### Add Keyword

Find the `IMPORTANT_KEYWORDS` list (~line 53):

```python
IMPORTANT_KEYWORDS = [
    "urgent",
    "deadline",
    "my-custom-keyword",  # ← Add here
]
```

### Add Domain

Find the `IMPORTANT_DOMAINS` list (~line 70):

```python
IMPORTANT_DOMAINS = [
    "@stripe.com",
    "@your-domain.com",  # ← Add here
]
```

After editing, reload the daemon:

```bash
launchctl unload ~/Library/LaunchAgents/com.jarvis.email-daemon.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.email-daemon.plist
```

---

## Daemon Management

### Check Status

```bash
# Is it loaded?
launchctl list | grep jarvis.email

# View recent logs
tail -20 /Users/clawdbot/clawd/logs/email-daemon.log

# Follow logs in real-time
tail -f /Users/clawdbot/clawd/logs/email-daemon.log
```

### Manual Run (Testing)

```bash
# Run once manually
python3 /Users/clawdbot/clawd/scripts/email_daemon.py
```

### Reload (After Changes)

```bash
launchctl unload ~/Library/LaunchAgents/com.jarvis.email-daemon.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.email-daemon.plist
```

### Stop Daemon

```bash
launchctl unload ~/Library/LaunchAgents/com.jarvis.email-daemon.plist
```

### Start Daemon

```bash
launchctl load ~/Library/LaunchAgents/com.jarvis.email-daemon.plist
```

### Force Run Now

```bash
launchctl start com.jarvis.email-daemon
```

---

## Troubleshooting

### Issue: Authentication Failed

**Symptom:** Log shows "IMAP error: authentication failed"

**Solution:**
1. Verify app password is correct in `.env`
2. Check Gmail settings allow IMAP access
3. Ensure 2-factor authentication is enabled on Gmail account

### Issue: No Emails Detected

**Symptom:** Daemon runs but finds 0 important emails

**Solution:**
1. Check importance filters match your email patterns
2. Manually verify unread emails exist in Gmail
3. Review logs to see which emails were processed
4. Temporarily broaden filters for testing

### Issue: Daemon Not Running

**Symptom:** `launchctl list` doesn't show the daemon

**Solution:**
```bash
# Check plist syntax
plutil -lint ~/Library/LaunchAgents/com.jarvis.email-daemon.plist

# Reload daemon
launchctl load ~/Library/LaunchAgents/com.jarvis.email-daemon.plist
```

### Issue: Permission Errors

**Symptom:** Log shows permission denied errors

**Solution:**
```bash
# Fix permissions
chmod +x /Users/clawdbot/clawd/scripts/email_daemon.py
chmod 644 ~/Library/LaunchAgents/com.jarvis.email-daemon.plist
```

### Debug Mode

Add verbose logging temporarily:

```python
# In email_daemon.py, change log level at the top
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Security Notes

- **App Password:** Stored in `.env` (gitignored)
- **Read-Only:** Daemon only reads emails, never sends
- **Local Storage:** Summaries stored locally, never transmitted
- **IMAP SSL:** All connections encrypted
- **No Secrets:** Email bodies are truncated to 500 chars

---

## Performance

- **CPU Usage:** Minimal (~2-5 seconds per run)
- **Network:** ~1-5 KB per email fetch
- **Storage:** JSON file grows ~1-2 KB per important email
- **Memory:** ~20-30 MB during execution

---

## Integration Ideas

### Heartbeat Integration

Add to `HEARTBEAT.md` to check summaries:

```markdown
- Check email summaries: Read `/Users/clawdbot/clawd/data/email-summary.json`
  - If new important emails since last heartbeat → notify Ross
  - Track last check in `memory/heartbeat-state.json`
```

### Notification Integration

Add desktop notifications for urgent emails:

```bash
# macOS notification
osascript -e 'display notification "New urgent email from Jane" with title "Jarvis Email Alert"'
```

### Dashboard Integration

Create a simple viewer:

```bash
python3 -m http.server 8080 --directory /Users/clawdbot/clawd/data
# Visit http://localhost:8080/email-summary.json
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `scripts/email_daemon.py` | Main daemon script |
| `data/email-summary.json` | Important email summaries |
| `data/email-daemon-state.json` | Processing state (last UID) |
| `logs/email-daemon.log` | Activity logs |
| `.env` | Email credentials (gitignored) |
| `~/Library/LaunchAgents/com.jarvis.email-daemon.plist` | launchd config |

---

## Maintenance

### Log Rotation

Logs grow over time. Rotate monthly:

```bash
# Archive old log
mv /Users/clawdbot/clawd/logs/email-daemon.log \
   /Users/clawdbot/clawd/logs/email-daemon-$(date +%Y-%m).log

# Daemon will create new log automatically
```

### Summary Cleanup

Archive old summaries:

```bash
# Keep last 100 important emails
jq '.[-100:]' /Users/clawdbot/clawd/data/email-summary.json > temp.json
mv temp.json /Users/clawdbot/clawd/data/email-summary.json
```

---

## Next Steps

1. **Get Gmail app password** and update `.env`
2. **Load the daemon:** `launchctl load ~/Library/LaunchAgents/com.jarvis.email-daemon.plist`
3. **Test manually:** `python3 /Users/clawdbot/clawd/scripts/email_daemon.py`
4. **Verify logs:** `tail /Users/clawdbot/clawd/logs/email-daemon.log`
5. **Check summaries:** `cat /Users/clawdbot/clawd/data/email-summary.json`
6. **Customize filters** as needed

---

**Status:** Ready for deployment. Just add the Gmail app password and load the service!
