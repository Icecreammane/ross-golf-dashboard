# Sub-Agent Framework - Integration Examples

This document shows how to integrate sub-agent monitoring into existing Jarvis systems.

---

## Heartbeat Integration

### Option 1: Add to HEARTBEAT.md

Add this section to your `HEARTBEAT.md`:

```markdown
## Sub-Agent Monitoring (every 4 hours)

Check sub-agent progress periodically:

1. List running agents: `./scripts/track-subagents.py list --status running --json`
2. Check for completions in last 4 hours
3. Check for stuck agents (>6 hours runtime, no log activity)
4. Report if any completed or need attention

**When to notify Ross:**
- ✅ Agent completed successfully
- ❌ Agent failed or errored
- ⚠️ Agent stuck (>6h no progress)
- ⏰ Agent approaching 12h limit

**Don't spam:** Only notify if something actually happened.
```

### Option 2: Python Integration

Add to your heartbeat handler:

```python
import json
import subprocess
from datetime import datetime, timedelta

def check_subagents():
    """Check sub-agent progress during heartbeat."""
    try:
        # Get running agents
        result = subprocess.run(
            ["python3", "scripts/track-subagents.py", "list", "--status", "running", "--json"],
            cwd="/Users/clawdbot/clawd",
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return None
        
        agents = json.loads(result.stdout)
        notifications = []
        
        for agent in agents:
            # Check if stuck (>6h no log activity)
            log_file = f"/Users/clawdbot/clawd/logs/subagents/{agent['session_id']}.log"
            if os.path.exists(log_file):
                last_modified = datetime.fromtimestamp(os.path.getmtime(log_file))
                age_hours = (datetime.now() - last_modified).total_seconds() / 3600
                
                if age_hours > 6:
                    notifications.append(f"⚠️ Agent stuck: {agent['session_id']} (no activity for {age_hours:.1f}h)")
            
            # Check if approaching limit
            if agent.get('runtime', 0) > 10:
                notifications.append(f"⏰ Agent near limit: {agent['session_id']} ({agent['runtime']:.1f}h/12h)")
        
        # Check completed agents (last 4 hours)
        result = subprocess.run(
            ["python3", "scripts/track-subagents.py", "list", "--status", "completed", "--json"],
            cwd="/Users/clawdbot/clawd",
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            completed = json.loads(result.stdout)
            recent_completions = []
            
            for agent in completed:
                if "completed_at" in agent:
                    completed_at = datetime.fromisoformat(agent["completed_at"])
                    if datetime.now() - completed_at < timedelta(hours=4):
                        recent_completions.append(agent)
            
            for agent in recent_completions:
                task = agent['task'][:60]
                cost = agent.get('actual_cost', agent.get('estimated_cost', 0))
                notifications.append(f"✅ Completed: {task}... (${cost:.2f})")
        
        return notifications if notifications else None
    
    except Exception as e:
        return [f"❌ Error checking sub-agents: {e}"]

# In your heartbeat handler:
subagent_updates = check_subagents()
if subagent_updates:
    # Send to Ross
    for update in subagent_updates:
        print(update)
```

---

## Morning Brief Integration

### Example: Add Sub-Agent Summary

Add this to your morning brief generation:

```python
import json
import subprocess
from datetime import datetime, timedelta

def get_subagent_summary():
    """Generate sub-agent summary for morning brief."""
    try:
        # Get all agents
        result = subprocess.run(
            ["python3", "scripts/track-subagents.py", "summary", "--json"],
            cwd="/Users/clawdbot/clawd",
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return None
        
        summary = json.loads(result.stdout)
        
        # Get completed agents from last 24h
        result = subprocess.run(
            ["python3", "scripts/track-subagents.py", "list", "--status", "completed", "--json"],
            cwd="/Users/clawdbot/clawd",
            capture_output=True,
            text=True
        )
        
        completions = []
        if result.returncode == 0:
            completed = json.loads(result.stdout)
            
            for agent in completed:
                if "completed_at" in agent:
                    completed_at = datetime.fromisoformat(agent["completed_at"])
                    if datetime.now() - completed_at < timedelta(hours=24):
                        completions.append(agent)
        
        # Build summary
        if not completions and summary.get('running', 0) == 0:
            return None  # Nothing to report
        
        brief = "\n## 🤖 Sub-Agent Activity\n\n"
        
        if completions:
            brief += "**Overnight Completions:**\n"
            for agent in completions:
                task = agent['task'][:60]
                cost = agent.get('actual_cost', agent.get('estimated_cost', 0))
                completed_at = datetime.fromisoformat(agent['completed_at'])
                time_str = completed_at.strftime("%I:%M %p")
                
                brief += f"- ✅ {task}... (${cost:.2f}) at {time_str}\n"
                
                # Add link to logs if available
                brief += f"  📝 Logs: `~/clawd/logs/subagents/{agent['session_id']}.log`\n"
            
            brief += "\n"
        
        if summary.get('running', 0) > 0:
            brief += f"**Currently Running:** {summary['running']} agent(s)\n"
            
            # List running agents
            result = subprocess.run(
                ["python3", "scripts/track-subagents.py", "list", "--status", "running", "--json"],
                cwd="/Users/clawdbot/clawd",
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                running = json.loads(result.stdout)
                for agent in running:
                    task = agent['task'][:60]
                    runtime = agent.get('runtime', 0)
                    brief += f"- 🟢 {task}... ({runtime:.1f}h runtime)\n"
            
            brief += "\n"
        
        if summary.get('total_actual_cost', 0) > 0:
            brief += f"**Total Costs:** ${summary['total_estimated_cost']:.2f} estimated, ${summary['total_actual_cost']:.2f} actual\n\n"
        
        return brief
    
    except Exception as e:
        return f"\n## 🤖 Sub-Agent Activity\n\n❌ Error: {e}\n\n"

# In your morning brief:
subagent_summary = get_subagent_summary()
if subagent_summary:
    morning_brief += subagent_summary
```

