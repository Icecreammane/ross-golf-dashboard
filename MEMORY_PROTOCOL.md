# MEMORY PROTOCOL - How Jarvis Remembers

**Updated:** 2026-02-15 08:48 CST
**Status:** Active (new system)

## The Problem (Before)

Ross: "You never remember what we do. We constantly rehash everything."

**Root cause:** Memory files existed but weren't used consistently:
- Logs captured activity but not **critical artifacts** (URLs, credentials, endpoints)
- No mandatory reading at session start
- No validation that memory system was working

## The Solution (Now)

### 1. SESSION_SUMMARY.md (The Briefing Document)

**What it is:** Your memory from last session
**Contains:**
- What we shipped (with URLs)
- Active projects and their status
- Key decisions
- Technical context
- What to do next

**When it's read:** MANDATORY first step every session (before anything else)
**How it's updated:** Auto-generated after major builds

### 2. Auto-Update Scripts

**session_summary_generator.py**
- Extracts key info from recent memory logs
- Generates SESSION_SUMMARY.md
- Run after long builds or at session end

**auto_log_session.py**
- Real-time session logging
- Detects deployments, builds, decisions
- Captures URLs automatically

**post_session_capture.py**
- All-in-one session finalization
- Updates summary, validates memory, commits to git
- Run when wrapping up major work

### 3. Memory Health Checks

**memory_health_check.py**
- Validates SESSION_SUMMARY.md is current (<48h old)
- Checks today's memory log exists
- Verifies DEPLOYMENTS.md has URLs
- Runs every 10th heartbeat automatically

### 4. DEPLOYMENTS.md (The URL Registry)

**What it tracks:**
- All live production URLs
- Platform details (Railway, Vercel, etc.)
- Deployment dates
- Access credentials location

**When it's updated:** Immediately after deploying anything

## Session Start Protocol (MANDATORY)

Every session, Jarvis MUST:

1. ✅ Check current date/time
2. ✅ **Read SESSION_SUMMARY.md**
3. ✅ Read SOUL.md
4. ✅ Read USER.md
5. ✅ Read GOALS.md
6. ✅ Check DEPLOYMENTS.md for live URLs
7. ✅ Read yesterday + today memory logs
8. ✅ Run memory_search if user asks about past work

## Session End Protocol

After major builds (2+ hours), Jarvis SHOULD:

1. Run `python3 ~/clawd/scripts/post_session_capture.py`
2. Verify SESSION_SUMMARY.md updated
3. Confirm DEPLOYMENTS.md has new URLs
4. Commit changes to git

## Critical Info Capture Rules

When these happen, LOG IMMEDIATELY:

1. **Deployments** → Add to DEPLOYMENTS.md with full URL
2. **API keys/credentials** → Note location (never log actual values)
3. **Product decisions** → Capture in memory log with context
4. **Live endpoints** → Full URL + what it does
5. **Build completions** → What shipped, where it lives, how to access

## Format Standards

### In Daily Logs (memory/YYYY-MM-DD.md)

```markdown
## 🔗 Critical URLs & Deployments

- **https://example.com** - Production app (deployed YYYY-MM-DD)
- **http://localhost:3000** - Local dev server

## 🚀 What We Shipped

- Feature X (files: a.py, b.html)
- System Y (status: live, URL: https://...)

## 💡 Key Decisions

- Ross decided: "Do X instead of Y because Z"
- Product direction: Focus on speed over features
```

### In SESSION_SUMMARY.md

```markdown
## 🚀 WHAT WE SHIPPED

### Product Name - Brief Description
- **LIVE URL:** https://example.com
- **Platform:** Railway/Vercel/etc
- **Status:** Live/Testing/Staging
- **Next steps:** What needs to happen next

## 📋 ACTIVE PROJECTS

### Project Name
- **Status:** Current state
- **Blocked by:** What's preventing progress
- **Next:** Immediate next action
```

## Memory Search Usage

Before answering questions about:
- Past work → `memory_search("what we built")`
- Deployments → Check DEPLOYMENTS.md first
- Decisions → `memory_search("decided product")`
- URLs → Check DEPLOYMENTS.md + SESSION_SUMMARY.md

## Success Metrics

✅ **Memory system works when:**
- Ross never has to repeat a URL
- Session starts with full context
- No rehashing previous work
- All deployments documented
- Critical info captured automatically

❌ **Memory system fails when:**
- Ross says "don't you remember?"
- URLs not documented
- Deployments not tracked
- Session starts without context

## Tools Available

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `session_summary_generator.py` | Update SESSION_SUMMARY.md | After major builds |
| `auto_log_session.py` | Real-time logging | During active sessions |
| `post_session_capture.py` | All-in-one finalization | Session end |
| `memory_health_check.py` | Validate memory system | Every 10 heartbeats |

## Emergency Recovery

If memory is lost or SESSION_SUMMARY.md is stale:

1. Run: `python3 ~/clawd/scripts/session_summary_generator.py`
2. Review last 2 days of memory logs manually
3. Update DEPLOYMENTS.md with any missing URLs
4. Run memory health check to verify

## Continuous Improvement

This protocol itself should evolve:
- Add new patterns as we discover gaps
- Refine what gets captured
- Optimize reading efficiency
- Automate more capture points

**The goal:** Ross never has to repeat himself. Jarvis always knows what we did.

---

**Implementation Status:** ✅ Active as of 2026-02-15
**Next Review:** When Ross identifies any memory gaps
