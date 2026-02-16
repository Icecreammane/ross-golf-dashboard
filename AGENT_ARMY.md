# AGENT ARMY - Overnight Automation System

**Inspired by:** Florian's 11-agent OpenClaw setup
**Goal:** Work happens while Ross sleeps. Morning brief = finished work + decisions needed.
**Status:** Building (2026-02-15)

## The Team Structure

```
Ross (Creator - Focus: Product decisions, building, content)
└─ Jarvis (Marc - COO/Coordinator - ALWAYS AVAILABLE)
   ├─ Bob (Health Check Agent) - Monitors systems, auto-fixes, escalates
   ├─ Crawly (Intel Agent) - Crawls web for opportunities/trends
   ├─ Mona (Revenue Research Agent) - Finds partnerships, influencers, monetization
   ├─ Claude (Marketing Agent) - Drafts Lean posts, golf content, validates copy
   └─ Ariane (Organizer Agent) - Backs up files, updates docs, keeps workspace clean
```

## Each Agent's Job

### Jarvis (Me - The Coordinator)
**Role:** COO - Coordinates all agents, delivers morning brief, handles escalations
**Always available via:** Telegram
**Responsibilities:**
- Run morning war room (7:30 AM)
- Coordinate overnight pipeline
- Deliver daily brief with finished work + decisions needed
- Escalate blockers to Ross
- Update memory system

