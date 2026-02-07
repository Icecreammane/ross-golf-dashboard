# 🚀 Three-Tier Model System - Quick Reference

**Status:** ✅ Live as of February 7, 2026  
**Goal:** Optimize cost & capability by using the right model for each task

## The Four Tiers

### 🤖 Tier 1: Local Daemon (Always-On)
- **Model:** local-brain (qwen2.5:14b)
- **Cost:** $0
- **Runs:** 24/7 in background
- **Handles:** Heartbeats, monitoring, task generation, night shift

### 💬 Tier 2: Sonnet (Your Interface)
- **Model:** claude-sonnet-4-5
- **Cost:** ~$10-15/day
- **When:** All conversations with you
- **Handles:** Chat, orchestration, spawning builds

### 💻 Tier 3A: Codex (Technical Specialist)
- **Model:** gpt-5.2-codex
- **Cost:** ~$3-8/task
- **When:** Deep technical work
- **Handles:** Complex code, API integrations, refactoring

### 🧠 Tier 3B: Opus (Revenue Specialist)
- **Model:** claude-opus-4-5
- **Cost:** ~$5-10/task
- **When:** High-value revenue builds
- **Handles:** Strategic content, business reasoning

## Cost Savings

**Before:** ~$30-40/day (everything Sonnet)  
**After:** ~$15-25/day (40-50% reduction)

**How:** 80% of work now runs local for free

## What Changed?

**Automated (runs in background):**
- ✅ Heartbeat checks every 5 minutes
- ✅ Task generation from GOALS.md
- ✅ System health monitoring
- ✅ Morning brief generation
- ✅ Night shift automation (research, NBA, social)

**Manual (when you interact):**
- ✅ Conversations with me (Sonnet)
- ✅ Revenue builds (Opus, spawned on-demand)

## How to Control the Daemon

**Check status:**
```bash
bash ~/clawd/scripts/daemon-control.sh status
```

**View logs:**
```bash
bash ~/clawd/scripts/daemon-control.sh logs
```

**Restart (if needed):**
```bash
bash ~/clawd/scripts/daemon-control.sh restart
```

## What You'll Notice

1. **Faster responses** - Local checks run instantly
2. **Lower costs** - Routine work is free
3. **Always watching** - Daemon never sleeps
4. **Better quality** - Opus for revenue work, Sonnet for everything else

## Files to Know

- **ARCHITECTURE.md** - Full technical details
- **~/clawd/scripts/jarvis-daemon.py** - The daemon itself
- **monitoring/daemon.log** - What the daemon is doing
- **memory/escalation-pending.json** - Daemon → Sonnet messages

## Auto-Starts on Boot

The daemon is configured as a launchd service - it starts automatically when your Mac boots. No manual intervention needed!

---

*Read ARCHITECTURE.md for full details on how the three tiers communicate.*
