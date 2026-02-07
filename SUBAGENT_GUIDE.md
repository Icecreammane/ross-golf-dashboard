# Sub-Agent Framework - Complete Guide

## Table of Contents

1. [Quick Start](#quick-start)
2. [When to Use Sub-Agents](#when-to-use-sub-agents)
3. [The Three-Tier System](#the-three-tier-system)
4. [Cost Management](#cost-management)
5. [Model Selection](#model-selection)
6. [Spawning Sub-Agents](#spawning-sub-agents)
7. [Tracking Progress](#tracking-progress)
8. [Safety & Guardrails](#safety--guardrails)
9. [Common Workflows](#common-workflows)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Spawn a sub-agent in 3 steps:

```bash
# 1. Estimate the cost
./scripts/spawn-agent.sh "Fix the calendar sync bug" --analyze-only

# 2. Review the estimate (automatic)

# 3. Launch it
./scripts/spawn-agent.sh "Fix the calendar sync bug"
```

### Interactive mode (recommended for beginners):

```bash
./scripts/spawn-agent.sh --interactive
```

---

## When to Use Sub-Agents

### ✅ Use sub-agents for:

- **Background tasks** - Let it work while you do other things
- **Long-running builds** - Tasks that take >1 hour
- **Defined deliverables** - Clear goal and success criteria
- **Isolated work** - Won't interfere with your main session
- **Time you're unavailable** - Overnight, during meetings, at concerts 🎸

### ❌ Don't use sub-agents for:

- **Quick questions** - Just ask Jarvis directly
- **Exploratory work** - When you're not sure what you want yet
- **Iterative feedback** - When you need to review and adjust frequently
- **Personal context** - Accessing your MEMORY.md or private info
- **Interactive debugging** - When you need back-and-forth troubleshooting

### The Rule of Thumb:

**If the task would take >30 minutes of focused work and has a clear definition, spawn a sub-agent.**

---

## The Three-Tier System

### 🟢 Quick Builder (1-2 hours, $2-5)

**Best for:**
- Bug fixes
- Small optimizations
- Documentation updates
- Code cleanup
- Simple feature additions

**Model:** Gemini 2.0 Flash (cheap, fast, good enough)

**Examples:**
```bash
./scripts/spawn-agent.sh "Fix the health monitor timeout bug" --tier quick
./scripts/spawn-agent.sh "Update API documentation" --tier quick
./scripts/spawn-agent.sh "Optimize database query in user.py" --tier quick
```

---

### 🟡 Deep Builder (4-6 hours, $10-20)

**Best for:**
- Complex features
- System integrations
- Multi-file refactors
- API implementations
- Architectural work

**Model:** Claude Sonnet 4.5 (best reasoning) or Codex (code-heavy)

**Examples:**
```bash
./scripts/spawn-agent.sh "Build Spotify integration for music control" --tier deep
./scripts/spawn-agent.sh "Refactor authentication to use OAuth2" --tier deep
./scripts/spawn-agent.sh "Implement GitHub webhook handler" --tier deep
```

---

### 🔴 The Enforcer (8-12 hours, $30-50)

**Best for:**
- Full system builds
- Major infrastructure changes
- Multi-system integrations
- Complete feature sets

**Model:** Claude Sonnet 4.5 (best for complex reasoning)

**Examples:**
```bash
./scripts/spawn-agent.sh "Build complete task management dashboard" --tier enforcer
./scripts/spawn-agent.sh "Create automated backup and monitoring system" --tier enforcer
./scripts/spawn-agent.sh "Implement multi-service notification aggregator" --tier enforcer
```

---

## Cost Management

### Before Spawning

**Always estimate first:**
```bash
./scripts/spawn-agent.sh "Your task" --analyze-only
```

This shows:
- Estimated time
- Estimated cost
- Recommended tier
- Recommended model

### Cost Breakdown

Token usage is split ~20% input, ~80% output for typical coding tasks.

**Pricing (Feb 2026):**
- **Sonnet 4.5:** $3/M input, $15/M output
- **Gemini Flash:** $0.075/M input, $0.30/M output
- **Codex:** $2.50/M input, $10/M output

**Token estimates:**
- 1 hour = ~25k tokens
- Quick (1-2h) = 25-50k tokens → $0.50-5
- Deep (4-6h) = 100-150k tokens → $10-20
- Enforcer (8-12h) = 200-300k tokens → $30-50

### Safety Limits

- **Max cost per task:** $50 (hard limit)
- **Max concurrent agents:** 3
- **Max runtime:** 12 hours (auto-kill after)

### Tracking Costs

```bash
# Get cost summary
./scripts/track-subagents.py summary

# Check specific agent
./scripts/track-subagents.py status <session-id>
```

---

## Model Selection

The system auto-selects models based on task characteristics, but you can override.

### Decision Tree

1. **Complex reasoning** (architecture, system design) → **Sonnet 4.5**
2. **Code-heavy** (APIs, algorithms) → **Codex** (or Sonnet)
3. **Simple/routine** (bug fixes, cleanup) → **Gemini Flash**

### Model Strengths

**Claude Sonnet 4.5:**
- ✅ Best reasoning
- ✅ Architecture & system design
- ✅ Complex problem-solving
- ✅ Multi-step planning
- ❌ More expensive

**Gemini 2.0 Flash:**
- ✅ Very fast
- ✅ Very cheap
- ✅ Good for simple tasks
- ✅ Quick iteration
- ❌ Weaker reasoning

**GPT-5.2 Codex:**
- ✅ Strong code generation
- ✅ Good for algorithms
- ✅ API implementations
- ❌ Medium cost

### Manual Override

```bash
# Force Sonnet
./scripts/spawn-agent.sh "Task" --model anthropic/claude-sonnet-4-5

# Force Gemini (cheap)
./scripts/spawn-agent.sh "Task" --model google/gemini-2.0-flash-exp:free

# Let the system choose (recommended)
./scripts/spawn-agent.sh "Task"
```

---

## Spawning Sub-Agents

### Method 1: Direct Command

```bash
./scripts/spawn-agent.sh "Task description" [OPTIONS]
```

**Options:**
- `--tier` - Force tier (quick/deep/enforcer)
- `--model` - Force model
- `--label` - Human-readable label
- `--analyze-only` - Just estimate, don't spawn
- `--yes` / `-y` - Skip confirmation

### Method 2: Interactive Mode

```bash
./scripts/spawn-agent.sh --interactive
```

Guides you through:
1. Task description
2. Automatic analysis
3. Confirmation
4. Spawning

### Method 3: Python API

```python
from spawn_agent import SubAgentSpawner

spawner = SubAgentSpawner()

# Analyze task
analysis = spawner.analyze_task("Build calendar integration")
print(analysis)

# Spawn agent
result = spawner.spawn(
    "Build calendar integration",
    tier="deep",
    auto_approve=False  # Prompt for confirmation
)

print(result)
```

### Using Templates

Templates provide pre-written prompts for common tasks:

```bash
# List available templates
cat ~/clawd/subagents/task-templates.json | python3 -m json.tool

# Use a template (manually for now)
# Copy template, fill in placeholders, spawn
```

**Available templates:**
- `bug_fix`
- `feature_build`
- `optimization`
- `integration`
- `full_system`
- `refactor`
- `documentation`
- `testing`
- `research`
- `security_audit`

---

## Tracking Progress

### List All Agents

```bash
./scripts/track-subagents.py list
```

Shows all agents with status, runtime, costs.

### Check Specific Agent

```bash
./scripts/track-subagents.py status <session-id>
```

Shows detailed status and recent logs.

### View Logs

```bash
./scripts/track-subagents.py logs <session-id>
```

Last 50 lines by default. Use `--lines N` for more.

### Get Summary

```bash
./scripts/track-subagents.py summary
```

Total agents, costs, status breakdown.

### Kill a Running Agent

```bash
./scripts/track-subagents.py kill <session-id>
```

Immediately stops the agent.

---

## Safety & Guardrails

### Automatic Safety Checks

Before spawning, the system checks:
- ✅ Cost < $50
- ✅ Less than 3 concurrent agents
- ✅ Task has clear description

### Guardian Monitoring

The guardian monitors running agents:

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

**Guardian checks:**
- ⏰ Runtime limits (auto-kill >12h)
- 🔢 Concurrent limit (max 3)
- 💤 Stuck agents (no activity >60 min)
- 💰 Cost warnings (>$50)

### Manual Intervention

If something goes wrong:

```bash
# Kill all running agents
for agent in $(./scripts/track-subagents.py list --status running --json | python3 -c "import sys, json; [print(a['session_id']) for a in json.load(sys.stdin)]"); do
    ./scripts/track-subagents.py kill $agent
done
```

---

## Common Workflows

### Workflow 1: Quick Bug Fix While You're Busy

```bash
# 1. Estimate
./scripts/spawn-agent.sh "Fix the calendar timeout bug" --analyze-only

# 2. Launch
./scripts/spawn-agent.sh "Fix the calendar timeout bug" --yes

# 3. Check later
./scripts/track-subagents.py list
```

---

### Workflow 2: Overnight Complex Feature

```bash
# Before bed:
./scripts/spawn-agent.sh "Build Spotify integration with play/pause/search" --tier deep

# In the morning:
./scripts/track-subagents.py status <session-id>

# If complete:
# Review the code, test it, merge it
```

---

### Workflow 3: Weekend Monster Build

```bash
# Friday afternoon:
./scripts/spawn-agent.sh "Create complete task management dashboard" --tier enforcer

# Enable monitoring:
./scripts/subagent-guardian.py monitor --interval 60 &

# Monday morning:
./scripts/track-subagents.py summary
```

---

### Workflow 4: Multiple Small Tasks

```bash
# Spawn several quick builders
./scripts/spawn-agent.sh "Fix auth bug" --tier quick --yes
./scripts/spawn-agent.sh "Update API docs" --tier quick --yes
./scripts/spawn-agent.sh "Optimize search query" --tier quick --yes

# Track them all
./scripts/track-subagents.py list --status running
```

---

## Troubleshooting

### Problem: Agent stuck / no progress

**Check logs:**
```bash
./scripts/track-subagents.py logs <session-id>
```

**If truly stuck:**
```bash
./scripts/track-subagents.py kill <session-id>
```

---

### Problem: Cost higher than expected

**Possible causes:**
- Task more complex than estimated
- Agent iterating on errors
- Long debugging sessions

**Solution:**
- Kill if cost is runaway
- Review task description (be more specific next time)
- Use cheaper model for simpler tasks

---

### Problem: Agent completed but result is wrong

**This isn't a retry system.** Sub-agents are one-shot.

**Solutions:**
- Review the code/output
- Fix manually
- Spawn a new agent with more specific requirements
- Use main Jarvis for iterative work

---

### Problem: Can't spawn (concurrent limit)

**Check running agents:**
```bash
./scripts/track-subagents.py list --status running
```

**Kill one or wait for completion:**
```bash
./scripts/track-subagents.py kill <session-id>
```

---

### Problem: Agent exceeded 12 hours

**Automatically killed by guardian.**

**Possible causes:**
- Task too complex for tier
- Agent stuck in loop
- Underestimated scope

**Solution:**
- Review logs to see what happened
- Spawn new agent with better-scoped task
- Consider breaking into smaller sub-tasks

---

## Best Practices

### ✅ Do:

- **Be specific** in task descriptions
- **Define clear deliverables**
- **Estimate costs first** (`--analyze-only`)
- **Monitor long-running agents** periodically
- **Review completed work** before deploying
- **Use templates** for common tasks
- **Start small** (Quick tier) until confident

### ❌ Don't:

- **Spawn for everything** - Use main Jarvis for quick stuff
- **Forget to track** - Check progress regularly
- **Ignore cost estimates** - They're there for a reason
- **Spawn during debugging** - Iterative work needs human feedback
- **Leave agents unmonitored** - Check in at least once
- **Expect perfection** - Sub-agents are good, not magic

---

## Integration with Heartbeat & Morning Brief

### Heartbeat Integration

Jarvis checks sub-agent progress during heartbeats and will notify you when:
- Agent completes
- Agent fails
- Agent exceeds expected time

### Morning Brief Integration

Your morning brief includes:
- Overnight sub-agent completions
- Costs and deliverables
- Links to outputs
- Any errors or issues

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./scripts/spawn-agent.sh "Task"` | Spawn an agent |
| `./scripts/spawn-agent.sh --interactive` | Interactive mode |
| `./scripts/spawn-agent.sh "Task" --analyze-only` | Estimate cost only |
| `./scripts/track-subagents.py list` | List all agents |
| `./scripts/track-subagents.py status <id>` | Check agent status |
| `./scripts/track-subagents.py logs <id>` | View agent logs |
| `./scripts/track-subagents.py kill <id>` | Kill running agent |
| `./scripts/track-subagents.py summary` | Get cost summary |
| `./scripts/subagent-guardian.py check` | Run safety checks |
| `./scripts/subagent-guardian.py report` | Health report |

---

## Support

If you run into issues:

1. Check the logs: `./scripts/track-subagents.py logs <session-id>`
2. Review this guide
3. Ask Jarvis: "What happened with sub-agent <session-id>?"
4. Check guardian logs: `cat ~/clawd/logs/subagents/guardian.log`

---

**Happy building! 🚀**
