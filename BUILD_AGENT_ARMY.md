# BUILD: Agent Army System - Overnight Automation

**Built:** 2026-02-15 08:55 AM - 09:30 AM (while Ross at coffee)
**Inspired by:** Florian's 11-agent OpenClaw setup (Profitable Founder Podcast)
**Goal:** Work happens while Ross sleeps → Morning brief = finished work + decisions needed

## What Got Shipped

### 1. **AGENT_ARMY.md** - Master Documentation
Complete system design:
- Team structure (5 agents + Jarvis as coordinator)
- Each agent's role and responsibilities
- Overnight pipeline schedule (11pm-7:30am)
- Morning brief format
- Success metrics
- Implementation phases

### 2. **5 Agent Skill Files** (Like Florian's Team)

**Bob - Health Check Agent** (`skills/bob-health-agent/SKILL.md`)
- Monitors: Lean production, local services, disk space, memory system
- Runs: Every 30 minutes (24/7)
- Auto-fixes: Restart services, clean logs, free space
- Escalates: Critical failures only
- Output: `monitoring/health_check_YYYY-MM-DD.log`

**Crawly - Intel Agent** (`skills/crawly-intel-agent/SKILL.md`)
- Crawls: Reddit (fitness/golf/notion/SaaS), X, YouTube, Hacker News
- Finds: Trending topics, product ideas, competitive intel
- Runs: 11:00 PM nightly
- Output: `intel/daily_intel_YYYY-MM-DD.md`
- Delivers: Top trends + opportunities by morning

**Mona - Revenue Research Agent** (`skills/mona-revenue-agent/SKILL.md`)
- Finds: Fitness influencers (10K-100K), golf coaches, Notion demand, sponsors
- Drafts: Personalized DM templates (ready to send)
- Runs: 12:00 AM nightly
- Output: `revenue/opportunities_YYYY-MM-DD.md`
- Delivers: 5 partnership targets with DMs ready

**Claude - Marketing Agent** (`skills/claude-marketing-agent/SKILL.md`)
- Drafts: 3 Lean posts/day for X/Instagram
- Creates: Golf content ideas from trends
- Validates: All facts (no hallucinations)
- Runs: 1:00 AM nightly
- Output: `content/posts_YYYY-MM-DD.md`
- Delivers: Posts ready to schedule

**Ariane - Organizer Agent** (`skills/ariane-organizer-agent/SKILL.md`)
- Backs up: Critical files (SESSION_SUMMARY, DEPLOYMENTS, memory logs)
- Cleans: Old logs, temp files, stale backups
- Updates: DEPLOYMENTS.md, documentation
- Commits: Changes to git
- Runs: 3:00 AM nightly
- Output: `backups/backup_YYYY-MM-DD/backup_log.md`

### 3. **Agent Coordinator** (`scripts/agent_coordinator.py`)
Jarvis as "Marc" (COO):
- Coordinates all agents
- Checks agent outputs
- Generates morning brief
- Reports status
- Handles escalations

Commands:
```bash
python3 scripts/agent_coordinator.py morning-brief  # Generate brief
python3 scripts/agent_coordinator.py status         # Check agents
python3 scripts/agent_coordinator.py run-pipeline   # Show schedule
```

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

**Every 30 min:** Bob runs health checks, auto-fixes issues

## Morning Brief Format

Ross wakes up to:

```
🌅 Morning Brief - YYYY-MM-DD

✅ FINISHED OVERNIGHT:
• 3 Lean posts drafted
• 5 partnership opportunities found
• Trending fitness topic surfaced
• Systems healthy

🎯 DECISIONS NEEDED:
1. Review Lean posts → approve or edit (5 min)
2. Pick 2 partnerships → send DMs (10 min)
3. [Any blockers]

⚡ YOUR FOCUS TODAY:
Build. Create. Ship.

📊 Review time: ~15 minutes
🔗 Lean: https://lean-fitness-tracker-production.up.railway.app/
```

## Ross's Day (After System is Live)

**Morning (30 minutes max):**
- Read brief (30 seconds)
- Review Lean posts, schedule (5 min)
- Pick partnerships, send DMs (10 min)
- Check decisions needed (5 min)

**Rest of day:**
- Build Lean features
- Create golf content
- Make product decisions
- Focus on craft

**Everything else runs automatically.**

## Key Insights from Florian's Setup

### 1. **Specialized Agents > General Assistant**
- Each agent has ONE job
- Clear ownership, clear output
- Easy to debug, easy to improve

