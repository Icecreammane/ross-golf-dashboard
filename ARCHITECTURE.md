# ARCHITECTURE.md - Three-Tier Model System

**Implemented:** February 7, 2026  
**Goal:** Optimize cost, responsiveness, and capability by using the right model for each task.

## 🏗️ The Three Tiers

### Tier 1: Local Daemon (Always-On Background Worker)
**Model:** `local-brain` (qwen2.5:14b via Ollama)  
**Cost:** $0 (just electricity)  
**Purpose:** Continuous monitoring, routine checks, task generation

**Responsibilities:**
- ✅ Heartbeat checks every 5 minutes
- ✅ Autonomous task generation (reads GOALS.md, updates BUILD_QUEUE.md)
- ✅ System health monitoring (disk, processes, services)
- ✅ Morning brief generation (7:30am)
- ✅ Night shift automation (2:00am - research, NBA intel, social posts)
- ✅ Escalation signaling (when human interaction needed)

**How it works:**
- Runs as macOS launchd service (auto-starts on login)
- Python daemon loop, checks every 60 seconds
- Writes escalations to `memory/escalation-pending.json`
- Writes spawn signals to `memory/spawn-signal.json`
- Logs to `monitoring/daemon.log`

**Control:**
```bash
bash ~/clawd/scripts/daemon-control.sh {start|stop|restart|status|logs}
```

### Tier 2: Sonnet (Conversational Interface)
**Model:** `anthropic/claude-sonnet-4-5`  
**Cost:** ~$10-15/day in active usage  
**Purpose:** All human conversations, orchestration, decision-making

**Responsibilities:**
- ✅ Chat with Ross (main session)
- ✅ Check escalations during heartbeats
- ✅ Spawn Opus builds when ready
- ✅ Handle morning brief delivery
- ✅ Send evening check-in messages
- ✅ Route alerts and notifications
- ✅ Complex reasoning and planning

**Workflow:**
1. Receive message from Ross
2. Check for escalations: `python3 ~/clawd/scripts/check_escalations.py`
3. Handle escalations (spawn, notify, etc.)
4. Respond to Ross

### Tier 3: Opus (Revenue Specialist)
**Model:** `anthropic/claude-opus-4-5`  
**Cost:** ~$5-10 per task  
**Purpose:** High-value revenue builds, complex content creation

**Responsibilities:**
- ✅ Revenue-generating projects (per AUTONOMOUS_AGENT.md)
- ✅ Strategic planning documents
- ✅ High-stakes content creation
- ✅ Complex code generation

**Trigger:**
- Spawned by Sonnet via `sessions_spawn` tool
- Isolated session with specific task
- Reports completion back to main session
- Only used when ROI justifies cost

## 📊 Cost Comparison

### Before (All Sonnet):
- Background checks: Sonnet ($$$)
- Heartbeats: Sonnet ($$$)
- Task generation: Sonnet ($$$)
- Conversations: Sonnet ($$$)
- Revenue builds: Sonnet ($$$)
- **Total:** ~$30-40/day

### After (Three-Tier):
- Background checks: Local ($0)
- Heartbeats: Local ($0)
- Task generation: Local ($0)
- Conversations: Sonnet ($10-15)
- Revenue builds: Opus ($5-10)
- **Total:** ~$15-25/day

**Savings:** ~40-50% cost reduction while improving quality where it matters

## 🔄 Data Flow

### Normal Heartbeat (No Escalation):
1. Daemon runs health checks
2. Daemon runs autonomous_check.py
3. Updates BUILD_QUEUE.md
4. Logs to daemon.log
5. No escalation → Sonnet unaware

### Escalation Required (Morning Brief):
1. Daemon detects 7:30am window
2. Daemon runs generate-morning-brief.py
3. Daemon writes escalation: `{"type": "morning_brief"}`
4. Sonnet reads escalation during next heartbeat
5. Sonnet sends brief to Ross via Telegram
6. Escalation file deleted

### Spawn Ready:
1. Daemon runs autonomous_check.py
2. autonomous_check writes spawn-signal.json
3. Daemon reads signal, writes escalation
4. Sonnet reads escalation
5. Sonnet spawns Opus build via sessions_spawn
6. Signal & escalation deleted
7. Opus works in isolation
8. Opus announces completion to Ross

## 🎯 Model Selection Rules

| Task | Model | Why |
|------|-------|-----|
| Heartbeat checks | Local | Free, fast, good enough |
| Task generation | Local | Reads GOALS.md, generates tasks |
| Health monitoring | Local | Simple checks, no cloud needed |
| Chat with Ross | Sonnet | Conversational, contextual |
| Build orchestration | Sonnet | Needs context & spawn capability |
| Revenue builds | Opus | Best quality, ROI justifies cost |
| Code generation | Opus/Codex | Complex work, high quality |
| Research summaries | Local | Data extraction, basic reasoning |

## 🚀 Startup Sequence

**On Mac boot:**
1. launchd starts jarvis-daemon
2. Daemon begins heartbeat loop
3. Daemon runs initial health checks
4. Daemon generates tasks if queue empty

**On Ross's first message:**
1. Sonnet receives message
2. Sonnet checks for escalations
3. Sonnet handles any pending actions
4. Sonnet responds to Ross

## 📁 Key Files

**Daemon:**
- `/Users/clawdbot/clawd/scripts/jarvis-daemon.py` - Main daemon loop
- `/Users/clawdbot/Library/LaunchAgents/com.clawdbot.jarvis-daemon.plist` - launchd config
- `/Users/clawdbot/clawd/scripts/daemon-control.sh` - Start/stop/status

**Communication:**
- `memory/escalation-pending.json` - Daemon → Sonnet messages
- `memory/spawn-signal.json` - Build ready to spawn
- `memory/heartbeat-state.json` - State tracking

**Logs:**
- `monitoring/daemon.log` - Daemon activity
- `monitoring/daemon-stdout.log` - Daemon stdout
- `monitoring/daemon-stderr.log` - Daemon errors

## 🛠️ Maintenance

**Check daemon status:**
```bash
bash ~/clawd/scripts/daemon-control.sh status
```

**View daemon logs:**
```bash
bash ~/clawd/scripts/daemon-control.sh logs
```

**Restart daemon:**
```bash
bash ~/clawd/scripts/daemon-control.sh restart
```

**Check for escalations (Sonnet):**
```bash
python3 ~/clawd/scripts/check_escalations.py
```

## 🎓 Why This Works

1. **Cost Efficiency:** 80% of work runs local, zero cloud cost
2. **Responsiveness:** Local checks run every 5 min, no API latency
3. **Quality:** Cloud models only for human-facing & revenue work
4. **Always-On:** Mac mini runs 24/7, daemon never sleeps
5. **Smart Escalation:** Daemon only bothers Sonnet when needed
6. **Isolated Builds:** Opus spawns handle complex work without cluttering main session

## 🔮 Future Enhancements

- [ ] Auto-tune model selection based on task complexity
- [ ] Add GPT-5/Codex for specialized coding tasks
- [ ] Implement local-fast for ultra-lightweight checks
- [ ] Add model performance metrics to dashboard
- [ ] Create model cost tracking & budget alerts

---

*This architecture allows Jarvis to be autonomous, cost-effective, and always available while keeping the best models for the work that matters most.*
