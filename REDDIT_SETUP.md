# Reddit API Setup Guide

**Status:** Placeholder mode (manual scanning until API configured)  
**Time to set up:** 10 minutes  
**Cost:** Free (Reddit API is free for personal use)

---

## 🎯 What This Unlocks

**Automated Reddit scanning:**
- Finds "need help" posts in target subreddits
- Scores by relevance + urgency
- Drafts personalized responses
- Appears in your morning brief

**Result:** First-mover advantage on hot opportunities

---

## 📋 Setup Steps

### 1. Create Reddit App

1. Go to https://www.reddit.com/prefs/apps
2. Scroll to bottom, click "create another app"
3. Fill in:
   - **Name:** Ross's Opportunity Scanner
   - **Type:** script
   - **Description:** Personal opportunity scanner
   - **Redirect URI:** http://localhost:8080
4. Click "create app"

### 2. Get Credentials

After creating, you'll see:
- **client_id:** (under the app name, looks like: `abc123def456`)
- **client_secret:** (labeled "secret")

**Copy these - you'll need them next.**

### 3. Add to Environment

```bash
# Edit .env file
nano ~/clawd/.env

# Add these lines:
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USER_AGENT=OpportunityScanner/1.0 by u/your_username

# Save: Ctrl+X, Y, Enter
```

### 4. Install PRAW (Reddit API Wrapper)

```bash
pip3 install praw
```

### 5. Test the Scanner

```bash
python3 ~/clawd/scripts/reddit_scanner.py
```

**You should see:**
- ✅ Opportunities found
- 📁 Report generated in `~/clawd/revenue/`

---

## 🔧 Configuration

**Edit target subreddits:**
Open `~/clawd/scripts/reddit_scanner.py` and modify:

```python
TARGET_SUBS = [
    "Fitness",           # Fitness tracker opportunities
    "SideProject",       # Builders looking for solutions
    "Entrepreneur",      # Business automation needs
    "webdev",           # Technical problems
    "productivity",     # Workflow optimization
    "learnprogramming"  # Beginners needing tools
]
```

**Edit keywords:**
```python
OPPORTUNITY_KEYWORDS = [
    "fitness app",
    "track workouts",
    # Add your own...
]
```

---

## 🤖 Integrate with Night Shift

Once working, add to `scripts/jarvis-daemon.py`:

```python
# In night_shift() function:
run_command(
    "python3 ~/clawd/scripts/reddit_scanner.py",
    "Reddit opportunity scan"
)
```

**Now it runs automatically at 2am every night.**

---

## 📊 What You'll Get

**Every morning in your brief:**

```
🔥 Reddit Opportunities (3 high priority)

1. "Looking for fitness tracking app" - r/Fitness
   - 45 upvotes, 12 comments
   - Relevance: 90%
   - Suggested response: [personalized template]

2. "Anyone building meal planning automation?" - r/SideProject
   - 23 upvotes, 8 comments  
   - Relevance: 85%
   - Suggested response: [personalized template]
```

---

## 🎯 Usage Strategy

**Don't spam. Build relationships.**

**Good approach:**
1. Reply with genuine help first
2. Mention you're building something similar
3. Ask what features they need
4. Offer early access if there's fit

**Bad approach:**
1. "Check out my product!" ❌
2. Generic sales pitch ❌
3. No context or value ❌

**Remember:** Audience → Trust → Customers

---

## 🚀 Current Status

**Placeholder mode:** Scanner generates example opportunities

**After API setup:** Real-time scanning of Reddit

**Takes 10 minutes to set up when you're ready.**

---

*For now, you can manually check r/Fitness and r/SideProject daily. When ready to automate, follow this guide.*
