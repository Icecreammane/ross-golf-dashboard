# MODE TRIGGERS

## How Modes Activate

Each mode can be triggered in three ways:
1. **Scheduled** (time-based, automatic)
2. **Event-driven** (bugs, emails, alerts)
3. **Manual** (Ross explicitly requests)

---

## 📊 SALES MODE

### Scheduled Triggers
```
DAILY (Monday-Friday):
- 8:00am CST → Activate SALES MODE
- Duration: 4 hours (8am-12pm)
- Auto-deactivate: 12pm (send report)
```

### Manual Triggers
**Ross says any of these:**
- "Jarvis, sales mode"
- "Jarvis, find customers"
- "Find me leads"
- "Research competitors"
- "Draft outreach messages"

**Action:** Activate SALES MODE immediately, regardless of schedule

### Event-Driven Triggers
**Condition:** Revenue stagnates
```
IF:
- Zero new signups in 7 days
- Zero warm leads in pipeline
- MRR declining
THEN:
- Alert Ross
- Suggest intensive SALES MODE session
```

**Condition:** Competitor makes major move
```
IF:
- Competitor launches competing feature
- Competitor changes pricing significantly
- Competitor gets press coverage
THEN:
- Brief SALES MODE activation
- Research competitor impact
- Recommend response strategy
```

### Deactivation Triggers
- 12:00pm (scheduled end)
- Ross says "exit sales mode"
- P0 bug detected (switch to DEV MODE)
- Customer emergency (switch to SUPPORT MODE)

---

## 🛡️ SUPPORT MODE

### Scheduled Triggers
```
DAILY:
- 10:00am CST → Support Check #1
- 2:00pm CST → Support Check #2
- 6:00pm CST → Support Check #3
- 10:00pm CST → Support Check #4 (emergency only)

WEEKEND:
- 10:00am CST → Emergency check
- 6:00pm CST → Emergency check
```

### Manual Triggers
**Ross says any of these:**
- "Jarvis, check support"
- "Jarvis, support mode"
- "Check the inbox"
- "Any customer issues?"
- "What's the support status?"

**Action:** Run support check immediately

### Event-Driven Triggers
**Condition:** Email received at bigmeatyclawd@gmail.com
```
IF:
- New email from known customer
- Subject contains: "bug", "broken", "help", "urgent"
THEN:
- Alert Ross
- Run immediate support check
- Triage priority
```

**Condition:** Bug report from customer
```
IF:
- Customer reports P0/P1 bug
THEN:
- Immediate support check
- Draft response
- Switch to DEV MODE if needed
- Escalate to Ross
```

**Condition:** Multiple users report same issue
```
IF:
- 2+ users report same issue within 24 hours
THEN:
- Elevate priority to P1
- Alert Ross
- Generate incident report
```

### Deactivation Triggers
- Check complete (report sent)
- Ross says "exit support mode"
- No urgent issues (return to previous mode)

---

## 🔍 RESEARCH MODE

### Scheduled Triggers
```
DAILY (Monday-Friday):
- 6:00pm CST → Activate RESEARCH MODE
- Duration: 2 hours (6pm-8pm)
- Auto-deactivate: 8pm (send report)
```

### Manual Triggers
**Ross says any of these:**
- "Jarvis, research mode"
- "Research [topic]"
- "Analyze [competitor]"
- "What's trending in [market]?"
- "Find opportunities"

**Action:** Activate RESEARCH MODE immediately

**Topic-specific triggers:**
```
"Research MyFitnessPal" → Deep dive on MFP
"What's trending on Reddit?" → Trending topics scan
"Find gym partnership opportunities" → Opportunity research
"Competitor analysis" → Full competitor sweep
```

### Event-Driven Triggers
**Condition:** Major competitor move detected
```
IF:
- Competitor raises funding
- Competitor launches new product
- Competitor changes pricing >20%
- Competitor gets acquired
THEN:
- Alert Ross
- Activate RESEARCH MODE
- Deep dive on implications
```

**Condition:** Market shift detected
```
IF:
- Trending topic mentions "macro tracking"
- Viral post about fitness apps
- Regulatory change affecting SaaS
THEN:
- Brief RESEARCH MODE session
- Analyze implications
- Report to Ross
```

### Deactivation Triggers
- 8:00pm (scheduled end)
- Ross says "exit research mode"
- Research complete (report sent)

---

## 🔧 DEV MODE

### Scheduled Triggers
```
DAILY:
- 2:00pm-6:00pm → DEV MODE (if bugs in queue)
- 10:00pm-7:00am → DEV MODE (background work, if approved)
```

### Manual Triggers
**Ross says any of these:**
- "Jarvis, dev mode"
- "Fix [bug]"
- "Deploy [feature]"
- "Investigate [issue]"
- "What's broken?"

**Action:** Activate DEV MODE immediately

### Event-Driven Triggers (HIGHEST PRIORITY)

**P0 Bug (Emergency):**
```
IF:
- Site completely down
- Payment system broken
- Data loss detected
- Security breach
THEN:
- IMMEDIATELY switch ALL modes to DEV MODE
- Alert Ross (urgent)
- Fix ASAP
- Don't wait for permission
```

**P1 Bug (Urgent):**
```
IF:
- Login broken
- Core feature not working
- Dashboard won't load
- Stripe webhook failing
THEN:
- Switch to DEV MODE within 1 hour
- Alert Ross
- Fix within 4 hours
- Deploy after testing
```

**P2 Bug (Important):**
```
IF:
- UI bug reported
- Performance degraded
- Mobile issue
- 2+ users report same problem
THEN:
- Add to DEV MODE queue
- Fix within 7 days
- Bundle with other fixes
```

