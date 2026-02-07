# MODE SCHEDULER

## Daily Rhythm (Monday-Friday)

This is the default schedule. Modes can be triggered manually or by events, but this is the baseline rhythm.

---

## 🌅 MORNING (7:30am - 12:00pm)

### 7:30am - ACCOUNTABILITY MODE: Morning Brief
**Duration:** 5 minutes
**Action:** Send morning brief + get today's commitment

**Output:**
```
☀️ GOOD MORNING

Yesterday's recap + Today's recommended commitment
Get explicit YES from Ross
```

**Files Updated:**
- `memory/accountability-commitments.json` (log commitment)
- `memory/accountability-daily-[DATE].md` (start daily log)

---

### 8:00am - SALES MODE ACTIVATE
**Duration:** 4 hours (8am-12pm)
**Action:** Find leads, draft outreach, research competitors

**Parallel:** ACCOUNTABILITY MODE monitoring in background

**Activities:**
1. Scan Reddit for leads (30 min)
2. Qualify leads (30 min)
3. Draft personalized outreach (1.5 hours)
4. Competitor research (1 hour)
5. Warm lead follow-ups (30 min)

**Output:** Sales Mode Report at 12pm

**Files Updated:**
- `memory/sales-crm.json` (leads)
- `memory/sales-drafts-[DATE].md` (messages)
- `memory/sales-context.json` (state)

---

### 10:00am - SUPPORT MODE CHECK #1
**Duration:** 15-30 minutes
**Action:** Check inbox, triage issues, draft responses

**Interrupts:** SALES MODE temporarily (then resumes)

**Activities:**
1. Check bigmeatyclawd@gmail.com inbox
2. Triage new emails by priority
3. Draft responses for each
4. Escalate urgent issues

**Output:** Support Check Report

**Files Updated:**
- `memory/support-tickets.json` (ticket status)
- `memory/support-history-[DATE].md` (daily log)

**Resumes:** SALES MODE

---

### 12:00pm - ACCOUNTABILITY MODE: Commitment Check-in
**Duration:** 5 minutes
**Action:** Check progress on today's commitment

**Output:**
```
🕐 MIDDAY CHECK-IN

Status? A/B/C/D?
Adjust if needed
```

**Files Updated:**
- `memory/accountability-commitments.json` (status update)

---

## 🌞 AFTERNOON (12:00pm - 6:00pm)

### 12:00pm - SALES MODE COMPLETE
**Action:** Send Sales Mode Report to Ross
**Next:** Transition to afternoon priorities

---

### 2:00pm - SUPPORT MODE CHECK #2
**Duration:** 15-30 minutes
**Action:** Afternoon inbox check

**Same as 10am check:**
- Check inbox
- Triage issues
- Draft responses
- Escalate urgent

**Output:** Support Check Report

**Files Updated:**
- `memory/support-tickets.json`
- `memory/support-history-[DATE].md`

---

### 2:00pm - 6:00pm - DEV MODE (If Bugs) OR SALES MODE (If No Bugs)

**Decision Tree:**
```
Are there P0/P1 bugs in the queue?
├─ YES → DEV MODE (fix bugs, deploy)
└─ NO → Continue SALES MODE (more leads, outreach follow-ups)
```

**DEV MODE Activities:**
1. Review bug queue
2. Prioritize by severity
3. Fix P0/P1 bugs
4. Test thoroughly
5. Deploy to production
6. Monitor for issues

**SALES MODE Activities:**
1. Find more leads (target: 10/day total)
2. Follow up warm leads
3. Refine messaging
4. Update CRM

**Parallel:** ACCOUNTABILITY MODE monitoring

---

## 🌆 EVENING (6:00pm - 10:00pm)

### 6:00pm - SUPPORT MODE CHECK #3
**Duration:** 15-30 minutes
**Action:** Evening inbox check before research mode

**Output:** Support Check Report

---

### 6:00pm - RESEARCH MODE ACTIVATE
**Duration:** 2 hours (6pm-8pm)
**Action:** Competitor analysis, market intelligence, opportunities

**Activities:**
1. Competitor monitoring (30 min)
2. Market trends research (30 min)
3. Opportunity identification (30 min)
4. Content idea generation (30 min)

**Output:** Research Mode Report at 8pm

**Files Updated:**
- `memory/research-competitors.json` (snapshots)
- `memory/research-trends.json` (trends)
- `memory/research-opportunities.json` (pipeline)

**Parallel:** ACCOUNTABILITY MODE monitoring

---

### 8:00pm - RESEARCH MODE COMPLETE
**Action:** Send Research Mode Report to Ross

---

### 9:00pm - ACCOUNTABILITY MODE: Daily Scorecard
**Duration:** 10 minutes
**Action:** Comprehensive daily wrap-up

**Activities:**
1. Compile all mode data from today
2. Analyze time allocation
3. Check commitment status
4. Detect patterns
5. Calculate streak
6. Generate scorecard
7. Recommend tomorrow's commitment

**Output:** Full Accountability Scorecard

