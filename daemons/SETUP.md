# Twitter Daemon Setup Guide

Complete setup instructions for the Twitter monitoring daemon.

---

## 1. Install Dependencies

```bash
cd /Users/clawdbot/clawd
pip3 install tweepy python-dotenv
```

---

## 2. Configure Twitter API Credentials

### Option A: Using 1Password (Recommended)

If credentials are already stored in 1Password:

```bash
# Use 1Password CLI to fetch credentials
op item get "Twitter API" --fields api_key,api_secret,access_token,access_secret,bearer_token
```

### Option B: Get Credentials from Twitter Developer Portal

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Create a new app or use existing app
3. Generate API Keys and Access Tokens
4. Ensure you have **Elevated** or **Academic** access for DM functionality (optional)

### Option C: Manual .env Configuration

Add these lines to `/Users/clawdbot/clawd/.env`:

```bash
# Twitter API Credentials
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
```

**Security Note:** The .env file should NOT be committed to git (it's already in .gitignore).

---

## 3. Test the Daemon Manually

Before setting up launchd, test that everything works:

```bash
cd /Users/clawdbot/clawd
python3 daemons/twitter_daemon.py
```

Expected output:
```
============================================================
🐦 Twitter Daemon starting...
   Time: 2024-XX-XX XX:XX:XX
✅ Authenticated as @_icecreammane (ID: ...)
   Last run: never
🔍 Checking mentions...
  Found 0 new opportunities in mentions
💬 Checking DMs...
  Found 0 important DMs
✅ No new opportunities to add
🐦 Twitter Daemon completed successfully
============================================================
```

Check the logs:
```bash
tail -f /Users/clawdbot/clawd/logs/twitter-daemon.log
```

Check the output file:
```bash
cat /Users/clawdbot/clawd/data/twitter-opportunities.json
```

---

## 4. Install launchd Service

Once testing is successful, install the daemon to run automatically every 15 minutes:

```bash
# Copy the plist to LaunchAgents directory
cp /Users/clawdbot/clawd/daemons/com.clawdbot.twitter-daemon.plist \
   ~/Library/LaunchAgents/

# Load and start the daemon
launchctl load ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist

# Verify it's loaded
launchctl list | grep twitter-daemon
```

---

## 5. Managing the Daemon

### Check Status
```bash
launchctl list | grep twitter-daemon
```

### View Logs
```bash
# Main application log (structured)
tail -f ~/clawd/logs/twitter-daemon.log

# Stdout log (console output)
tail -f ~/clawd/logs/twitter-daemon-stdout.log

# Stderr log (errors only)
tail -f ~/clawd/logs/twitter-daemon-stderr.log
```

### Stop the Daemon
```bash
launchctl unload ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist
```

### Restart the Daemon
```bash
launchctl unload ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist
```

### Trigger Manual Run (without waiting 15 minutes)
```bash
launchctl start com.clawdbot.twitter-daemon
```

---

## 6. View Opportunities

### View JSON directly
```bash
cat ~/clawd/data/twitter-opportunities.json | python3 -m json.tool
```

### Pretty print top opportunities
```bash
python3 -c "
import json
with open('/Users/clawdbot/clawd/data/twitter-opportunities.json') as f:
    opps = json.load(f)
    print(f'Total opportunities: {len(opps)}\n')
    for opp in sorted(opps, key=lambda x: x['score'], reverse=True)[:10]:
        print(f\"Score: {opp['score']} | Type: {opp['opportunity_type']} | From: @{opp['sender']}\")
        print(f\"  {opp['content'][:100]}...\")
        print(f\"  {opp['url']}\n\")
"
```

---

## 7. Adjusting Importance Filters

The daemon uses a scoring system to identify important opportunities. You can adjust the filters by editing `/Users/clawdbot/clawd/daemons/twitter_daemon.py`:

### Opportunity Keywords (Lines 42-68)

```python
KEYWORDS = {
    'golf': {
        'keywords': ['golf', 'golfer', 'course', ...],
        'weight': 8  # Increase/decrease this
    },
    'fitness': {
        'keywords': ['fitness', 'workout', ...],
        'weight': 9
    },
    # ... add more categories
}
```

**To add a new category:**
```python
'real_estate': {
    'keywords': ['property', 'real estate', 'housing', 'investment'],
    'weight': 7
}
```

### Score Thresholds

- **Mentions:** Minimum score of **5** to be saved (line 274)
- **DMs:** Minimum score of **10** to be saved (line 346)
- **DM Boost:** DMs get +10 bonus points (line 336)

**To make filters more selective** (fewer alerts):
- Increase minimum score thresholds
- Reduce keyword weights
- Remove generic keywords

**To make filters less selective** (more alerts):
- Decrease minimum score thresholds
- Increase keyword weights
- Add more keywords

### Urgency and Engagement Signals (Lines 70-81)

Add or remove signals that boost importance:

```python
URGENCY_SIGNALS = [
    'asap', 'urgent', 'quickly', ...
    # Add: 'deadline', 'time-sensitive', etc.
]

ENGAGEMENT_SIGNALS = [
    'love', 'amazing', 'awesome', ...
    # Add: 'interested', 'curious', etc.
]
```

### Author Influence (Lines 109-116)

Adjust follower count thresholds:

```python
if followers > 10000:    # Change to 50000 for higher bar
    score += 5            # Increase bonus
elif followers > 1000:
    score += 2
```

---

## 8. Troubleshooting

### Daemon not running
```bash
# Check system logs
log show --predicate 'process == "launchd"' --info --last 1h | grep twitter

# Check if file permissions are correct
ls -la ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist
# Should be readable by user
```

### Authentication errors
```bash
# Verify credentials are loaded
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv('/Users/clawdbot/clawd/.env')
print('API Key:', os.getenv('TWITTER_API_KEY')[:10] + '...' if os.getenv('TWITTER_API_KEY') else 'NOT SET')
"
```

### Rate limiting
The daemon uses `wait_on_rate_limit=True`, so it will automatically wait if rate limited. Check logs for "Rate limit" messages.

### DM access denied
DM access requires **Elevated** API access from Twitter. If you see "DM access requires elevated API access" in logs, this is expected for Basic access tier. The daemon will continue monitoring mentions.

---

## 9. Files and Locations

| File | Purpose |
|------|---------|
| `/Users/clawdbot/clawd/daemons/twitter_daemon.py` | Main daemon script |
| `/Users/clawdbot/clawd/daemons/com.clawdbot.twitter-daemon.plist` | launchd configuration |
| `/Users/clawdbot/clawd/.env` | API credentials (sensitive) |
| `/Users/clawdbot/clawd/data/twitter-opportunities.json` | Detected opportunities |
| `/Users/clawdbot/clawd/data/twitter-daemon-state.json` | Daemon state (last checked IDs) |
| `/Users/clawdbot/clawd/logs/twitter-daemon.log` | Structured application log |
| `~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist` | Installed launchd config |

---

## 10. Security Considerations

- ✅ API credentials stored in `.env` (not committed to git)
- ✅ Logs do NOT contain sensitive data (credentials, tokens)
- ✅ Opportunities JSON is local-only (not shared publicly)
- ✅ Daemon runs with user permissions (not root)
- ⚠️  Consider encrypting `.env` file with `gpg` for additional security
- ⚠️  Regularly rotate Twitter API credentials

---

## Quick Reference

```bash
# Install
pip3 install tweepy python-dotenv
cp daemons/com.clawdbot.twitter-daemon.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist

# Status
launchctl list | grep twitter-daemon

# Logs
tail -f ~/clawd/logs/twitter-daemon.log

# Restart
launchctl unload ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist

# Manual run
launchctl start com.clawdbot.twitter-daemon

# View opportunities
cat ~/clawd/data/twitter-opportunities.json
```

---

**Need help?** Check logs first, then consult this guide's Troubleshooting section.
