# Social Media Post Scheduler

Automated system for generating and posting high-value social media content to Twitter/X.

## 📋 Overview

This system generates 2-3 social media post variations daily on topics including:
- Golf coaching insights
- Fitness and training
- Monetization journey
- Product updates
- High-value business content

Posts are automatically queued and posted to Twitter at optimal times (2am, 6am, 12pm, 6pm CST).

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Social Scheduler System                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌─────────────────┐           │
│  │ Post Generator   │────────>│  Queue (JSON)   │           │
│  │  (Daily 11pm)    │         │                 │           │
│  └──────────────────┘         └────────┬────────┘           │
│                                         │                    │
│                                         v                    │
│                               ┌─────────────────┐           │
│                               │ Twitter Poster  │           │
│                               │ (4x daily)      │           │
│                               └────────┬────────┘           │
│                                         │                    │
│                                         v                    │
│                               ┌─────────────────┐           │
│                               │  Twitter API    │           │
│                               └─────────────────┘           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Components

### 1. Post Generator (`scripts/generate_social_posts.py`)
- **Schedule:** Daily at 11:00 PM CST
- **Function:** Generates 2-3 post variations
- **Method:** Template-based (fast) with optional LLM enhancement
- **Output:** Writes to `data/social-posts-queue.json`

**Templates Cover:**
- Golf coaching tips and insights
- Fitness routines for golfers
- Business monetization lessons
- Product announcements and results
- High-value mental models and tactics

**LLM Mode (Optional):**
- Set `USE_LLM = True` in script for AI-generated variations
- Requires local Ollama with llama3.1:8b or similar
- Slower but more varied content
- Falls back to templates if LLM fails

### 2. Twitter Poster (`scripts/post_to_twitter.py`)
- **Schedule:** 2am, 6am, 12pm, 6pm CST (4x daily)
- **Function:** Posts next unposted item from queue
- **Features:**
  - 15-minute posting window around scheduled time
  - Automatic queue management
  - Posted item tracking
  - Comprehensive logging

### 3. Queue System (`data/social-posts-queue.json`)
- JSON array of post objects
- Tracks: ID, text, theme, timestamps, posting status
- Auto-cleanup: Removes posted items older than 7 days

### 4. Management Script (`scripts/manage_social_scheduler.sh`)
One-stop control for the entire system:
```bash
bash scripts/manage_social_scheduler.sh [command]
```

**Commands:**
- `install` - Install and activate all launchd jobs
- `uninstall` - Remove all jobs
- `start` - Start all jobs
- `stop` - Stop all jobs
- `status` - Show system status and queue
- `test` - Test post generation (dry run)

## 🚀 Quick Start

### 1. Twitter API Setup

