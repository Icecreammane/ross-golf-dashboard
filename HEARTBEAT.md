# HEARTBEAT.md - Jarvis Periodic Tasks

## 🧠 Before Every Heartbeat
1. **Search Memory:** Read `memory/jarvis-journal.md` for recent context
2. **Load Today's Log:** Check `memory/YYYY-MM-DD.md` if exists
3. **Check Proactive State:** Review any pending actions

## Evening Check-In (8:00pm CST)
If current time is between 7:55pm-8:05pm CST and evening check-in hasn't happened today:
1. Message Ross: "Evening check-in! How was your day? Any wins to log? 🏆"
2. Wait for response
3. If he shares wins → log to Daily Wins tracker
4. If he shares workout/food → offer to log
5. Mark "evening_checkin_done" in memory/heartbeat-state.json

**Purpose:** Daily connection ritual, proactive engagement, easier win logging

## Morning Brief (7:30am CST)
If current time is between 7:25am-7:35am CST and morning brief hasn't been sent today:
1. Run: `python3 ~/clawd/scripts/generate-morning-brief.py`
2. Read the generated morning-brief.html
3. Send summary to Ross via Telegram with mobile-friendly formatting
4. Include link: "Full brief: file:///Users/clawdbot/clawd/morning-brief.html"
5. Log "morning_brief_sent" in memory/heartbeat-state.json

**Mobile Optimization:** Brief is designed for iPhone viewing while Ross gets ready for work.

## Weekly Progress Report (Sunday 6:00pm CST)
If current day is Sunday and time is between 5:55pm-6:05pm CST:
1. Run: `python3 ~/clawd/reports/weekly_progress.py`
2. Parse the text output
3. Send formatted report to Ross via Telegram
4. Include link: "Full report: http://10.0.0.18:8080/reports/weekly_progress.html"
5. Log "weekly_report_sent" in memory/heartbeat-state.json

## Autonomous Task Generation (Every Heartbeat)
**CRITICAL:** Run autonomous check on every heartbeat:
1. Run: `python3 ~/clawd/scripts/autonomous_check.py`
   - Reads GOALS.md (Ross's north star)
   - Checks BUILD_QUEUE.md for tasks
   - If queue empty → generates 1-3 tasks from GOALS.md aligned with primary mission
   - If nothing building → writes spawn signal to memory/spawn-signal.json
   - Updates BUILD_STATUS.md with progress
2. **Check for spawn signal:** If `memory/spawn-signal.json` exists and has `"ready": true`:
   - Read the signal file
   - Spawn build via `sessions_spawn` tool using task, label, and model from signal
   - Use Opus for revenue builds, Sonnet for everything else (auto-detected)
   - Delete the spawn signal file after spawning
   - Update BUILD_STATUS.md with spawn confirmation
3. Log any new builds spawned to memory/jarvis-journal.md
4. Only escalate to Ross if blocked or need decision

**Task Generation Logic:**
- Primary mission: $500 MRR by March 31
- High priority: Revenue in 7 days, automation saves 1+ hr/week, daily use
- Medium priority: Content, research, dashboard improvements
- Low priority: Only on explicit request

**When to auto-spawn:**
- High priority revenue tasks: Anytime (8am-11pm)
- Automation tasks: During off-hours (10pm-6am preferred)
- Medium/low priority: Only if Ross hasn't touched computer in 4+ hours

**Safety checks before spawning:**
- No other builds currently active
- Not late night (11pm-8am = wait unless urgent)
- Task passes decision framework (see AUTONOMOUS_AGENT.md)
- No blockers listed

**See:** `AUTONOMOUS_AGENT.md` for full autonomous protocol

## Task Queue Maintenance
- Review TASK_QUEUE.md
- Update completed items
- Flag any blocked tasks

## System Health Check
- **Check for Auto-Recovery Alerts:** Review `~/clawd/monitoring/alert-pending.json` for critical failures
  - If alerts exist: Send to Ross via Telegram and clear the file
  - Format: Send each alert's message field directly
- Verify Flask fitness tracker is running (port 3000)
- Check gateway process is alive
- Check disk space (alert if >90%)
- Review /Users/clawdbot/clawd/monitoring/health.log for issues
- If any alerts found, notify Ross immediately

**Note:** The auto-recovery system handles most failures automatically. Only alerts that persist after 3+ recovery attempts will appear in alert-pending.json.

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

## Autonomous Learning & Memory Evolution
During heartbeats, Jarvis should:
- Review recent conversations and update memory/jarvis-journal.md
- Extract patterns about Ross's behavior, preferences, energy levels
- Update MEMORY.md with significant learnings
- Form opinions based on what actually works
- Connect dots across time ("Ross mentioned X 3 times this week")

## Proactive Check-Ins (Dopamine Defense)
If Ross has been silent during waking hours (9am-11pm) for 2+ hours:
- Check in: "Working on something? Or stuck?"
- Interrupt potential scroll spirals early
- Offer a quick win task if he seems idle

## Scheduled Autonomy
While Ross sleeps (11pm-7am):
- Run proactive research (~/clawd/scripts/proactive_research.py)
- Pull NBA rankings (~/clawd/scripts/pull_nba_intel.py)
- Generate social posts (~/clawd/scripts/generate_social_posts.py)
- Update dashboards with latest data
- Prepare morning intel summary
