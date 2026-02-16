# Hinge Auto-Pilot - Quick Start 🚀

**Get up and running in 10 minutes.**

---

## Step 1: Install Dependencies (2 min)

```bash
bash ~/clawd/scripts/setup_hinge_autopilot.sh
```

This installs Playwright and Chromium browser.

---

## Step 2: Configure Your Preferences (2 min)

Edit your preferences:
```bash
nano ~/clawd/data/hinge_preferences.json
```

Or just use the defaults (already set to your type):
- Blonde/light brown hair
- 5'6" - 5'9" height
- 25-32 age
- Athletic/fit body
- 20 mile max distance

Save and exit (Ctrl+X, Y, Enter)

---

## Step 3: Login to Hinge (One-Time, 3 min)

```bash
python3 ~/clawd/scripts/hinge_browser.py
```

- Browser opens automatically
- Log into Hinge manually (phone + code)
- Wait for "Discover" page to load
- Script detects login and saves session
- Browser closes

**Your login is saved** - won't need to do this again!

---

## Step 4: Test Run (Dry Run, 2 min)

```bash
python3 ~/clawd/scripts/hinge_auto_swipe.py --dry-run --max-profiles 5
```

This will:
- Open Hinge
- Analyze 5 profiles
- Show scores and decisions
- **NOT actually swipe** (just testing)

Example output:
```
[1/5] Analyzing profile...

👤 Sarah, 27
📍 5.2 miles
📏 5'7"
⭐ Score: 8/10
🎯 Decision: LIKE
💭 Age 27 ✓ | 5'7" ✓ | 5.2mi ✓ | ✨ volleyball, fitness
✨ Green flags: volleyball, fitness

💚 Would like (dry run - not sent)
```

**Verify:**
- Scores look reasonable
- Decisions match your preferences
- Red flags are caught

---

## Step 5: First Real Run (1 min)

Ready to go live? Start small:

```bash
python3 ~/clawd/scripts/hinge_auto_swipe.py --max-profiles 5
```

This will actually swipe on 5 profiles.

**Watch for:**
- Likes being sent
- Match notifications
- Stats being tracked

---

## Step 6: Full Auto-Pilot (Optional)

If you want it to run automatically 2x per day:

```bash
python3 ~/clawd/scripts/setup_hinge_cron.py
```

Follow instructions to add cron jobs.

---

## Usage Commands

### Manual Runs
```bash
# Standard session (20 profiles)
python3 ~/clawd/scripts/hinge_auto_swipe.py

# Small session (10 profiles)
python3 ~/clawd/scripts/hinge_auto_swipe.py --max-profiles 10

# Test without swiping
python3 ~/clawd/scripts/hinge_auto_swipe.py --dry-run
```

### View Stats
```bash
# Open dashboard
open ~/clawd/dashboard/hinge_stats.html

# View raw activity
cat ~/clawd/data/hinge_activity.json | jq

# View matches
cat ~/clawd/data/hinge_matches.json | jq
```

### Check Notifications
```bash
python3 ~/clawd/scripts/hinge_notification_handler.py
```

---

## What Happens Next?

### Automated Mode (If you set up cron):
- **8:00 AM:** Morning swipe session (15 profiles)
- **7:00 PM:** Evening swipe session (15 profiles)
- **Silent:** No notifications except matches
- **Smart:** Stops at daily limit (12 likes)

### Manual Mode:
- Run whenever you want
- Control number of profiles
- Test with dry runs
- View stats anytime

---

## Expected Results

### First Week:
- **Profiles seen:** 200-300
- **Likes sent:** ~80-100 (12/day limit)
- **Matches:** 5-15 (varies by area/profile quality)
- **Time saved:** ~3.5 hours

### After Match:
- You get Telegram notification
- Open Hinge app
- Already matched
- Just send message

**No more endless swiping!**

---

## Troubleshooting

### "Login failed"
```bash
# Clear session and re-login
rm ~/clawd/data/hinge_session.json
python3 ~/clawd/scripts/hinge_browser.py
```

### "No profiles found"
- Hinge daily stack exhausted
- Wait a few hours
- Expand distance/age preferences

### "ModuleNotFoundError: playwright"
```bash
pip3 install playwright
python3 -m playwright install chromium
```

### Dashboard shows zeros
- Run at least one real swipe session first
- Refresh browser

---

## Tips

### Optimize Preferences:
- Start narrow (your exact type)
- Expand if too few matches
- Track what works in dashboard

### Avoid Bans:
- Keep daily limit ≤12 likes
- Don't disable random delays
- Mix in manual swiping occasionally

### Maximize Matches:
- Good profile pictures (on your Hinge)
- Interesting prompts (bio)
- Let the system run consistently

---

## Next Steps

1. ✅ **Setup complete** - System is ready
2. 📱 **Run first session** - Test with 5-10 profiles
3. 📊 **Check dashboard** - Verify stats tracking
4. ⏰ **Automate (optional)** - Set up cron jobs
5. 🔥 **Get matches** - Let it run!

**Questions?** See full docs: `HINGE_AUTOPILOT.md`

---

**Welcome to life without doom scrolling.** 🎉