**P3 Bug (Nice to have):**
```
IF:
- Cosmetic issue
- Edge case bug
- Low-impact problem
THEN:
- Log to backlog
- Fix when time allows
```

**Performance Alert:**
```
IF:
- Page load time >5 seconds
- API response time >2 seconds
- Error rate >1%
THEN:
- Activate DEV MODE
- Investigate immediately
- Optimize and deploy
```

**Security Alert:**
```
IF:
- npm audit shows critical vulnerability
- Security researcher reports issue
- Suspicious activity detected
THEN:
- IMMEDIATE DEV MODE
- Alert Ross
- Fix before resuming other work
```

### Deactivation Triggers
- Bug fixed and deployed
- Ross says "exit dev mode"
- Scheduled dev window ends
- Can't fix bug in 2 hours (escalate to Ross, pause)

---

## 📊 ACCOUNTABILITY MODE

### Scheduled Triggers
```
ALWAYS ON (runs in parallel)

Active checkpoints:
- 7:30am → Morning brief + commitment
- 12:00pm → Midday check-in
- 9:00pm → Daily scorecard

Sunday:
- 9:00pm → Weekly report
```

### Manual Triggers
**Ross says any of these:**
- "What's my streak?"
- "Accountability check"
- "Am I procrastinating?"
- "Show me my scorecard"
- "What's my pattern?"

**Action:** Generate accountability report immediately

### Event-Driven Triggers

**Silent for >2 hours (during work hours):**
```
IF:
- No activity from Ross 9am-6pm
- >2 hours since last message
- Today's commitment not completed
THEN:
- Send gentle nudge
- "Working on [commitment] or stuck?"
```

**Deadline approaching:**
```
IF:
- Commitment deadline in 30 minutes
- Status unknown
THEN:
- Send reminder
- "[Time] deadline in 30 min. Status?"
```

**Working on wrong task:**
```
IF:
- Ross is working on Task X
- Today's commitment is Task Y
- Tasks are different
THEN:
- Send clarifying question
- "Working on [X], but committed to [Y]. Change of plans?"
```

**Commitment broken 3 days in row:**
```
IF:
- 3 consecutive missed commitments
THEN:
- Trigger serious conversation
- "We need to talk about what's blocking you"
```

**Procrastination detected:**
```
IF:
- Social media activity during work hours
- >30 minutes on non-work apps
THEN:
- Note in daily log (don't interrupt immediately)
- Include in 9pm scorecard
```

### Deactivation Triggers
**Never deactivates.** ACCOUNTABILITY MODE runs 24/7.

---

## 🔄 MODE PRIORITY (When Multiple Triggers Fire)

**Priority Order:**
```
1. P0 Bug (DEV MODE) → Drop everything
2. Customer Emergency (SUPPORT MODE) → Immediate
3. Manual Request (Any mode) → Ross overrides schedule
4. P1 Bug (DEV MODE) → Within 1 hour
5. Scheduled Trigger (Any mode) → Default schedule
6. Event-Driven (Any mode) → Opportunistic
```

**Example Scenario:**
```
Situation: 8:00am, SALES MODE scheduled to start
Trigger: P0 bug detected (site down)

Resolution:
1. Cancel SALES MODE activation
2. Switch to DEV MODE immediately
3. Alert Ross
4. Fix bug ASAP
5. Resume SALES MODE after fix deployed
```

**Example Scenario:**
```
Situation: 6:00pm, RESEARCH MODE active
Trigger: Ross says "Jarvis, check support"

Resolution:
1. Pause RESEARCH MODE (save state)
2. Switch to SUPPORT MODE
3. Run support check
4. Send report
5. Resume RESEARCH MODE
```

---

## 🧪 TESTING TRIGGERS

**For Ross to test the system:**

**Test SALES MODE:**
- Say "Jarvis, sales mode" (should activate immediately)
- Wait for 8am tomorrow (should auto-activate)

**Test SUPPORT MODE:**
- Say "Jarvis, check support" (should run check)
- Send test email to bigmeatyclawd@gmail.com (should detect)

**Test RESEARCH MODE:**
- Say "Research MyFitnessPal" (should deep dive)
- Wait for 6pm today (should auto-activate)

**Test DEV MODE:**
- Say "Fix [bug name]" (should investigate)
- Report P1 bug (should switch modes)

**Test ACCOUNTABILITY MODE:**
- Say "What's my streak?" (should report)
- Wait for 9pm (should send scorecard)

---

## 📝 TRIGGER LOGGING

**All triggers are logged to:**
`memory/mode-triggers-[DATE].json`

**Format:**
```json
{
  "timestamp": "2024-01-30T08:00:00Z",
  "mode": "SALES_MODE",
  "trigger_type": "scheduled",
  "trigger_source": "daily_schedule",
  "previous_mode": "ACCOUNTABILITY_MODE",
  "action_taken": "activated_sales_mode"
}
```

**Why log triggers:**
- Debug mode switching issues
- Analyze mode effectiveness
- Optimize scheduling
- Report to Ross

---

## 🚀 FIRST TRIGGER: Tomorrow 7:30am

**What happens:**
```
7:30am CST:
- ACCOUNTABILITY MODE triggers (scheduled)
- Generate morning brief
- Send to Ross
- Wait for commitment confirmation
- Log to memory/accountability-commitments.json

8:00am CST:
- SALES MODE triggers (scheduled)
- Load sales context
- Begin lead scanning
- ACCOUNTABILITY monitors in parallel

[Schedule continues as defined in MODE_SCHEDULER.md]
```

System is ready. Triggers configured. Let's go. 🚀
