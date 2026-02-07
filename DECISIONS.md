# DECISIONS - Architectural & Strategic Decisions

Major decisions documented for transparency and future reference.

## 2026-02-01

### Decision: Use Codex for All Code Generation
**Context:** Multiple coding tools available (Claude Code, Codex, OpenCode, etc.)
**Decision:** Use Codex CLI exclusively
**Rationale:** Ross's explicit preference
**Implications:** Need to ensure Codex is installed and configured
**Status:** ✅ Documented in AUTONOMOUS_WORK.md

### Decision: No Git Commits, PRs Only
**Context:** Need to ship code daily but maintain review process
**Decision:** Stage all work, never commit/push directly
**Rationale:** Ross wants to review and test before going live
**Implications:** All projects go to projects/ directory, Ross commits when approved
**Status:** ✅ Safety rail in place

### Decision: 30-Minute Heartbeat Interval
**Context:** Need to balance responsiveness vs. API cost
**Decision:** 30min intervals during active hours (7am-11pm CST)
**Rationale:** 
- 15min = too frequent, burns tokens
- 1hr = too slow, miss urgent items
- 30min = sweet spot for responsiveness + cost
**Implications:** ~32 heartbeats/day
**Status:** ✅ Configured

### Decision: Sonnet 4 as Primary Model
**Context:** Need to choose between Opus 4, Sonnet 4, Haiku 4
**Decision:** Sonnet 4 for now
**Rationale:** 
- Opus 4 = 5x cost, overkill for most tasks
- Haiku 4 = 95% cheaper but may lack reasoning
- Sonnet 4 = best balance for general work
**Implications:** May switch to Haiku for simple tasks, Opus for complex reasoning
**Status:** ✅ Can be adjusted per-task

### Decision: Nightly Build Strategy
**Context:** Ship daily projects, need process
**Decision:** Pick from TODO.md high priority, build 11pm-6am, brief at 7:30am
**Rationale:** 
- Gives Ross testable work every morning
- Uses his sleep hours productively
- Small daily wins > big monthly launches
**Implications:** Need to scope projects to ~6hr builds
**Status:** ✅ Starts tonight

---

*Add major decisions here as they come up. Don't wait for approval—document and proceed.*
