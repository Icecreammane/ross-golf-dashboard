#!/usr/bin/env python3
"""
Escalation Checker - Read signals from daemon and determine action

Called by heartbeat to check if daemon needs Sonnet's help.
Returns JSON with escalation details or {"status": "no_escalations"}
"""

import json
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / "clawd"
ESCALATIONS = WORKSPACE / "escalations"

def load_signals():
    """Load all pending signal files"""
    if not ESCALATIONS.exists():
        return []
    
    signals = []
    for signal_file in ESCALATIONS.glob("*.json"):
        try:
            with open(signal_file) as f:
                signal = json.load(f)
                signal["file"] = str(signal_file)
                signals.append(signal)
        except Exception as e:
            print(f"Error loading {signal_file}: {e}", file=sys.stderr)
    
    # Sort by priority (urgent > high > medium > low)
    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    signals.sort(key=lambda s: priority_order.get(s.get("priority", "medium"), 2))
    
    return signals

def format_escalation(signal):
    """Format signal for Sonnet to handle"""
    signal_type = signal.get("type", "unknown")
    data = signal.get("data", {})
    priority = signal.get("priority", "medium")
    created = signal.get("created", "unknown")
    
    # Build action message based on signal type
    actions = {
        "goals_updated": {
            "action": "notify",
            "message": f"🎯 {data.get('message', 'Goals updated')}",
            "requires_response": False
        },
        "task_queue_growing": {
            "action": "notify",
            "message": f"📋 Task backlog: {data.get('pending_tasks')} tasks pending",
            "requires_response": True
        },
        "generate_tasks": {
            "action": "spawn",
            "task": "Generate new tasks from GOALS.md and add to TASK_QUEUE.md",
            "requires_response": False
        },
        "system_health": {
            "action": "notify",
            "message": f"⚠️ System issues: {', '.join(data.get('issues', []))}",
            "requires_response": True
        },
        "daemon_crashed": {
            "action": "notify",
            "message": f"🚨 Daemon crashed: {data.get('error', 'Unknown error')}",
            "requires_response": True
        }
    }
    
    escalation = actions.get(signal_type, {
        "action": "notify",
        "message": f"Signal: {signal_type}",
        "requires_response": False
    })
    
    escalation.update({
        "signal_file": signal["file"],
        "priority": priority,
        "created": created,
        "type": signal_type
    })
    
    return escalation

def main():
    """Check for escalations and return action"""
    signals = load_signals()
    
    if not signals:
        print(json.dumps({"status": "no_escalations"}))
        return
    
    # Return highest priority escalation
    escalation = format_escalation(signals[0])
    escalation["pending_count"] = len(signals)
    
    print(json.dumps(escalation, indent=2))

if __name__ == "__main__":
    main()
