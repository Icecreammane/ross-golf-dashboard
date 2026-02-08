#!/usr/bin/env python3
"""
God Mode Real-Time Tracker

Logs events in real-time to build better behavioral model:
- Decisions made
- Tasks started/completed
- Energy level changes
- Context switches
- Distractions

Call this from anywhere to log events. Data feeds into God Mode analyzer.
"""

import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / "clawd"
TRACKER_LOG = WORKSPACE / "god_mode" / "realtime_log.jsonl"

TRACKER_LOG.parent.mkdir(exist_ok=True)

def log_event(event_type, data, metadata=None):
    """
    Log a behavioral event
    
    event_type: decision, task_start, task_complete, energy_change, distraction, context_switch
    data: dict with event-specific data
    metadata: optional additional context
    """
    
    event = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "data": data,
        "metadata": metadata or {}
    }
    
    # Append to JSONL log
    with open(TRACKER_LOG, 'a') as f:
        f.write(json.dumps(event) + '\n')
    
    return event

def log_decision(decision_text, outcome=None, confidence=None):
    """Log a decision"""
    return log_event("decision", {
        "text": decision_text,
        "outcome": outcome,
        "confidence": confidence
    })

def log_task_start(task_name, estimated_time=None):
    """Log task started"""
    return log_event("task_start", {
        "task": task_name,
        "estimated_time": estimated_time
    })

def log_task_complete(task_name, actual_time=None, quality=None):
    """Log task completed"""
    return log_event("task_complete", {
        "task": task_name,
        "actual_time": actual_time,
        "quality": quality
    })

def log_energy_change(level, reason=None):
    """
    Log energy level change
    level: 0-100 or "low", "medium", "high"
    """
    if isinstance(level, str):
        level_map = {"low": 30, "medium": 60, "high": 90}
        level = level_map.get(level.lower(), 50)
    
    return log_event("energy_change", {
        "level": level,
        "reason": reason
    })

def log_distraction(source, duration_seconds=None):
    """Log distraction (phone, social media, etc.)"""
    return log_event("distraction", {
        "source": source,
        "duration": duration_seconds
    })

def log_context_switch(from_activity, to_activity, reason=None):
    """Log context switch (task switching)"""
    return log_event("context_switch", {
        "from": from_activity,
        "to": to_activity,
        "reason": reason
    })

def log_win(win_text, impact="medium"):
    """Log a win"""
    return log_event("win", {
        "text": win_text,
        "impact": impact  # low, medium, high
    })

def get_todays_events():
    """Get all events logged today"""
    if not TRACKER_LOG.exists():
        return []
    
    today = datetime.now().date()
    events = []
    
    with open(TRACKER_LOG) as f:
        for line in f:
            try:
                event = json.loads(line.strip())
                event_date = datetime.fromisoformat(event['timestamp']).date()
                if event_date == today:
                    events.append(event)
            except:
                continue
    
    return events

def get_event_summary():
    """Get summary of today's events"""
    events = get_todays_events()
    
    summary = {
        "total_events": len(events),
        "decisions": len([e for e in events if e['type'] == 'decision']),
        "tasks_started": len([e for e in events if e['type'] == 'task_start']),
        "tasks_completed": len([e for e in events if e['type'] == 'task_complete']),
        "distractions": len([e for e in events if e['type'] == 'distraction']),
        "wins": len([e for e in events if e['type'] == 'win']),
        "context_switches": len([e for e in events if e['type'] == 'context_switch']),
        "energy_changes": [e for e in events if e['type'] == 'energy_change']
    }
    
    return summary

def main():
    """CLI interface for tracker"""
    import sys
    
    if len(sys.argv) < 2:
        print("God Mode Tracker - Real-time behavioral logging")
        print("\nUsage:")
        print("  python3 god_mode_tracker.py decision 'Decided to build X'")
        print("  python3 god_mode_tracker.py task_start 'Build feature Y'")
        print("  python3 god_mode_tracker.py task_complete 'Build feature Y' 3600")
        print("  python3 god_mode_tracker.py energy high 'After workout'")
        print("  python3 god_mode_tracker.py win 'Shipped new feature'")
        print("  python3 god_mode_tracker.py distraction 'phone' 600")
        print("  python3 god_mode_tracker.py summary")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "summary":
        summary = get_event_summary()
        print(json.dumps(summary, indent=2))
    
    elif command == "decision":
        text = sys.argv[2] if len(sys.argv) > 2 else "Decision logged"
        event = log_decision(text)
        print(f"✅ Logged: {event['type']} at {event['timestamp']}")
    
    elif command == "task_start":
        task = sys.argv[2] if len(sys.argv) > 2 else "Task"
        event = log_task_start(task)
        print(f"▶️  Started: {task}")
    
    elif command == "task_complete":
        task = sys.argv[2] if len(sys.argv) > 2 else "Task"
        time = sys.argv[3] if len(sys.argv) > 3 else None
        event = log_task_complete(task, time)
        print(f"✅ Completed: {task}")
    
    elif command == "energy":
        level = sys.argv[2] if len(sys.argv) > 2 else "medium"
        reason = sys.argv[3] if len(sys.argv) > 3 else None
        event = log_energy_change(level, reason)
        print(f"⚡ Energy: {level}")
    
    elif command == "win":
        text = sys.argv[2] if len(sys.argv) > 2 else "Win logged"
        event = log_win(text)
        print(f"🏆 Win: {text}")
    
    elif command == "distraction":
        source = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        duration = int(sys.argv[3]) if len(sys.argv) > 3 else None
        event = log_distraction(source, duration)
        print(f"📱 Distraction: {source}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
