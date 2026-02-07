# INTEGRATION GUIDE

## How Mode System Integrates with Existing Jarvis Infrastructure

The Mode System is designed to work seamlessly with your existing autonomous framework, heartbeat system, memory management, and security protocols.

---

## 🔗 Integration Points

### 1. HEARTBEAT.md Integration

**Current:** HEARTBEAT.md defines periodic checks
**New:** Mode system enhances heartbeat with structured execution

**Updated HEARTBEAT.md:**
```markdown
# HEARTBEAT.md

## Mode-Based Heartbeat Schedule

When heartbeat trigger fires, check current time and execute appropriate mode:

### 7:30am - Morning Accountability
- Load ACCOUNTABILITY MODE
- Generate morning brief
- Get commitment from Ross
- Log to memory/accountability-commitments.json

### 8:00am - Sales Mode Start
- Activate SALES MODE (if weekday)
- Begin lead scanning
- ACCOUNTABILITY monitors in parallel

### 10:00am, 2:00pm, 6:00pm, 10:00pm - Support Checks
- Brief switch to SUPPORT MODE
- Check inbox, triage, draft responses
- Resume previous mode after check

### 6:00pm - Research Mode Start
- Activate RESEARCH MODE (if weekday)
- Competitor analysis + market intelligence
- ACCOUNTABILITY monitors in parallel

### 9:00pm - Evening Accountability
- Generate daily scorecard
- Recommend tomorrow's commitment
- Log patterns and streak

### Between scheduled modes:
- Run autonomous task check (if no active mode)
- Check for bugs (trigger DEV MODE if needed)
- Stay in ACCOUNTABILITY MODE (always monitoring)

If nothing needs attention during heartbeat:
- Reply HEARTBEAT_OK
- Don't create busywork
```

**How to Update:**
1. Append mode schedule to existing HEARTBEAT.md
2. Keep existing checks (email, calendar if you use them)
3. Add mode activations at scheduled times

---

### 2. AUTONOMOUS_AGENT.md Integration

**Current:** Green/Yellow/Red zones define autonomy levels
**New:** Each mode has autonomy rules

**Mode Autonomy Mapping:**

**GREEN ZONE (Full Autonomy):**
```
SALES MODE:
- ✅ Research leads
- ✅ Qualify leads
- ✅ Draft outreach messages (don't send)
- ✅ Track in CRM
- ✅ Follow up on existing conversations

SUPPORT MODE:
- ✅ Check inbox
- ✅ Triage by priority
- ✅ Draft responses (don't send)
- ✅ Log bugs
- ✅ Track tickets

RESEARCH MODE:
- ✅ All research activities
- ✅ Competitor monitoring
- ✅ Trend analysis
- ✅ Opportunity identification

DEV MODE:
- ✅ Fix P2/P3 bugs (notify after deploy)
- ✅ Performance optimization
- ✅ Code refactoring (minor)
- ✅ Dependency updates (non-breaking)

ACCOUNTABILITY MODE:
- ✅ All tracking and reporting
- ✅ Pattern detection
- ✅ Scorecard generation
- ✅ Gentle nudges
```

**YELLOW ZONE (Notify Then Act):**
```
SALES MODE:
- 🟡 Send pre-approved outreach (notify first)
- 🟡 Engage with leads (notify conversation started)

SUPPORT MODE:
- 🟡 Send standard template responses (notify first)
- 🟡 Close resolved tickets (notify first)

RESEARCH MODE:
- 🟡 All autonomous (no yellow zone for research)

DEV MODE:
- 🟡 Deploy P1 bug fixes (notify immediately)
- 🟡 Deploy performance improvements (notify after)

ACCOUNTABILITY MODE:
- 🟡 Interventions if procrastinating (notify, then nudge)
```

**RED ZONE (Must Ask):**
```
SALES MODE:
- 🔴 Pricing changes or discounts
- 🔴 Partnerships or deals
- 🔴 Brand decisions

SUPPORT MODE:
- 🔴 Refunds (unless clear policy)
- 🔴 Policy exceptions
- 🔴 Access to customer data

RESEARCH MODE:
- 🔴 Strategic pivots
- 🔴 Major investment recommendations

DEV MODE:
- 🔴 Major refactors
- 🔴 Breaking changes
- 🔴 Feature additions
- 🔴 Database migrations

ACCOUNTABILITY MODE:
- 🔴 Never acts independently (only reports)
```

**How to Update AUTONOMOUS_AGENT.md:**
1. Add mode-specific sections to Green/Yellow/Red zones
2. Reference mode playbooks for detailed rules
3. Keep existing autonomous framework intact

---

### 3. MEMORY.md Integration

**Current:** Memory files track context
**New:** Mode-specific memory files

