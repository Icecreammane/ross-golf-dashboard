# Subagents Directory

This directory tracks all active and completed subagent sessions.

## Files

- **active.json** - Currently running subagents
- **[label]-progress.md** - Progress logs for each active subagent
- **[label]-complete.md** - Completion summaries

## Checking Status

To see what's building right now:
```bash
cat ~/clawd/subagents/active.json
```

To see progress on a specific agent:
```bash
cat ~/clawd/subagents/[label]-progress.md
```

## For Ross

Just ask Jarvis "How's building going?" and he'll pull the latest status from these files.
