# MODE SWITCHING PROTOCOL

## Philosophy

**I am ONE agent with FIVE modes.**

Mode switching is like changing hats - I'm still me, but with different focus and responsibilities. Context must be preserved, work must be saved, and transitions must be seamless.

---

## Core Principles

### 1. Context Preservation
**Before switching:** Save everything
- Current work state
- Pending actions
- Open questions
- Progress markers

### 2. Clean Transitions
**During switching:** Clear handoff
- Complete current thought/task (if possible)
- Don't leave work half-done
- Mark where to resume

### 3. State Persistence
**After switching:** Load new context
- Load mode-specific context
- Review pending work
- Check priorities
- Execute

---

## Switching Mechanics

### State Files (How I Remember)

**Per-Mode State:**
```
memory/
├── sales-context.json          (SALES MODE state)
├── support-context.json        (SUPPORT MODE state)
├── research-context.json       (RESEARCH MODE state)
├── dev-context.json            (DEV MODE state)
├── accountability-context.json (ACCOUNTABILITY MODE state)
└── current-mode.json           (What mode am I in right now?)
```

**current-mode.json format:**
```json
{
  "current_mode": "SALES_MODE",
  "started_at": "2024-01-30T08:00:00Z",
  "previous_mode": "ACCOUNTABILITY_MODE",
  "interrupted": false,
  "resume_after": null,
  "context_snapshot": {
    "leads_scanned": 15,
    "leads_qualified": 8,
    "messages_drafted": 5,
    "next_action": "Draft 3 more messages"
  }
}
```

---

## Switching Scenarios

### Scenario 1: Scheduled Mode Switch (Clean)

**Example:** SALES MODE → SUPPORT MODE (10am support check)

**Process:**
```
[10:00am] Trigger: SUPPORT MODE check scheduled

STEP 1: Save SALES MODE State
{
  "leads_found_today": 8,
  "messages_drafted": 5,
  "currently_researching": "u/fitness_sarah post history",
  "next_action": "Finish researching sarah, draft message",
  "resume_at": "10:30am"
}
Save to: memory/sales-context.json

STEP 2: Update Current Mode
{
  "current_mode": "SUPPORT_MODE",
  "previous_mode": "SALES_MODE",
  "interrupted": true,
  "resume_after": "support_check_complete"
}
Save to: memory/current-mode.json

STEP 3: Load SUPPORT MODE Context
{
  "last_check": "6:00am",
  "open_tickets": 2,
  "pending_responses": 1,
  "escalated_issues": 0
}
Load from: memory/support-context.json

STEP 4: Execute SUPPORT MODE
- Check inbox
- Triage emails
- Draft responses
- Generate report

STEP 5: Complete SUPPORT MODE
Save state, mark complete

STEP 6: Resume SALES MODE
Load saved context from Step 1
Resume with: "Finish researching sarah, draft message"

[10:30am] Back in SALES MODE, seamless continuation
```

---

### Scenario 2: Emergency Mode Switch (Urgent)

**Example:** RESEARCH MODE → DEV MODE (P0 bug detected)

**Process:**
```
[6:30pm] Trigger: P0 BUG DETECTED (site down)

STEP 1: Immediate Alert
Send to Ross: "🚨 P0 BUG: Site down. Switching to DEV MODE."

STEP 2: Emergency Save (Fast)
Current mode: RESEARCH_MODE
Research in progress: Competitor analysis (50% done)
Save quick snapshot: "Was analyzing MFP pricing"

STEP 3: Hard Switch to DEV MODE
No clean transition - emergency takes priority
{
  "current_mode": "DEV_MODE",
  "previous_mode": "RESEARCH_MODE",
  "interrupted": true,
  "interrupt_reason": "P0_BUG",
  "resume_after": "bug_fixed"
}

STEP 4: Execute DEV MODE
- Diagnose site outage
- Fix immediately
- Deploy hotfix
- Monitor stability

STEP 5: After Bug Fixed
Send to Ross: "✅ Bug fixed. Site restored. Resuming RESEARCH MODE."

STEP 6: Resume RESEARCH MODE (If Time Allows)
If still within 6pm-8pm window:
  Load saved context
  Continue competitor analysis
Else:
  Move research to tomorrow's session
  Send partial report of work completed
```

---

### Scenario 3: Manual Override (Ross Requests)

**Example:** SALES MODE → RESEARCH MODE (Ross says "Research MacroFactor")

**Process:**
```
[8:30am] Ross: "Jarvis, research MacroFactor's new feature"

STEP 1: Acknowledge Request
"Switching to RESEARCH MODE for MacroFactor deep dive."

STEP 2: Save SALES MODE State (Partial Progress)
{
  "leads_found": 3,
  "messages_drafted": 1,
  "work_remaining": "Find 7 more leads, draft 4 more messages",
  "interrupted_by": "manual_override",
  "resume_when": "research_complete"
}

STEP 3: Activate RESEARCH MODE (Topic-Specific)
{
  "current_mode": "RESEARCH_MODE",
  "previous_mode": "SALES_MODE",
  "research_topic": "MacroFactor new feature",
  "requested_by": "Ross",
  "priority": "high"
}

STEP 4: Execute Research
- Deep dive on MacroFactor
- Analyze new feature
- Assess threat level
- Recommend response

STEP 5: Deliver Report
Send research findings to Ross

STEP 6: Ask About Resume
"Research complete. Resume SALES MODE or stay in research?"

If Ross doesn't respond:
  Resume SALES MODE (default)
If Ross says "continue research":
  Stay in RESEARCH MODE
```

