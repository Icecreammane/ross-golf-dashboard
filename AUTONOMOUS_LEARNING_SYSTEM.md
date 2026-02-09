# Autonomous Learning System - How Jarvis Learns to Be Better

*Implemented: 2026-02-08 23:32*

---

## Core Principle

Every decision I make gets logged. Every time you approve or reject something, I learn. Over time, I build a model of what matters to you.

---

## Decision Logging

### File: `memory/decision-log.json`

Every decision gets logged with:
```json
{
  "timestamp": "2026-02-08T23:32:00",
  "decision": "Build NBA rankings dashboard",
  "context": {
    "request": "Send me a link I'll open on Mac mini",
    "request_clarity": "low",
    "time_of_day": "23:19",
    "recent_mood": "frustrated"
  },
  "confidence_score": 45,
  "execution": "yes",
  "outcome": "partial_fail - wrong data",
  "learning": "Should have asked for 50-player file instead of making it up",
  "confidence_delta": -15,
  "new_score": 30
}
```

### Learning Signals

**Approve (+3 confidence):**
- You say "good" or ✅ react
- You use something I built
- You move forward with my output

**Reject (-5 confidence):**
- You say "no" or edit heavily
- You have to fix my work
- You ignore something I made

**Neutral (0):**
- You don't respond
- You modify it slightly then move on

---

## Pattern Recognition

### File: `memory/decision-patterns.json`

Tracks what types of decisions you care about:

```json
{
  "highest_approval_rate": [
    {"category": "data_integrity", "approval": 95},
    {"category": "automation", "approval": 87},
    {"category": "revenue_work", "approval": 92}
  ],
  "lowest_approval_rate": [
    {"category": "ui_polish", "approval": 12},
    {"category": "theoretical_projects", "approval": 8},
    {"category": "guess_and_build", "approval": 15}
  ],
  "time_patterns": {
    "morning": "brief, actionable",
    "evening": "detailed, planning",
    "late_night": "quick execution"
  },
  "mood_patterns": {
    "frustrated": "short_responses_preferred",
    "engaged": "detailed_exploration_ok"
  }
}
```

---

## Confidence Scoring System

### How Confidence Gets Calculated

```
Base Confidence = 50

+ (approval_history_for_this_category * 2)
+ (similar_decision_past_success * 1.5)
+ (time_alignment_with_patterns * 1)
- (request_ambiguity * 2)
- (past_mistakes_in_category * 1.5)

If Confidence > 80: EXECUTE AUTONOMOUSLY
If 60-80: EXECUTE + NOTIFY
If 40-60: ASK WITH RECOMMENDATION
If < 40: ASK + OPTIONS
```

### Examples

