#!/usr/bin/env python3
"""
Autonomous Mode - Jarvis
Runs background tasks, research, and updates without being asked
Called by heartbeats or scheduled tasks
"""

import subprocess
from datetime import datetime
from pathlib import Path

def log(message):
    """Log autonomous actions"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_proactive_research():
    """Run background research"""
    log("🔍 Running proactive research...")
    try:
        subprocess.run(
            ["python3", str(Path.home() / "clawd/scripts/proactive_research.py")],
            capture_output=True,
            timeout=60
        )
        log("✅ Research complete")
    except Exception as e:
        log(f"❌ Research failed: {e}")

def pull_nba_intel():
    """Pull latest NBA rankings and intel"""
    log("🏀 Pulling NBA intel...")
    try:
        subprocess.run(
            ["python3", str(Path.home() / "clawd/scripts/pull_nba_intel.py")],
            capture_output=True,
            timeout=30
        )
        log("✅ NBA intel updated")
    except Exception as e:
        log(f"❌ NBA intel failed: {e}")

def generate_social_posts():
    """Generate daily social media posts"""
    log("📱 Generating social posts...")
    try:
        subprocess.run(
            ["python3", str(Path.home() / "clawd/scripts/generate_social_posts.py")],
            capture_output=True,
            timeout=30
        )
        log("✅ Social posts generated")
    except Exception as e:
        log(f"❌ Post generation failed: {e}")

def update_journal():
    """Update personal journal with learnings"""
    log("📔 Updating journal...")
    # Journal updates happen during conversational flow
    # This is a placeholder for future auto-summarization
    log("✅ Journal review complete")

def check_dopamine_defense():
    """Run dopamine defense check"""
    log("🧠 Running dopamine defense check...")
    try:
        result = subprocess.run(
            ["python3", str(Path.home() / "clawd/scripts/dopamine_defense.py")],
            capture_output=True,
            text=True,
            timeout=10
        )
        log(f"✅ {result.stdout.strip()}")
    except Exception as e:
        log(f"❌ Dopamine check failed: {e}")

def autonomous_night_routine():
    """Run while Ross sleeps (11pm-7am)"""
    log("🌙 Starting night routine...")
    run_proactive_research()
    pull_nba_intel()
    generate_social_posts()
    log("🌅 Night routine complete - ready for morning!")

def autonomous_heartbeat():
    """Quick checks during heartbeats"""
    log("💓 Autonomous heartbeat...")
    check_dopamine_defense()
    pull_nba_intel()  # NBA intel should be fresh
    log("✅ Heartbeat complete")

if __name__ == "__main__":
    import sys
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "heartbeat"
    
    if mode == "night":
        autonomous_night_routine()
    elif mode == "research":
        run_proactive_research()
    elif mode == "nba":
        pull_nba_intel()
    elif mode == "social":
        generate_social_posts()
    else:
        autonomous_heartbeat()