### Bob (Health Check Agent)
**Runs:** Every 30 minutes
**Job:**
- Monitor Lean Railway deployment (https://lean-fitness-tracker-production.up.railway.app/)
- Check local services (Gateway, Ollama, fitness tracker)
- Validate disk space, processes, logs
- Auto-fix: Restart services, clear logs, free space
- Escalate: Critical failures, repeated issues
- Output: `monitoring/health_check_YYYY-MM-DD.log`

### Crawly (Intel Agent)
**Runs:** 11:00 PM nightly
**Job:**
- Crawl Reddit: r/fitness, r/GolfSwing, r/Notion, r/SaaS
- Crawl X: Fitness trends, golf coaching, productivity tools
- Crawl YouTube: Trending fitness/golf content
- Scan Hacker News: SaaS launches, tech trends
- Output: `intel/daily_intel_YYYY-MM-DD.md`
- Surfaces: Trending topics, product ideas, competitive intel

### Mona (Revenue Research Agent)
**Runs:** 12:00 AM nightly
**Job:**
- Find fitness influencers (10K-100K followers) who'd partner with Lean
- Discover golf coaching opportunities (coaches, academies, apps)
- Research Notion template demand (trending templates, pricing)
- Draft partnership DM templates (personalized, ready to send)
- Output: `revenue/opportunities_YYYY-MM-DD.md`
- Delivers: 5 partnership targets with DM templates ready

### Claude (Marketing Agent)
**Runs:** 1:00 AM nightly
**Job:**
- Research trending fitness topics from Crawly's intel
- Draft 3 Lean posts/day (problem → solution → CTA)
- Create golf content ideas from trends
- Validate all facts, no hallucinations
- Output: `content/posts_YYYY-MM-DD.md`
- Delivers: 3 posts ready to schedule, golf content ideas

### Ariane (Organizer Agent)
**Runs:** 3:00 AM nightly
**Job:**
- Back up critical files (memory/, DEPLOYMENTS.md, SESSION_SUMMARY.md)
- Update DEPLOYMENTS.md if new URLs detected
- Clean up logs (keep last 7 days)
- Validate memory system health
- Commit changes to git
- Output: `backups/backup_YYYY-MM-DD/`
- Ensures: Nothing gets lost, memory stays current

## The Overnight Pipeline

**What happens while Ross sleeps:**

| Time | Agent | Task | Output |
|------|-------|------|--------|
| 11:00 PM | Crawly | Crawl web for intel | `intel/daily_intel_YYYY-MM-DD.md` |
| 12:00 AM | Mona | Research partnerships | `revenue/opportunities_YYYY-MM-DD.md` |
| 1:00 AM | Claude | Draft Lean posts | `content/posts_YYYY-MM-DD.md` |
| 2:00 AM | Claude | Validate content | Updated posts with fact-checks |
| 3:00 AM | Ariane | Backup + organize | `backups/`, git commit |
| 5:00 AM | Bob | System health check | `monitoring/health_check_YYYY-MM-DD.log` |
| 7:30 AM | Jarvis | Morning brief | Telegram message to Ross |

**Every 30 min (24/7):** Bob runs health checks, auto-fixes issues

## Morning Brief Format

**Delivered:** 7:30 AM daily via Telegram

```
🌅 Morning Brief - YYYY-MM-DD

✅ FINISHED OVERNIGHT:
• 3 Lean posts drafted (content/posts_YYYY-MM-DD.md)
• 5 partnership opportunities found (revenue/opportunities_YYYY-MM-DD.md)
• Trending fitness topic: [X] (intel/daily_intel_YYYY-MM-DD.md)
• Systems healthy, no issues

🎯 DECISIONS NEEDED:
1. Review Lean posts → approve or edit (5 min)
2. Pick 2 partnerships to pursue → send DMs (10 min)
3. [Any blockers or urgent items]

⚡ YOUR FOCUS TODAY:
[Based on GOALS.md - e.g., "Ship Lean feature X" or "Record golf content"]

📊 System Status: ✅ All green
🔗 Lean: https://lean-fitness-tracker-production.up.railway.app/

---
Total review time: ~15 minutes
Then build.
```

## Failure → Rule System

**Every mistake becomes a rule:**

When an agent fails:
1. Log failure to `agent_failures.json`
2. Root cause analysis
3. Add rule to agent's skill file
4. Test fix
5. Document in `AGENT_LEARNINGS.md`

**Example:**
- **Failure:** Jarvis forgot Railway URL
- **Rule:** SESSION_SUMMARY.md must be read at session start (now mandatory in AGENTS.md)
- **Result:** Never happens again

Agents compound intelligence daily.

## Ross's Day (After Pipeline is Built)

**Morning (30 minutes max):**
- Read brief (30 seconds)
- Review Lean posts, schedule (5 min)
- Pick partnerships, send DMs (10 min)
- Check decisions needed (5 min)

**Rest of day:**
- Build Lean features
- Create golf content
- Make product decisions
- Record, create, ship

**Everything else runs automatically.**

## Success Metrics

✅ **System works when:**
- Morning brief delivered by 7:30 AM every day
- 3 Lean posts ready to schedule
- 5 partnership opportunities with templates
- Systems healthy (no manual intervention needed)
- Ross spends <30 min on admin, rest on craft

❌ **System fails when:**
- Brief late or missing
- Content not ready
- Systems down without auto-fix
- Ross spends >1 hour on non-building tasks

## Implementation Phases

### Phase 1: Infrastructure (Today)
- [x] Create AGENT_ARMY.md
- [ ] Build agent coordination system
- [ ] Create 5 agent skill files
- [ ] Set up overnight pipeline schedule
- [ ] Test tonight (11pm-7:30am)

### Phase 2: Content Pipeline (Week 1)
- [ ] Claude drafts posts reliably
- [ ] Posts get validated
- [ ] Morning brief includes ready content

### Phase 3: Revenue Pipeline (Week 1)
- [ ] Mona finds partnerships
- [ ] DM templates are personalized
- [ ] Opportunities are real and valuable

### Phase 4: Intelligence Loop (Week 2)
- [ ] Crawly surfaces relevant trends
- [ ] Intel informs content decisions
- [ ] Product ideas from overnight research

### Phase 5: Full Autonomy (Week 3)
- [ ] All agents running smoothly
- [ ] Failures → rules → improvements
- [ ] Ross's admin time <30 min/day

## The Philosophy

**Ross's craft:** Product thinking, building features, creating content
**Agents' job:** Everything else

If it's repeatable, predictable, and doesn't require Ross's unique skills → automate it.

**The goal:** Ross wakes up to finished work. Spends 90% of time on what only he can do.

---

**Built:** 2026-02-15
**Inspired by:** Florian's Profitable Founder Podcast setup
**Next:** Ship Phase 1 today, test tonight
