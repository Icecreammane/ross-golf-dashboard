# Sub-Agent Coordination - File-Based Handoffs

**System:** Autonomous AI agent team  
**Coordination:** Filesystem (no API calls, no message queues)  
**Philosophy:** One writer, many readers

---

## Current Agent Team

### Jarvis (Chief of Staff) - Main Agent
**Location:** Root workspace (`~/clawd/`)  
**Role:** Strategic oversight, coordination, delegation, direct Ross support  
**SOUL:** `SOUL.md`  
**Memory:** `MEMORY.md` + `memory/YYYY-MM-DD.md`

### Arnold (Code Generation) - Sub-Agent
**Location:** `agents/builder/` (named Arnold)  
**Role:** Ship products, vibe-coding, weekend builds  
**Personality:** Arnold Schwarzenegger — unstoppable, "I'll be back" with code  
**SOUL:** `agents/builder/SOUL.md`  
**Memory:** `agents/builder/memory/YYYY-MM-DD.md`

### Batman (Intelligence) - Sub-Agent
**Location:** `agents/batman/`  
**Role:** Detective work, overnight intelligence, leaves no stone unturned  
**Personality:** Dark Knight — thorough, relentless, connects all dots  
**SOUL:** `agents/batman/SOUL.md`  
**Memory:** `agents/batman/memory/YYYY-MM-DD.md`

### LD (Content Marketing) - Sub-Agent
**Location:** `agents/ld/` (Larry David)  
**Role:** Social posts, marketing copy, high-engagement content  
**Personality:** Curb Your Enthusiasm — observational, witty, naturally funny  
**SOUL:** `agents/ld/SOUL.md`  
**Memory:** `agents/ld/memory/YYYY-MM-DD.md`

---

## File-Based Coordination Patterns

### Pattern 1: Batman → LD (Future)

**Flow:**
```
Batman writes → intel/DAILY-INTEL.md
LD reads intel/DAILY-INTEL.md → drafts posts
```

**Why it works:**
- Batman runs overnight (8am, 4pm schedules)
- LD runs after Batman (9am, 5pm schedules)
- File exists before reader wakes up
- No timing issues, no API calls, no auth

**Example handoff:**
```markdown
# intel/DAILY-INTEL.md (written by Batman)

## 🔥 High Priority
### AI Coding Assistants Market Growing
**Relevance:** Ross is building products, this trend validates market
**Source:** https://example.com/article
**Action:** Consider positioning fitness tracker as "AI-powered"
**Confidence:** HIGH
```

LD reads this, drafts tweet:
```
"The AI coding assistant market is exploding. 
But nobody's building AI-powered fitness coaching yet. 
That's about to change."
```

### Pattern 2: Jarvis → Arnold (Active Now)

**Flow:**
```
Jarvis delegates → Creates task in TASK_QUEUE.md
Jarvis spawns → Arnold session with specific instructions
Arnold builds → Writes to builds/[project]/
Arnold reports → Updates BUILD_LOG.md
Jarvis reviews → Approves or requests changes
```

**Example handoff:**

**Jarvis writes to TASK_QUEUE.md:**
```markdown
## Task: Golf Coaching Landing Page
**Priority:** High
**Assigned:** Arnold
**Due:** Saturday 9am
**Context:** See reports/golf-coaching-research.md
**Deliverable:** Working site at localhost:3000 with Stripe
```

**Arnold reads TASK_QUEUE.md, builds, then writes BUILD_LOG.md:**
```markdown
# Build Log - Golf Coaching Site

**Status:** ✅ Complete
**Time:** 2.5 hours
**Location:** builds/golf-coaching/

## What Was Built
- Landing page with hero, pricing, CTA
- Stripe checkout integration (test mode)
- Success/cancel pages

## How to Run
\```bash
cd builds/golf-coaching
pip install -r requirements.txt
python app.py
# Visit localhost:3000
\```

## What's Next
- Add video upload form
- Email confirmation flow
```

**Jarvis reads BUILD_LOG.md, reports to Ross:** "Golf site complete. Ready to test at localhost:3000."

