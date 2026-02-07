# Sub-Agent Framework - Quick Reference Card

## 🚀 Launch Commands

```bash
# Interactive (recommended for first time)
./scripts/spawn-agent.sh --interactive

# Direct launch
./scripts/spawn-agent.sh "Task description"

# With options
./scripts/spawn-agent.sh "Task" --tier quick --yes

# Estimate only (no spawn)
./scripts/spawn-agent.sh "Task" --analyze-only
```

---

## 📊 The Three Tiers

| Tier | Time | Cost | Use For |
|------|------|------|---------|
| 🟢 **Quick** | 1-2h | $2-5 | Bug fixes, docs, cleanup |
| 🟡 **Deep** | 4-6h | $10-20 | Features, integrations, refactors |
| 🔴 **Enforcer** | 8-12h | $30-50 | Full systems, infrastructure |

---

## 🤖 Models

| Model | Best For | Cost |
|-------|----------|------|
| **Sonnet 4.5** | Complex reasoning, architecture | $$$ |
| **Gemini Flash** | Simple tasks, speed | $ |
| **Codex** | Code-heavy, algorithms | $$ |

---

## 📈 Tracking Commands

```bash
# List all agents
./scripts/track-subagents.py list

# List only running
./scripts/track-subagents.py list --status running

# Check specific agent
./scripts/track-subagents.py status <session-id>

# View logs
./scripts/track-subagents.py logs <session-id>

# Kill agent
./scripts/track-subagents.py kill <session-id>

# Get summary (costs, counts)
./scripts/track-subagents.py summary
```

---

## 🛡️ Safety & Monitoring

```bash
# Run safety checks
./scripts/subagent-guardian.py check

# Get health report
./scripts/subagent-guardian.py report

# Auto-recover stuck agents
./scripts/subagent-guardian.py recover

# Continuous monitoring
./scripts/subagent-guardian.py monitor --interval 30
```

---

## 💰 Cost Estimates

| Task Type | Example | Tier | Cost |
|-----------|---------|------|------|
| Bug fix | "Fix calendar timeout" | Quick | $0.50-2 |
| Small feature | "Add export button" | Quick | $2-5 |
| Complex feature | "Build Spotify integration" | Deep | $10-20 |
| Integration | "Add OAuth2 auth" | Deep | $10-20 |
| Full system | "Task management dashboard" | Enforcer | $30-50 |

---

## 🎯 Task Templates

Located: `~/clawd/subagents/task-templates.json`

Available templates:
- `bug_fix` - Bug fixes with testing
- `feature_build` - New features
- `optimization` - Performance improvements
- `integration` - External service integration
- `full_system` - Complete systems
- `refactor` - Code restructuring
- `documentation` - Write docs
- `testing` - Write test suites
- `research` - Research & recommendations
- `security_audit` - Security review

---

## 🔧 Common Options

```bash
--tier <quick|deep|enforcer>   # Force tier
--model <model-name>           # Force model
--label "Name"                 # Human-readable label
--analyze-only                 # Just estimate, don't spawn
--yes / -y                     # Skip confirmation
--json                         # JSON output
```

---

## ⚠️ Safety Limits

- **Max concurrent:** 3 agents
- **Max cost:** $50 per task
- **Max runtime:** 12 hours (auto-kill)
- **Stuck threshold:** 60 min no activity

---

## 🔥 Quick Workflows

### Quick Bug Fix
```bash
./scripts/spawn-agent.sh "Fix bug in user.py" --tier quick --yes
```

### Overnight Feature
```bash
./scripts/spawn-agent.sh "Build calendar sync" --tier deep
# Check in morning: ./scripts/track-subagents.py list
```

### Weekend Build
```bash
./scripts/spawn-agent.sh "Complete dashboard system" --tier enforcer
./scripts/subagent-guardian.py monitor --interval 60 &
```

---

## 📁 File Locations

```
~/clawd/
├── scripts/
│   ├── spawn-agent.sh              # Main CLI launcher
│   ├── spawn_agent.py              # Python API
│   ├── track-subagents.py          # Progress tracking
│   ├── subagent-guardian.py        # Safety monitoring
│   ├── tier-classifier.py          # Tier recommendation
│   ├── select-model.py             # Model selection
│   └── subagent-cost-calculator.py # Cost estimation
├── subagents/
│   ├── task-templates.json         # Task templates
│   ├── active_agents.json          # Active agent state
│   └── <session-id>_context.md     # Agent contexts
└── logs/subagents/
    ├── <session-id>.log            # Agent logs
    └── guardian.log                # Guardian logs
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Agent stuck | `./scripts/track-subagents.py kill <id>` |
| High cost | Review task description, use cheaper model |
| Can't spawn | Kill running agent or wait for completion |
| Wrong result | Review output, spawn new agent with better prompt |
| Exceeded 12h | Auto-killed. Review logs, re-scope task |

---

## 💡 Best Practices

✅ **Do:**
- Be specific in task descriptions
- Estimate costs first
- Monitor long-running agents
- Review completed work

❌ **Don't:**
- Spawn for everything
- Ignore cost estimates
- Leave agents unmonitored
- Expect perfection

---

## 📞 Get Help

```bash
# Command help
./scripts/spawn-agent.sh --help
./scripts/track-subagents.py --help
./scripts/subagent-guardian.py --help

# View full guide
cat ~/clawd/SUBAGENT_GUIDE.md

# Ask Jarvis
"How do I spawn a sub-agent?"
"What happened with sub-agent <session-id>?"
```

---

## 🎯 The Goal

Ross says:

> "Build a calendar integration system"

Jarvis responds:

> "📊 **Cost Estimate:**
> - Tier: Deep Builder (🟡)
> - Model: Sonnet 4.5
> - Time: ~5 hours
> - Cost: ~$15
> 
> Ready to launch? [Y/n]"

Sub-agent builds. Ross comes back to:

> "✅ Calendar integration complete. Cost: $14.23. Ready to test."

**That's the bar.** 🚀
