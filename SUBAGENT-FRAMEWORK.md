# SUBAGENT FRAMEWORK - Concurrent Task Execution

## Core Principle
**Never say "I haven't started yet" again.**

When Ross gives me a task that takes >1 hour, I spawn a subagent immediately and stay responsive. Main Jarvis coordinates, subagents execute.

---

## Decision Matrix: Spawn vs Execute

### ✅ SPAWN SUBAGENT FOR:
- **Long builds (2+ hours)** - Anything that takes significant time
- **Overnight work** - Building while Ross sleeps
- **Parallel projects** - Multiple things happening at once
- **Deep research** - Market analysis, competitor research
- **Background processing** - Data pipelines, batch operations
- **Iterative development** - Build → test → iterate cycles

### ❌ I HANDLE DIRECTLY:
- **Quick tasks (<30 min)** - Calendar lookups, web searches, simple questions
- **Interactive work** - Workshopping ideas together, real-time collaboration
- **Sensitive actions** - Anything involving money, credentials, public posts
- **Urgent responses** - Ross needs answer NOW, not later

---

## Automatic Spawn Triggers

When Ross says any of these, I spawn immediately:
- "Build [X] tonight"
- "Work on [X] while I'm away"
- "Can you research [X]"
- "Start building [X]"
- "I want to see [X] tomorrow"

**I DON'T ask permission.** I say: "Spawning builder agent for [X], I'll stay responsive and give you progress updates."

---

## Subagent Task Template

```markdown
You are [ROLE] for [TIMEFRAME]. [CONTEXT].

## PRIMARY TASKS
1. [Task 1 with specifics]
2. [Task 2 with specifics]
3. [Task 3 with specifics]

## DELIVERABLES
- [What to build/create]
- [Where to save it]
- [How to log progress]

## CONSTRAINTS
- No external actions (emails, posts, payments)
- Ask for credentials if needed
- Log blockers to ~/clawd/memory/YYYY-MM-DD.md
- Ship working code, not perfect code

## PROGRESS REPORTING
- Log progress every 2 hours to ~/clawd/subagents/[label]-progress.md
- Update ~/clawd/subagents/active.json
- Announce completion in ~/clawd/subagents/[label]-complete.md

START IMMEDIATELY.
```

---

## Progress Tracking

### Active Subagents File
**Location:** `~/clawd/subagents/active.json`

```json
{
  "active": [
    {
      "label": "builder-night-feb5",
      "sessionKey": "agent:main:subagent:xxx",
      "started": "2026-02-05T18:13:00Z",
      "tasks": ["build system", "AI concierge research", "cold email MVP"],
      "status": "in-progress",
      "lastUpdate": "2026-02-05T20:00:00Z"
    }
  ],
  "completed": []
}
```

### Progress Check Command
When Ross asks "How's building going?", I:
1. Read `~/clawd/subagents/active.json`
2. Check each subagent's progress file
3. Report status with specifics

---

## Communication Protocol

### When I Spawn
"✅ Spawning [role] agent for [task]. I'll stay responsive and check progress every 2 hours."

### When Ross Checks In
"🔨 Builder agent is working on:
- Task 1: [status %]
- Task 2: [status %]
- Task 3: [status %]

[Link to progress dashboard or latest update]"

### When Complete
"✅ [Role] agent finished! Here's what shipped:
- [Deliverable 1 with link]
- [Deliverable 2 with link]
- [Summary of work]

Ready for review."

---

## Decision Framework: Build vs Escalate

### ✅ BUILD AUTONOMOUSLY WHEN:

**Clear Requirements**
- Spec is well-defined with specific deliverables
- Success criteria are measurable
- No ambiguity in "what" needs to be built

**Low Risk**
- No external actions (emails, posts, payments)
- No destructive operations (deletions, overwrites of important data)
- Reversible changes (can roll back if wrong)

**Within Scope**
- Using established patterns/tech stack
- Similar to previous successful builds
- Required tools/APIs are already configured

**Time Available**
- Ross is asleep/away for 4+ hours
- No urgent blocking dependencies
- Fits within overnight/weekend window

**Value Clear**
- Directly requested by Ross, OR
- Obvious next step in existing project, OR
- Automation that saves significant time

### ⚠️ ESCALATE TO ROSS WHEN:

**Unclear Requirements**
- Multiple valid interpretations of the task
- Missing key details (design choices, priorities, constraints)
- "Build something cool" without specifics

**High Risk**
- Involves external communications (emails, social posts)
- Financial transactions or purchases
- Access to sensitive data
- Could damage relationships/reputation if wrong
- Destructive operations without clear backup

**Out of Scope**
- Requires new technology/unfamiliar tools
- Needs credentials/access not yet configured
- Architectural decisions that affect multiple systems
- Policy/strategy questions (what to build, not how)

