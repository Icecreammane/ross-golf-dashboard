# Twitter Daemon - Quick Start Guide

Get the daemon running in 5 minutes.

---

## Step 1: Get Twitter API Credentials (5 minutes)

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Sign in with @_icecreammane account
3. Create app: "Ross Twitter Monitor"
4. Generate:
   - API Key & Secret
   - Access Token & Secret
   - Bearer Token
5. Set permissions to: **Read + Write + Direct Messages**

📖 Detailed instructions: `cat daemons/CREDENTIALS.md`

---

## Step 2: Add Credentials to .env

```bash
nano /Users/clawdbot/clawd/.env
```

Add at the bottom:
```bash
TWITTER_API_KEY=your_actual_api_key
TWITTER_API_SECRET=your_actual_api_secret
TWITTER_ACCESS_TOKEN=your_actual_access_token
TWITTER_ACCESS_SECRET=your_actual_access_secret
TWITTER_BEARER_TOKEN=your_actual_bearer_token
```

Save and exit (Ctrl+X, Y, Enter)

---

## Step 3: Test It Works

```bash
cd /Users/clawdbot/clawd
python3 daemons/test_twitter_daemon.py
```

✅ Should see: "All tests passed! Daemon is ready for production."

If tests fail, check credentials and review error messages.

---

## Step 4: Install & Start Daemon

```bash
# Copy launchd config
cp daemons/com.clawdbot.twitter-daemon.plist ~/Library/LaunchAgents/

# Start it
launchctl load ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist

# Verify running
launchctl list | grep twitter-daemon
```

✅ Should see: "com.clawdbot.twitter-daemon" with a PID

---

## Step 5: Watch It Work

```bash
# Watch logs (live)
tail -f logs/twitter-daemon.log

# Or view opportunities
cat data/twitter-opportunities.json
```

The daemon runs every 15 minutes automatically!

---

## Daily Usage

### View Top Opportunities
```bash
cd /Users/clawdbot/clawd
python3 -c "
import json
with open('data/twitter-opportunities.json') as f:
    opps = sorted(json.load(f), key=lambda x: x['score'], reverse=True)[:10]
    for o in opps:
        print(f\"\n🔥 Score {o['score']}: {o['opportunity_type'].upper()}\")
        print(f\"   From: @{o['sender']} ({o['author_followers']:,} followers)\")
        print(f\"   {o['content'][:100]}...\")
        print(f\"   {o['url']}\")
"
```

### Check Logs
```bash
tail -20 logs/twitter-daemon.log
```

### Manual Run (don't wait 15 min)
```bash
launchctl start com.clawdbot.twitter-daemon
```

---

## Troubleshooting

### "Authentication failed"
- Double-check credentials in `.env`
- Ensure no extra spaces
- Verify app permissions include DMs

### "No opportunities found"
- Normal if no recent mentions
- Check `logs/twitter-daemon.log` for details
- Try lowering score threshold in `twitter_daemon.py` line 274

### "Daemon not running"
```bash
# Check errors
cat logs/twitter-daemon-stderr.log

# Restart
launchctl unload ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist
```

---

## Stop/Remove Daemon

```bash
# Stop
launchctl unload ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist

# Remove (optional)
rm ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist
```

---

## What's Next?

- Adjust importance filters: `nano daemons/twitter_daemon.py`
- Review setup guide: `cat daemons/SETUP.md`
- Check credentials guide: `cat daemons/CREDENTIALS.md`
- Read full README: `cat daemons/README.md`

---

**That's it! Your Twitter monitoring daemon is now running 24/7.** 🎉