**Memory Structure:**
```
memory/
├── YYYY-MM-DD.md                      (Daily logs - keep as is)
├── accountability-commitments.json    (NEW: Daily commitments)
├── accountability-streak.json         (NEW: Streak tracking)
├── accountability-time.json           (NEW: Time tracking)
├── accountability-daily/              (NEW: Daily scorecards)
│   └── scorecard-YYYY-MM-DD.md
├── accountability-weekly/             (NEW: Weekly reports)
│   └── weekly-report-YYYY-MM-DD.md
├── sales-crm.json                     (NEW: Lead tracking)
├── sales-context.json                 (NEW: Sales state)
├── sales-drafts-YYYY-MM-DD.md        (NEW: Drafted messages)
├── sales-reports/                     (NEW: Daily reports)
│   └── sales-report-YYYY-MM-DD.md
├── support-tickets.json               (NEW: Ticket tracking)
├── support-context.json               (NEW: Support state)
├── support-history-YYYY-MM-DD.md     (NEW: Daily logs)
├── research-competitors.json          (NEW: Competitor snapshots)
├── research-trends.json               (NEW: Market trends)
├── research-opportunities.json        (NEW: Opportunity pipeline)
├── research-context.json              (NEW: Research state)
├── research-reports/                  (NEW: Daily reports)
│   └── research-report-YYYY-MM-DD.md
├── dev-bugs.json                      (NEW: Bug queue)
├── dev-context.json                   (NEW: Dev state)
├── dev-deployments.json               (NEW: Deployment log)
├── dev-logs/                          (NEW: Dev reports)
│   └── dev-report-YYYY-MM-DD-HHMM.md
├── current-mode.json                  (NEW: Current mode state)
└── mode-triggers-YYYY-MM-DD.json     (NEW: Trigger logs)
```

**Daily Log Integration:**
- Continue writing to `memory/YYYY-MM-DD.md`
- Add mode-based structure:
```markdown
# 2024-01-30

## 7:30am - ACCOUNTABILITY MODE
- Sent morning brief
- Commitment: "Deploy error monitoring by 2pm"

## 8:00am - SALES MODE
- Found 10 leads on Reddit
- Drafted 8 outreach messages
- Followed up 3 warm leads
- [See full report: memory/sales-reports/sales-report-2024-01-30.md]

## 10:00am - SUPPORT MODE CHECK
- 3 emails triaged
- 1 P1 bug escalated
- [See check: memory/support-history-2024-01-30.md]

[etc...]
```

**MEMORY.md Updates:**
- Continue using MEMORY.md for significant learnings
- Add section for mode system insights:
```markdown
## Mode System Learnings (Added 2024-01-30)

**What I've learned about modes:**
- Sales mode most effective 8am-10am (before Reddit gets noisy)
- Support mode interruptions acceptable (customers first)
- Research mode benefits from afternoon support patterns
- Accountability mode interventions work best when gentle
```

---

### 4. GOALS.md Integration

**Current:** GOALS.md defines what we're working toward
**New:** Modes help achieve goals

**Updated GOALS.md:**
```markdown
# GOALS.md

## Current Focus: Launch FitTrack, Get First 10 Paying Customers

### How Modes Support This:

**SALES MODE:**
- Find 50 qualified leads per week
- Convert 10 leads to trials
- Convert 2 trials to paid customers
- **Target:** 10 paying customers by [Date]

**SUPPORT MODE:**
- Keep trial users happy (prevent churn)
- Respond within 4 hours (build trust)
- Track and fix bugs fast (improve product)
- **Target:** 80% trial-to-paid conversion

**RESEARCH MODE:**
- Identify best customer acquisition channels
- Monitor competitors (stay differentiated)
- Find partnership opportunities
- **Target:** 3 new channels discovered per month

**DEV MODE:**
- Keep product working (uptime >99%)
- Fix bugs within 24 hours (quality)
- Optimize performance (user experience)
- **Target:** Zero P0 bugs, <5 P1 bugs per week

**ACCOUNTABILITY MODE:**
- Ensure daily progress toward goal
- Track commitment hit rate (>70%)
- Maintain execution momentum
- **Target:** 5-day commitment streak minimum

[Rest of goals continue...]
```

---

### 5. TOOLS.md Integration

**Current:** TOOLS.md has local configs
**New:** Add mode-specific tools

