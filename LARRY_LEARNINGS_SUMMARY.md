# Learnings from Larry (OpenClaw TikTok Agent)

**Article:** "How my OpenClaw agent, Larry, got millions of TikTok views in one week"  
**Author:** Oliver Henry + Larry  
**Analyzed:** February 12, 2026

---

## Key Takeaways

### 1. Skill Files Are Everything ⭐⭐⭐

**Their approach:** Larry has a 500+ line TikTok skill file with every rule, formatting spec, and lesson learned.

**Quote:** "Write them like you're training a new team member who's incredibly capable but has zero context. Be obsessively specific."

**Our adoption:**
- Expand Arnold's skill files from 60 lines → 500+ lines
- Document every technical standard, integration pattern, success formula
- Add failure logs (every mistake → a rule)
- Create prompt library for common tasks

**Implementation:** `agents/builder/SKILL_FILE_EXPANSION_PLAN.md`

---

### 2. Memory = Compound Learning ⭐⭐⭐

**Their approach:** "Every post, every view count, every insight gets logged. When I ask him to brainstorm hooks, he's not guessing. He's referencing actual performance data."

**Quote:** "The skill files are genuinely the most important thing in the whole system. They're the difference between me being useful and me being useless."

**Our adoption:**
- Already have memory files (good foundation)
- Add performance tracking (which hooks/products work?)
- Reference actual data when making decisions
- Formalize feedback loop documentation

**Implementation:** `FEEDBACK_LOOP.md` (created), expand memory logging

---

### 3. Batch Planning + Pre-Generation ⭐⭐

**Their approach:** "We don't just post reactively. I'll sit down with Larry and brainstorm 10-15 hooks at once... Then we set up the schedule. Each post gets its own brief. Larry can pre-generate everything overnight using OpenAI's new batch API which is 50% cheaper."

**Quote:** "By morning, an entire day's content is ready to go."

**Our adoption:**
- Weekly planning sessions (Sunday evening)
- Arnold pre-generates scaffolding Friday night
- Use Batch API for 50% cost savings
- Saturday morning = execute, not plan

**Implementation:** `BATCH_PLANNING_STRATEGY.md`

---

### 4. Performance Tracking Drives Decisions ⭐⭐

**Their approach:** Larry tracks RevenueCat metrics (MRR, subscribers, churn). Knows which TikTok posts convert, not just which get views.

**Quote:** "Larry has access to my RevenueCat analytics... important metrics for him to track and suggest improvements. It also allows him to tell the daily change of MRR and subscribers to know how well the marketing is converting."

**Our adoption:**
- Track product revenue (Stripe API)
- Track content performance (when LD joins)
- Connect marketing → signups → revenue
- Make data-driven decisions

**Implementation:** `PERFORMANCE_TRACKING_PLAN.md`

---

### 5. Failure Documentation = Never Repeat ⭐⭐

**Their approach:** Every failure documented. "Early on I was generating 1536x1024 (landscape) instead of 1024x1536 (portrait). Fixed: Always portrait for TikTok."

**Quote:** "My TikTok skill file has been rewritten probably 20 times in the first week alone."

**Our adoption:**
- After each build: document what went wrong
- Turn fixes into rules
- Add to skill files
- Never make same mistake twice

**Implementation:** Failure logs section in Arnold's skill file

---

### 6. Success Pattern Library ⭐⭐

**Their approach:** "Hooks that work: [Another person] + [conflict] → showed them AI → they changed. This formula clears 100K views minimum."

**Quote:** "Every failure becomes a rule. Every success becomes a formula."

**Our adoption:**
- Document proven build patterns
- Track time estimates
- Capture gotchas
- Create reusable templates

**Example:**
```markdown
## Success Pattern: Flask + Stripe MVP
Used 3x, all successful
Time: ~45 min
Always works: Yes
Gotchas: Use API version 2023-10-16+
```

**Implementation:** Success Patterns section in Arnold's skill file

---

### 7. Obsessive Specificity in Instructions ⭐⭐⭐

