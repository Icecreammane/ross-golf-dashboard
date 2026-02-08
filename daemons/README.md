# Twitter Monitoring Daemon

Production-ready daemon that monitors Ross's Twitter account (@_icecreammane) for opportunities.

---

## Features

✅ **Monitors mentions** every 15 minutes  
✅ **Checks DMs** for important messages  
✅ **Intelligent scoring** - flags golf, fitness, coaching, partnerships, product feedback  
✅ **Persistent storage** - JSON database of opportunities  
✅ **Auto-start** - launchd integration for reliability  
✅ **Error handling** - comprehensive logging and graceful failures  
✅ **Configurable filters** - adjust importance thresholds  

---

## Quick Start

### 1. Setup Credentials
```bash
# Follow guide to get Twitter API credentials
cat daemons/CREDENTIALS.md

# Add credentials to .env file
nano /Users/clawdbot/clawd/.env
```

### 2. Test
```bash
cd /Users/clawdbot/clawd
python3 daemons/test_twitter_daemon.py
```

### 3. Install
```bash
# Copy launchd configuration
cp daemons/com.clawdbot.twitter-daemon.plist ~/Library/LaunchAgents/

# Load and start
launchctl load ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist

# Verify running
launchctl list | grep twitter-daemon
```

### 4. Monitor
```bash
# Watch logs
tail -f logs/twitter-daemon.log

# View opportunities
cat data/twitter-opportunities.json | python3 -m json.tool
```

---

## Documentation

| File | Description |
|------|-------------|
| `CREDENTIALS.md` | How to get Twitter API credentials |
| `SETUP.md` | Complete setup and configuration guide |
| `README.md` | This file - quick overview |

---

## File Structure

```
daemons/
├── twitter_daemon.py              # Main daemon script
├── test_twitter_daemon.py         # Test suite
├── com.clawdbot.twitter-daemon.plist  # launchd config
├── README.md                      # This file
├── SETUP.md                       # Detailed setup guide
└── CREDENTIALS.md                 # How to get API keys

data/
├── twitter-opportunities.json     # Detected opportunities
└── twitter-daemon-state.json      # Daemon state (last IDs)

logs/
├── twitter-daemon.log             # Structured application log
├── twitter-daemon-stdout.log      # Console output
└── twitter-daemon-stderr.log      # Error output
```

---

## Opportunity Scoring

Opportunities are scored 0-100 based on:

| Category | Keywords | Weight |
|----------|----------|--------|
| **Golf** | golf, course, handicap, swing | 8 |
| **Fitness** | fitness, workout, training, nutrition | 9 |
| **Coaching** | coach, mentor, consulting, help me | 10 |
| **Partnership** | partner, collaborate, joint venture | 10 |
| **Product Feedback** | feedback, feature, suggestion, bug | 7 |

**Bonus points for:**
- Urgency signals (+5): "asap", "need", "looking for"
- Engagement (+3): "love", "amazing", "great"
- Questions (+2): Contains "?"
- Influential authors (+2-5): Based on follower count
- Direct messages (+10): DMs are prioritized

---

## Example Opportunities

```json
{
  "id": "mention_1234567890",
  "type": "mention",
  "sender": "golfer_pro",
  "content": "Hey @_icecreammane! Love your fitness approach. Looking for a coach to help with golf-specific training. Interested?",
  "timestamp": "2024-02-07T15:30:00+00:00",
  "url": "https://twitter.com/golfer_pro/status/1234567890",
  "score": 45,
  "opportunity_type": "coaching",
  "all_types": ["coaching", "fitness", "golf"],
  "reasons": [
    "coaching: coach",
    "fitness: fitness, training",
    "golf: golf",
    "urgency: looking for",
    "positive engagement: love",
    "contains question"
  ],
  "author_followers": 5420
}
```

---

## Adjusting Filters

To make filters more/less selective, edit `twitter_daemon.py`:

### More selective (fewer alerts):
- Increase minimum score: Line 274 (mentions) and 346 (DMs)
- Reduce keyword weights: Lines 45-68
- Remove generic keywords

### Less selective (more alerts):
- Decrease minimum score
- Increase keyword weights
- Add more keywords

See `SETUP.md` section 7 for detailed instructions.

---

## Management Commands

```bash
# Status
launchctl list | grep twitter-daemon

# Logs
tail -f ~/clawd/logs/twitter-daemon.log

# Manual run (don't wait 15 min)
launchctl start com.clawdbot.twitter-daemon

# Restart
launchctl unload ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist
launchctl load ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist

# Stop
launchctl unload ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist

# View top opportunities
python3 -c "
import json
with open('/Users/clawdbot/clawd/data/twitter-opportunities.json') as f:
    opps = json.load(f)
    for opp in sorted(opps, key=lambda x: x['score'], reverse=True)[:5]:
        print(f\"{opp['score']}: {opp['opportunity_type']} - @{opp['sender']}\")
"
```

---

## Troubleshooting

### Daemon not running
```bash
# Check system logs
log show --predicate 'process == "launchd"' --info --last 1h | grep twitter

# Check stderr
cat ~/clawd/logs/twitter-daemon-stderr.log
```

### No opportunities found
- Normal if no recent mentions/DMs
- Check score thresholds aren't too high
- Verify authentication worked (check logs)

### Rate limiting
- Daemon automatically waits if rate limited
- Running every 15 min stays within limits

---

## Security

✅ Credentials in `.env` (not committed to git)  
✅ Logs sanitized (no sensitive data)  
✅ User-level permissions (not root)  
✅ Local storage only (no cloud sync)  

---

## Support

- Check logs first: `tail -f ~/clawd/logs/twitter-daemon.log`
- Review setup guide: `cat daemons/SETUP.md`
- Test suite: `python3 daemons/test_twitter_daemon.py`

---

**Built with ❤️ by Jarvis for Ross**
