#!/usr/bin/env python3
"""
sub_agent_progress.py - Progress Tracking for Sub-Agents

Sub-agents call this to log their progress for real-time dashboard display.

Usage:
    from sub_agent_progress import log_progress
    log_progress(session_id, state, message, percent)

States: Starting, 25%, 50%, 75%, Testing, Complete, Failed
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

WORKSPACE = Path.home() / "clawd"
PROGRESS_FILE = WORKSPACE / "progress-data.json"


def log_progress(
    session_id: str,
    state: str,
    message: str = "",
    percent: int = 0,
    task_name: Optional[str] = None
):
    """
    Log progress for a sub-agent build.
    
    Args:
        session_id: Sub-agent session ID
        state: Progress state (Starting, 25%, 50%, 75%, Testing, Complete, Failed)
        message: Human-readable progress message
        percent: Progress percentage (0-100)
        task_name: Optional task name override
    """
    # Load existing progress data
    progress_data = {}
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r") as f:
                progress_data = json.load(f)
        except json.JSONDecodeError:
            progress_data = {}
    
    # Initialize agents dict if not exists
    if "agents" not in progress_data:
        progress_data["agents"] = {}
    
    # Create or update agent entry
    timestamp = datetime.now().isoformat()
    
    if session_id not in progress_data["agents"]:
        progress_data["agents"][session_id] = {
            "session_id": session_id,
            "task_name": task_name or "Unknown Task",
            "started_at": timestamp,
            "state": state,
            "percent": percent,
            "message": message,
            "updated_at": timestamp,
            "history": []
        }
    else:
        progress_data["agents"][session_id].update({
            "state": state,
            "percent": percent,
            "message": message,
            "updated_at": timestamp
        })
        
        if task_name:
            progress_data["agents"][session_id]["task_name"] = task_name
    
    # Append to history
    progress_data["agents"][session_id]["history"].append({
        "state": state,
        "message": message,
        "percent": percent,
        "timestamp": timestamp
    })
    
    # Limit history to last 20 entries
    if len(progress_data["agents"][session_id]["history"]) > 20:
        progress_data["agents"][session_id]["history"] = \
            progress_data["agents"][session_id]["history"][-20:]
    
    # Add last_updated timestamp to root
    progress_data["last_updated"] = timestamp
    
    # Write back to file
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress_data, f, indent=2)
    
    print(f"📊 Progress logged: {session_id} → {state} ({percent}%) - {message}")


def get_progress(session_id: str) -> Optional[dict]:
    """Get progress for a specific session"""
    if not PROGRESS_FILE.exists():
        return None
    
    try:
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
        return data.get("agents", {}).get(session_id)
    except json.JSONDecodeError:
        return None


def get_all_progress() -> dict:
    """Get all progress data"""
    if not PROGRESS_FILE.exists():
        return {"agents": {}, "last_updated": None}
    
    try:
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"agents": {}, "last_updated": None}


def clean_completed(hours: int = 24):
    """Remove completed/failed entries older than X hours"""
    if not PROGRESS_FILE.exists():
        return
    
    try:
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return
    
    if "agents" not in data:
        return
    
    now = datetime.now()
    to_remove = []
    
    for session_id, agent_data in data["agents"].items():
        if agent_data["state"] in ["Complete", "Failed"]:
            updated_at = datetime.fromisoformat(agent_data["updated_at"])
            age_hours = (now - updated_at).total_seconds() / 3600
            
            if age_hours > hours:
                to_remove.append(session_id)
    
    for session_id in to_remove:
        del data["agents"][session_id]
    
    # Write back
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    
    if to_remove:
        print(f"🧹 Cleaned {len(to_remove)} old progress entries")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: sub_agent_progress.py <session_id> <state> [message] [percent]")
        print("States: Starting, 25%, 50%, 75%, Testing, Complete, Failed")
        sys.exit(1)
    
    session_id = sys.argv[1]
    state = sys.argv[2]
    message = sys.argv[3] if len(sys.argv) > 3 else ""
    percent = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    
    log_progress(session_id, state, message, percent)