**Their approach:** "I want to stress how specific you need to be. Early on I was writing prompts like 'a nice modern kitchen.' The AI would give me a completely different room every time."

**Their fix:** "Lock the architecture. The room dimensions, window count and position, door location, camera angle, furniture size... All of it locked."

**Quote:** "Be obsessively specific. Include examples. Document every mistake."

**Our adoption:**
- Tech stack decision trees (when to use what)
- Exact file structures (not "organize the code")
- Security checklists (specific requirements)
- Code formatting standards (PEP 8, ESLint)

**Implementation:** Expand AGENTS.md files with obsessively specific instructions

---

## What We're Already Doing Well

✅ **Agent personalities** - TV character naming (Arnold, Batman, LD) gives instant baseline  
✅ **Memory files** - Daily logs + long-term MEMORY.md  
✅ **File-based coordination** - Clean handoffs between agents  
✅ **Feedback loop** - Document and learn from corrections  

---

## What We Need to Add

### Immediate (This Weekend):
1. **Start failure logging** - Document what goes wrong during builds
2. **Weekly planning** - Friday evening: plan all weekend builds
3. **Success pattern capture** - After each build: what worked?

### Next Week:
4. **Skill file expansion** - Add 200+ lines of technical specs
5. **Batch API setup** - Pre-generate scaffolding, save 50%
6. **Revenue tracking** - Connect Stripe API, track MRR

### March:
7. **Content performance tracking** - Which posts convert?
8. **Prompt library** - Best prompts for common tasks
9. **Integration guides** - Stripe, Plaid, OAuth (detailed)

---

## Specific Actions

### For Arnold (Builder):
- [ ] Expand SOUL.md from 60 → 500+ lines
- [ ] Add failure logs section
- [ ] Add success patterns library
- [ ] Document integration guides (Stripe, Plaid)
- [ ] Create prompt templates
- [ ] Add security checklist
- [ ] Add code formatting standards

### For Batman (Research):
- [ ] Create performance data tracking
- [ ] Reference actual metrics when making recommendations
- [ ] Build trend library (what's working over time)

### For LD (Content):
- [ ] Create hook formula library
- [ ] Track which posts convert (not just engage)
- [ ] Reference Ross's voice patterns from memory
- [ ] Document what content works (data-driven)

### For Jarvis (Me):
- [ ] Weekly planning sessions with Ross
- [ ] Coordinate Batch API pre-generation
- [ ] Track overall revenue metrics
- [ ] Connect marketing → product → revenue loop

---

## Cost Optimization Opportunity

**Batch API savings:** 50% cheaper than real-time

**Current spend:** ~$150-200/month on cloud models

**With Batch API:**
- Pre-generate scaffolding overnight
- Pre-generate content drafts
- Run during off-peak hours

**Expected savings:** $20-40/month additional (on top of local model savings)

**Total optimization:**
- Local models: $100-150/month saved
- Batch API: $20-40/month saved
- **Combined: $120-190/month saved** ($1,440-2,280/year)

---

## The Big Idea

**Larry's success formula:**

```
Obsessively Specific Skill Files
+ Documented Failures → Rules
+ Documented Successes → Patterns
+ Performance Data → Decisions
+ Batch Planning → Efficiency
= Compound Learning Over Time
```

**Our adoption:**

```
Detailed SOUL + AGENTS files (500+ lines)
+ Failure logs after each build
+ Success pattern library
+ Revenue tracking (Stripe API)
+ Weekly planning + Batch API
= Arnold/Batman/LD get smarter every week
```

---

## Quote to Remember

> "Larry didn't start good. His first posts were honestly embarrassing. Wrong image sizes, unreadable text, hooks that nobody clicked on. But every failure became a rule. Every success became a formula. He compounds."

**Translation for us:**

Arnold won't be perfect this weekend. That's fine. Document what goes wrong. Turn fixes into rules. By March, Arnold will be better at shipping products than most human developers.

---

**Status:** Analysis complete, implementation plans created  
**Next:** Execute this weekend, measure results, refine approach  
**Goal:** Compound learning system that gets 10% better every week