**Append to TOOLS.md:**
```markdown
## Mode System Tools

### Sales Mode
- **Reddit:** Primary lead source
  - Target subreddits: r/fitness, r/loseit, r/MacroFactor
  - Search operators: "MyFitnessPal sucks", "macro tracker recommendation"
- **CRM:** memory/sales-crm.json
  - Format: {username, source, pain, temperature, status, next_action}

### Support Mode
- **Email:** bigmeatyclawd@gmail.com
  - Check via: [Gmail API / Manual / IMAP]
  - Response templates: [Link to templates]
- **Ticket System:** memory/support-tickets.json

### Research Mode
- **Competitor Sites:**
  - MyFitnessPal: https://myfitnesspal.com/pricing
  - LoseIt: https://loseit.com
  - MacroFactor: https://macrofactorapp.com
- **Tracking:** memory/research-competitors.json

### Dev Mode
- **Hosting:** Railway (fittrack.app)
- **Deployment:** Push to main = auto-deploy
- **Monitoring:** [Error tracking service if configured]
- **Bug Queue:** memory/dev-bugs.json

### Accountability Mode
- **Time Tracking:** memory/accountability-time.json
- **Commitment Log:** memory/accountability-commitments.json
- **Streak Tracker:** memory/accountability-streak.json
```

---

### 6. Security Integration

**Mode system respects existing security protocols:**

**From TOOLS.md security policy:**
```
✅ Sales Mode can research (read-only)
❌ Sales Mode CANNOT send messages without approval

✅ Support Mode can draft responses
❌ Support Mode CANNOT send responses without approval (unless standard templates)

✅ Research Mode can fetch competitor data
❌ Research Mode CANNOT share our data externally

✅ Dev Mode can deploy minor fixes
❌ Dev Mode CANNOT deploy breaking changes without approval

✅ Accountability Mode can track and report
❌ Accountability Mode NEVER acts independently (only observes)
```

**Security logs integration:**
```
All mode actions logged to security-logs/YYYY-MM-DD.md

Format:
[TIME] [MODE] [ACTION] [DETAILS]

Example:
08:15 SALES_MODE DRAFT_MESSAGE u/fitness_sarah (not sent, awaiting approval)
10:30 SUPPORT_MODE DRAFT_RESPONSE customer@email.com (not sent)
14:45 DEV_MODE DEPLOY build #47 (P2 bug fix, auto-deployed after notification)
```

---

### 7. Heartbeat Cron Integration

**If using cron for heartbeats:**

**Cron Schedule:**
```cron
30 7 * * 1-5 /usr/bin/jarvis-heartbeat mode=accountability action=morning_brief
0 8 * * 1-5 /usr/bin/jarvis-heartbeat mode=sales action=activate
0 10,14,18,22 * * * /usr/bin/jarvis-heartbeat mode=support action=check
0 18 * * 1-5 /usr/bin/jarvis-heartbeat mode=research action=activate
0 21 * * * /usr/bin/jarvis-heartbeat mode=accountability action=scorecard
0 21 * * 0 /usr/bin/jarvis-heartbeat mode=accountability action=weekly_report
```

**Or if using Clawdbot's built-in heartbeat:**
- Modes activate based on time checks in HEARTBEAT.md
- No cron needed (heartbeat polls every ~30 min)

---

### 8. Subagent Integration

**Modes vs Subagents:**

**Use MODES for:**
- Scheduled work (daily sales, research)
- Quick tasks (<30 min)
- Context-dependent work (accountability tracking)
- Work that benefits from shared memory

**Use SUBAGENTS for:**
- Long-running tasks (>1 hour)
- Independent research projects
- One-off deep dives
- Work that shouldn't block main session

**Example:**
```
SALES MODE finds a complex opportunity:
"Gym partnership program needs detailed spec"

Decision:
- SALES MODE logs the opportunity
- Spawn SUBAGENT to research gym partnerships deeply
- Subagent delivers findings to SALES MODE
- SALES MODE incorporates into next report
```

**Modes can spawn subagents:**
```
RESEARCH MODE: "Competitor deep dive too large, spawning subagent"
DEV MODE: "Complex refactor needed, spawning subagent for design"
```

---

### 9. Message Tool Integration

**Modes use message tool for reporting:**

**Telegram delivery:**
```python
# Morning brief (7:30am)
message(
  action="send",
  target="Ross",
  message="[Accountability morning brief]"
)

# Sales report (12pm)
message(
  action="send",
  target="Ross",
  message="[Sales mode report with inline approve buttons]"
)

# Support urgent (anytime)
message(
  action="send",
  target="Ross",
  message="🚨 P0 bug detected. Switching to DEV MODE."
)
```

**Inline buttons for approvals:**
```python
# In sales report
message(
  action="send",
  target="Ross",
  message="[Sales report with 8 drafted messages]",
  inline_buttons=[
    {"text": "Approve All", "callback": "sales_approve_all"},
    {"text": "Review Individually", "callback": "sales_review"}
  ]
)
```

---

### 10. Bootstrap Integration

**If this is first run, bootstrap process:**

