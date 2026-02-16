#!/usr/bin/env python3
"""
Activity Tracker - Monitor user interaction patterns and detect idle periods.

Tracks:
- Last interaction timestamp
- Idle periods >20 minutes during work hours (9am-11pm CST)
- Activity patterns for productivity analysis
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# Paths
WORKSPACE = Path.home() / "clawd"
DATA_DIR = WORKSPACE / "data"
ACTIVITY_LOG = DATA_DIR / "activity_log.json"
HEARTBEAT_STATE = WORKSPACE / "memory" / "heartbeat-state.json"

# Timezone
CST = ZoneInfo('America/Chicago')

# Configuration
IDLE_THRESHOLD_MINUTES = 20
WORK_HOURS_START = 9  # 9am
WORK_HOURS_END = 23   # 11pm


def get_current_time():
    """Get current time in CST."""
    return datetime.now(CST)


def is_work_hours(dt=None):
    """Check if current time is within work hours (9am-11pm CST)."""
    if dt is None:
        dt = get_current_time()
    hour = dt.hour
    return WORK_HOURS_START <= hour < WORK_HOURS_END


def load_activity_log():
    """Load activity log from JSON file."""
    if not ACTIVITY_LOG.exists():
        return {
            "last_interaction": None,
            "sessions": [],
            "idle_periods": []
        }
    
    with open(ACTIVITY_LOG, 'r') as f:
        return json.load(f)


def save_activity_log(data):
    """Save activity log to JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(ACTIVITY_LOG, 'w') as f:
        json.dump(data, f, indent=2)


def record_interaction(interaction_type="message"):
    """
    Record a user interaction.
    
    Args:
        interaction_type: Type of interaction (message, command, etc.)
    
    Returns:
        dict: Activity status including idle detection
    """
    now = get_current_time()
    log = load_activity_log()
    
    # Check if this ends an idle period
    idle_detected = False
    idle_duration_minutes = 0
    
    if log["last_interaction"]:
        last_time = datetime.fromisoformat(log["last_interaction"])
        duration = (now - last_time).total_seconds() / 60
        
        if duration >= IDLE_THRESHOLD_MINUTES and is_work_hours(last_time):
            # Record idle period
            idle_period = {
                "start": log["last_interaction"],
                "end": now.isoformat(),
                "duration_minutes": round(duration, 1),
                "detected_at": now.isoformat()
            }
            log["idle_periods"].append(idle_period)
            idle_detected = True
            idle_duration_minutes = duration
    
    # Update last interaction
    log["last_interaction"] = now.isoformat()
    
    # Add to sessions
    session = {
        "timestamp": now.isoformat(),
        "type": interaction_type,
        "work_hours": is_work_hours(now)
    }
    log["sessions"].append(session)
    
    # Keep only last 7 days of sessions
    cutoff = (now - timedelta(days=7)).isoformat()
    log["sessions"] = [s for s in log["sessions"] if s["timestamp"] > cutoff]
    log["idle_periods"] = [p for p in log["idle_periods"] if p["end"] > cutoff]
    
    save_activity_log(log)
    
    return {
        "interaction_recorded": True,
        "timestamp": now.isoformat(),
        "idle_detected": idle_detected,
        "idle_duration_minutes": idle_duration_minutes if idle_detected else 0,
        "work_hours": is_work_hours(now)
    }


def get_idle_status():
    """
    Check current idle status without recording interaction.
    
    Returns:
        dict: Idle status information
    """
    now = get_current_time()
    log = load_activity_log()
    
    if not log["last_interaction"]:
        return {
            "is_idle": False,
            "minutes_idle": 0,
            "should_interrupt": False,
            "work_hours": is_work_hours(now)
        }
    
    last_time = datetime.fromisoformat(log["last_interaction"])
    minutes_idle = (now - last_time).total_seconds() / 60
    
    is_idle = minutes_idle >= IDLE_THRESHOLD_MINUTES
    should_interrupt = is_idle and is_work_hours(now)
    
    return {
        "is_idle": is_idle,
        "minutes_idle": round(minutes_idle, 1),
        "should_interrupt": should_interrupt,
        "work_hours": is_work_hours(now),
        "last_interaction": log["last_interaction"]
    }


def get_daily_summary(date=None):
    """
    Get summary of activity for a specific day.
    
    Args:
        date: datetime object for the day (defaults to today)
    
    Returns:
        dict: Daily activity summary
    """
    if date is None:
        date = get_current_time()
    
    log = load_activity_log()
    
    # Filter sessions and idle periods for the specific day
    day_start = date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    day_end = date.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()
    
    day_sessions = [s for s in log["sessions"] if day_start <= s["timestamp"] <= day_end]
    day_idle_periods = [p for p in log["idle_periods"] if day_start <= p["start"] <= day_end]
    
    # Calculate active time (rough estimate based on sessions)
    total_sessions = len(day_sessions)
    total_idle_minutes = sum(p["duration_minutes"] for p in day_idle_periods)
    
    # Estimate active time: assume 15 min of activity per session cluster
    # Group sessions within 30 min of each other
    active_minutes = 0
    if day_sessions:
        sorted_sessions = sorted(day_sessions, key=lambda s: s["timestamp"])
        clusters = 1
        for i in range(1, len(sorted_sessions)):
            prev_time = datetime.fromisoformat(sorted_sessions[i-1]["timestamp"])
            curr_time = datetime.fromisoformat(sorted_sessions[i]["timestamp"])
            if (curr_time - prev_time).total_seconds() / 60 > 30:
                clusters += 1
        active_minutes = clusters * 15  # Rough estimate
    
    return {
        "date": date.strftime("%Y-%m-%d"),
        "total_sessions": total_sessions,
        "idle_periods": len(day_idle_periods),
        "total_idle_minutes": round(total_idle_minutes, 1),
        "estimated_active_minutes": active_minutes,
        "productivity_score": round(active_minutes / (active_minutes + total_idle_minutes), 2) if (active_minutes + total_idle_minutes) > 0 else 0,
        "idle_periods_detail": day_idle_periods
    }


def format_time_duration(minutes):
    """Format minutes into human-readable duration."""
    if minutes < 60:
        return f"{int(minutes)}m"
    hours = minutes / 60
    if hours < 10:
        return f"{hours:.1f}h"
    return f"{int(hours)}h"


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "record":
            interaction_type = sys.argv[2] if len(sys.argv) > 2 else "message"
            result = record_interaction(interaction_type)
            print(json.dumps(result, indent=2))
        
        elif command == "status":
            status = get_idle_status()
            print(json.dumps(status, indent=2))
        
        elif command == "summary":
            summary = get_daily_summary()
            print(json.dumps(summary, indent=2))
            
            # Print formatted version
            print(f"\n📊 Today's Activity Summary")
            print(f"Active time: {format_time_duration(summary['estimated_active_minutes'])}")
            print(f"Idle time: {format_time_duration(summary['total_idle_minutes'])}")
            print(f"Productivity score: {int(summary['productivity_score'] * 100)}%")
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: activity_tracker.py [record|status|summary]")
    else:
        # Default: show status
        status = get_idle_status()
        print(json.dumps(status, indent=2))
