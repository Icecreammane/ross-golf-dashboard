#!/usr/bin/env python3
"""
Commitment Tracker - Prevent excessive pivoting
Lock in on builds and finish them
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
COMMITMENT_FILE = WORKSPACE / "memory" / "current-commitment.json"
HISTORY_FILE = WORKSPACE / "memory" / "commitment-history.json"

def start_commitment(task, estimated_hours, level="locked"):
    """
    Start a new commitment
    
    Args:
        task: Description of what we're building
        estimated_hours: How long it should take
        level: "locked" (no pivots) or "flexible" (can pivot with reason)
    """
    commitment = {
        "task": task,
        "started": datetime.now().isoformat(),
        "estimated_hours": estimated_hours,
        "estimated_completion": (datetime.now() + timedelta(hours=estimated_hours)).isoformat(),
        "commitment_level": level,
        "can_pivot": False if level == "locked" else True,
        "pivot_requires": "Ross explicit instruction" if level == "locked" else "Good reason",
        "status": "active"
    }
    
    COMMITMENT_FILE.parent.mkdir(exist_ok=True)
    with open(COMMITMENT_FILE, 'w') as f:
        json.dump(commitment, f, indent=2)
    
    print(f"🔒 Commitment locked: {task}")
    print(f"   Estimated: {estimated_hours} hours")
    print(f"   Level: {level}")
    return commitment

def get_current_commitment():
    """Get current active commitment"""
    if not COMMITMENT_FILE.exists():
        return None
    
    with open(COMMITMENT_FILE) as f:
        return json.load(f)

def can_pivot(reason=None):
    """Check if we can pivot away from current commitment"""
    commitment = get_current_commitment()
    
    if not commitment:
        return True, "No active commitment"
    
    if commitment["status"] != "active":
        return True, "Commitment not active"
    
    # Check if past estimated completion (2x over)
    started = datetime.fromisoformat(commitment["started"])
    elapsed = (datetime.now() - started).total_seconds() / 3600
    estimated = commitment["estimated_hours"]
    
    if elapsed > estimated * 2:
        return True, f"Exceeded 2x time estimate ({elapsed:.1f}h / {estimated}h)"
    
    # Check commitment level
    if commitment["can_pivot"]:
        if reason:
            return True, f"Flexible commitment + reason: {reason}"
        else:
            return False, "Flexible commitment requires reason"
    else:
        return False, f"Locked commitment. {commitment['pivot_requires']}"

def complete_commitment(outcome="completed"):
    """Mark current commitment as complete"""
    commitment = get_current_commitment()
    
    if not commitment:
        print("⚠️  No active commitment to complete")
        return
    
    # Calculate actual time
    started = datetime.fromisoformat(commitment["started"])
    elapsed = (datetime.now() - started).total_seconds() / 3600
    
    commitment["status"] = outcome
    commitment["completed"] = datetime.now().isoformat()
    commitment["actual_hours"] = round(elapsed, 2)
    commitment["on_time"] = elapsed <= commitment["estimated_hours"] * 1.5
    
    # Log to history
    HISTORY_FILE.parent.mkdir(exist_ok=True)
    history = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            history = json.load(f)
    
    history.append(commitment)
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
    
    # Clear current
    COMMITMENT_FILE.unlink()
    
    print(f"✅ Commitment completed: {commitment['task']}")
    print(f"   Estimated: {commitment['estimated_hours']}h")
    print(f"   Actual: {commitment['actual_hours']}h")
    if commitment['on_time']:
        print(f"   ✅ Delivered on time!")
    else:
        print(f"   ⚠️  Went over estimate")

def pivot(reason, new_task=None):
    """
    Attempt to pivot away from current commitment
    Requires explicit reason
    """
    commitment = get_current_commitment()
    
    if not commitment:
        print("No active commitment to pivot from")
        return True
    
    allowed, message = can_pivot(reason)
    
    if not allowed:
        print(f"❌ Cannot pivot: {message}")
        print(f"   Current: {commitment['task']}")
        print(f"   To pivot, need: {commitment['pivot_requires']}")
        return False
    
    print(f"⚠️  Pivoting away from: {commitment['task']}")
    print(f"   Reason: {reason}")
    
    # Mark as abandoned
    complete_commitment("pivoted")
    
    if new_task:
        print(f"   New direction: {new_task}")
    
    return True

def status():
    """Show current commitment status"""
    commitment = get_current_commitment()
    
    if not commitment:
        print("✅ No active commitment - free to start new work")
        return
    
    started = datetime.fromisoformat(commitment["started"])
    elapsed = (datetime.now() - started).total_seconds() / 3600
    estimated = commitment["estimated_hours"]
    
    print(f"🔒 Active Commitment:")
    print(f"   Task: {commitment['task']}")
    print(f"   Started: {started.strftime('%I:%M %p')}")
    print(f"   Elapsed: {elapsed:.1f}h / {estimated}h")
    print(f"   Level: {commitment['commitment_level']}")
    print(f"   Can pivot: {'Yes' if commitment['can_pivot'] else 'No'}")
    
    if elapsed > estimated:
        print(f"   ⚠️  Running over estimate")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Commitment Tracker - Usage:")
        print()
        print("  python3 commitment_tracker.py start <task> <hours> [locked|flexible]")
        print("  python3 commitment_tracker.py status")
        print("  python3 commitment_tracker.py complete")
        print("  python3 commitment_tracker.py pivot <reason>")
        print()
        print("Examples:")
        print('  python3 commitment_tracker.py start "Build revenue dashboard" 4 locked')
        print('  python3 commitment_tracker.py pivot "Ross changed priority"')
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "start":
        task = sys.argv[2]
        hours = float(sys.argv[3])
        level = sys.argv[4] if len(sys.argv) > 4 else "locked"
        start_commitment(task, hours, level)
        
    elif action == "status":
        status()
        
    elif action == "complete":
        complete_commitment()
        
    elif action == "pivot":
        reason = sys.argv[2] if len(sys.argv) > 2 else "No reason given"
        new_task = sys.argv[3] if len(sys.argv) > 3 else None
        pivot(reason, new_task)
        
    else:
        print(f"Unknown action: {action}")
