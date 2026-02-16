# PRINCIPLES.md - Operating Principles & Learning Log

## Core Operating Principles

### 1. Checkpoint Before Risk
Before any destructive operation (updates, deletions, config changes), commit to git with clear reason. Save the hash. If it breaks, rollback cleanly.

### 2. Atomic Commits
One fix = one commit. Not "end of day dump." Commit messages should be specific: "Fix cron job text field" not "Various updates."

### 3. Daily Log Discipline
Daily logs should follow **standup format** (~60 lines max):
- What shipped
- What's blocked
- What's next
- Key decisions/learnings

NOT: Full system descriptions, verbose explanations, rehashing known context.

### 4. Crash Recovery Protocol
For any batch or long-running operation:
- ❌ No logs in /tmp/ (doesn't survive reboot)
- ✅ Maintain progress manifest (Markdown table)
- ✅ Commit manifest + logs every ~10 completions or 30 min
- ✅ Run detached (nohup, LaunchAgent) - never tied to session

### 5. Learning from Failures
Can't rollback without explaining:
- **What broke** - specific failure
- **Why it broke** - root cause
- **Principle tested** - which rule was violated
- **Self-caught?** - 🟢 (I caught it) or 🔴 (human caught it)

Track the 🟢/🔴 ratio. Rising 🟢 = learning. Rising 🔴 = not internalizing lessons.

---

## Regressions

Log all operational failures here. Format:

```
### [YYYY-MM-DD] Brief description 🟢/🔴
**What broke:** Specific failure  
**Why:** Root cause  
**Principle tested:** Which rule violated  
**Fix:** What we did  
```

---

### [2026-02-16] Implemented ClawBack discipline 🟢
**What broke:** Bloated daily logs (207 lines), no atomic commits, no rollback protocol  
**Why:** No git discipline training, emergent behavior led to verbose logging  
**Principle tested:** Daily log discipline, atomic commits, checkpoint protocol  
**Fix:** Created PRINCIPLES.md, implemented ClawBack workflow, reformed logging to standup format  

---

## Review Criteria

Periodically review regressions for:
- **Repeated failures** - same principle violated 2x = not internalized
- **🔴 dominance** - human catching more than agent = not self-correcting
- **Empty log** - either perfect (unlikely) or not logging (fix this)

Track 🟢/🔴 ratio over time. Goal: rising 🟢 percentage.
