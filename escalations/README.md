# Escalation System

This directory contains signal files written by the autonomous daemon when it needs Sonnet's help.

## Signal Format

Each signal is a JSON file with this structure:

```json
{
  "type": "signal_type",
  "priority": "low|medium|high|urgent",
  "created": "2026-02-07T18:30:00",
  "data": {
    "message": "Human-readable description",
    "key": "additional context"
  }
}
```

## Signal Types

### `goals_updated`
GOALS.md changed with high-priority items
- **Action:** Notify Ross
- **Priority:** high

### `task_queue_growing`
Too many pending tasks in TASK_QUEUE.md
- **Action:** Notify Ross, offer to delegate
- **Priority:** medium

### `generate_tasks`
Task queue is empty or low, need new tasks
- **Action:** Spawn agent to generate tasks from GOALS.md
- **Priority:** low

### `system_health`
System issues detected (disk space, process down, etc.)
- **Action:** Notify Ross immediately
- **Priority:** high

### `daemon_crashed`
Daemon encountered fatal error
- **Action:** Alert Ross, restart daemon
- **Priority:** urgent

## Workflow

1. **Daemon writes signal** → creates `{timestamp}_{type}.json`
2. **Heartbeat checks** → runs `check_escalations.py`
3. **Sonnet handles** → executes action (notify/spawn/fix)
4. **Signal cleared** → file deleted after handling

## Adding New Signals

To add a new signal type:
1. Update `autonomous_daemon.py` to write the signal
2. Update `check_escalations.py` to handle it
3. Document it here
4. Test end-to-end

## Testing

Write a test signal:
```bash
cat > ~/clawd/escalations/test_signal.json << 'EOF'
{
  "type": "goals_updated",
  "priority": "medium",
  "created": "2026-02-07T18:30:00",
  "data": {
    "message": "This is a test signal"
  }
}
EOF
```

Check it:
```bash
python3 ~/clawd/scripts/check_escalations.py
```

Should return the escalation details.
