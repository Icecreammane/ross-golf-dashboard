# 📅 Google Calendar Integration Setup

**Status:** Ready to implement - needs Ross's authorization

## Why This Matters:

With calendar access, I can:
- ✅ Know when you're at work (don't interrupt during meetings)
- ✅ Remind you about upcoming events proactively
- ✅ "Meeting at 2pm, you haven't eaten lunch yet" type alerts
- ✅ Plan workouts around your schedule
- ✅ Track patterns ("You always skip breakfast on Tuesdays")

## What I Need From You:

### 1. Google Calendar API Access

**Steps:**
1. Go to: https://console.cloud.google.com/
2. Create new project (or use existing)
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Download credentials JSON
6. Give me the credentials file

**I can walk you through this step-by-step tomorrow morning!**

### 2. Permission Scope

I'll only request:
- ✅ Read calendar events (not create/edit)
- ✅ View free/busy times
- ❌ NO access to modify your calendar
- ❌ NO access to other Google services

## What I'll Build (Once I Have Access):

### Phase 1: Basic Integration
- Read today's events
- Show upcoming events on command ("What's on my calendar?")
- Morning brief includes today's schedule

### Phase 2: Proactive Alerts
- "Meeting in 30 minutes"
- "Free window 2-4pm - good time for gym?"
- "Busy day tomorrow, 6 meetings scheduled"

### Phase 3: Pattern Recognition
- "You always workout on days with <3 meetings"
- "Your most productive time: 10am-12pm (fewest interruptions)"
- Suggest optimal meal/workout times based on patterns

## Alternative: Apple Calendar

If you prefer, I can use macOS Calendar instead:
```bash
osascript -e 'tell application "Calendar" to get name of every calendar'
```

Pros: No OAuth, instant access
Cons: Less features than Google Calendar API

## Ready When You Are

Tomorrow morning, let me know if you want:
1. **Google Calendar** (more features, needs OAuth setup)
2. **Apple Calendar** (instant, less features)
3. **Both** (sync between them)

I'll guide you through setup and have it working in <10 minutes.

---

**Built:** 2026-02-02 20:41 CST
