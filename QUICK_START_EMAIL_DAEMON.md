# Quick Start: Email Daemon

**Time to deploy:** 5 minutes  
**Status:** Ready to go!

---

## 🚀 One-Time Setup

### 1. Get Gmail App Password (2 minutes)

```bash
# Open this URL in your browser:
open "https://myaccount.google.com/apppasswords"

# 1. Sign in as: bigmeatyclawd@gmail.com
# 2. Click "Create" or "Generate"
# 3. Select app: "Mail"
# 4. Select device: "Mac mini"
# 5. Copy the 16-character password (example: abcd efgh ijkl mnop)
# 6. Remove the spaces: abcdefghijklmnop
```

### 2. Add Password to .env (1 minute)

```bash
# Open .env file
nano /Users/clawdbot/clawd/.env

# Find this line:
JARVIS_EMAIL_PASSWORD=your-gmail-app-password-here

# Replace with your actual password (no spaces):
JARVIS_EMAIL_PASSWORD=abcdefghijklmnop

# Save: Ctrl+O, Enter, Ctrl+X
```

### 3. Run Setup (2 minutes)

```bash
# This will test and load the daemon
bash /Users/clawdbot/clawd/scripts/setup_email_daemon.sh
```

Done! The daemon is now running and will check emails every 30 minutes.

---

## 📧 View Your Email Summaries

```bash
# Pretty viewer
python3 /Users/clawdbot/clawd/scripts/view_email_summaries.py

# Raw JSON
cat /Users/clawdbot/clawd/data/email-summary.json | python3 -m json.tool

# Or just ask me: "Show me important emails"
```

---

## 🔧 Common Commands

```bash
# Force run now (don't wait 30 min)
launchctl start com.jarvis.email-daemon

# Check logs
tail -f /Users/clawdbot/clawd/logs/email-daemon.log

# Check service status
launchctl list | grep jarvis.email

# Reload after changes
launchctl unload ~/Library/LaunchAgents/com.jarvis.email-daemon.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.email-daemon.plist
```

---

## 🎯 What It Does

Every 30 minutes:
1. Connects to bigmeatyclawd@gmail.com
2. Fetches unread emails
3. Identifies important ones (urgent keywords, key senders, etc.)
4. Creates summaries with key points
5. Stores in `/Users/clawdbot/clawd/data/email-summary.json`
6. Logs everything to `/Users/clawdbot/clawd/logs/email-daemon.log`

**Important email criteria:**
- From: boss, investors, financial services
- Subject: urgent, deadline, action needed, payment, invoice
- Domains: stripe.com, github.com, openai.com, anthropic.com

---

## 📚 Full Docs

- **Complete guide:** `EMAIL_DAEMON.md`
- **Test report:** `EMAIL_DAEMON_TEST_REPORT.md`
- **Filter customization:** Edit `scripts/email_daemon.py`

---

That's it! Super simple. The daemon handles the rest automatically.