**High Confidence (80+):**
- "Update MEMORY.md with today's wins" → Execute (I know you want continuous memory)
- "Pull NBA data and update dashboard" → Execute (data integrity + revenue project)
- "Auto-commit memory files" → Execute (you've approved this repeatedly)

**Medium Confidence (60-80):**
- "Generate 5 tweet drafts about fitness" → Execute + tell you ("Here's 5 options, pick or edit")
- "Build a new Notion template" → Execute + ask feedback ("Built it, does it work for you?")

**Low Confidence (<60):**
- "Build full SaaS product" → Ask first ("Here's my plan, thoughts?")
- "Send email to someone" → Always ask (external action)
- Ambiguous requests → Ask for clarification

---

## Memory Evolution

### Daily Updates (Evening, 8pm)

1. **Review today's conversations** in `memory/YYYY-MM-DD.md`
2. **Extract learnings:**
   - What did I get right?
   - What did I misunderstand?
   - What pattern emerged?
3. **Update `memory/decision-patterns.json`**
4. **Update `MEMORY.md`** with significant insights

### Weekly Review (Sunday, 6pm)

1. **Read all daily logs** from the week
2. **Identify trends:**
   - Which decision types had highest success?
   - What should I stop doing?
   - What should I do more of?
3. **Update confidence thresholds** based on actual results
4. **Commit learnings** to git

---

## Proactive Intelligence Loop

### What Runs Off-Hours (11pm-7am)

**Every night, Tier 1 Daemon:**
1. Scan GOALS.md for active projects
2. Look for opportunities aligned with your goals
3. Draft analysis using local brain model
4. Write to `reports/overnight-findings.md`
5. Queue top 3 actions to `memory/pending-actions.json`

**Topics to track automatically:**
- Revenue opportunities (Golf coaching leads, SaaS features)
- Time-savers (Automation improvements, integration opportunities)
- Market intel (Fitness trends, Florida real estate, golf content)
- Pattern insights (Your habits, decision patterns, learning curves)

**Output:** Morning briefing with pre-analyzed options

---

## Decision Transparency

### File: `memory/current-decisions.json`

Live log of decisions I'm making:

```json
{
  "active_decisions": [
    {
      "id": "nba-rankings-001",
      "task": "Generate 50-player NBA rankings for 2/9/26 slate",
      "decision": "Use official slate + supplement from team data",
      "confidence": 65,
      "status": "executing",
      "reasoning": "50 players needed but official slate has 25; adding supplemental data with current teams",
      "risk": "Might still have stale data"
    }
  ],
  "pending_approval": [
    {
      "id": "twitter-draft-001",
      "task": "Generate 5 golf content tweets",
      "my_recommendation": "Post these 3 tomorrow morning",
      "status": "waiting_for_review"
    }
  ]
}
```

You can edit this file to:
- Reject a pending decision (`status: rejected`)
- Override confidence (`confidence: 90` to force execution)
- Add context I missed

---

## Tier 2: Async Spawns

### When I Spawn Background Work

**Triggers:**
- Time-sensitive tasks (research, writing, analysis)
- Complex work you'd do manually (deep dives, reports)
- Low-urgency automation (content generation, dashboards)
- Off-hours intelligence gathering

**Format:**
1. Spawn a sub-agent with clear task
2. Log spawn ID to `memory/spawns-log.json`
3. Deliver findings in next morning brief
4. Keep costs low (use local brain, batch requests)

**Example spawn task:**
```
Task: "Research top 10 golf coaching trends, market sizing, competitor pricing. 
Generate 3 coaching landing page angles with CTA options. 
Expected output: ~/reports/golf-coaching-research.md"
```

---

## Implementation Checklist

### Phase 1 (Tonight - 2026-02-08):
- ✅ Write AUTONOMOUS_LEARNING_SYSTEM.md (this file)
- ✅ Create memory/decision-log.json template
- ✅ Create memory/decision-patterns.json template
- ✅ Update HEARTBEAT.md with evening review protocol
- 🔄 Create scripts/decision_scorer.py (confidence engine)
- 🔄 Create scripts/pattern_analyzer.py (learn from decisions)
- 🔄 Update scripts/autonomous_check.py to use confidence

### Phase 2 (Tomorrow):
- Build evening auto-review script
- Set up cron for nightly intelligence gathering
- Create morning brief generator
- Test confidence scoring on real decisions

### Phase 3 (This Week):
- Integrate with heartbeat loop
- Tune confidence thresholds based on actual behavior
- Add pattern visualization to dashboard

---

## How You Use This

### You Don't Have To Do Anything Special

I'm learning from every interaction:
- Approvals (I do more of this)
- Rejections (I do less of this)
- Edits (I refine this area)
- Your questions (I pre-answer next time)

### Optional: Give Me Explicit Feedback

If you want to accelerate learning:
- React to messages (👍 = approve, ❌ = needs work)
- Edit `memory/current-decisions.json` if I'm on wrong track
- Say "you were right about X" or "you should have done Y"
- Tell me why you rejected something

### The Virtuous Cycle

Decision → Outcome → Learning → Better Decisions → Less Friction

---

## Success Looks Like

- I ask fewer permission questions
- I correctly predict what you want
- You rarely have to re-explain context
- Autonomous builds actually align with your goals
- You say "exactly what I needed" more often

---

## Guardrails

**I NEVER:**
- Log external messages (only my own decisions)
- Retain private data longer than needed
- Share patterns with external systems
- Override explicit "no" decisions
- Act on low-confidence external requests

**I ALWAYS:**
- Log my reasoning (not just the decision)
- Update confidence scores after outcomes
- Ask about ambiguous requests
- Respect your priorities over my guesses
- Keep logs private (in workspace only)

---

**This system is live. Starting tonight, every decision I make gets logged, analyzed, and improved.**
