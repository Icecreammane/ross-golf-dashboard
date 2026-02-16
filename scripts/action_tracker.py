#!/usr/bin/env python3
"""
Action Tracker - Logs all tool calls for Mission Control visibility
Usage: Import and call log_action() after each tool call
"""

import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/clawdbot/clawd')
LOGS_DIR = WORKSPACE / 'logs'
ACTION_LOG = LOGS_DIR / 'action-tracker.jsonl'

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

def estimate_cost(tool, action, tokens=None):
    """
    Estimate cost of an action based on tool and operation
    Claude Sonnet 4.5: $3/MTok input, $15/MTok output
    """
    
    # Free operations
    free_ops = ['read', 'write', 'edit', 'heartbeat']
    if tool in free_ops:
        return 0.0
    
    # Estimate tokens if not provided
    if tokens is None:
        if tool == 'exec':
            tokens = 1000  # Typical exec call
        elif tool == 'web_fetch':
            tokens = 3000  # Fetching web content
        elif tool == 'web_search':
            tokens = 2000  # Search results
        elif tool == 'browser':
            tokens = 5000  # Browser automation
        elif tool == 'message':
            tokens = 1500  # Sending messages
        else:
            tokens = 2000  # Default estimate
    
    # Cost calculation (simplified - assumes 50/50 input/output)
    input_tokens = tokens * 0.5
    output_tokens = tokens * 0.5
    
    input_cost = (input_tokens / 1_000_000) * 3.0
    output_cost = (output_tokens / 1_000_000) * 15.0
    
    return round(input_cost + output_cost, 6)

def log_action(tool, action, result='success', cost_estimate=None, tokens=None, metadata=None):
    """
    Log a tool call to the action tracker
    
    Args:
        tool: Tool name (exec, read, write, web_fetch, etc.)
        action: Description of what was done
        result: 'success' or 'error'
        cost_estimate: Manual cost override
        tokens: Token count if known
        metadata: Additional data to log
    """
    
    if cost_estimate is None:
        cost_estimate = estimate_cost(tool, action, tokens)
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'tool': tool,
        'action': action,
        'result': result,
        'cost_estimate': cost_estimate,
        'tokens_used': tokens,
        'metadata': metadata or {}
    }
    
    try:
        with open(ACTION_LOG, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Warning: Failed to log action: {e}")

def get_recent_actions(limit=20, filter_type=None):
    """
    Get recent actions from the log
    
    Args:
        limit: Number of actions to return
        filter_type: 'high-cost', 'errors', or None for all
    """
    if not ACTION_LOG.exists():
        return []
    
    actions = []
    
    try:
        with open(ACTION_LOG) as f:
            lines = f.readlines()
            for line in reversed(lines[-100:]):  # Last 100 lines
                try:
                    action = json.loads(line.strip())
                    
                    if filter_type:
                        if filter_type == 'high-cost' and action.get('cost_estimate', 0) < 0.01:
                            continue
                        if filter_type == 'errors' and action.get('result') != 'error':
                            continue
                    
                    actions.append(action)
                    if len(actions) >= limit:
                        break
                except:
                    continue
    except:
        pass
    
    return actions

def get_daily_summary():
    """Get summary of today's actions"""
    if not ACTION_LOG.exists():
        return {
            'total_actions': 0,
            'total_cost': 0,
            'errors': 0,
            'by_tool': {}
        }
    
    today = datetime.now().date()
    actions = []
    
    try:
        with open(ACTION_LOG) as f:
            for line in f:
                try:
                    action = json.loads(line.strip())
                    action_date = datetime.fromisoformat(action['timestamp']).date()
                    if action_date == today:
                        actions.append(action)
                except:
                    continue
    except:
        pass
    
    summary = {
        'total_actions': len(actions),
        'total_cost': sum(a.get('cost_estimate', 0) for a in actions),
        'errors': sum(1 for a in actions if a.get('result') == 'error'),
        'by_tool': {}
    }
    
    for action in actions:
        tool = action['tool']
        if tool not in summary['by_tool']:
            summary['by_tool'][tool] = {'count': 0, 'cost': 0}
        summary['by_tool'][tool]['count'] += 1
        summary['by_tool'][tool]['cost'] += action.get('cost_estimate', 0)
    
    return summary

if __name__ == '__main__':
    # Example usage
    log_action('exec', 'ls -la', result='success')
    log_action('web_fetch', 'https://example.com', result='success')
    log_action('read', 'MEMORY.md', result='success')
    
    print("Logged example actions")
    
    # Show recent actions
    recent = get_recent_actions(limit=5)
    print(f"\nRecent {len(recent)} actions:")
    for action in recent:
        print(f"  {action['timestamp']} - {action['tool']}: {action['action']} (${action['cost_estimate']:.4f})")
    
    # Show daily summary
    summary = get_daily_summary()
    print(f"\nDaily Summary:")
    print(f"  Total actions: {summary['total_actions']}")
    print(f"  Total cost: ${summary['total_cost']:.2f}")
    print(f"  Errors: {summary['errors']}")
    print(f"  By tool: {summary['by_tool']}")
