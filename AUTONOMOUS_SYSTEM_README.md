# Autonomous Build System - Complete Documentation

**Last updated:** 2026-02-06

---

## What Is This?

This is Jarvis's autonomous build system — the meta-build that changes everything.

**Before:** Ross → "Build X" → Jarvis builds X  
**After:** Jarvis → Checks goals → Builds X, Y, Z autonomously → Ross reviews

**Ross becomes reviewer, not director. Jarvis becomes builder, not order-taker.**

---

## How It Works

### The Autonomous Loop

```
Wake up → Read GOALS.md → Check BUILD_QUEUE.md → 
Generate tasks if empty → Spawn build if ready → Build → 
Notify Ross when done → Ross reviews → Pivot or ship → 
Log learnings → Repeat
```

### Key Components

1. **GOALS.md** — Ross's north star (what we're working toward)
2. **autonomous_check.py** — The brain (generates tasks, spawns builds)
3. **BUILD_QUEUE.md** — Task list (what needs to be built)
4. **BUILD_STATUS.md** — Current state (what's building now)
5. **AUTONOMOUS_AGENT.md** — Operating protocol (how to decide what to build)

---

## What Gets Built Automatically

Jarvis uses a **decision framework** to determine what to build:

### Ask These Questions:
1. **Revenue?** Does it move toward $500 MRR?
2. **Time Savings?** Does it save Ross 1+ hour/week?
3. **Daily Use?** Will Ross use it every day?
4. **Ship Fast?** Can we deliver in <4 hours?

**Decision matrix:**
- ✅ Yes to 2+ questions → **Build it**
- ⏳ Yes to 1 question → **Queue it**
- ❌ No to all → **Skip it**

### High Priority (Build Immediately):
- Anything that generates revenue within 7 days
- Automation that saves Ross 1+ hour/week
- Fitness tracking improvements (he uses daily)
- Side project MVPs (ship fast, iterate)

### Medium Priority (Build During Downtime):
- Dashboard improvements
- Integration polish (calendar, Spotify, bank)
- Content generation (social posts, blog drafts)
- Research/intel gathering (market analysis, competitor research)

### Low Priority (Only If Explicit Request):
- "Cool but not urgent" features
- Complex systems without clear ROI
- Anything that takes >4 hours without revenue tie-in

---

## When Builds Happen

**Session Startup:**
- Every time Jarvis wakes up, `autonomous_check.py` runs
- Checks if queue is empty → generates tasks
- Checks if nothing is building → spawns next build

**Heartbeats (Every 30 Minutes):**
- `autonomous_check.py` runs again
- Checks BUILD_QUEUE.md
- Generates tasks if queue is empty
- Spawns builds if ready

**Time Windows:**
- High priority revenue tasks: 8am-11pm
- Automation tasks: 10pm-6am preferred (off-hours)
- No builds during late night: 11pm-8am (unless urgent)

---

## How Ross Can Influence Direction

### Option 1: Update GOALS.md

Edit `/Users/clawdbot/clawd/GOALS.md` to:
- Change primary mission
- Adjust priorities
- Add/remove sub-goals
- Update success metrics

Jarvis reads GOALS.md on every startup and heartbeat. Changes take effect immediately.

### Option 2: Add to BUILD_QUEUE.md

Manually add tasks to `/Users/clawdbot/clawd/BUILD_QUEUE.md`:

```markdown
- [ ] Your Task Name Here
  - **Priority:** high/medium/low
  - **Category:** revenue/automation/content
  - **Rationale:** Why this matters
```

Jarvis will pick it up on next heartbeat.

### Option 3: Tell Jarvis Directly

Just say:
- "Build X tonight"
- "Add Y to the queue"
- "Prioritize Z"

Jarvis will update BUILD_QUEUE.md and spawn builds accordingly.

---

## How to Pause Autonomy

If you need to pause autonomous building:

**Method 1: Direct Command**
Say to Jarvis:
- "Pause autonomous mode"
- "Stop building autonomously"
- "/autonomous off"

Jarvis will:
1. Stop generating new tasks
2. Finish current build (don't abandon mid-work)
3. Wait for explicit "resume autonomous mode"

**Method 2: Edit HEARTBEAT.md**
Comment out the autonomous check section in `/Users/clawdbot/clawd/HEARTBEAT.md`:

```markdown
## Autonomous Task Generation (Every Heartbeat)
<!-- PAUSED BY ROSS 2026-02-XX
**CRITICAL:** Run autonomous check on every heartbeat:
...
-->
```

**Method 3: Delete GOALS.md**
If `GOALS.md` doesn't exist, autonomous check won't run. (Not recommended — better to pause explicitly)

---

## Monitoring & Logs

### Check What's Building

**View current status:**
```bash
cat ~/clawd/BUILD_STATUS.md
```

**View task queue:**
```bash
cat ~/clawd/BUILD_QUEUE.md
```

**View autonomous decisions:**
```bash
tail -50 ~/clawd/memory/jarvis-journal.md
```

### Jarvis Journal Entries

Autonomous check logs every decision to `~/clawd/memory/jarvis-journal.md`:

```markdown
[2026-02-06 14:30] 🤖 Autonomous check started
[2026-02-06 14:30] ✅ Generated 3 tasks and added to BUILD_QUEUE.md
[2026-02-06 14:30] 🚀 Ready to spawn build: Add Stripe to fitness tracker
[2026-02-06 14:30] ✅ Autonomous check complete
```

You can review this anytime to see what Jarvis is thinking.

---

## Troubleshooting

### "Queue is always empty"

**Check:** Is GOALS.md clear and specific?
- Task generation reads GOALS.md and recent memory
- If goals are vague, task generation won't produce results
- Update GOALS.md with specific, actionable priorities

### "Nothing is building"

**Check:** Is it appropriate time?
- Builds don't spawn 11pm-8am (late night)
- If something is already building, won't spawn new one
- View BUILD_STATUS.md to see current state

**Force a build:**
Say to Jarvis: "Check autonomous system and spawn next build if ready"

### "Jarvis built the wrong thing"

**Fix it:**
1. Tell Jarvis: "This wasn't aligned with goals. Here's why..."
2. Jarvis will log the lesson to jarvis-journal.md
3. Task generation will improve based on feedback
4. Update GOALS.md if priorities changed

**The system learns from mistakes.**

### "How do I know what's in the queue?"

**Ask Jarvis:**
- "What's in the build queue?"
- "What are you building next?"
- "Show me BUILD_STATUS.md"

---

## File Locations

**Core System:**
- `/Users/clawdbot/clawd/GOALS.md` — Ross's north star
- `/Users/clawdbot/clawd/scripts/autonomous_check.py` — The brain
- `/Users/clawdbot/clawd/BUILD_QUEUE.md` — Task list
- `/Users/clawdbot/clawd/BUILD_STATUS.md` — Current state
- `/Users/clawdbot/clawd/AUTONOMOUS_AGENT.md` — Operating protocol

**Configuration:**
- `/Users/clawdbot/clawd/AGENTS.md` — Session startup (runs autonomous check)
- `/Users/clawdbot/clawd/HEARTBEAT.md` — Heartbeat actions (runs autonomous check)

**Logs:**
- `/Users/clawdbot/clawd/memory/jarvis-journal.md` — Autonomous decisions
- `/Users/clawdbot/clawd/memory/YYYY-MM-DD.md` — Daily logs

---

## Testing the System

### Verify It Works

**Test 1: Task Generation**
```bash
# Clear the queue
echo "# Build Queue" > ~/clawd/BUILD_QUEUE.md

# Run autonomous check
cd ~/clawd && python3 scripts/autonomous_check.py

# Verify tasks were generated
cat ~/clawd/BUILD_QUEUE.md
```

**Test 2: Build Spawning**
```bash
# Add a simple test task
echo "- [ ] Test Build: Echo Hello World" >> ~/clawd/BUILD_QUEUE.md

# Run autonomous check
cd ~/clawd && python3 scripts/autonomous_check.py

# Check if build is ready to spawn
cat ~/clawd/BUILD_STATUS.md
```

**Test 3: End-to-End**
1. Tell Jarvis: "Clear the build queue and test autonomous system"
2. Jarvis will:
   - Clear BUILD_QUEUE.md
   - Run autonomous_check.py
   - Generate tasks from GOALS.md
   - Spawn a test build
   - Report results
3. Verify everything worked

---

## Success Metrics

### Jarvis is succeeding when Ross says:

- ✅ "I logged in and you already built what I needed"
- ✅ "I don't have to tell you what to do anymore"
- ✅ "You're always working on something useful"

### Failure signals:

- ❌ "Why did you build this?"
- ❌ "This isn't what I need"
- ❌ "You're building the wrong things"

**If you see failure signals:** Review GOALS.md, check jarvis-journal.md for patterns, adjust task generation logic.

---

## What This Unlocks

**Before Autonomous System:**
- Ross directs every build
- Jarvis waits for instructions
- Progress happens only when Ross has time to ask
- Single-threaded execution

**After Autonomous System:**
- Jarvis reads goals and builds autonomously
- Ross reviews finished work instead of directing every step
- Constant forward motion (builds happen overnight, during downtime)
- Ross shifts from director to reviewer
- Parallel workstreams via sub-agents

**This is the meta-build.** Everything else becomes automatic once this system is working correctly.

---

## Version History

- **v1.0** (2026-02-06): Initial autonomous system created
  - GOALS.md established
  - autonomous_check.py operational
  - AUTONOMOUS_AGENT.md protocol defined
  - AGENTS.md updated (runs on startup)
  - HEARTBEAT.md updated (runs every 30min)
  - Documentation complete

---

## Questions?

Ask Jarvis:
- "Explain the autonomous system"
- "How does task generation work?"
- "What are you building next?"
- "Show me AUTONOMOUS_AGENT.md"

Or read the source:
- `/Users/clawdbot/clawd/scripts/autonomous_check.py` (well-commented)
- `/Users/clawdbot/clawd/AUTONOMOUS_AGENT.md` (operating protocol)