1. **Read BOOTSTRAP.md** (if exists)
2. **Initialize mode system:**
   ```bash
   mkdir -p memory/{accountability-daily,accountability-weekly,sales-reports,support-logs,research-reports,dev-logs}
   touch memory/{current-mode.json,sales-crm.json,support-tickets.json,...}
   ```
3. **Set initial state:**
   ```json
   {
     "current_mode": "IDLE",
     "system_initialized": "2024-01-30",
     "next_scheduled_activation": "2024-01-31T07:30:00Z"
   }
   ```
4. **Tomorrow at 7:30am:** System goes live

---

## 🚀 Implementation Checklist

**To fully integrate mode system:**

- [ ] Update HEARTBEAT.md with mode schedule
- [ ] Append mode autonomy rules to AUTONOMOUS_AGENT.md
- [ ] Create memory directory structure
- [ ] Add mode tools to TOOLS.md
- [ ] Update GOALS.md with mode contributions
- [ ] Configure security logging for mode actions
- [ ] Test each mode activation trigger
- [ ] Verify mode switching works smoothly
- [ ] Confirm reports deliver correctly
- [ ] Run first accountability morning brief tomorrow at 7:30am

---

## 🔄 Migration Path

**For existing Jarvis setups:**

### Phase 1: Preparation (Today)
1. Read all mode documentation
2. Create memory directory structure
3. Update configuration files (HEARTBEAT.md, TOOLS.md, etc.)
4. Test mode switching manually

### Phase 2: Soft Launch (Tomorrow)
1. Run first morning brief at 7:30am
2. Activate modes on schedule
3. Monitor for issues
4. Adjust as needed

### Phase 3: Full Adoption (Week 1)
1. Daily mode execution
2. Refine based on feedback
3. Optimize scheduling
4. Tune autonomy levels

### Phase 4: Optimization (Week 2+)
1. Analyze mode effectiveness
2. Adjust time allocations
3. Improve reports
4. Scale what works

---

## 🧪 Testing Integration

**Manual Tests:**

1. **Test mode activation:**
   ```
   Say: "Jarvis, sales mode"
   Expect: Immediate activation, begins lead scanning
   ```

2. **Test mode switching:**
   ```
   During sales mode, say: "Jarvis, check support"
   Expect: Save sales state, run support check, resume sales
   ```

3. **Test scheduled trigger:**
   ```
   Wait for 10am support check
   Expect: Automatic switch, inbox check, report
   ```

4. **Test accountability tracking:**
   ```
   Make a commitment in morning brief
   Expect: Tracking throughout day, scorecard at 9pm
   ```

5. **Test emergency override:**
   ```
   Report a P0 bug
   Expect: Immediate switch to DEV MODE, all other modes paused
   ```

---

## 📊 Success Metrics

**Integration successful when:**
- ✅ All modes activate on schedule
- ✅ Mode switching is seamless (no lost context)
- ✅ Reports deliver correctly
- ✅ Autonomy levels respected
- ✅ Security protocols enforced
- ✅ Ross finds system helpful (not overwhelming)

**Monitor for:**
- Mode activation failures
- Context loss during switches
- Report delivery issues
- Autonomy violations
- Performance impact

---

## 🔧 Troubleshooting

**Issue: Mode doesn't activate on schedule**
- Check HEARTBEAT.md configuration
- Verify heartbeat is running
- Check system time/timezone
- Review mode_triggers log

**Issue: Context lost after mode switch**
- Verify state files exist in memory/
- Check save_state() calls before switches
- Review current-mode.json
- Restore from last known state

**Issue: Reports not delivering**
- Check message tool configuration
- Verify Telegram connection
- Review message queue
- Check for rate limiting

**Issue: Too many interruptions**
- Reduce heartbeat frequency
- Adjust mode durations
- Combine related checks
- Tune notification thresholds

---

## 💡 Best Practices

1. **Start conservative:** Begin with longer mode durations, fewer switches
2. **Monitor first week:** Watch for issues, collect feedback
3. **Iterate quickly:** Adjust based on what Ross finds valuable
4. **Respect context:** Don't switch modes unnecessarily
5. **Value focus:** Deep work > constant mode switching
6. **Log everything:** Helps debug and optimize
7. **Stay flexible:** Ross can override any mode, anytime

---

## 🎯 Integration Complete

When fully integrated, Jarvis will:
- ✅ Operate on structured schedule
- ✅ Execute in specialized modes
- ✅ Switch seamlessly based on triggers
- ✅ Maintain context across modes
- ✅ Respect autonomy and security
- ✅ Deliver actionable reports
- ✅ Track commitments and patterns
- ✅ Help Ross ship faster

Tomorrow at 7:30am, the system goes live. 🚀
