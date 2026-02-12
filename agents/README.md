# AI Agent Team

**System:** Autonomous AI agents coordinated via filesystem  
**Philosophy:** One writer, many readers. No APIs, no message queues. Just files.

---

## Team Structure

### Jarvis (Chief of Staff) - Root Agent
**Location:** `~/clawd/` (workspace root)  
**Role:** Strategic oversight, coordination, delegation, Ross's primary interface  
**Files:** `SOUL.md`, `AGENTS.md`, `MEMORY.md`, `HEARTBEAT.md`  
**Schedule:** Always on (Telegram), hourly heartbeats

### Builder (Code Generation) - Sub-Agent ✅ ACTIVE
**Location:** `agents/builder/`  
**Role:** Ship products, vibe-coding, weekend builds  
**Files:** `SOUL.md`, `AGENTS.md`, `memory/`  
**Schedule:** On-demand (spawned by Jarvis)  
**Status:** Active as of Feb 12, 2026

### Research (Intelligence) - Sub-Agent 🔜 PLANNED
**Location:** `agents/research/` (not yet created)  
**Role:** Overnight intelligence, market analysis, trend tracking  
**Schedule:** 8am, 4pm daily  
**Status:** Planned for March 2026

### Content (Marketing) - Sub-Agent 🔜 PLANNED
**Location:** `agents/content/` (not yet created)  
**Role:** Social posts, marketing copy, product descriptions  
**Schedule:** 9am, 5pm daily (after Research)  
**Status:** Planned for March 2026

---

## How Agents Coordinate

**No API calls. No message queues. Just files.**

### Pattern: Research → Content (Future)
```
Research writes → intel/DAILY-INTEL.md
Content reads intel/DAILY-INTEL.md → drafts posts
```

### Pattern: Jarvis → Builder (Active Now)
```
Jarvis writes → TASK_QUEUE.md
Jarvis spawns Builder
Builder reads TASK_QUEUE.md → builds product
Builder writes → builds/[project]/BUILD_LOG.md
Jarvis reads BUILD_LOG.md → reports to Ross
```

**See:** `SUB_AGENT_COORDINATION.md` for complete coordination guide

---

## File Ownership

**One writer per file. Many readers allowed.**

| File | Writer | Readers |
|------|--------|---------|
| `GOALS.md` | Jarvis | All |
| `TASK_QUEUE.md` | Jarvis | All |
| `intel/DAILY-INTEL.md` | Research (future) | Content, Jarvis |
| `builds/[project]/BUILD_LOG.md` | Builder | Jarvis |
| `agents/[name]/memory/*.md` | That agent | That agent only |

---

## Adding a New Agent

### 1. Create Directory Structure
```bash
mkdir -p agents/[name]/memory
```

### 2. Write SOUL.md
Define:
- Identity (TV character personality)
- Role (what do they do?)
- Principles (how do they operate?)
- Outputs (what files do they write?)

### 3. Write AGENTS.md
Define:
- Session startup checklist
- File read/write permissions
- Quality standards
- Communication protocol

### 4. Test in Isolation
```bash
openclaw sessions spawn --agent [name] --task "Test task"
```

### 5. Document Coordination
Update `SUB_AGENT_COORDINATION.md` with handoff patterns.

**See:** `SUB_AGENT_COORDINATION.md` for complete process

---

## Current Status

**Agents active:** 2 (Jarvis + Builder)  
**Agents planned:** 2 (Research + Content)  
**Coordination:** File-based, working  
**Next milestone:** Builder ships 3 products this weekend

---

**Last updated:** February 12, 2026  
**Maintained by:** Jarvis
