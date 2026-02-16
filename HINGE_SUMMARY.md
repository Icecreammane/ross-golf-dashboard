# Hinge Auto-Pilot: Build Complete ✅

## What You Got

**A system that turns Hinge from a dopamine slot machine into a useful notification service.**

Instead of:
- Opening Hinge
- Swiping 100 times
- Getting 2-3 matches
- Wasting 30 minutes

You get:
- Telegram notification: "🔥 New match: Sarah, 27, loves volleyball"
- Open Hinge
- Already matched
- Just message

---

## Quick Start (10 Minutes)

### 1. Install (1 command, 2 min)
```bash
bash ~/clawd/scripts/setup_hinge_autopilot.sh
```

### 2. Login (one-time, 3 min)
```bash
python3 ~/clawd/scripts/hinge_browser.py
```
Browser opens → Log into Hinge → Done

### 3. Test (dry run, 2 min)
```bash
python3 ~/clawd/scripts/hinge_auto_swipe.py --dry-run --max-profiles 5
```
See scores, verify preferences work

### 4. Go Live (1 min)
```bash
python3 ~/clawd/scripts/hinge_auto_swipe.py --max-profiles 5
```
Actually swipes on 5 profiles

### 5. Automate (optional)
```bash
python3 ~/clawd/scripts/setup_hinge_cron.py
```
Runs 2x daily (8am, 7pm)

---

## What It Does

### Smart Scoring (1-10)
- ✅ Blonde/light brown hair
- ✅ 5'6" - 5'9" height
- ✅ 25-32 age
- ✅ Fit/athletic body
- ✅ Within 20 miles
- ❌ Red flags (drama, exes, money)
- ✨ Green flags (fitness, volleyball)

**Score ≥7 = Like**  
**Score <7 = Skip**

### Automation
- Logs into Hinge
- Reviews 15-20 profiles per session
- Auto-likes high-scoring profiles
- Respects 12 likes/day limit
- Random delays (15-45 sec) to appear human
- Detects matches
- Sends Telegram notification on match only

### Dashboard
```bash
open ~/clawd/dashboard/hinge_stats.html
```
- Profiles seen/liked/matched
- Match rate %
- Today's activity
- Recent matches

---

## Files

- **Main:** `scripts/hinge_auto_swipe.py`
- **Config:** `data/hinge_preferences.json`
- **Stats:** `data/hinge_activity.json`
- **Matches:** `data/hinge_matches.json`
- **Dashboard:** `dashboard/hinge_stats.html`
- **Docs:** `HINGE_AUTOPILOT.md` (complete)
- **Quick Start:** `HINGE_QUICKSTART.md`

---

## Commands

```bash
# Standard run (20 profiles)
python3 ~/clawd/scripts/hinge_auto_swipe.py

# Small run (10 profiles)
python3 ~/clawd/scripts/hinge_auto_swipe.py --max-profiles 10

# Test (no swipes)
python3 ~/clawd/scripts/hinge_auto_swipe.py --dry-run

# View dashboard
open ~/clawd/dashboard/hinge_stats.html

# View stats
cat ~/clawd/data/hinge_activity.json | jq
```

---

## Expected Results

**Week 1:**
- 200-300 profiles seen
- 80-100 likes sent (12/day limit)
- 5-15 matches
- 3.5 hours saved

**After Match:**
- Get Telegram notification
- Open Hinge
- Already matched
- Just message

---

## What's Next

1. **Test it:** Run dry-run to verify
2. **Try it:** 5-profile real run
3. **Automate it:** Set up cron if you like it
4. **Phase 2:** Add vision analysis (analyze photos with AI)

---

## Safety

- ✅ Respects rate limits (12 likes/day)
- ✅ Human-like delays
- ✅ No mass-liking
- ✅ No automated messaging
- ✅ Local data only

---

## The Impact

**Before:** Dating app = dopamine trap  
**After:** Dating app = notification system

**Time saved:** ~30 min/day = 182 hours/year

**Focus shift:** From process to outcome

---

**Status:** ✅ Ready to test  
**Built:** 2026-02-07 (90 minutes)  
**Committed:** Git + pushed to GitHub

**Read full docs:** `cat ~/clawd/HINGE_AUTOPILOT.md`  
**Quick start:** `cat ~/clawd/HINGE_QUICKSTART.md`
