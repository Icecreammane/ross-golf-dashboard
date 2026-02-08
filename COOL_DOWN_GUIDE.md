# 🧘 Cool Down System

**Post-build mental recovery • Like a 20-min walk after lifting, but for your brain**

---

## What It Is

After an intense build session, your brain needs a structured wind-down to:
- Consolidate what you learned
- Save context for next time
- Transition smoothly (no abrupt stops)
- Lock in the lessons

**Just like walking after lifting:**
- Flushes mental "metabolic waste"
- Prevents cognitive stiffness
- Active recovery (productive but low intensity)
- Signals completion to your brain

---

## The 3-Step Routine (15-20 min)

### 1. 📝 Document (5 min)
**What:** Quick notes about what you built

**Prompts:**
- What did you just build? (one sentence)
- Key features/components?

**Output:** Auto-added to today's memory file

---

### 2. 💾 Commit (5 min)
**What:** Save your work to git

**Prompts:**
- Commit message?
- Detailed description? (optional)
- Push to GitHub? (y/n)

**Output:** Changes committed + optionally pushed

---

### 3. 🤔 Reflect & Plan (10 min)
**What:** Learn from this session, prep for next

**Prompts:**
- What worked well?
- What could be better?
- What's next? (tasks for next session)
- Add to TASK_QUEUE.md? (y/n)

**Output:** Lessons captured, next session planned

---

### 🏆 BONUS: Log Win (1 min)
**What:** Add this build to your Win Streak

**Prompt:**
- Log this as a build win? (y/n)

**Output:** +points, streak continues, combo multiplier

---

## How To Use

### Full Routine (Recommended)
```bash
cd ~/clawd
./scripts/cooldown
```

**When:** After any build session 45+ minutes

**Time:** 15-20 minutes

**Result:** Complete cool down, context saved, brain ready

---

### Quick Version (5 min)
```bash
cd ~/clawd
./scripts/cooldown quick
```

**When:** Short builds or when you're rushed

**Time:** 5 minutes

**Result:** Essentials logged, good enough

---

## Integration With Your Flow

### Your Build Sessions:
1. **Warm up (5 min):** Review what you're building, load context
2. **Build (45-90 min):** Deep work, ship it
3. **Cool down (15-20 min):** Run `./scripts/cooldown`
4. **Done:** Brain ready to switch modes

---

## What Gets Tracked

**Cool Down History:**
- Total cool downs completed
- Current streak (consecutive days)
- Session notes (last 30 sessions)

**Stats:**
```
📊 Cool Down Stats:
   Total: 15
   Streak: 7 days
```

**Where:** `memory/cooldown_log.json`

---

## Why This Works

### Without Cool Down:
- ❌ Abrupt stop (brain still in "build mode")
- ❌ Lessons forgotten (didn't write them down)
- ❌ Context lost (what was I doing?)
- ❌ Harder to switch tasks

### With Cool Down:
- ✅ Smooth transition
- ✅ Learning locked in
- ✅ Context saved for next time
- ✅ Feels complete (satisfying closure)
- ✅ Ready for next activity

---

## The Science

**Active Recovery:**
- Physical cool down: Flushes lactic acid
- Mental cool down: Processes what you learned

**State Transition:**
- Physical cool down: Brings heart rate down gradually
- Mental cool down: Transitions from deep focus to normal mode

**Memory Consolidation:**
- Physical cool down: Prevents injury/stiffness
- Mental cool down: Locks in learning (reflection = retention)

---

## Pro Tips

### 1. **Do it every time**
- Even short builds benefit from quick cool down
- Builds the habit (like stretching after gym)

### 2. **Don't skip documentation**
- Future you will thank you
- "What was I thinking?" moments = lack of documentation

### 3. **Be honest in reflection**
- What actually worked vs. what you wish worked
- Learning happens in the "what didn't work" section

### 4. **Use quick mode when needed**
- 5-min cool down > no cool down
- Better to do something than nothing

### 5. **Track your streak**
- Gamify it (like workout streaks)
- Cool down after every build = discipline

---

## Examples

### After Tonight's Build:
```bash
cd ~/clawd
./scripts/cooldown

# Step 1: Document
What did you just build?
→ Built cool down system for post-build recovery

Key features/components?
→ 3-step routine, git integration, win streak bonus

# Step 2: Commit
Commit message:
→ feat: cool down system for post-build mental recovery

Push to GitHub? (y/n):
→ y

# Step 3: Reflect
What worked well?
→ Clear prompts, guided process, integrates with existing tools

What could be better?
→ Could add timer between steps, voice mode option

What's next?
→ Polish fitness tracker, test party demos

# Bonus
Log this as a build win? (y/n):
→ y

✅ Cool Down Complete
🔨 Builder Mode: 2 day streak
🎯 Combo: 1.75x
```

---

## Quick Commands

```bash
# Full cool down
./scripts/cooldown

# Quick version
./scripts/cooldown quick

# Check history
cat memory/cooldown_log.json | jq
```

---

## Integration Points

### Win Streak System:
- Cool down can log build wins
- Keeps 🔨 Builder Mode streak alive

### Memory System:
- Auto-updates today's memory file
- Captures what you built + lessons learned

### Task Queue:
- Can auto-add next tasks
- Sets up tomorrow's session

### Git Workflow:
- Guided commit process
- Encourages good commit messages

---

## Files Created

- `scripts/cool_down.py` - Main system
- `scripts/cooldown` - Quick launcher
- `memory/cooldown_log.json` - History tracking
- `COOL_DOWN_GUIDE.md` - This guide

---

**Your mind is clear. Context is saved. Ready for what's next.** 🧘