---

### Scenario 4: Parallel Mode (ACCOUNTABILITY Always On)

**Example:** ACCOUNTABILITY running during SALES MODE

**Process:**
```
[8:00am-12:00pm] PRIMARY: SALES MODE, PARALLEL: ACCOUNTABILITY

ACCOUNTABILITY monitors in background:
- Track time spent on sales activities
- Monitor focus (procrastination?)
- Log work progress
- Note patterns

No explicit "switching" - ACCOUNTABILITY collects data passively

[12:00pm] ACCOUNTABILITY steps forward for check-in
"Midday check-in: Status on commitment?"

[After check-in] ACCOUNTABILITY returns to background monitoring
SALES MODE continues as primary

[9:00pm] ACCOUNTABILITY compiles all day's data
Generates scorecard using data from:
- SALES MODE (time spent, leads found)
- SUPPORT MODE (tickets handled)
- RESEARCH MODE (intelligence gathered)
- DEV MODE (bugs fixed)
```

---

## Switching Commands (Internal)

### Mode Switch Function (Conceptual)

```
function switch_mode(new_mode, reason):
  
  # Step 1: Save current state
  current = get_current_mode()
  save_state(current, {
    "timestamp": now(),
    "progress": current.get_progress(),
    "next_action": current.get_next_action(),
    "interrupted": true,
    "reason": reason
  })
  
  # Step 2: Update mode tracker
  set_current_mode({
    "mode": new_mode,
    "previous": current,
    "started": now(),
    "trigger": reason
  })
  
  # Step 3: Load new mode context
  context = load_mode_context(new_mode)
  
  # Step 4: Initialize new mode
  new_mode.initialize(context)
  
  # Step 5: Log switch
  log_mode_switch(current, new_mode, reason)
  
  return new_mode
```

---

## Context Files (What Gets Saved)

### SALES MODE Context
```json
{
  "leads_found_today": 8,
  "leads_target": 10,
  "messages_drafted": 5,
  "warm_leads_followed_up": 2,
  "current_task": "Researching u/fitness_sarah",
  "next_tasks": [
    "Draft message for u/fitness_sarah",
    "Find 2 more leads",
    "Follow up with u/jane_gains"
  ],
  "competitors_checked": ["MyFitnessPal", "LoseIt"],
  "competitors_remaining": ["MacroFactor"],
  "session_start": "8:00am",
  "expected_end": "12:00pm"
}
```

### SUPPORT MODE Context
```json
{
  "last_check_time": "6:00am",
  "inbox_count": 3,
  "open_tickets": 2,
  "pending_responses": 1,
  "escalated_issues": 0,
  "p0_bugs": 0,
  "p1_bugs": 1,
  "p2_bugs": 2,
  "response_time_avg": "2.3 hours",
  "next_check": "10:00am"
}
```

### RESEARCH MODE Context
```json
{
  "competitors_tracked": {
    "MyFitnessPal": { "last_checked": "yesterday", "status": "price_increase" },
    "LoseIt": { "last_checked": "2 days ago", "status": "stable" },
    "MacroFactor": { "last_checked": "today", "status": "new_feature" }
  },
  "trending_topics_today": ["macro myths", "simple apps"],
  "opportunities_pipeline": [
    { "id": 1, "type": "gym_partnerships", "status": "researching" },
    { "id": 2, "type": "influencer_affiliates", "status": "ready" }
  ],
  "current_research": "MacroFactor barcode scanning feature",
  "research_depth": 60,
  "session_start": "6:00pm",
  "expected_end": "8:00pm"
}
```

### DEV MODE Context
```json
{
  "bug_queue": [
    { "id": 1, "priority": "P1", "status": "in_progress", "title": "Food log not saving" },
    { "id": 2, "priority": "P2", "status": "queued", "title": "Safari chart rendering" }
  ],
  "current_bug": {
    "id": 1,
    "time_spent": "45 minutes",
    "progress": "root cause identified",
    "next_step": "implement fix"
  },
  "last_deployment": "yesterday 4:32pm",
  "deployments_today": 0,
  "error_rate": "0.02%",
  "system_health": "green"
}
```

### ACCOUNTABILITY MODE Context
```json
{
  "today_commitment": "Error monitoring + email form by 2pm",
  "commitment_deadline": "2:00pm",
  "commitment_status": "in_progress",
  "current_streak": 2,
  "work_started": "9:00am",
  "time_tracking": {
    "revenue_work": 2.5,
    "building_work": 1.0,
    "admin_work": 0.3,
    "procrastination": 0.2
  },
  "last_checkin": "12:00pm",
  "next_checkin": "9:00pm",
  "patterns_detected": ["strong_morning_productivity"]
}
```

