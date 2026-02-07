# SHORTCUTS - Anti-Circle Commands

**Purpose:** Prevent running in circles. Fast commands to check status, see what's done, and move forward.

---

## 🚫 Anti-Circle Commands

### Check What's Already Done
```
/done
```
Shows everything in DONE.md - prevents rebuilding what exists.

### Check Current Status
```
/status
```
Full system status: builds running, queue, health, what's next.

### What's Blocking Me?
```
/blocked
```
Shows all tasks marked as blocked + why. Clear the path forward.

### What Should I Do Next?
```
/next
```
Top priority task from queue. No thinking, just execute.

### What Shipped This Week?
```
/wins
```
Everything completed in last 7 days. See the progress.

---

## 📅 Calendar Shortcuts (Already Built)

**Quick event creation:**
```bash
python3 ~/clawd/calendar/quick_calendar.py "leg 6pm"
python3 ~/clawd/calendar/quick_calendar.py "chest friday 630"
python3 ~/clawd/calendar/quick_calendar.py "meal sunday 5"
```

**Shorthand:**
- `leg 6pm` → Leg Day workout today at 6pm
- `chest fri 7` → Chest Day Friday at 7pm
- `meal sun 5` → Meal Prep Sunday at 5pm

---

## 🏗️ Build Commands

### Queue New Build
```
/build [description]
```
Adds to BUILD_QUEUE.md, auto-spawns when ready.

### Check Build Status
```
/building
```
What's currently building + ETA.

### Pause Autonomy
```
/pause
```
Stops auto-spawning builds (when you need focus time).

### Resume Autonomy
```
/resume
```
Restart auto-spawning.

---

## 💰 Revenue Tracking

### Current MRR
```
/mrr
```
Shows current monthly recurring revenue (auto-updated from Stripe once live).

### Revenue This Month
```
/revenue
```
Total revenue month-to-date.

### Days to $500 MRR
```
/countdown
```
Based on current growth rate, when you hit the goal.

---

## 📊 Dashboard Commands

### Open Dashboard
```
/dash
```
Opens Florida Freedom Dashboard in browser.

### Refresh Dashboard Data
```
/refresh
```
Pulls latest data and regenerates dashboard.

---

## 🧠 Memory Commands

### What Did We Build Yesterday?
```
/yesterday
```
Quick summary from yesterday's memory file.

### Search Memory
```
/remember [query]
```
Semantic search across all memory files.

Example: `/remember stripe integration` → finds all discussions about Stripe.

---

## ⚡ Content Commands

### Generate Tweet Batch
```
/tweets
```
Generate 7 days of tweet drafts, ready to approve.

### Approve Tweet
```
/approve [number]
```
Approve tweet #N from pending folder, queue for posting.

### Post Now
```
/post [number]
```
Post tweet #N immediately.

---

## 🎯 Focus Commands

### Clear My Mind
```
/brain-dump
```
Dump all your ideas into a file. I'll organize and queue tasks from it.

### What's the Plan?
```
/plan
```
Today's plan: what you should work on, when, and why.

### Block Time
```
/block [task] [hours]
```
Example: `/block "Revenue Dashboard" 3` → blocks 3 hours on calendar for deep work.

---

## 🔥 Emergency Commands

### Kill All Builds
```
/killall
```
Stop all running builds (if something goes wrong).

### Reset Queue
```
/reset-queue
```
Clear BUILD_QUEUE.md (fresh start).

### What's Broken?
```
/health
```
System health check - shows what's not working.

---

## 🎮 Quick Wins

### Ship Something Small
```
/quick-win
```
Generate a task that can ship in <1 hour. Momentum boost.

### Celebrate a Win
```
/win [description]
```
Log a win to daily tracker. Builds momentum.

Example: `/win "Shipped hybrid model strategy"`

---

## 📱 Voice Commands (Coming Soon)

Once voice integration is live:
- "Schedule leg day tomorrow at 6"
- "What's my MRR?"
- "What should I build next?"
- "Show me this week's wins"

---

## 🧭 Navigation

### Where Am I?
```
/context
```
Current goals, active builds, next steps. Full orientation in 30 seconds.

### What's the Mission?
```
/mission
```
Shows primary goal ($500 MRR by March 31) + current progress.

---

## 💡 Pro Tips

**Prevent Circular Work:**
1. Always check `/done` before starting something new
2. Use `/status` daily to stay oriented
3. Run `/wins` weekly to see momentum
4. Trust the system - if it's not in `/next`, don't do it

**Speed Up Decisions:**
- `/next` → tells you what to do
- `/quick-win` → when you need momentum
- `/blocked` → when stuck

**Stay Focused:**
- `/pause` → when you need heads-down time
- `/plan` → when you wake up lost
- `/mission` → when you forget why you're building

---

*Updated: 2026-02-07*

**Add new shortcuts anytime by telling Jarvis - this file evolves with your workflow.**