### 2. **Overnight Pipeline = Leverage**
- Work happens while you sleep
- Wake up to finished work
- 8 hours of productivity, zero effort

### 3. **Morning Brief = Decision Layer**
- Don't wake up to questions ("What should we work on?")
- Wake up to options ("Here's what's ready, pick which to act on")
- Ross focuses on decisions only he can make

### 4. **Failure → Rule System**
- Every mistake becomes a documented rule
- Agents compound intelligence daily
- Never make the same mistake twice

### 5. **Quality > Quantity**
- 5 great opportunities > 20 mediocre ones
- 3 perfect posts > 10 decent posts
- Focus on what Ross will actually act on

## Implementation Status

### ✅ Phase 1: Infrastructure (COMPLETE)
- [x] AGENT_ARMY.md created
- [x] 5 agent skill files written
- [x] Agent coordinator built
- [x] Pipeline designed

### ⏳ Phase 2: Build Agent Scripts (Next)
- [ ] Bob's health check script
- [ ] Crawly's crawl script
- [ ] Mona's research script
- [ ] Claude's content script
- [ ] Ariane's backup script

### ⏳ Phase 3: Set Up Cron Jobs (Next)
- [ ] Bob: Every 30 minutes
- [ ] Crawly: 11:00 PM daily
- [ ] Mona: 12:00 AM daily
- [ ] Claude: 1:00 AM daily
- [ ] Ariane: 3:00 AM daily
- [ ] Jarvis brief: 7:30 AM daily

### ⏳ Phase 4: Test Tonight (Next)
- [ ] Run pipeline manually tonight
- [ ] Verify all outputs generated
- [ ] Test morning brief format
- [ ] Fix any issues found

### ⏳ Phase 5: Go Live Tomorrow (Goal)
- [ ] Pipeline runs automatically tonight
- [ ] Ross wakes to morning brief with finished work
- [ ] Iterate based on feedback

## Expected Impact

### Time Savings
**Before:** Ross spends 2-3 hours/day on:
- Research (finding influencers, trends, opportunities)
- Content creation (drafting posts, planning content)
- Admin (backups, organization, system checks)

**After:** Ross spends 15-30 minutes/day on:
- Reviewing finished work
- Making decisions (which partnerships, which posts)
- Acting on high-value opportunities

**Time saved:** 1.5-2.5 hours/day = 10-17 hours/week

### Revenue Impact
**More time for craft:**
- Build Lean features → more users → more revenue
- Create golf content → grow audience → more opportunities
- Design Notion templates → passive revenue

**Better opportunities:**
- Mona finds better partnerships (targeted, pre-qualified)
- Claude creates better content (trend-aware, validated)
- Crawly surfaces opportunities competitors miss

**Goal:** $500 MRR by March 31
**Strategy:** This system frees Ross to focus on revenue-generating work

## Success Metrics

✅ **System works when:**
- Morning brief delivered by 7:30 AM every day
- 3 Lean posts ready to schedule
- 5 partnership opportunities with templates
- Systems healthy (no manual intervention)
- Ross spends <30 min on admin/day

❌ **System fails when:**
- Brief late or missing
- Content not ready
- Systems down without auto-fix
- Ross spends >1 hour on non-building tasks

## Files Created

```
AGENT_ARMY.md                                  # Master doc
BUILD_AGENT_ARMY.md                            # This file
scripts/agent_coordinator.py                   # Coordinator
skills/bob-health-agent/SKILL.md              # Bob
skills/crawly-intel-agent/SKILL.md            # Crawly
skills/mona-revenue-agent/SKILL.md            # Mona
skills/claude-marketing-agent/SKILL.md        # Claude
skills/ariane-organizer-agent/SKILL.md        # Ariane
```

## Next Steps

1. **Today:** Build agent execution scripts
2. **Tonight:** Test pipeline manually
3. **Tomorrow morning:** Ross wakes to first automated brief
4. **Week 1:** Iterate based on output quality
5. **Week 2:** Expand agents (more intel sources, better content)
6. **Week 3:** Full autonomy (agents run perfectly, minimal intervention)

## The Philosophy

**Ross's craft:** Product thinking, building features, creating content
**Agents' job:** Everything else

If it's repeatable, predictable, and doesn't require Ross's unique skills → automate it.

**The goal:** Ross wakes up to finished work. Spends 90% of time on what only he can do.

---

**Built by:** Jarvis (while Ross was at coffee)
**Inspired by:** Florian's Profitable Founder Podcast setup
**Status:** Phase 1 complete, ready for Phase 2
**Next:** Build execution scripts + set up cron jobs
