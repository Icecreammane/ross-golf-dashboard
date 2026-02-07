#!/usr/bin/env python3
"""
Dopamine Defense System - Jarvis
Tracks Ross's activity patterns and intervenes when needed
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

STATE_FILE = Path.home() / "clawd" / "memory" / "activity_state.json"

def load_state():
    """Load activity state"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "last_activity": None,
        "last_checkin": None,
        "builder_streak": 0,
        "idle_alerts_today": 0
    }

def save_state(state):
    """Save activity state"""
    STATE_FILE.parent.mkdir(exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def check_idle_time():
    """Check if Ross has been idle too long"""
    state = load_state()
    
    if not state['last_activity']:
        return False, "No activity data yet"
    
    last = datetime.fromisoformat(state['last_activity'])
    now = datetime.now()
    idle_minutes = (now - last).total_seconds() / 60
    
    # During waking hours (9am-11pm), check if idle > 2 hours
    if 9 <= now.hour <= 23:
        if idle_minutes > 120:
            return True, f"Idle for {int(idle_minutes)} minutes"
    
    return False, "Activity level normal"

def log_activity():
    """Log current activity"""
    state = load_state()
    state['last_activity'] = datetime.now().isoformat()
    state['builder_streak'] += 1
    save_state(state)

def send_check_in():
    """Send proactive check-in message"""
    state = load_state()
    
    # Don't spam - max 3 check-ins per day
    if state['idle_alerts_today'] >= 3:
        return False
    
    state['last_checkin'] = datetime.now().isoformat()
    state['idle_alerts_today'] += 1
    save_state(state)
    
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "log":
        log_activity()
        print("✅ Activity logged")
    else:
        is_idle, reason = check_idle_time()
        if is_idle:
            if send_check_in():
                print("🔔 Should send check-in")
                print(f"Reason: {reason}")
            else:
                print("Already sent max check-ins today")
        else:
            print(f"✓ {reason}")