Get your API credentials from [Twitter Developer Portal](https://developer.twitter.com/):

1. Create a new app or use existing
2. Get API keys and tokens
3. Create credentials file:

```bash
cp credentials/twitter-api.json.template credentials/twitter-api.json
```

4. Edit `credentials/twitter-api.json` with your credentials:
```json
{
  "api_key": "your_actual_api_key",
  "api_secret": "your_actual_api_secret",
  "access_token": "your_actual_access_token",
  "access_token_secret": "your_actual_access_token_secret"
}
```

### 2. Install Python Dependencies

```bash
pip3 install tweepy
```

### 3. Test the System

```bash
# Test post generation
bash scripts/manage_social_scheduler.sh test

# Test posting (dry run - won't actually post)
python3 scripts/post_to_twitter.py --dry-run
```

### 4. Install and Activate

```bash
# Install all launchd jobs
bash scripts/manage_social_scheduler.sh install

# Check status
bash scripts/manage_social_scheduler.sh status
```

## 📊 Monitoring

### Check Queue Status
```bash
bash scripts/manage_social_scheduler.sh status
```

### View Logs
```bash
# Recent activity
tail -50 logs/social-scheduler.log

# Follow live
tail -f logs/social-scheduler.log

# Search for errors
grep ERROR logs/social-scheduler.log
```

### Manual Actions

**Generate posts now:**
```bash
python3 scripts/generate_social_posts.py
```

**Post next item now (force, ignoring schedule):**
```bash
python3 scripts/post_to_twitter.py --force
```

**Dry run (test without posting):**
```bash
python3 scripts/post_to_twitter.py --dry-run
```

## ⚙️ Configuration

### Posting Schedule
Edit launchd plist files in `launchd/` to change times:
- `com.clawdbot.social-post-generator.plist` - Generation time (default: 11pm)
- `com.clawdbot.social-post-2am.plist` - 2am posting
- `com.clawdbot.social-post-6am.plist` - 6am posting
- `com.clawdbot.social-post-12pm.plist` - 12pm posting
- `com.clawdbot.social-post-6pm.plist` - 6pm posting

After editing, reload jobs:
```bash
bash scripts/manage_social_scheduler.sh stop
bash scripts/manage_social_scheduler.sh start
```

### Content Templates
Edit templates in `scripts/generate_social_posts.py`:
- Add new themes to `POST_TEMPLATES` dict
- Add variations to existing themes
- Customize hashtags and style

### Enable LLM Generation
1. Ensure Ollama is running: `ollama list`
2. Edit `scripts/generate_social_posts.py`
3. Change `USE_LLM = False` to `USE_LLM = True`
4. Test: `bash scripts/manage_social_scheduler.sh test`

**Note:** LLM generation is slower (~2-3 min per post) but creates more varied content.

## 🔧 Troubleshooting

### Posts Not Generating
```bash
# Check if generator job is loaded
launchctl list | grep social-post-generator

# Check logs
tail -50 logs/social-scheduler.log

# Test manually
python3 scripts/generate_social_posts.py
```

### Posts Not Posting
```bash
# Check if posting jobs are loaded
launchctl list | grep social-post

# Verify Twitter credentials
test -f credentials/twitter-api.json && echo "Credentials exist" || echo "Credentials missing"

# Test posting (dry run)
python3 scripts/post_to_twitter.py --dry-run

# Check queue has unposted items
cat data/social-posts-queue.json
```

### Twitter API Errors
- **401 Unauthorized:** Check API credentials
- **403 Forbidden:** Check app permissions (needs Read and Write)
- **429 Rate Limited:** Too many requests, wait 15 minutes
- **503 Service Unavailable:** Twitter API down, retry later

### LLM Timeouts
If using LLM mode and getting timeouts:
1. Increase timeout in script (current: 180s)
2. Use smaller model (llama3.1:8b recommended)
3. Switch to template mode: `USE_LLM = False`

## 📁 File Structure

```
/Users/clawdbot/clawd/
├── scripts/
│   ├── generate_social_posts.py       # Post generator
│   ├── post_to_twitter.py             # Twitter poster
│   └── manage_social_scheduler.sh     # Management script
├── launchd/
│   ├── com.clawdbot.social-post-generator.plist
│   ├── com.clawdbot.social-post-2am.plist
│   ├── com.clawdbot.social-post-6am.plist
│   ├── com.clawdbot.social-post-12pm.plist
│   └── com.clawdbot.social-post-6pm.plist
├── data/
│   └── social-posts-queue.json        # Post queue
├── credentials/
│   ├── twitter-api.json               # Your API keys (DO NOT COMMIT)
│   └── twitter-api.json.template      # Template file
├── logs/
│   └── social-scheduler.log           # System logs
└── SOCIAL_SCHEDULER.md                # This file
```

## 🛡️ Security Notes

1. **Never commit credentials:** `credentials/twitter-api.json` is gitignored
2. **Secure permissions:** Credentials directory is chmod 700
3. **API rate limits:** System respects Twitter's rate limits (4 posts/day well under limit)
4. **Logs contain no secrets:** Safe to share logs for debugging

## 🔄 Daily Workflow

**Automated (no action needed):**
1. **11:00 PM** - System generates 2-3 new posts
2. **2:00 AM** - First post of the day goes live
3. **6:00 AM** - Second post
4. **12:00 PM** - Third post
5. **6:00 PM** - Fourth post (if available)

**Manual maintenance (optional):**
- Review queue: `bash scripts/manage_social_scheduler.sh status`
- Add custom posts: Edit queue JSON directly
- Check results: View Twitter/X profile

## 🎯 Best Practices

1. **Review queue weekly:** Ensure content quality and variety
2. **Monitor logs:** Check for errors every few days
3. **Adjust templates:** Update based on what performs well
4. **Rotate themes:** System automatically rotates, but manual review helps
5. **Keep credentials secure:** Never share or commit API keys

## 🚦 Production Checklist

- [x] Twitter API credentials configured
- [x] Post generation tested
- [x] Twitter posting tested (dry run)
- [x] launchd jobs installed
- [x] System status verified
- [x] Logs monitoring set up
- [x] Backup credentials securely stored

## 📈 Future Enhancements

Potential additions:
- [ ] Analytics integration (track engagement)
- [ ] Image generation and upload
- [ ] Multi-platform support (LinkedIn, Instagram)
- [ ] A/B testing variations
- [ ] Reply automation
- [ ] Thread support
- [ ] Sentiment analysis
- [ ] Performance dashboard

## 📞 Support

**Check system status:**
```bash
bash scripts/manage_social_scheduler.sh status
```

**View recent logs:**
```bash
tail -50 logs/social-scheduler.log
```

**Force immediate post (testing):**
```bash
python3 scripts/post_to_twitter.py --force
```

---

**Built:** February 8, 2026  
**Version:** 1.0  
**Platform:** macOS (launchd)  
**License:** Personal use
