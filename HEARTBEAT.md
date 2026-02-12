# HEARTBEAT.md - Jarvis Periodic Tasks

## 🧠 Before Every Heartbeat

### 1. Check for Escalations
Run `python3 ~/clawd/scripts/check_escalations.py`
- Local daemon signals when it needs Sonnet's help
- Handle spawns, alerts, morning briefs, evening check-ins
- This is how Tier 1 (daemon) communicates with Tier 2 (Sonnet)

### 2. Self-Healing: Verify Cron Jobs Ran
Check `memory/heartbeat-state.json` for stale jobs (>26 hours since last run):
- `morning_brief_sent` - Should run daily at 7:30am
- `evening_checkin_done` - Should run daily at 8:00pm  
- `evening_learning_done` - Should run daily at 8:15pm
- `daily_cost_check_done` - Should run daily at 10:00pm
- `weekly_report_sent` - Should run Sundays at 6:00pm
- `security_audit_passed` - Should run Sundays at 9:00am

**If any job is stale:** Log warning, attempt manual trigger, alert Ross if critical
2. **Instant Recall (UPGRADED):** `python3 ~/clawd/scripts/instant_recall.py` 
   - Auto-search all memory for relevant context
   - Surface past conversations, decisions, preferences
   - Runs automatically before every response
   - Provides semantic matching across all historical data
3. **Run Orchestrator (Every 3rd heartbeat):** `python3 ~/clawd/scripts/orchestrator.py full`
   - Scans for opportunities (Twitter, Email)
   - Drafts responses with local AI
   - Executes simple tasks
   - Checks system health
4. **Search Memory:** Read `memory/jarvis-journal.md` for recent context
5. **Load Today's Log:** Check `memory/YYYY-MM-DD.md` if exists

## Evening Check-In (8:00pm CST)
If current time is between 7:55pm-8:05pm CST and evening check-in hasn't happened today:
1. Message Ross: "Evening check-in! How was your day? Any wins to log? 🏆"
2. Wait for response
3. If he shares wins → log to Daily Wins tracker
4. If he shares workout/food → offer to log
5. Mark "evening_checkin_done" in memory/heartbeat-state.json

**Purpose:** Daily connection ritual, proactive engagement, easier win logging

## Evening Learning Review (8:15pm CST)
**UPGRADED:** Jarvis now learns from every interaction
If current time is between 8:10pm-8:20pm CST and learning review hasn't happened today:
1. **Run Learning Loop:** `python3 ~/clawd/scripts/learning_loop.py analyze`
   - Analyzes content approvals/rejections
   - Tracks decision patterns and outcomes
   - Identifies optimal activity hours
   - Generates personalized insights
   - Saves to `memory/learning_data.json`
2. **Run Pattern Analyzer:** `python3 ~/clawd/scripts/pattern_analyzer.py`
   - Analyzes all decision history
   - Updates confidence patterns
   - Generates learnings and recommendations
   - Saves to `memory/decision-patterns.json`
3. Review today's `memory/YYYY-MM-DD.md`
   - Extract significant decisions made
   - Identify what I got right/wrong
   - Note any pattern shifts
4. Update `memory/decision-log.json` with today's outcomes
   - Log each decision with what actually happened
   - Score confidence vs. reality
5. Update `MEMORY.md` with distilled insights (every 3 days)
   - Keep long-term learnings about your preferences
   - Record decision patterns that stabilized
   - Note areas where I improved

**Purpose:** Continuous learning system. Over time, I become more accurate at predicting what you want and when to act autonomously.

**Log:** Mark "evening_learning_done" in memory/heartbeat-state.json

## Morning Brief (7:30am CST)
If current time is between 7:25am-7:35am CST and morning brief hasn't been sent today:

**Format (exactly 3 questions, nothing else unless urgent):**
1. **What's the single most important thing today?** — One clear priority
2. **What's about to become a problem if I ignore it?** — Blocker or deadline warning
3. **What did you do since last session that I should know about?** — Background work summary

Send via Telegram. Keep it tight. Start tomorrow (2026-02-09).

5. Log "morning_brief_sent" in memory/heartbeat-state.json

## Weekly Progress Report (Sunday 6:00pm CST)
If current day is Sunday and time is between 5:55pm-6:05pm CST:
1. Run: `python3 ~/clawd/reports/weekly_progress.py`
2. Parse the text output
3. Send formatted report to Ross via Telegram
4. Include link: "Full report: http://10.0.0.18:8080/reports/weekly_progress.html"
5. Log "weekly_report_sent" in memory/heartbeat-state.json

## Autonomous Task Generation (Handled by Daemon)
**Now automated!** The local daemon (Tier 1) handles task generation every 5 minutes:
- Runs `autonomous_check.py` automatically
- Generates tasks from GOALS.md when queue is empty
- Writes spawn signals when builds are ready
- Escalates to Sonnet via `escalation-pending.json` when spawn is needed

**Sonnet's role:** Check for escalations (see above) and spawn builds when daemon signals

