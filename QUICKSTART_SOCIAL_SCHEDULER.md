# Social Scheduler - Quick Start Guide

Get automated social media posting running in 5 minutes.

## ⚡ Quick Setup

### 1. Get Twitter API Credentials (5 minutes)

1. Go to https://developer.twitter.com/
2. Sign in and create a new app (or use existing)
3. Generate API keys and tokens
4. Save credentials:

```bash
cp credentials/twitter-api.json.template credentials/twitter-api.json
nano credentials/twitter-api.json  # Edit with your credentials
```

### 2. Install Dependencies

```bash
pip3 install tweepy
```

### 3. Test Everything

```bash
# Test post generation
bash scripts/manage_social_scheduler.sh test

# Test posting (dry run - won't actually post)
python3 scripts/post_to_twitter.py --dry-run --force
```

### 4. Go Live

```bash
# Install and start automated jobs
bash scripts/manage_social_scheduler.sh install

# Verify it's running
bash scripts/manage_social_scheduler.sh status
```

## ✅ You're Done!

The system will now:
- Generate 2-3 posts every night at 11pm
- Automatically post at 2am, 6am, 12pm, and 6pm CST
- Log everything to `logs/social-scheduler.log`

## 📊 Daily Monitoring

Check status anytime:
```bash
bash scripts/manage_social_scheduler.sh status
```

View recent posts:
```bash
tail -20 logs/social-scheduler.log
```

## 🛠️ Common Commands

```bash
# Check system status
bash scripts/manage_social_scheduler.sh status

# Generate posts now
python3 scripts/generate_social_posts.py

# Post next item now (ignoring schedule)
python3 scripts/post_to_twitter.py --force

# Stop all automation
bash scripts/manage_social_scheduler.sh stop

# Start automation again
bash scripts/manage_social_scheduler.sh start

# View logs
tail -50 logs/social-scheduler.log
```

## 🎯 What Gets Posted?

**Topics:**
- Golf coaching insights and tips
- Fitness routines for golfers
- Business and monetization lessons
- Product updates and student results
- High-value business tactics

**Schedule:**
- 2am CST - First post
- 6am CST - Second post
- 12pm CST - Third post
- 6pm CST - Fourth post

**Content Style:**
- Direct, conversational tone
- Specific and actionable
- 2-3 relevant hashtags
- Under 280 characters

## 🔍 Troubleshooting

**Posts not posting?**
```bash
# Check credentials
test -f credentials/twitter-api.json && echo "✅ Found" || echo "❌ Missing"

# Check jobs are running
launchctl list | grep social-post

# Try manual post
python3 scripts/post_to_twitter.py --force --dry-run
```

**Need to stop?**
```bash
bash scripts/manage_social_scheduler.sh stop
```

## 📖 Full Documentation

See `SOCIAL_SCHEDULER.md` for complete documentation.

---

**Ready to go!** The system is now managing your social media presence automatically. 🚀