---

## Memory Integration

### Logging Sub-Agent Activity

Add this to your memory logging:

```python
def log_subagent_activity(agent_data, event_type):
    """
    Log significant sub-agent events to memory.
    
    event_type: 'spawned' | 'completed' | 'failed' | 'killed'
    """
    from datetime import datetime
    
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = f"/Users/clawdbot/clawd/memory/{today}.md"
    
    # Build log entry
    if event_type == "spawned":
        entry = f"- **Spawned sub-agent:** {agent_data['task'][:60]}... ({agent_data['tier']} tier, ${agent_data['estimated_cost']:.2f})"
    elif event_type == "completed":
        entry = f"- **Sub-agent completed:** {agent_data['task'][:60]}... (${agent_data.get('actual_cost', 0):.2f}, {agent_data['runtime']:.1f}h)"
    elif event_type == "failed":
        entry = f"- **Sub-agent failed:** {agent_data['task'][:60]}... ({agent_data.get('error', 'Unknown error')})"
    elif event_type == "killed":
        entry = f"- **Sub-agent killed:** {agent_data['task'][:60]}... ({agent_data['runtime']:.1f}h runtime)"
    else:
        entry = f"- **Sub-agent event ({event_type}):** {agent_data['task'][:60]}..."
    
    # Append to daily memory
    os.makedirs(os.path.dirname(memory_file), exist_ok=True)
    with open(memory_file, 'a') as f:
        f.write(f"\n{entry}\n")
```

### Building Pattern Library

Track what works and what doesn't:

```python
def analyze_completed_agents():
    """
    Analyze completed agents to build pattern library.
    Returns insights about successful patterns.
    """
    result = subprocess.run(
        ["python3", "scripts/track-subagents.py", "list", "--status", "completed", "--json"],
        cwd="/Users/clawdbot/clawd",
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return None
    
    completed = json.loads(result.stdout)
    
    patterns = {
        "successful_tiers": {},
        "successful_models": {},
        "average_costs": {},
        "common_tasks": {}
    }
    
    for agent in completed:
        tier = agent.get('tier', 'unknown')
        model = agent.get('model', 'unknown')
        actual_cost = agent.get('actual_cost')
        estimated_cost = agent.get('estimated_cost', 0)
        
        # Track tier success
        patterns["successful_tiers"][tier] = patterns["successful_tiers"].get(tier, 0) + 1
        
        # Track model usage
        patterns["successful_models"][model] = patterns["successful_models"].get(model, 0) + 1
        
        # Track cost accuracy
        if actual_cost:
            variance = (actual_cost - estimated_cost) / estimated_cost if estimated_cost > 0 else 0
            if tier not in patterns["average_costs"]:
                patterns["average_costs"][tier] = []
            patterns["average_costs"][tier].append(variance)
    
    return patterns
```

---

## Slash Command Integration

### Add to Telegram/Discord Commands

