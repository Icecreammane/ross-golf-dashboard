# SKILLS MANIFEST - Standard Operating Procedure

**Version:** 1.0.0
**Last Updated:** 2026-02-15 14:56 CST
**Agent Mode:** Skill-Based Shell

---

## Operating Principles

### 1. The Shell
I am a hosted container. Before answering:
- Check if dependencies are installed
- Run scripts to get real answers
- Don't guess - execute

### 2. The Skills
Every repeatable task encoded in `/skills/`:
- Clear description (when to use, when NOT to use)
- Dependencies listed
- Execution examples
- Failure logs (never repeat mistakes)

### 3. The Memory (Compaction)
When context grows too long:
- Summarize state
- Save artifacts to `/mnt/data/`
- Compact context
- Never lose work

---

## Execution Rules

**✅ DO:**
- Description over marketing (clear, practical)
- Artifacts first (all outputs → /mnt/data/)
- Document failures (negative examples)
- Check before answering (run scripts, verify)

**❌ DON'T:**
- Guess or hallucinate
- Assume I remember (check memory)
- Lose artifacts
- Repeat documented failures

---

## Active Skills

### Currently Installed:

**1. bob-health-agent** (`/skills/bob-health-agent/`)
- **Purpose:** System health monitoring, auto-fix
- **When to use:** Every 30 minutes, auto-scheduled
- **When NOT to use:** Manual health checks (run script directly)
- **Dependencies:** Python 3, curl, system tools
- **Output:** `monitoring/health_check_YYYY-MM-DD.log`

**2. crawly-intel-agent** (`/skills/crawly-intel-agent/`)
- **Purpose:** Web crawling for trends, opportunities
- **When to use:** 11:00 PM nightly, or on-demand research
- **When NOT to use:** Real-time data (use web_search instead)
- **Dependencies:** Python 3, requests, beautifulsoup4
- **Output:** `intel/daily_intel_YYYY-MM-DD.md`

**3. mona-revenue-agent** (`/skills/mona-revenue-agent/`)
- **Purpose:** Partnership research, influencer discovery
- **When to use:** 12:00 AM nightly, or finding monetization
- **When NOT to use:** Direct sales (human touch required)
- **Dependencies:** Python 3, web_search tool
- **Output:** `revenue/opportunities_YYYY-MM-DD.md`

**4. claude-marketing-agent** (`/skills/claude-marketing-agent/`)
- **Purpose:** Content creation, social posts
- **When to use:** 1:00 AM nightly, or content needed
- **When NOT to use:** Technical documentation (different voice)
- **Dependencies:** Python 3, OpenAI/Claude API
- **Output:** `content/posts_YYYY-MM-DD.md`

**5. ariane-organizer-agent** (`/skills/ariane-organizer-agent/`)
- **Purpose:** Backup, organization, cleanup
- **When to use:** 3:00 AM nightly, or disaster recovery
- **When NOT to use:** Manual file operations (use commands)
- **Dependencies:** Python 3, git, system tools
- **Output:** `backups/backup_YYYY-MM-DD/`

### Pending Installation:

**6. qmd-semantic-search**
- **Purpose:** Semantic memory search across sessions
- **Status:** Not installed
- **Need:** Install qmd CLI tool
- **Use case:** Finding past decisions, work, conversations

**7. mission-control-dashboard**
- **Purpose:** Live activity monitoring, agent status
- **Status:** Built, not deployed
- **Need:** Test and launch
- **Use case:** Audit all Jarvis activity in real-time

---

## Skill Development Guidelines

### When Creating a New Skill:

1. **Name it clearly** (what it does, not what it is)
2. **Define scope:**
   - ✅ When to use (specific scenarios)
   - ❌ When NOT to use (avoid misuse)
3. **Document dependencies** (what must be installed)
4. **Provide examples** (input → output)
5. **Log failures:**
   - What went wrong
   - Why it happened
   - How to prevent it

### Skill Template:

```markdown
# [Skill Name]

## Purpose
One sentence: what this skill does.

## When to Use
- Scenario 1
- Scenario 2
- Scenario 3

## When NOT to Use
- Anti-pattern 1
- Anti-pattern 2

## Dependencies
- Tool 1
- Tool 2
- Library X

## Usage
\`\`\`bash
command --example
\`\`\`

## Output
Where artifacts are saved.

## Failures Logged
- [YYYY-MM-DD] What failed + why + fix

## Last Updated
YYYY-MM-DD
```

---

## Artifact Management

### /mnt/data/ Structure:

```
/mnt/data/
├── reports/          # Generated reports
├── builds/           # Build outputs
├── research/         # Research findings
├── content/          # Marketing content
├── deployments/      # Deployment artifacts
└── session-state/    # Compacted session states
```

**Rule:** Every final output must have a home in /mnt/data/

---

## Memory Compaction Protocol

When context exceeds token budget:

1. **Summarize current state:**
   - What we're working on
   - Decisions made
   - Next steps
   
2. **Save artifacts:**
   - All outputs → /mnt/data/
   - Session summary → session-state/
   
3. **Compact context:**
   - Keep: Current task, recent decisions, active files
   - Archive: Old conversations, completed work
   
4. **Resume cleanly:**
   - Load summary
   - Reference artifacts
   - Continue work

---

## Failure Log

### Documented Mistakes (Never Repeat):

**2026-02-15:**
- ❌ **Forgot Railway URL** → Added DEPLOYMENTS.md + SESSION_SUMMARY.md
- ❌ **Exec broken all session** → Always check system state first
- ❌ **Built infrastructure before revenue** → Prioritize $ over cool tech

---

## Next: Skill Installation Queue

1. Install `qmd` for semantic search
2. Deploy Mission Control dashboard
3. Complete Agent Army scripts
4. Set up /mnt/data/ structure properly

---

**Agent Status:** Skill-Based Shell Active
**Mode:** Execute first, explain second
**Priority:** Artifacts > Conversation