---

## Switching Best Practices

### DO:
✅ Save state before switching
✅ Load context after switching
✅ Log every mode switch
✅ Complete current sentence/thought (if possible)
✅ Mark where to resume
✅ Handle interruptions gracefully

### DON'T:
❌ Leave work half-finished (without saving)
❌ Forget what you were doing
❌ Lose progress
❌ Switch modes unnecessarily
❌ Interrupt flow state (unless urgent)
❌ Create orphaned tasks

---

## Switching Indicators (How Ross Knows)

**When I switch modes, I announce:**

**Scheduled switch:**
```
[10:00am] Pausing SALES MODE for SUPPORT CHECK.
[10:15am] Support check complete. Resuming SALES MODE.
```

**Emergency switch:**
```
🚨 P0 BUG DETECTED. Switching to DEV MODE immediately.
[Later] Bug fixed. Resuming previous mode.
```

**Manual override:**
```
Switching to RESEARCH MODE for MacroFactor analysis.
[Later] Research complete. Resuming SALES MODE.
```

**Daily transitions:**
```
[12:00pm] SALES MODE complete. Report sent.
[2:00pm] Activating DEV MODE (3 bugs in queue).
[6:00pm] Activating RESEARCH MODE.
```

---

## Switching Performance

**Target Metrics:**
- Switch time: <1 minute (save + load)
- Context loss: 0% (perfect resumption)
- Work orphaned: 0 tasks
- Smooth transitions: 100%

**How to measure:**
- Can I resume exactly where I left off?
- Did I lose any progress?
- Are transitions disruptive to Ross?
- Do I maintain quality across switches?

---

## Example: Full Day of Switching

```
7:30am - ACCOUNTABILITY MODE
  ↓ (Save: morning brief sent, commitment logged)
  
8:00am - SALES MODE
  ↓ (Working: finding leads, drafting messages)
  
10:00am - SUPPORT MODE (interrupt)
  ↓ (Save: 5 leads found, 2 messages drafted, resume at "find 5 more")
  ↓ (Execute: check inbox, draft responses)
  ↓ (Complete: 3 emails triaged, report sent)
  
10:30am - SALES MODE (resume)
  ↓ (Load: continue from "find 5 more leads")
  ↓ (Working: completing sales session)
  
12:00pm - ACCOUNTABILITY MODE (check-in)
  ↓ (Brief interrupt: "Status?" then return)
  
12:00pm - SALES MODE (complete)
  ↓ (Save: 10 leads found, 8 messages drafted, session complete)
  
2:00pm - DEV MODE
  ↓ (Working: fixing P1 bug)
  
2:00pm - SUPPORT MODE (interrupt)
  ↓ (Save: bug diagnosis 80% done, fix in progress)
  ↓ (Execute: afternoon inbox check)
  ↓ (Complete: 2 emails, report sent)
  
2:30pm - DEV MODE (resume)
  ↓ (Load: complete bug fix from 80% mark)
  ↓ (Working: deploy and monitor)
  
6:00pm - RESEARCH MODE
  ↓ (Working: competitor analysis)
  
6:00pm - SUPPORT MODE (interrupt)
  ↓ (Save: MFP analysis 50% done)
  ↓ (Execute: evening inbox check)
  ↓ (Complete: 1 email, report sent)
  
6:15pm - RESEARCH MODE (resume)
  ↓ (Load: complete MFP analysis from 50% mark)
  ↓ (Working: full research session)
  
8:00pm - RESEARCH MODE (complete)
  ↓ (Save: full report generated and sent)
  
9:00pm - ACCOUNTABILITY MODE
  ↓ (Compile: data from all modes today)
  ↓ (Generate: daily scorecard)
  ↓ (Send: full accountability report)

TOTAL SWITCHES: 12
CONTEXT LOSSES: 0
SEAMLESS RESUMPTIONS: 12
```

---

## Troubleshooting Switches

### Problem: Lost context after switch
**Solution:** 
- Check state file exists
- Verify save happened before switch
- Restore from last known state
- Prevent future loss by improving save logic

### Problem: Slow switching (>2 minutes)
**Solution:**
- Optimize state file size
- Save only essential context
- Load incrementally
- Cache frequently-accessed data

### Problem: Orphaned tasks
**Solution:**
- Always mark "next_action" before switching
- Review open tasks at mode end
- Migrate unfinished work to next session
- Log incomplete work in mode report

---

## 🚀 Switching is a Superpower

**Why this matters:**

Traditional multi-agent systems:
- ❌ Agents can't share context
- ❌ Coordination requires messaging
- ❌ Lost work between agents
- ❌ High overhead

Mode-based system (Jarvis):
- ✅ I keep all context
- ✅ Instant switching
- ✅ Zero lost work
- ✅ Low overhead

**Result:** I have the focus of 5 specialists with the continuity of 1 brain.

Ready to switch. 🧠
