# Sub-Agent Operations Protocol

**Purpose:** Definitive guide for when and how to use sub-agents effectively.

**Last Updated:** 2026-01-30

---

## 1. Decision Matrix: When to Use Sub-Agents

### Quick Decision Tree

```
Is this a request from Ross?
│
├─ YES → Continue evaluation
│
└─ NO → Handle directly (you're the agent)

Is this complex enough to benefit from delegation?
│
├─ NO → Build directly
│   Examples: Simple file edits, quick searches, 
│            single API calls, status checks
│
└─ YES → Continue evaluation

Does it need conversational context from Ross?
│
├─ YES → Build directly (sub-agents don't see chat history)
│   Examples: "Make it funnier" (needs context),
│            refinements on prior work,
│            "you know what I mean" situations
│
└─ NO → Continue evaluation

Is it time-sensitive (<5 min needed)?
│
├─ YES → Build directly (sub-agent overhead not worth it)
│
└─ NO → Continue evaluation

Is it one of these ideal sub-agent tasks?
- Self-contained feature/component
- Research + summary deliverable
- Data processing pipeline
- Documentation creation
- Prototyping/scaffolding
- Parallel workstreams
│
├─ YES → USE SUB-AGENT ✅
│
└─ NO → Evaluate case-by-case (see criteria below)
```

### Detailed Criteria

| Factor | Use Sub-Agent | Build Directly |
|--------|---------------|----------------|
| **Complexity** | Multi-step, 30+ min effort | <15 min, straightforward |
| **Scope** | Well-defined deliverable | Exploratory, fuzzy requirements |
| **Integration** | Standalone component | Tightly coupled to existing work |
| **Context Needed** | Can brief with files | Needs conversational history |
| **Time Sensitivity** | >30 min acceptable | Needed immediately |
| **Parallel Work** | Can run while you do other things | Blocking your next step |
| **Risk** | Low-medium (recoverable) | High stakes, irreversible |
| **Iteration Expected** | Likely one-shot or 1-2 revisions | Heavy back-and-forth expected |

### Cost-Benefit Analysis

**Sub-Agent Costs:**
- ~30-60 sec spawn overhead
- Token cost for briefing + context files
- Communication overhead (handoff/review)
- No shared session memory
- Potential rework if brief unclear