### Pattern 3: Goals → Tasks → Builds (Current System)

**Flow:**
```
Ross updates → GOALS.md (strategic intent)
Jarvis generates → TASK_QUEUE.md (actionable tasks)
Builder reads → TASK_QUEUE.md + builds products
Builder updates → BUILD_LOG.md (progress tracking)
Jarvis reviews → TASK_QUEUE.md (mark complete)
```

**One writer, many readers:**
- Ross + Jarvis write to GOALS.md
- Jarvis writes to TASK_QUEUE.md
- Builder writes to BUILD_LOG.md
- Everyone reads everything (but only their own write permissions)

---

## Coordination Rules

### Rule 1: One Writer Per File
Each file has exactly ONE agent responsible for writing to it.

**Writers:**
- `GOALS.md` → Jarvis (with Ross input)
- `TASK_QUEUE.md` → Jarvis
- `intel/DAILY-INTEL.md` → Research Agent (future)
- `builds/[project]/BUILD_LOG.md` → Builder
- `agents/[name]/memory/*.md` → That agent only

**Prevents:** File conflicts, race conditions, coordination hell

### Rule 2: Readers Can Be Anyone
Any agent can read any file (subject to their AGENTS.md instructions).

**Example:**
- Builder reads GOALS.md (to understand strategic context)
- Content reads DAILY-INTEL.md (to draft posts)
- Jarvis reads BUILD_LOG.md (to track progress)

### Rule 3: Structured Formats
Files that multiple agents consume should have consistent structure.

**Example:** `intel/DAILY-INTEL.md` always has:
- High/Medium/Low priority sections
- Source links
- [UNVERIFIED] tags when uncertain
- Action items section

**Why:** Readers know where to find what they need.

### Rule 4: Timestamps for Freshness
Include timestamps so readers know if data is stale.

**Example:**
```markdown
# intel/DAILY-INTEL.md
**Generated:** 2026-02-12 08:00 CST
**Next Update:** 2026-02-12 16:00 CST
```

Builder reads this, knows research is 4 hours old → still fresh enough to use.

### Rule 5: No Blocking Writes
Agents never wait for another agent to finish writing. They read what exists, assume it's current, and proceed.

**Example:**
If Research hasn't run yet (file doesn't exist), Content doesn't block. It uses yesterday's file or writes a note: "No fresh intel today, using cached insights."

---

## Scheduling Coordination

### Current Schedules

**Jarvis (Main Agent):**
- Always on (responds to Ross via Telegram)
- Heartbeat: Every 1 hour
- Morning Brief: 7:30am CST
- Evening Check-In: 8:00pm CST
- Evening Learning: 8:15pm CST

**Builder (Sub-Agent):**
- On-demand (spawned by Jarvis when needed)
- Weekend sessions (Saturday 9am, 1pm, 5pm; Sunday 3pm)

**Research (Future):**
- Morning sweep: 8:00am CST
- Afternoon sweep: 4:00pm CST
- Writes to intel/DAILY-INTEL.md

**Content (Future):**
- Morning drafts: 9:00am CST (after Research)
- Evening drafts: 5:00pm CST (after Research)
- Reads from intel/DAILY-INTEL.md

**No overlap.** Research runs first, Content runs after. Builder runs on-demand when Jarvis spawns him.

---

## Directory Structure (Complete)