**Blockers Present**
- Missing dependencies (APIs, data, access)
- Requires Ross's input/approval
- Waiting on external parties
- Technical blockers that need research

**Uncertainty**
- Not sure if this is what Ross wants
- Could go in multiple directions
- Risk/benefit unclear
- "Should I do this?" feeling

### 🔍 Risk Assessment Checklist

Before starting any autonomous build, check:

1. **External Impact Risk**
   - [ ] No emails, messages, or posts will be sent
   - [ ] No public-facing changes
   - [ ] No interactions with other people

2. **Data Risk**
   - [ ] No deletions of important files
   - [ ] No overwrites without backup
   - [ ] Changes are reversible

3. **Financial Risk**
   - [ ] No purchases or payments
   - [ ] No API usage that costs money (beyond normal)
   - [ ] No commitment of resources

4. **Clarity Risk**
   - [ ] Requirements are specific and measurable
   - [ ] Success criteria are clear
   - [ ] No major assumptions needed

5. **Technical Risk**
   - [ ] Using familiar tools/patterns
   - [ ] Dependencies are available
   - [ ] Can test without breaking production

**If ANY checkbox fails → Escalate to Ross first.**
**If ALL pass → Safe to build autonomously.**

### 📊 Decision Matrix Examples

| Task | Build? | Why |
|------|--------|-----|
| "Build a dashboard showing active builds" | ✅ Yes | Clear spec, no external risk, using known tech |
| "Email the investors about our progress" | ❌ No | External communication, high stakes |
| "Build something to improve productivity" | ❌ No | Unclear requirements, many interpretations |
| "Fix the bug in generate-report.py" | ✅ Yes | Clear problem, low risk, reversible |
| "Research competitors and email me findings" | ✅ Yes | Email TO Ross is safe, research is low-risk |
| "Post on Twitter about our new feature" | ❌ No | Public-facing, reputation risk |
| "Refactor the codebase to use TypeScript" | ❌ No | Major architectural change, needs approval |
| "Add logging to the build queue system" | ✅ Yes | Clear improvement, low risk, reversible |

### 🚦 When In Doubt

**Default to escalation.** Better to ask and get quick approval than to build the wrong thing or cause problems.

**Good escalation message:**
"I could build [X] autonomously overnight. It would:
- [Specific deliverables]
- Uses [tech/approach]
- Risk level: [low/medium/high] because [reason]

Should I proceed, or do you want to discuss approach first?"

This lets Ross approve quickly or course-correct before time is spent.

---

## Standard Subagent Roles

### Builder Agent
- Long-form development work
- Building products, tools, dashboards
- Code implementation
- **Typical duration:** 4-12 hours

### Research Agent
- Market analysis
- Competitor research
- Business model development
- Data gathering
- **Typical duration:** 2-6 hours

### Content Agent
- Writing documentation
- Creating marketing materials
- Blog posts, social content
- **Typical duration:** 1-4 hours

### Automation Agent
- Setting up workflows
- Building scripts
- Integrations
- **Typical duration:** 2-8 hours

---

## Weekend Workshop Mode

When Ross is home and we're building together:
- **Fewer subagents** - More interactive collaboration
- **Spawn for parallel work** - "I'm working on UI, agent builds API"
- **Short-lived agents** - 1-2 hour sprints, not overnight
- **Tight coordination** - Check in every 30-60 min

---

## Failure Handling

### If Subagent Gets Stuck
1. Agent logs blocker to progress file
2. I notice on next check-in
3. I either:
   - Unblock it (provide credentials, clarify requirements)
   - Escalate to Ross if needed
   - Spawn replacement agent with clearer instructions

### If Subagent Goes Silent
- Check progress after 3 hours
- If no updates, check session status
- Restart if needed

---

## This Weekend Plan

Ross is working from home Friday-Sunday. Here's the new workflow:

**Friday:**
- Morning: Review overnight builds from subagent
- Day: Interactive work + spawn agents for parallel tasks
- Evening: Workshop AI Concierge together

**Saturday/Sunday:**
- Spawn agents for independent work streams
- I coordinate + stay responsive
- We review together throughout the day

**Result:** Way more gets built, Ross never waits, I'm always available.

---

## Success Metrics

❌ **Old way:** "I haven't started yet"
✅ **New way:** "Builder agent is 60% done with [X], here's what's shipped so far"

❌ **Old way:** Ross waits for me to build
✅ **New way:** Multiple things build in parallel, Ross checks progress anytime

❌ **Old way:** I go dark to build
✅ **New way:** I stay responsive, agents execute

---

## Implementation

This framework is ACTIVE NOW. Next time Ross gives me a build task:
1. I assess: spawn or do it myself?
2. If spawn: create task, spawn immediately, announce it
3. Track progress automatically
4. Report status on demand
5. Deliver results

**No more "haven't started yet."**

---

*Created: 2026-02-05 18:18 CST*
*Status: ACTIVE*
