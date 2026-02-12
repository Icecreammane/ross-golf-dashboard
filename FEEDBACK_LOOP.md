# Feedback Loop - Corrective Prompt Engineering

**Purpose:** Continuous improvement through structured feedback

---

## How It Works

### 1. Agent Produces Output
- Code, content, research, analysis, decisions

### 2. Ross Provides Feedback
**Good feedback:**
- "No emojis in tweets"
- "Be more direct, less hedging"
- "Focus on ROI, not features"
- "This code works but explain why"

**Bad feedback:**
- "Better" (too vague)
- "Fix it" (no direction)
- "I don't like it" (no learning)

### 3. Agent Updates Memory
Feedback gets logged to:
- `memory/YYYY-MM-DD.md` (immediate capture)
- `memory/learning_data.json` (pattern tracking)
- `MEMORY.md` (long-term wisdom, updated every 3 days)

### 4. Pattern Detection
After 10+ feedback instances on same topic:
- Extract principle
- Add to SOUL.md or AGENTS.md
- Becomes default behavior

---

## Examples (Real)

### Tweet Voice (Feb 8, 2026)
**Feedback:** "Stop using emojis and hashtags in tweets"  
**Action:** Updated memory, removed from templates  
**Result:** All tweets now match voice

### Decision Confidence (Feb 6, 2026)
**Feedback:** "Stop hedging with 'it depends' - commit to a take"  
**Action:** Updated SOUL.md principle #4  
**Result:** Strong opinions, clear recommendations

### Communication Style (Feb 8, 2026)
**Feedback:** "Brevity is mandatory - one sentence if possible"  
**Action:** Updated SOUL.md principle #3  
**Result:** Concise, executive-ready responses

---

## Tracking Progress

**Weekly review** (during Sunday planning):
1. Read this week's `memory/YYYY-MM-DD.md` files
2. Identify repeated feedback themes
3. Update `MEMORY.md` with distilled learnings
4. Update `SOUL.md` if principle-level change needed

**Monthly review** (first Sunday of month):
1. Review pattern data in `memory/learning_data.json`
2. Identify stabilized behaviors
3. Archive old daily logs (keep last 30 days)
4. Celebrate improvements

---

## Quality Metrics

Track in `memory/feedback-quality.json`:
- Feedback instances per week
- Repeat feedback (indicates not learning)
- Weeks since last feedback on topic (indicates mastery)
- Positive reinforcement (what's working well)

**Goal:** Fewer corrections over time = learning happening

---

## Current Focus Areas (As of Feb 12, 2026)

1. **Voice consistency** - Match Ross's executive, no-BS style ✓ Improving
2. **Strategic thinking** - Focus on leverage/optionality/mastery ✓ Good
3. **Proactive anticipation** - Surface needs before asked ⏳ In progress
4. **Code quality** - Explain decisions, not just solutions ⏳ Next focus

---

**Status:** Active feedback loop  
**Update frequency:** Daily logs → Weekly MEMORY.md → Monthly SOUL.md  
**Owner:** Ross (feedback) + Jarvis (learning)