**Files Updated:**
- `memory/accountability-daily-[DATE].md` (complete)
- `memory/accountability-streak.json` (updated)
- `memory/accountability-time.json` (logged)

---

### 10:00pm - SUPPORT MODE CHECK #4 (Final)
**Duration:** 10 minutes
**Action:** Emergency check before sleep

**Scope:** 
- Only check for P0 emergencies
- Don't draft responses (handle in morning)
- Alert Ross if site down

**Output:** Brief status (or HEARTBEAT_OK if no issues)

---

## 🌙 NIGHT (10:00pm - 7:30am)

### 10:00pm - 7:30am - DEV MODE (Background Work)
**Only if:** Work queued and Ross approved

**Activities:**
- Fix P2/P3 bugs (non-urgent)
- Build requested features
- Optimize performance
- Refactor code
- Run maintenance tasks

**Boundaries:**
- ❌ Don't deploy major changes without approval
- ✅ Can deploy minor bug fixes (with logging)
- ✅ Prepare work for Ross to review in morning

---

## 📅 WEEKEND SCHEDULE (Saturday-Sunday)

### Saturday
**Minimal Mode:**
- 10:00am: SUPPORT MODE CHECK (emergencies only)
- 6:00pm: SUPPORT MODE CHECK (emergencies only)
- 9:00pm: ACCOUNTABILITY MODE (brief daily note, no scorecard)

**No Sales/Research:** Weekend off

---

### Sunday
**Planning Mode:**
- 10:00am: SUPPORT MODE CHECK
- 6:00pm: SUPPORT MODE CHECK
- 9:00pm: ACCOUNTABILITY MODE (weekly report + Monday prep)

**Output:** Weekly Accountability Report + Monday morning brief prep

---

## 📊 MODE ALLOCATION (Typical Week)

**SALES MODE:**
- Time: 20 hours/week (4 hours/day × 5 days)
- Focus: Lead generation, outreach, competitor intel

**SUPPORT MODE:**
- Time: 5-10 hours/week (4 checks/day × 20 min avg)
- Focus: Customer happiness, bug triage

**RESEARCH MODE:**
- Time: 10 hours/week (2 hours/day × 5 days)
- Focus: Strategic intelligence, opportunities

**DEV MODE:**
- Time: 5-15 hours/week (variable, bug-dependent)
- Focus: Fixing bugs, maintaining stability

**ACCOUNTABILITY MODE:**
- Time: Always on (2-3 hours/week of active reporting)
- Focus: Tracking commitments, pattern analysis

**TOTAL:** ~40-50 hours/week of active work

---

## ⚡ OVERRIDE SCENARIOS

### P0 Bug Detected
```
IMMEDIATELY:
1. Alert Ross
2. Switch all modes to DEV MODE
3. Fix bug ASAP
4. Resume normal schedule when resolved
```

### Major Competitor Move
```
WITHIN 1 HOUR:
1. Alert Ross
2. Deep dive in RESEARCH MODE
3. Draft response strategy
4. Resume normal schedule
```

### Customer Emergency
```
IMMEDIATELY:
1. Switch to SUPPORT MODE
2. Handle customer issue
3. Escalate to Ross if needed
4. Resume normal schedule
```

### Ross Manual Override
```
"Jarvis, [mode name]" → Switch immediately
Stay in that mode until:
- Task complete
- Ross says switch back
- Scheduled mode kicks in
```

---

## 🔄 SCHEDULE FLEXIBILITY

**Rules:**
1. ACCOUNTABILITY MODE is sacred (7:30am, 12pm, 9pm never skip)
2. SUPPORT MODE checks can flex by ±30 min (but must happen 4x/day)
3. SALES/RESEARCH can swap (if Ross prioritizes research over sales)
4. DEV MODE interrupts anything (P0/P1 bugs take precedence)
5. Weekend schedule is minimal (rest is important)

**Ross can adjust:**
- "Skip sales mode today" → Noted, more dev time
- "Research mode at 2pm instead" → Adjusted
- "No accountability scorecard tonight" → Okay (but breaks streak)

---

## 📈 OPTIMIZATION OVER TIME

**Weekly Review Questions:**
1. Is this schedule working? (Hitting commitments? Shipping product?)
2. Should we adjust mode allocation? (More sales? Less research?)
3. Are mode transitions smooth? (Or disruptive?)
4. Is Ross getting value from each mode? (Or just noise?)

**Adjust based on:**
- Commitment hit rate
- Product velocity
- Lead generation success
- Ross's feedback

**Goal:** Find the rhythm that maximizes execution while staying sustainable.

---

## 🚀 TOMORROW MORNING SEQUENCE

**Here's exactly what happens at 7:30am:**

1. **Load context** (yesterday's recap, current priorities)
2. **Generate morning brief** (commitment recommendation)
3. **Send to Ross** (get YES confirmation)
4. **Log commitment** (deadline, success criteria)
5. **Activate SALES MODE at 8am** (background ACCOUNTABILITY monitoring)
6. **Execute schedule** (as defined above)

The system goes live at 7:30am tomorrow. Ready. 🚀