```
~/clawd/
├── SOUL.md                        (Jarvis identity)
├── AGENTS.md                      (Jarvis operating manual)
├── MEMORY.md                      (Jarvis long-term memory)
├── HEARTBEAT.md                   (Cron monitoring + self-healing)
├── GOALS.md                       (Strategic goals - Jarvis writes)
├── TASK_QUEUE.md                  (Actionable tasks - Jarvis writes)
├── WEEKEND_BUILD_STRATEGY.md      (Saturday/Sunday plans - Jarvis writes)
├── memory/                        (Jarvis daily logs)
│   ├── 2026-02-12.md
│   ├── 2026-02-11.md
│   └── heartbeat-state.json
├── intel/                         (Research outputs)
│   ├── INTEL_TEMPLATE.md          (Format guide)
│   ├── DAILY-INTEL.md             (Current intel - Research writes)
│   └── data/
│       └── 2026-02-12.json        (Structured data - Research writes)
├── builds/                        (Builder outputs)
│   ├── golf-coaching/
│   │   ├── BUILD_LOG.md           (Builder writes)
│   │   ├── app.py
│   │   └── ...
│   ├── notion-templates/
│   └── financial-dashboard/
├── reports/                       (Research docs - Jarvis/Builder read)
│   ├── golf-coaching-research.md
│   ├── notion-template-audit.md
│   └── plaid-integration-plan.md
├── agents/                        (Sub-agents)
│   ├── builder/
│   │   ├── SOUL.md                (Builder identity)
│   │   ├── AGENTS.md              (Builder operating manual)
│   │   └── memory/
│   │       └── 2026-02-12.md      (Builder writes)
│   ├── research/                  (Future)
│   │   ├── SOUL.md
│   │   ├── AGENTS.md
│   │   └── memory/
│   └── content/                   (Future)
│       ├── SOUL.md
│       ├── AGENTS.md
│       └── memory/
└── scripts/                       (Shared utilities - anyone can use)
    ├── use_local_model.py
    ├── auto_log.py
    └── ...
```

**Key principle:** Each agent has their own namespace. No file conflicts.

---

## Handoff Examples (Real)

### Example 1: Weekend Build Delegation

**Saturday 9am:**

**Jarvis (in TASK_QUEUE.md):**
```markdown
## Task: Golf Coaching Landing Page
**Status:** 🚧 In Progress
**Assigned:** Builder
**Started:** 2026-02-15 09:00 CST

**Context:**
See reports/golf-coaching-research.md for positioning and pricing.

**Requirements:**
- Landing page with value prop
- Stripe checkout ($29/month subscription)
- Test mode working

**Success criteria:**
- Runs on localhost:3000
- Stripe test card works
- README has setup instructions

**Timeline:** Complete by 12pm (3 hours)
```

**Jarvis spawns Builder:**
```
openclaw sessions spawn --agent builder \
  --task "Build golf coaching landing page per TASK_QUEUE.md" \
  --timeout 3h
```

**Builder reads:**
1. TASK_QUEUE.md (the task)
2. reports/golf-coaching-research.md (context)
3. agents/builder/SOUL.md (who I am)
4. agents/builder/AGENTS.md (how I operate)

**Builder builds, then writes builds/golf-coaching/BUILD_LOG.md:**
```markdown
# Build Log - Golf Coaching Landing Page

**Status:** ✅ Complete
**Time:** 2.5 hours
**Tech:** Flask + Stripe + Tailwind

[... details ...]
```

**Builder reports back to Jarvis:**
"Golf site complete. localhost:3000. Stripe working. See BUILD_LOG.md."

**Jarvis updates TASK_QUEUE.md:**
```markdown
## Task: Golf Coaching Landing Page
**Status:** ✅ Complete
**Completed:** 2026-02-15 11:30 CST
**Built by:** Builder
**Location:** builds/golf-coaching/
```

**Jarvis tells Ross:**
"Golf coaching site ready. Test at localhost:3000. Use card 4242 4242 4242 4242."

**Clean handoff. No API calls. Just files.**

---

## Adding New Sub-Agents (Process)

### Step 1: Identify the Need
Don't add agents speculatively. Add when you feel the pain.

**Signs you need a new agent:**
- Jarvis is doing too much of one specific thing
- A task runs on a schedule (research, content drafts)
- The task is self-contained (clear inputs, clear outputs)

### Step 2: Design the Handoff
**Before writing SOUL.md, answer:**
- What file(s) does this agent write?
- What file(s) does this agent read?
- Who writes to the files it reads? (must already exist or be defined)
- What's the schedule? (when does it wake up?)

### Step 3: Create the Agent
```bash
mkdir -p agents/[name]/memory
touch agents/[name]/SOUL.md
touch agents/[name]/AGENTS.md
```