```python
# /subagents - List active sub-agents
@command("subagents")
def list_subagents(message):
    result = subprocess.run(
        ["python3", "scripts/track-subagents.py", "list", "--status", "running"],
        cwd="/Users/clawdbot/clawd",
        capture_output=True,
        text=True
    )
    return result.stdout

# /spawn - Quick spawn
@command("spawn")
def spawn_subagent(message):
    task = message.text.replace("/spawn", "").strip()
    if not task:
        return "Usage: /spawn <task description>"
    
    result = subprocess.run(
        ["bash", "scripts/spawn-agent.sh", task, "--analyze-only"],
        cwd="/Users/clawdbot/clawd",
        capture_output=True,
        text=True
    )
    
    return f"Estimated cost:\n{result.stdout}\n\nTo launch: /spawn-confirm {task}"

# /spawn-confirm - Actually spawn
@command("spawn-confirm")
def spawn_confirm(message):
    task = message.text.replace("/spawn-confirm", "").strip()
    
    result = subprocess.run(
        ["bash", "scripts/spawn-agent.sh", task, "--yes"],
        cwd="/Users/clawdbot/clawd",
        capture_output=True,
        text=True
    )
    
    return result.stdout
```

---

## Notification Examples

### Completion Notification

```python
def notify_completion(agent_data):
    """Send notification when agent completes."""
    task = agent_data['task'][:60]
    cost = agent_data.get('actual_cost', agent_data.get('estimated_cost', 0))
    runtime = agent_data.get('runtime', 0)
    
    message = f"""
✅ **Sub-Agent Complete**

Task: {task}...
Runtime: {runtime:.1f} hours
Cost: ${cost:.2f}

📝 Logs: ~/clawd/logs/subagents/{agent_data['session_id']}.log
    """.strip()
    
    # Send via your notification system
    send_notification(message)
```

### Stuck Agent Alert

```python
def alert_stuck_agent(agent_data):
    """Alert when agent appears stuck."""
    task = agent_data['task'][:60]
    runtime = agent_data.get('runtime', 0)
    
    message = f"""
⚠️ **Sub-Agent May Be Stuck**

Task: {task}...
Runtime: {runtime:.1f} hours
Last activity: >60 minutes ago

Actions:
- Check logs: ./scripts/track-subagents.py logs {agent_data['session_id']}
- Kill if stuck: ./scripts/track-subagents.py kill {agent_data['session_id']}
    """.strip()
    
    send_notification(message)
```

---

## Dashboard Integration

### Web Dashboard Endpoint

If you have a web dashboard:

```python
@app.route('/api/subagents')
def api_subagents():
    """API endpoint for sub-agent dashboard."""
    result = subprocess.run(
        ["python3", "scripts/track-subagents.py", "summary", "--json"],
        cwd="/Users/clawdbot/clawd",
        capture_output=True,
        text=True
    )
    
    summary = json.loads(result.stdout)
    
    # Get running agents
    result = subprocess.run(
        ["python3", "scripts/track-subagents.py", "list", "--status", "running", "--json"],
        cwd="/Users/clawdbot/clawd",
        capture_output=True,
        text=True
    )
    
    running = json.loads(result.stdout) if result.returncode == 0 else []
    
    return {
        "summary": summary,
        "running": running,
        "timestamp": datetime.now().isoformat()
    }
```

---

## Auto-Retry Failed Agents (Future)

```python
def auto_retry_failed_agent(agent_data, max_retries=2):
    """
    Automatically retry a failed agent with adjusted parameters.
    """
    retry_count = agent_data.get('retry_count', 0)
    
    if retry_count >= max_retries:
        # Give up
        log_memory(f"Agent failed after {max_retries} retries: {agent_data['task']}")
        return False
    
    # Adjust parameters for retry
    new_tier = "deep" if agent_data['tier'] == "quick" else "enforcer"
    new_model = "anthropic/claude-sonnet-4-5"  # Use best model for retry
    
    # Spawn retry
    result = subprocess.run(
        ["python3", "scripts/spawn_agent.py",
         agent_data['task'],
         "--tier", new_tier,
         "--model", new_model,
         "--label", f"RETRY-{agent_data['session_id']}",
         "--yes"],
        cwd="/Users/clawdbot/clawd"
    )
    
    return result.returncode == 0
```

---

## Testing Integrations

Test each integration individually:

```bash
# Test heartbeat check
python3 -c "from integration_examples import check_subagents; print(check_subagents())"

# Test morning brief
python3 -c "from integration_examples import get_subagent_summary; print(get_subagent_summary())"

# Test memory logging
python3 -c "from integration_examples import log_subagent_activity; log_subagent_activity({'task': 'Test', 'tier': 'quick', 'estimated_cost': 5}, 'spawned')"
```

---

## Best Practices

1. **Don't spam notifications** - Only notify when actionable
2. **Batch updates** - Combine multiple updates into one message
3. **Include session IDs** - Always link to logs for debugging
4. **Track costs** - Include costs in all summaries
5. **Learn from history** - Build pattern library over time

---

**Ready to integrate!** Pick the methods that fit your workflow.
