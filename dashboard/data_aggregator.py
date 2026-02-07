#!/usr/bin/env python3
"""
Dashboard Data Aggregator - Pulls from all 11 systems into single JSON
Updates every 60 seconds for live dashboard
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
OUTPUT = WORKSPACE / "dashboard" / "dashboard_data.json"

def get_night_shift_results():
    """Get latest night shift outputs"""
    latest = WORKSPACE / "reports" / "night-shift-latest.md"
    
    if latest.exists():
        with open(latest) as f:
            content = f.read()
        
        return {
            "status": "complete",
            "summary": content[:500],  # First 500 chars
            "full_path": str(latest)
        }
    
    return {"status": "pending", "summary": "No results yet"}

def get_twitter_status():
    """Get Twitter system status"""
    tweets_file = WORKSPACE / "content" / "tweets-scheduled.md"
    
    if tweets_file.exists():
        with open(tweets_file) as f:
            content = f.read()
        
        # Count scheduled tweets
        scheduled = content.count("##")
        
        return {
            "status": "active",
            "scheduled_tweets": scheduled,
            "account": "@_icecreammane",
            "next_tweet": "Monday Feb 10, 9:00 AM"
        }
    
    return {"status": "not_configured"}

def get_reddit_opportunities():
    """Get Reddit scanner results"""
    latest_scan = sorted(
        (WORKSPACE / "revenue").glob("reddit-scan-*.md"),
        reverse=True
    )
    
    if latest_scan:
        scan_file = latest_scan[0]
        with open(scan_file) as f:
            content = f.read()
        
        # Count high priority opportunities
        high_priority = content.count("🔥 High Priority")
        
        return {
            "status": "scanned",
            "opportunities": high_priority,
            "last_scan": scan_file.stem.split("-")[-1]
        }
    
    return {"status": "no_scans", "opportunities": 0}

def get_pattern_insights():
    """Get pattern detection insights"""
    pattern_file = WORKSPACE / "memory" / "pattern_data.json"
    
    if pattern_file.exists():
        with open(pattern_file) as f:
            data = json.load(f)
        
        insights = data.get("insights", [])
        
        return {
            "status": "analyzing",
            "insights": insights[:3]  # Top 3
        }
    
    return {"status": "collecting_data", "insights": []}

def get_recent_events():
    """Get recent events from monitor"""
    events_file = WORKSPACE / "memory" / "events.json"
    
    if events_file.exists():
        with open(events_file) as f:
            data = json.load(f)
        
        events = data.get("events", [])
        recent = events[-5:]  # Last 5
        
        return {
            "count": len(recent),
            "events": recent
        }
    
    return {"count": 0, "events": []}

def get_pending_decisions():
    """Get decisions needing outcomes"""
    decisions_file = WORKSPACE / "memory" / "decisions.json"
    
    if decisions_file.exists():
        with open(decisions_file) as f:
            data = json.load(f)
        
        decisions = data.get("decisions", [])
        pending = [d for d in decisions if d.get("outcome") is None]
        
        # Check age
        aged = []
        for decision in pending:
            timestamp = datetime.fromisoformat(decision["timestamp"])
            age_hours = (datetime.now() - timestamp).total_seconds() / 3600
            if age_hours >= 24:
                aged.append({
                    "id": decision["id"],
                    "decision": decision["decision"],
                    "age_days": int(age_hours / 24)
                })
        
        return {
            "total_pending": len(pending),
            "aged_pending": aged
        }
    
    return {"total_pending": 0, "aged_pending": []}

def get_system_status():
    """Check status of all 11 systems"""
    systems = {
        "persistent_memory": check_file_exists("memory/memory_index.json"),
        "learning_loop": check_file_exists("memory/learning_data.json"),
        "proactive_permissions": check_file_exists("TOOLS.md"),
        "twitter": check_file_exists("content/tweets-scheduled.md"),
        "reddit_scanner": check_file_exists("scripts/reddit_scanner.py"),
        "voice_briefs": check_file_exists("scripts/voice_brief.py"),
        "event_monitor": check_file_exists("scripts/event_monitor.py"),
        "pattern_detection": check_file_exists("scripts/pattern_detection.py"),
        "vision_processor": check_file_exists("scripts/vision_processor.py"),
        "decision_logger": check_file_exists("scripts/decision_logger.py"),
        "context_loader": check_file_exists("scripts/context_loader.py")
    }
    
    operational = sum(1 for status in systems.values() if status)
    
    return {
        "total": 11,
        "operational": operational,
        "systems": systems
    }

def check_file_exists(relative_path):
    """Check if file exists"""
    return (WORKSPACE / relative_path).exists()

def get_goal_progress():
    """Get progress toward $500 MRR goal"""
    # Placeholder - would pull from actual revenue tracking
    return {
        "target": 500,
        "current": 0,
        "deadline": "2026-03-31",
        "days_remaining": (datetime(2026, 3, 31) - datetime.now()).days
    }

def get_fitness_summary():
    """Get recent fitness data"""
    fitness_file = WORKSPACE / "data" / "fitness_data.json"
    
    if fitness_file.exists():
        with open(fitness_file) as f:
            data = json.load(f)
        
        workouts = data.get("workouts", [])
        nutrition = data.get("nutrition", [])
        
        return {
            "workouts_logged": len(workouts),
            "meals_logged": len(nutrition),
            "last_workout": workouts[-1].get("raw_text") if workouts else None,
            "last_meal": nutrition[-1].get("raw_text") if nutrition else None
        }
    
    return {"workouts_logged": 0, "meals_logged": 0}

def aggregate_all_data():
    """Aggregate data from all systems"""
    
    print("📊 Aggregating dashboard data...")
    
    dashboard_data = {
        "generated_at": datetime.now().isoformat(),
        "timestamp_friendly": datetime.now().strftime("%I:%M %p CST"),
        
        # Intelligence
        "night_shift": get_night_shift_results(),
        "pattern_insights": get_pattern_insights(),
        "recent_events": get_recent_events(),
        
        # External Tools
        "twitter": get_twitter_status(),
        "reddit": get_reddit_opportunities(),
        
        # Decisions & Context
        "pending_decisions": get_pending_decisions(),
        
        # System Health
        "system_status": get_system_status(),
        
        # Goals & Progress
        "goal_progress": get_goal_progress(),
        "fitness": get_fitness_summary(),
        
        # Quick Stats
        "stats": {
            "systems_operational": get_system_status()["operational"],
            "opportunities": get_reddit_opportunities()["opportunities"],
            "pending_actions": get_pending_decisions()["total_pending"],
            "tweets_scheduled": get_twitter_status().get("scheduled_tweets", 0)
        }
    }
    
    # Save to JSON
    OUTPUT.parent.mkdir(exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"✅ Dashboard data updated: {OUTPUT}")
    print(f"   Systems: {dashboard_data['stats']['systems_operational']}/11")
    print(f"   Opportunities: {dashboard_data['stats']['opportunities']}")
    print(f"   Pending: {dashboard_data['stats']['pending_actions']}")
    
    return dashboard_data

def main():
    """Generate dashboard data"""
    aggregate_all_data()

if __name__ == "__main__":
    main()