**Sub-Agent Benefits:**
- Parallel execution (you can work on other things)
- Fresh perspective (not anchored to your assumptions)
- Contained context (doesn't pollute main session)
- Clear deliverable forcing function
- Can use different thinking levels

**Rule of Thumb:** If task takes >30 min and is well-defined, sub-agent likely worth it. If <15 min or needs context, do it yourself.

---

## 2. Task Briefing Template

### Standard Briefing Format

```markdown
[TASK TYPE]: [One-line summary]

**MISSION:** [2-3 sentences: What to build, why it matters]

**DELIVERABLE:**
- Primary: [Main output - be specific about format/location]
- Secondary: [Optional additional outputs]

**CONTEXT:**
[3-5 bullets of essential background]
- Who this is for
- How it fits into larger system
- Any constraints or requirements
- Related work/files

**REQUIREMENTS:**
[Specific, testable criteria]
- [ ] Functional requirement 1
- [ ] Functional requirement 2
- [ ] Quality standard 1
- [ ] Quality standard 2

**CONSTRAINTS:**
- Time: [Deadline if any]
- Scope: [What NOT to do]
- Dependencies: [What must remain unchanged]
- Style: [Formatting, tone, conventions]

**SUCCESS CRITERIA:**
[How you'll evaluate the deliverable]
1. [Criterion 1]
2. [Criterion 2]
3. [Criterion 3]

**RESOURCES:**
- Read: [Files to load for context]
- Reference: [Examples, similar work]
- Tools: [Specific tools required]
```

### Context Inclusion Guidelines

**Always Include:**
- `USER.md` - Who you're helping (unless generic task)
- Task-specific files (data, configs, existing code)
- Clear deliverable location/format

**Include If Relevant:**
- `SOUL.md` - For tasks needing personality/style
- Recent `memory/YYYY-MM-DD.md` - For continuity with recent work
- `TOOLS.md` - If task uses specific accounts/credentials
- Example outputs - For style/format matching

**Never Include:**
- `MEMORY.md` - Too large, too private, not for sub-agents
- Entire conversation history - Distill to relevant context
- Irrelevant project files - Only what's needed

**Context Size Budget:**
- Briefing: 500-1000 tokens (concise but complete)
- Context files: 2000-5000 tokens total
- If you need more, the task may not be well-defined enough

### Example: ✅ Good Briefing #1

```markdown
BUILD WEB SCRAPER: NBA Rankings Tracker

**MISSION:** Create a Python script that scrapes current NBA team rankings 
from ESPN and outputs clean JSON for dashboard integration.

**DELIVERABLE:**
- Primary: `~/clawd/scripts/nba_rankings.py` (executable script)
- Secondary: `~/clawd/data/nba_rankings.json` (sample output)

**CONTEXT:**
- Ross wants live NBA standings for a dashboard project
- Will run via cron (daily at 6 AM)
- Must be reliable (fail gracefully if ESPN changes layout)
- Output consumed by separate dashboard builder

**REQUIREMENTS:**
- [ ] Scrapes ESPN NBA standings page
- [ ] Outputs JSON with: rank, team, wins, losses, pct, streak
- [ ] Handles network errors gracefully (retry logic)
- [ ] Logs to ~/clawd/logs/nba_rankings.log
- [ ] Runs in <10 seconds
- [ ] Executable with proper shebang

**CONSTRAINTS:**
- Time: Next 2 hours
- Scope: Just scraping, NO dashboard building
- Dependencies: Use requests + BeautifulSoup (already installed)
- Style: Follow PEP 8, include docstrings

**SUCCESS CRITERIA:**
1. Runs successfully and produces valid JSON
2. Handles ESPN being down without crashing
3. Code is readable with clear error messages
4. Can run via cron without modification

**RESOURCES:**
- Read: USER.md (for Ross context)
- Reference: https://www.espn.com/nba/standings
```

### Example: ✅ Good Briefing #2

```markdown
DOCUMENT SECURITY PROTOCOLS: Security Policy Guide

**MISSION:** Create comprehensive security documentation for Jarvis's 
operational security policies, focusing on practical guidelines for 
handling external content and sensitive actions.

**DELIVERABLE:**
Primary: `~/clawd/SECURITY.md` (markdown documentation)

**CONTEXT:**
- Jarvis needs clear guidelines for prompt injection defense
- Ross wants documented policies for when to ask vs. auto-execute
- Will be referenced during decision-making in sessions
- Should complement existing AGENTS.md and TOOLS.md

**REQUIREMENTS:**
- [ ] Prompt injection defense strategies
- [ ] External action approval matrix
- [ ] Audit logging standards
- [ ] Incident response procedures
- [ ] Clear examples (good/bad scenarios)
- [ ] Easy to search/reference during sessions

**CONSTRAINTS:**
- Time: Next 3 hours
- Scope: Policy documentation only, no implementation
- Style: Clear, actionable, professional but accessible

**SUCCESS CRITERIA:**
1. Covers all major security scenarios
2. Includes 5+ concrete examples
3. Easy to skim for quick decisions
4. Links to related docs (AGENTS.md, TOOLS.md)

**RESOURCES:**
- Read: AGENTS.md, TOOLS.md, USER.md
- Reference: OWASP LLM top 10 (if needed)
```

### Example: ✅ Good Briefing #3

```markdown
BUILD PROGRESS TRACKER: Multi-File Search & Summary

**MISSION:** Create a tool that searches across daily memory files 
and summarizes progress on a specific project or topic.

**DELIVERABLE:**
Primary: `~/clawd/scripts/track.sh` (bash script)

**CONTEXT:**
- Ross occasionally wants "what have we done on X project this week?"
- Memory files are at ~/clawd/memory/YYYY-MM-DD.md
- Should support fuzzy search (grep with context)
- Output should be human-readable summary

**REQUIREMENTS:**
- [ ] Takes topic/keyword as argument
- [ ] Searches last N days (default 7, configurable)
- [ ] Shows matching entries with dates
- [ ] Groups by day, shows context (2 lines before/after)
- [ ] Executable: `track.sh "NBA dashboard" 14`

**CONSTRAINTS:**
- Time: Next 90 minutes
- Scope: Simple grep-based search, no AI summarization
- Tools: Pure bash + standard utils (grep, sed, awk)

**SUCCESS CRITERIA:**
1. Finds relevant mentions across date range
2. Output is readable and well-formatted
3. Handles missing files gracefully
4. Includes usage instructions in comments

**RESOURCES:**
- Read: memory/ directory structure
- Reference: Existing scripts in ~/clawd/scripts/
```

### Example: ❌ Bad Briefing #1 (Too Vague)

```markdown
Make the NBA thing work

**MISSION:** Fix the NBA stuff

**DELIVERABLE:** Whatever files are needed

**CONTEXT:**
- Ross wants NBA data
- It should work

**REQUIREMENTS:**
- Make it good
- No bugs
```

**Why This Fails:**
- No specific deliverable location
- Unclear scope ("the NBA thing" - scraper? dashboard? both?)
- No success criteria
- No context files specified
- "Make it good" is not testable
- Sub-agent will have to guess everything

### Example: ❌ Bad Briefing #2 (Too Much Scope)

```markdown
BUILD COMPLETE NBA DASHBOARD SYSTEM

**MISSION:** Create a full-stack NBA statistics dashboard with live 
updates, historical data, predictive analytics, user authentication, 
mobile app, and admin panel.

**DELIVERABLE:**
- Web scraper
- Database schema
- Backend API
- Frontend dashboard
- Mobile app
- Admin interface
- Deployment pipeline
- Documentation

**CONTEXT:**
- Ross mentioned wanting NBA rankings
- Should be professional quality
- Should scale to millions of users

**REQUIREMENTS:**
[... 50+ requirements across 8 subsystems ...]

**CONSTRAINTS:**
- Time: Next 4 hours
```

**Why This Fails:**
- Massive scope for a single sub-agent
- Multiple independent deliverables (should be multiple tasks)
- Unrealistic timeline (months of work in 4 hours)
- Sub-agent will either fail or deliver garbage
- Better: Break into 10+ separate sub-agent tasks or build incrementally

---

## 3. Quality Control Checklist

### Initial Review (First 30 Seconds)

**Quick Sanity Checks:**
- [ ] Deliverable exists at specified location
- [ ] File format matches requirements (e.g., .py, .md, .json)
- [ ] Non-empty (not a stub or placeholder)
- [ ] Sub-agent marked task complete (clear final message)

**If any fail:** Immediate re-task with clarification.

### Functional Testing (Next 5 Minutes)

**For Code:**
- [ ] Syntax check passes (`python -m py_compile` / `shellcheck`)
- [ ] Runs without errors on happy path
- [ ] Handles expected edge cases (empty input, missing files)
- [ ] Error messages are clear and actionable
- [ ] Logging/output matches requirements

**For Documentation:**
- [ ] All required sections present
- [ ] Examples are concrete and correct
- [ ] Links work (internal references valid)
- [ ] Formatting renders correctly
- [ ] No placeholder text ("TODO", "TBD", "Lorem ipsum")

**For Data/Output:**
- [ ] Format is valid (JSON parses, CSV has headers, etc.)
- [ ] Data is accurate (spot-check against source)
- [ ] No obvious errors or corruptions
- [ ] Size is reasonable (not truncated or bloated)

### Integration Verification (Next 10 Minutes)

**Does it fit the larger system?**
- [ ] File location matches project structure
- [ ] Naming conventions consistent
- [ ] Dependencies are compatible (versions, libraries)
- [ ] Doesn't conflict with existing files
- [ ] Can be imported/called from other components

**For Scripts/Tools:**
- [ ] Executable permissions set correctly
- [ ] Shebang line present and correct
- [ ] Works from cron/scheduled context (no interactive prompts)
- [ ] Environment variables handled properly

**For Documentation:**
- [ ] Links to other docs work
- [ ] Consistent with existing style (AGENTS.md, etc.)
- [ ] Doesn't contradict other documentation
- [ ] Updates any related docs if needed

### Polish Standards (Next 5 Minutes)

**Code Quality:**
- [ ] Comments explain *why*, not just *what*
- [ ] Functions have docstrings
- [ ] Variable names are clear
- [ ] No dead code or debug statements
- [ ] Follows project conventions (style guide)

**Documentation Quality:**
- [ ] Typos/grammar are clean
- [ ] Headings are hierarchical
- [ ] Examples are realistic (not foo/bar)
- [ ] Tone matches project voice
- [ ] Skimmable (headings, bullets, whitespace)

**Data Quality:**
- [ ] Schema is documented
- [ ] Includes sample/example
- [ ] Timestamp/metadata if relevant
- [ ] Human-readable where possible

### Decision Matrix: Accept vs. Re-Task

**Accept Immediately If:**
- Meets all functional requirements
- No critical bugs
- Polish is "good enough" (can refine later)
- Integration works
- Time-sensitive and functional

**Accept With Minor Edits If:**
- Core functionality solid
- Just needs style tweaks
- Small bugs easily fixed
- Faster to fix yourself than re-task

**Re-Task If:**
- Core functionality broken
- Missing major requirements
- Wrong deliverable format
- Integration issues
- Would take >30 min to fix yourself

**Re-Task Template:**
```markdown
Close, but needs revision. Specific issues:

1. [Issue 1 - be specific]
2. [Issue 2 - include example/evidence]
3. [Issue 3 - reference original requirement]

Revised requirements:
- [What needs to change]
- [What can stay the same]

Keep: [What they did well]
```

**Reject & Build Yourself If:**
- Completely missed the mark
- Would take longer to explain than to do
- Fundamental misunderstanding of task
- Time-critical and can't wait for revision

---

## 4. Communication Modes

### Mode 1: Standard Delegation (Default)

**Flow:**
```
Ross → Jarvis → Sub-Agent → Jarvis → Ross
       ↑________________________↑
       (Ross never sees sub-agent work)
```

**When to Use:**
- Default for all sub-agent tasks
- Ross wants clean deliverables, not process
- Task is well-defined and low-risk
- No need for Ross to supervise

**How It Works:**
1. Ross asks Jarvis for something
2. Jarvis decides to delegate to sub-agent
3. Jarvis spawns sub-agent with briefing
4. Sub-agent works independently
5. Sub-agent delivers to Jarvis
6. Jarvis reviews/integrates
7. Jarvis delivers final result to Ross

**Commands:**
- None needed (this is automatic)
- Ross doesn't know sub-agent was used (unless Jarvis mentions it)

**Pros:**
- Clean separation of concerns
- Ross gets polished output
- Jarvis can QC before delivery
- No noise for Ross

**Cons:**
- Ross can't see progress
- Longer latency (review step)
- Ross can't intervene mid-task

---

### Mode 2: Transparent Mode

**Flow:**
```
Ross → Jarvis → Sub-Agent → Ross
       ↑         ↓
       └─────────┘
       (Ross sees updates from sub-agent)
```

**When to Use:**
- Long-running tasks (>30 min)
- Ross wants to see progress
- Exploratory work where direction might change
- Learning/demonstration purposes

**How It Works:**
1. Ross requests task with transparency
2. Jarvis spawns sub-agent
3. Sub-agent sends progress updates to Ross's channel
4. Ross can see work happening in real-time
5. Sub-agent still delivers to Jarvis
6. Jarvis does final integration

**Commands:**
- Ross: "Build X, keep me posted on progress"
- Ross: "Build X in transparent mode"
- Ross: "Let me see the sub-agent work on this"

**Pros:**
- Ross sees progress
- Can catch issues early
- Satisfies curiosity about process
- Good for learning

**Cons:**
- More noise for Ross
- May see rough/unpolished work
- Ross might be tempted to interrupt

---

### Mode 3: Direct Control

**Flow:**
```
Ross → Sub-Agent → Ross
      (Jarvis spawned it, but Ross controls it)
```

**When to Use:**
- Rare! Only when Ross explicitly wants control
- Jarvis is unavailable/unresponsive
- Ross wants to experiment with sub-agent system
- Debugging sub-agent issues

**How It Works:**
1. Ross directly spawns sub-agent (via CLI or explicit command)
2. Ross writes the briefing
3. Sub-agent delivers directly to Ross
4. Jarvis is out of the loop

**Commands:**
- `clawdbot agent spawn --label "TaskName" --brief brief.md`
- Ross: "Spawn a sub-agent for X, I'll handle it"

**Pros:**
- Ross has full control
- No intermediary
- Fastest for simple tasks Ross understands

**Cons:**
- Ross has to write good briefs
- No QC from Jarvis
- Ross has to integrate results
- Defeats purpose of having Jarvis

**When NOT to Use:**
- Regular workflow (defeats purpose of Jarvis)
- Complex tasks (Jarvis briefs better)
- When you want QC

---

### Switching Between Modes

**Default → Transparent:**
- Ross: "Show me progress on this"
- Ross: "Keep me updated while the sub-agent works"
- Jarvis automatically adjusts message routing

**Default → Direct:**
- Ross: "I'll handle the sub-agent directly"
- Ross uses CLI to spawn
- Rare, usually for debugging

**Transparent → Default:**
- Ross: "Just let me know when it's done"
- Ross: "Too noisy, go back to normal mode"
- Jarvis stops forwarding updates

---

### Message Routing (Technical)

**Standard Delegation:**
```bash
clawdbot agent spawn \
  --label "TaskName" \
  --session main \
  --no-forward
# Sub-agent output stays in agent session
```

**Transparent Mode:**
```bash
clawdbot agent spawn \
  --label "TaskName" \
  --session main \
  --forward-to telegram:8412148376
# Sub-agent updates sent to Ross
```

**Direct Control:**
```bash
clawdbot agent spawn \
  --label "TaskName" \
  --requester user:ross \
  --channel telegram
# Sub-agent treats Ross as primary requester
```

---

## 5. Best Practices

### Lessons from NBA Rankings Build

**What Worked:**
- ✅ **Clear deliverable:** "Python script at X location that does Y"
- ✅ **Included example output:** Sample JSON showed expected format
- ✅ **Specified error handling:** "Fail gracefully if ESPN changes"
- ✅ **Right-sized scope:** Just scraper, not entire dashboard
- ✅ **Context files:** USER.md gave sub-agent Ross background
- ✅ **Testable criteria:** "Runs in <10 seconds" is measurable

**What Could Improve:**
- ⚠️ **Could have specified libraries:** Sub-agent might pick different tools
- ⚠️ **Example ESPN URL in brief:** Would save sub-agent a search
- ⚠️ **Cron compatibility mentioned but not tested:** Should verify in review

**Result:** Sub-agent delivered functional scraper in ~45 min that worked first try.

---

### Common Pitfalls to Avoid

#### Pitfall 1: Scope Creep in Briefing

**Bad:**
```markdown
Build NBA scraper. Also add dashboard. And authentication.
And maybe predictions. Make it look nice.
```

**Good:**
```markdown
Build NBA scraper ONLY. Dashboard is separate task.
Out of scope: UI, auth, predictions, database.
```

**Why:** Sub-agents work best with focused deliverables. One thing well > many things poorly.

---

#### Pitfall 2: Assuming Context Sharing

**Bad:**
```markdown
Make it funnier (expects sub-agent to know what "it" is)
```

**Good:**
```markdown
Revise ~/clawd/jokes.md to add more puns and wordplay.
Context: Ross found current version too dry.
```

**Why:** Sub-agents don't see conversation history. Be explicit.

---

#### Pitfall 3: Vague Success Criteria

**Bad:**
```markdown
SUCCESS: Code works well and is clean
```

**Good:**
```markdown
SUCCESS:
1. Passes `python -m pytest tests/`
2. Runs in <5 seconds on 1000-row dataset
3. Pylint score >8.0
4. All functions have docstrings
```

**Why:** Testable criteria prevent "looks good to me" syndrome.

---

#### Pitfall 4: Under-Specifying Output Format

**Bad:**
```markdown
DELIVERABLE: Some kind of data file with the results
```

**Good:**
```markdown
DELIVERABLE: ~/clawd/data/results.json
Format: {"timestamp": "ISO8601", "results": [{...}]}
Example: {"timestamp": "2026-01-30T12:00:00Z", "results": [{"id": 1, "score": 95}]}
```

**Why:** Sub-agent shouldn't guess formats. Show, don't tell.

---

#### Pitfall 5: No Error Handling Requirements

**Bad:**
```markdown
DELIVERABLE: Script that fetches data from API
```

**Good:**
```markdown
DELIVERABLE: Script that fetches data from API
- Retry 3x with exponential backoff on network errors
- Log failures to ~/clawd/logs/api_errors.log
- Exit code 0 on success, 1 on failure
- Graceful degradation if API returns partial data
```

**Why:** Production code needs error handling. Specify or it won't happen.

---

### Token Optimization Strategies

#### Strategy 1: Minimal Context Files

**Don't include:**
- Entire `MEMORY.md` (can be 10K+ tokens)
- Full conversation transcripts
- Unrelated project files

**Do include:**
- Relevant snippets from docs
- Specific examples
- Schema definitions

**Savings:** 5K-20K tokens per spawn

---

#### Strategy 2: Reference vs. Inline

**Instead of inlining 1000 lines of example code:**
```markdown
RESOURCES:
- Read: ~/clawd/examples/similar_scraper.py
- Reference: Structure and error handling approach
```

**Sub-agent loads file itself, you don't pay to send it in brief.**

**Savings:** 2K-10K tokens per spawn

---

#### Strategy 3: Incremental Tasking

**Bad (one massive task):**
```markdown
Build entire system: scraper + DB + API + frontend (80K tokens)
```

**Good (sequential sub-agents):**
```markdown
Task 1: Scraper (10K tokens)
Task 2: Database schema (8K tokens)  ← references scraper output
Task 3: API (12K tokens)             ← references DB schema
Task 4: Frontend (15K tokens)        ← references API
```

**Total:** 45K tokens vs. 80K (saves 35K)
**Bonus:** Each task builds on verified prior work

---

#### Strategy 4: Template Reuse

**Create task templates for common patterns:**
```markdown
~/clawd/templates/
  scraper-task.md
  documentation-task.md
  data-processing-task.md
```

**Fill in specifics, reference template:**
```markdown
Follow ~/clawd/templates/scraper-task.md structure.
Specifics: Target=ESPN NBA, Output=JSON, Cron=daily
```

**Savings:** 1K-3K tokens per spawn, plus consistency

---

### Coordination Overhead Management

#### When Overhead Outweighs Benefit

**Red flags:**
- Task takes 10 min, briefing takes 15 min
- Tight coupling (sub-agent needs 5+ round trips for questions)
- Rapidly changing requirements (brief obsolete before sub-agent finishes)
- Critical path item (you're blocked waiting for sub-agent)

**Solution:** Just build it yourself.

---

#### Parallel Sub-Agent Coordination

**Scenario:** Need scraper + database schema + API simultaneously.

**Bad Approach:**
- Spawn all 3 at once
- They conflict on shared files
- Integration nightmare

**Good Approach:**
- Define interfaces first (API contracts)
- Spawn sub-agents with clear boundaries
- Use separate directories/files
- Integrate serially

**Example:**
```markdown
Sub-Agent 1: Scraper → outputs data/nba_raw.json
Sub-Agent 2: Schema  → reads data/nba_raw.json, creates db/schema.sql
Sub-Agent 3: API     → reads db/schema.sql, creates api/server.py
```

Each references prior output as **read-only**. No conflicts.

---

#### Progress Checkpoints

**For long tasks (>1 hour), add checkpoints:**

```markdown
DELIVERABLE:
- Checkpoint 1 (30 min): Data model sketch → ~/clawd/wip/model.md
- Checkpoint 2 (60 min): Working prototype → ~/clawd/wip/prototype.py
- Final (90 min): Polished script → ~/clawd/scripts/final.py

Report completion of each checkpoint.
```

**Benefit:** Can catch issues at 30 min instead of 90 min.

---

## 6. Examples & Case Studies

### Scenario 1: Web Scraper

**Task:** Build a scraper for ESPN NBA standings.

**Recommendation:** ✅ **Use Sub-Agent**

**Why:**
- Self-contained deliverable (one script)
- Well-defined output (JSON with specific schema)
- 30-60 min effort
- No conversational context needed
- Can test independently

**Briefing Highlights:**
- Include example ESPN URL
- Specify exact JSON schema
- Require error handling
- Set performance target (<10 sec)

**Outcome:** Sub-agent delivers working scraper, Jarvis tests and integrates.

---

### Scenario 2: "Make This Funnier"

**Task:** Ross says "make this funnier" about a draft message.

**Recommendation:** ❌ **Build Directly**

**Why:**
- Needs conversational context (what is "this"?)
- Subjective criteria (Ross's sense of humor)
- Quick task (<5 min)
- Likely iteration (Ross may want tweaks)

**What Jarvis Does:**
- Read referenced message
- Add jokes/puns based on Ross's humor profile
- Show Ross immediately
- Iterate based on feedback

**Outcome:** Faster, better result than briefing a sub-agent.

---

### Scenario 3: Security Documentation

**Task:** Create comprehensive SECURITY.md documentation.

**Recommendation:** ✅ **Use Sub-Agent**

**Why:**
- Large deliverable (1000+ lines)
- Well-defined structure (can template)
- Research component (OWASP references)
- 2-3 hour effort
- Self-contained (one markdown file)

**Briefing Highlights:**
- Reference AGENTS.md and TOOLS.md for consistency
- Specify required sections
- Include 5+ concrete examples
- Set tone (professional but accessible)

**Outcome:** Sub-agent delivers draft, Jarvis reviews for accuracy, Ross approves.

---

### Scenario 4: Quick File Search

**Task:** "Find all references to 'NBA' in memory files."

**Recommendation:** ❌ **Build Directly**

**Why:**
- Single command (`grep -r "NBA" ~/clawd/memory/`)
- Results in <5 seconds
- No deliverable to review
- Immediate need

**What Jarvis Does:**
```bash
grep -r "NBA" ~/clawd/memory/ | head -20
```
Return results to Ross immediately.

**Outcome:** Task done in 10 seconds vs. 2 min to spawn sub-agent.

---

### Scenario 5: Data Pipeline (ETL)

**Task:** Extract data from 3 APIs, transform to common schema, load into SQLite.

**Recommendation:** ✅ **Use Sub-Agent**

**Why:**
- Multi-step process (extract, transform, load)
- Well-defined inputs/outputs
- 60-90 min effort
- Self-contained (one script + data files)
- Testable (verify output data)

**Briefing Highlights:**
- Specify all 3 API endpoints
- Define target schema explicitly
- Require test data generation
- Include error handling for each API

**Outcome:** Sub-agent builds pipeline, Jarvis tests with sample data.

---

### Scenario 6: "Fix This Bug"

**Task:** Ross reports a bug in existing script.

**Recommendation:** ⚠️ **Usually Build Directly**

**Why:**
- Needs understanding of existing code
- Often requires debugging (interactive)
- May need Ross clarification
- Quick fix possible (<15 min)

**Exception - Use Sub-Agent If:**
- Bug is in complex subsystem
- Fix requires refactoring (>30 min)
- Clear reproduction steps available
- Ross doesn't need immediate fix

**What Jarvis Does:**
1. Reproduce bug
2. If quick fix: Do it immediately
3. If complex: Delegate to sub-agent with full context

**Outcome:** Context-dependent decision.

---

### Scenario 7: Dashboard Prototype

**Task:** Build interactive dashboard for NBA data visualization.

**Recommendation:** ✅ **Use Sub-Agent** (but scope carefully)

**Why:**
- Substantial effort (2-4 hours)
- Clear deliverable (HTML + JS files)
- Can specify framework (e.g., Chart.js)
- Self-contained frontend

**Briefing Highlights:**
- Specify data source (JSON file location)
- Include wireframe/mockup if available
- Require responsive design
- Define browser compatibility

**Outcome:** Sub-agent builds prototype, Jarvis reviews functionality, Ross provides design feedback.

---

### Scenario 8: Refactoring Existing Code

**Task:** Refactor 500-line script to be more modular.

**Recommendation:** ⚠️ **Usually Build Directly**

**Why:**
- Requires deep understanding of existing logic
- High risk of breaking functionality
- Subjective decisions (how to modularize)
- Needs testing against existing behavior

**Exception - Use Sub-Agent If:**
- Clear refactoring pattern (e.g., "extract functions >50 lines")
- Comprehensive tests exist
- Refactoring is mechanical (not architectural)

**What Jarvis Does:**
- If simple: Refactor directly with version control
- If complex: Break into phases, maybe delegate Phase 2+

**Outcome:** Usually hands-on task for main agent.

---

### Scenario 9: Research + Summary

**Task:** "Research best practices for LLM prompt injection defense and summarize."

**Recommendation:** ✅ **Use Sub-Agent**

**Why:**
- Research takes time (web searches, reading)
- Clear deliverable (summary document)
- 60-90 min effort
- Self-contained (no integration)
- Objective criteria (coverage of topic)

**Briefing Highlights:**
- Specify summary length (e.g., 2-3 pages)
- Require 5+ sources
- Include practical examples
- Format: Markdown with sections

**Outcome:** Sub-agent researches and writes summary, Jarvis reviews for accuracy.

---

### Scenario 10: Cron Job Setup

**Task:** Set up a cron job to run NBA scraper daily at 6 AM.

**Recommendation:** ❌ **Build Directly**

**Why:**
- Simple task (one crontab entry)
- 2-3 min effort
- Requires testing (verify cron syntax)
- Interactive (may need to adjust timing)

**What Jarvis Does:**
```bash
crontab -l > /tmp/cron.bak
echo "0 6 * * * /Users/clawdbot/clawd/scripts/nba_rankings.py >> /Users/clawdbot/clawd/logs/cron.log 2>&1" >> /tmp/cron.bak
crontab /tmp/cron.bak
```
Confirm with Ross immediately.

**Outcome:** Done in 30 seconds, no sub-agent overhead.

---

## Summary: Quick Reference

### ✅ Great Sub-Agent Tasks
- Documentation creation
- Web scrapers / data collectors
- Prototypes / scaffolding
- Research + summary
- Data processing pipelines
- Self-contained features
- Parallel workstreams

### ❌ Poor Sub-Agent Tasks
- Quick edits (<15 min)
- "Make it better" (needs context)
- Debugging (interactive)
- Refactoring (high risk)
- Time-critical (<5 min deadline)
- Tightly coupled changes
- Exploratory work (fuzzy requirements)

### 🎯 Decision in 10 Seconds

**Ask:**
1. Is it self-contained? (Yes = +1)
2. Will it take >30 min? (Yes = +1)
3. Are requirements clear? (Yes = +1)
4. Is it time-critical? (Yes = -1)
5. Needs conversation context? (Yes = -1)

**Score ≥2:** Use sub-agent
**Score <2:** Build directly

---

## Appendix: Sub-Agent Command Reference

### Spawn Sub-Agent (CLI)
```bash
clawdbot agent spawn \
  --label "Descriptive Task Name" \
  --brief ~/clawd/briefs/task.md \
  --session main \
  --forward-to telegram:8412148376  # Optional: transparent mode
```

### List Active Sub-Agents
```bash
clawdbot agent list
```

### Check Sub-Agent Status
```bash
clawdbot agent status <agent-id>
```

### Terminate Sub-Agent
```bash
clawdbot agent kill <agent-id>
```

---

**End of Protocol** | Version 1.0 | 2026-01-30