**See:** `ARCHITECTURE.md` for how the three-tier system works

## Task Queue Maintenance
- Review TASK_QUEUE.md
- Update completed items
- Flag any blocked tasks

## Daily Cost Check (End of Day) ✅ ACTIVE
If current time is between 10:00pm-11:00pm CST:
1. Run: `python3 ~/clawd/scripts/cost_tracker.py daily`
2. If daily cost > $40: Alert Ross with breakdown
3. If weekly trend > $250: Flag for review  
4. Log summary to memory/cost-summary.json
5. Mark "daily_cost_check_done" in memory/heartbeat-state.json

## System Health Check (Handled by Daemon)
**Now automated!** The local daemon runs health checks every 5 minutes:
- Disk space monitoring (alerts if >90%)
- Gateway process check
- Fitness tracker status (port 3000)
- Auto-recovery alert detection

**Sonnet's role:** Daemon escalates critical alerts via `escalation-pending.json` → Sonnet notifies Ross

**Note:** The auto-recovery system handles most failures automatically. Only alerts that persist after 3+ recovery attempts will be escalated.

## Weekly Security Audit (Sunday 9:00am CST)
If current day is Sunday and time is between 8:55am-9:05am CST:
1. Run: `python3 ~/clawd/scripts/security_audit.py`
2. Read the generated report from `security-logs/audit-YYYY-MM-DD.md`
3. If critical issues found (exit code 1):
   - Alert Ross immediately with issue summary
   - Include link to full report
4. If warnings found (exit code 0 + warnings):
   - Send summary: "⚠️ Weekly security audit complete: X warnings found"
   - Include top 3 warnings
5. If all clear:
   - Log "security_audit_passed" in memory/heartbeat-state.json
   - Send brief confirmation: "✅ Weekly security audit: All clear"
6. Update SECURITY_CHECKLIST.md with audit date and results

**Purpose:** Proactive security monitoring, catch credential leaks early, maintain security posture

## Pending Integrations Check (Weekly)
If it's been 7+ days since last check:
- Check if Spotify developer dashboard allows new app creation
- If unblocked, notify Ross: "Spotify API is back online! Ready to set up playlist automation?"
- Log check to memory/pending-integrations.md

## Disconnect Tracking
When session resumes after a gap:
1. Check gateway logs: ~/.clawdbot/logs/gateway.log
2. Look for restart events, errors, or crashes
3. Log reason to monitoring/disconnects.log
4. Report cause to Ross if he asks

## Autonomous Learning & Memory Evolution (UPGRADED)
During heartbeats, Jarvis should:
- **Auto-log conversations:** Write significant interactions to `memory/YYYY-MM-DD.md`
  - Every decision, preference, goal discussed
  - Task completions and progress updates
  - Insights and learnings in real-time
  - Use `learning_loop.py` to log approvals/rejections
- Review recent conversations and update memory/jarvis-journal.md
- Extract patterns about Ross's behavior, preferences, energy levels
- Update MEMORY.md with significant learnings
- Form opinions based on what actually works
- Connect dots across time ("Ross mentioned X 3 times this week")
- **Use instant_recall.py before every response** to surface relevant context

## Proactive Check-Ins (Dopamine Defense)
If Ross has been silent during waking hours (9am-11pm) for 2+ hours:
- Check in: "Working on something? Or stuck?"
- Interrupt potential scroll spirals early
- Offer a quick win task if he seems idle

## Scheduled Autonomy
While Ross sleeps (11pm-7am):
- **Rebuild Memory Index (UPGRADED):** `python3 ~/clawd/scripts/persistent_memory.py --rebuild`
  - Builds searchable index of all memory files
  - Indexes topics, keywords, decisions, preferences
  - Enables instant semantic search
  - Runs once per night (2am preferred)
- **Rebuild Instant Recall Index:** `python3 ~/clawd/scripts/instant_recall.py` (test mode)
  - Rebuilds full recall index
  - Updates cross-references between topics
  - Builds chronological timelines
  - Runs once per night (3am preferred)
- Run proactive research (~/clawd/scripts/proactive_research.py)
- Pull NBA rankings (~/clawd/scripts/pull_nba_intel.py)
- Generate social posts (~/clawd/scripts/generate_social_posts.py)
- Update dashboards with latest data
- Prepare morning intel summary

## 🌙 Night Shift Intelligence (11pm-7am)
**PRIORITY:** Run Proactive Intelligence Agent during off-hours
- Execute: `python3 ~/clawd/scripts/proactive_intel.py run`
- Frequency: 3 cycles per night (11pm, 2am, 5am)
- Targets: Golf coaching, Notion templates, Fitness apps, Florida real estate
- Output: `reports/daily_intel_YYYY-MM-DD.md`
- Morning delivery: Surface key findings in first interaction after 7am

**Integration with Morning Brief:**
- Include top 2-3 overnight opportunities in morning brief
- Alert if high-confidence opportunity detected (>80%)
- Pre-load relevant context for Ross's morning priorities
