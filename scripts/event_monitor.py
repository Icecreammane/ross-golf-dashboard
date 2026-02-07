#!/usr/bin/env python3
"""
Event Monitor - Watches for important changes and notifies proactively
Monitors: calendar changes, file edits, git commits, system events
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
import hashlib

WORKSPACE = Path("/Users/clawdbot/clawd")
MEMORY_DIR = WORKSPACE / "memory"
EVENTS_LOG = MEMORY_DIR / "events.json"
LAST_STATE = MEMORY_DIR / "monitor_state.json"

def load_events():
    """Load event log"""
    if EVENTS_LOG.exists():
        with open(EVENTS_LOG) as f:
            return json.load(f)
    return {"events": []}

def load_last_state():
    """Load last known state"""
    if LAST_STATE.exists():
        with open(LAST_STATE) as f:
            return json.load(f)
    return {
        "last_calendar_check": None,
        "last_git_commit": None,
        "watched_files": {}
    }

def log_event(event_type, description, priority="normal"):
    """Log an event"""
    events = load_events()
    
    event = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "description": description,
        "priority": priority
    }
    
    events["events"].append(event)
    
    # Keep only last 100 events
    events["events"] = events["events"][-100:]
    
    with open(EVENTS_LOG, "w") as f:
        json.dump(events, f, indent=2)
    
    return event

def check_calendar_changes():
    """Check if calendar has changed"""
    calendar_file = WORKSPACE / "calendar" / "upcoming-events.md"
    
    if not calendar_file.exists():
        return []
    
    state = load_last_state()
    
    # Get file hash
    with open(calendar_file, "rb") as f:
        current_hash = hashlib.md5(f.read()).hexdigest()
    
    last_hash = state.get("calendar_hash")
    
    if last_hash and current_hash != last_hash:
        # Calendar changed
        event = log_event(
            "calendar_change",
            "Calendar updated - new events or changes detected",
            priority="high"
        )
        
        state["calendar_hash"] = current_hash
        with open(LAST_STATE, "w") as f:
            json.dump(state, f, indent=2)
        
        return [event]
    elif not last_hash:
        # First run, just store hash
        state["calendar_hash"] = current_hash
        with open(LAST_STATE, "w") as f:
            json.dump(state, f, indent=2)
    
    return []

def check_git_changes():
    """Check for new git commits"""
    try:
        # Get latest commit
        result = subprocess.run(
            ["git", "-C", str(WORKSPACE), "log", "-1", "--format=%H|%s"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            commit_info = result.stdout.strip()
            commit_hash, commit_msg = commit_info.split("|", 1)
            
            state = load_last_state()
            last_commit = state.get("last_git_commit")
            
            if last_commit and last_commit != commit_hash:
                # New commit
                event = log_event(
                    "git_commit",
                    f"New commit: {commit_msg}",
                    priority="normal"
                )
                
                state["last_git_commit"] = commit_hash
                with open(LAST_STATE, "w") as f:
                    json.dump(state, f, indent=2)
                
                return [event]
            elif not last_commit:
                # First run
                state["last_git_commit"] = commit_hash
                with open(LAST_STATE, "w") as f:
                    json.dump(state, f, indent=2)
    except:
        pass
    
    return []

def check_file_changes(watch_files=None):
    """Check if important files have changed"""
    if watch_files is None:
        watch_files = [
            WORKSPACE / "GOALS.md",
            WORKSPACE / "TASK_QUEUE.md",
            WORKSPACE / "data" / "fitness_data.json"
        ]
    
    state = load_last_state()
    watched = state.get("watched_files", {})
    events = []
    
    for filepath in watch_files:
        if not filepath.exists():
            continue
        
        # Get file hash
        with open(filepath, "rb") as f:
            current_hash = hashlib.md5(f.read()).hexdigest()
        
        file_key = str(filepath)
        last_hash = watched.get(file_key)
        
        if last_hash and current_hash != last_hash:
            # File changed
            event = log_event(
                "file_change",
                f"{filepath.name} updated",
                priority="normal"
            )
            events.append(event)
        
        watched[file_key] = current_hash
    
    state["watched_files"] = watched
    with open(LAST_STATE, "w") as f:
        json.dump(state, f, indent=2)
    
    return events

def get_recent_events(hours=24, priority=None):
    """Get recent events"""
    events = load_events()["events"]
    
    cutoff = datetime.now().timestamp() - (hours * 3600)
    
    recent = []
    for event in events:
        event_time = datetime.fromisoformat(event["timestamp"]).timestamp()
        if event_time > cutoff:
            if priority is None or event["priority"] == priority:
                recent.append(event)
    
    return recent

def monitor_loop():
    """Run all monitoring checks"""
    print("🔍 Running event monitor...\n")
    
    all_events = []
    
    # Check calendar
    calendar_events = check_calendar_changes()
    all_events.extend(calendar_events)
    
    # Check git
    git_events = check_git_changes()
    all_events.extend(git_events)
    
    # Check important files
    file_events = check_file_changes()
    all_events.extend(file_events)
    
    # Report
    if all_events:
        print(f"✅ Detected {len(all_events)} events:\n")
        for event in all_events:
            priority_emoji = "🔥" if event["priority"] == "high" else "📌"
            print(f"{priority_emoji} {event['description']}")
    else:
        print("✅ No new events detected")
    
    return all_events

def main():
    """CLI for event monitoring"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 event_monitor.py check    - Run monitoring check")
        print("  python3 event_monitor.py recent   - Show recent events")
        print("  python3 event_monitor.py high     - Show high-priority events only")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check":
        monitor_loop()
    
    elif command == "recent":
        events = get_recent_events(hours=24)
        print(f"📊 Recent Events (last 24h): {len(events)}\n")
        for event in events[-10:]:  # Last 10
            time = datetime.fromisoformat(event["timestamp"]).strftime("%I:%M %p")
            print(f"{time} - {event['description']}")
    
    elif command == "high":
        events = get_recent_events(hours=24, priority="high")
        print(f"🔥 High Priority Events: {len(events)}\n")
        for event in events:
            time = datetime.fromisoformat(event["timestamp"]).strftime("%I:%M %p")
            print(f"{time} - {event['description']}")

if __name__ == "__main__":
    main()