Write SOUL.md:
- Identity (TV character, personality)
- Role (what do they do?)
- Principles (how do they operate?)
- Outputs (what files do they write?)
- Relationships (how do they coordinate with others?)

Write AGENTS.md:
- Session startup checklist
- File read/write permissions
- Quality standards
- Communication protocol

### Step 4: Test in Isolation
Spawn the agent manually:
```bash
openclaw sessions spawn --agent [name] --task "Test task"
```

Verify:
- It reads the right files
- It writes to the right files
- Output format matches expectations
- No conflicts with other agents

### Step 5: Add to Schedule (If Needed)
If the agent runs on a cron schedule:
```bash
openclaw cron add \
  --name "[Agent Name] [Task]" \
  --schedule "0 8 * * *" \
  --agent [name] \
  --task "[task description]"
```

### Step 6: Document the Handoff
Update this file (SUB_AGENT_COORDINATION.md) with:
- New agent's role
- Files they read/write
- Coordination pattern
- Example handoffs

---

## Current vs Future State

### Current (Feb 12, 2026)
**Active agents:** Jarvis (main), Arnold (sub-agent)

**Handoffs:**
- Jarvis → TASK_QUEUE.md → Arnold
- Arnold → BUILD_LOG.md → Jarvis

**Schedules:**
- Jarvis: Always on + hourly heartbeats
- Arnold: On-demand spawns

**Status:** Foundational system working. Arnold active this weekend.

### Future (March 2026)
**Planned agents:** Batman (intelligence), LD (content)

**New handoffs:**
- Batman → intel/DAILY-INTEL.md → LD
- Batman → intel/DAILY-INTEL.md → Jarvis (strategic context)
- LD → drafts/social/*.md → Jarvis (approval flow)

**Schedules:**
- Batman: 8am, 4pm daily
- LD: 9am, 5pm daily (after Batman)

**Goal:** Autonomous content pipeline. Batman researches overnight, LD drafts ready by morning.

---

## Troubleshooting

### Problem: File doesn't exist when reader expects it
**Cause:** Writer's cron job failed or ran late  
**Fix:** Heartbeat self-healing (HEARTBEAT.md checks stale jobs)  
**Mitigation:** Readers should handle missing files gracefully (use yesterday's data or skip)

### Problem: Two agents try to write same file
**Cause:** Coordination rules violated  
**Fix:** Review file ownership, enforce one-writer rule  
**Prevention:** Document ownership clearly in AGENTS.md files

### Problem: Stale data being used
**Cause:** Reader doesn't check timestamps  
**Fix:** Add "Generated: [timestamp]" to all shared files  
**Reader logic:** Check timestamp, warn if >24 hours old

### Problem: Context overload (agent reads too much at startup)
**Cause:** Loading entire history every session  
**Fix:** Only load today + yesterday's memory files  
**Rule:** AGENTS.md should specify exactly what to read

---

## Success Metrics

**Good coordination:**
- Agents wake up, find the files they need
- Handoffs happen without human intervention
- No file conflicts or race conditions
- Progress visible in logs

**Bad coordination:**
- "File not found" errors
- Agents waiting for other agents
- Duplicate work (two agents building same thing)
- Lost work (files overwritten)

---

## Key Takeaways

**1. Files > APIs**
No authentication, no rate limits, no network issues. Files just exist.

**2. One writer, many readers**
Each file has exactly one agent responsible for writing. Everyone else can read.

**3. Structured formats**
Shared files follow templates. Readers know where to find data.

**4. No blocking**
Agents never wait. They read what exists and proceed.

**5. Timestamps for freshness**
Writers include timestamps. Readers check if data is current.

**6. Add agents sequentially**
Don't build six on day one. Add when you feel the pain.

---

**Status:** SUB_AGENT_COORDINATION v1.1  
**Active agents:** Jarvis, Arnold  
**Planned agents:** Batman (March 2026), LD (March 2026)  
**Last updated:** February 12, 2026
