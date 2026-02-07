#!/usr/bin/env python3
"""
Jarvis Local Daemon - 24/7 Background Intelligence
Uses local-brain (qwen2.5:14b) for continuous monitoring and task generation.
Only escalates to cloud models when human interaction or high-value work is needed.
"""

import json
import time
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path

# Paths
WORKSPACE = Path("/Users/clawdbot/clawd")
MEMORY_DIR = WORKSPACE / "memory"
HEARTBEAT_STATE = MEMORY_DIR / "heartbeat-state.json"
SPAWN_SIGNAL = MEMORY_DIR / "spawn-signal.json"
JOURNAL = MEMORY_DIR / "jarvis-journal.md"
DAEMON_LOG = WORKSPACE / "monitoring" / "daemon.log"

# Ensure directories exist
MEMORY_DIR.mkdir(exist_ok=True)
(WORKSPACE / "monitoring").mkdir(exist_ok=True)

def log(message):
    """Log to daemon log and print to console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(DAEMON_LOG, "a") as f:
        f.write(log_line + "\n")

def load_state():
    """Load heartbeat state"""
    if HEARTBEAT_STATE.exists():
        with open(HEARTBEAT_STATE) as f:
            return json.load(f)
    return {
        "lastChecks": {},
        "morning_brief_sent": None,
        "evening_checkin_done": None,
        "weekly_report_sent": None
    }

def save_state(state):
    """Save heartbeat state"""
    with open(HEARTBEAT_STATE, "w") as f:
        json.dump(state, f, indent=2)

def run_command(cmd, description):
    """Run a shell command and return success status"""
    try:
        log(f"Running: {description}")
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        if result.returncode == 0:
            log(f"✓ {description} completed")
            return True, result.stdout
        else:
            log(f"✗ {description} failed: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        log(f"✗ {description} error: {str(e)}")
        return False, str(e)

def check_time_window(start_hour, start_min, end_hour, end_min):
    """Check if current time is within window (CST)"""
    now = datetime.now()
    start = now.replace(hour=start_hour, minute=start_min, second=0)
    end = now.replace(hour=end_hour, minute=end_min, second=0)
    return start <= now <= end

def is_today(timestamp_str):
    """Check if timestamp is from today"""
    if not timestamp_str:
        return False
    try:
        ts = datetime.fromisoformat(timestamp_str)
        return ts.date() == datetime.now().date()
    except:
        return False

def heartbeat_check():
    """Run heartbeat tasks"""
    state = load_state()
    now = datetime.now()
    
    log("=== Heartbeat Check ===")
    
    # 1. Autonomous task generation & spawn check (every heartbeat)
    success, output = run_command(
        "python3 ~/clawd/scripts/autonomous_check.py",
        "Autonomous task generation"
    )
    
    # Check for spawn signal
    if SPAWN_SIGNAL.exists():
        with open(SPAWN_SIGNAL) as f:
            signal = json.load(f)
        if signal.get("ready"):
            log(f"⚡ Spawn signal detected: {signal.get('label', 'unknown')}")
            # Write escalation for Sonnet to handle
            escalation = {
                "type": "spawn_ready",
                "signal": signal,
                "timestamp": now.isoformat()
            }
            escalation_file = MEMORY_DIR / "escalation-pending.json"
            with open(escalation_file, "w") as f:
                json.dump(escalation, f, indent=2)
            log("→ Escalated to Sonnet for spawn execution")
    
    # 2. Morning brief (7:25-7:35am)
    if check_time_window(7, 25, 7, 35) and not is_today(state.get("morning_brief_sent")):
        success, _ = run_command(
            "python3 ~/clawd/scripts/generate-morning-brief.py",
            "Morning brief generation"
        )
        if success:
            state["morning_brief_sent"] = now.isoformat()
            # Signal Sonnet to send it
            escalation = {
                "type": "morning_brief",
                "timestamp": now.isoformat()
            }
            with open(MEMORY_DIR / "escalation-pending.json", "w") as f:
                json.dump(escalation, f, indent=2)
    
    # 3. Evening check-in (7:55-8:05pm)
    if check_time_window(19, 55, 20, 5) and not is_today(state.get("evening_checkin_done")):
        escalation = {
            "type": "evening_checkin",
            "timestamp": now.isoformat()
        }
        with open(MEMORY_DIR / "escalation-pending.json", "w") as f:
            json.dump(escalation, f, indent=2)
        state["evening_checkin_done"] = now.isoformat()
    
    # 4. System health check
    success, output = run_command(
        "python3 ~/clawd/scripts/health_check.py",
        "System health check"
    )
    
    # 5. Check for auto-recovery alerts
    alert_file = WORKSPACE / "monitoring" / "alert-pending.json"
    if alert_file.exists():
        with open(alert_file) as f:
            alerts = json.load(f)
        if alerts:
            log(f"⚠️ {len(alerts)} critical alerts pending")
            escalation = {
                "type": "critical_alerts",
                "alerts": alerts,
                "timestamp": now.isoformat()
            }
            with open(MEMORY_DIR / "escalation-pending.json", "w") as f:
                json.dump(escalation, f, indent=2)
    
    save_state(state)
    log("=== Heartbeat Complete ===\n")

def night_shift():
    """Run autonomous night tasks"""
    log("=== Night Shift Starting ===")
    
    # Proactive research
    run_command(
        "python3 ~/clawd/scripts/proactive_research.py",
        "Proactive research"
    )
    
    # NBA intel pull
    run_command(
        "python3 ~/clawd/scripts/pull_nba_intel.py",
        "NBA rankings pull"
    )
    
    # Social post generation
    run_command(
        "python3 ~/clawd/scripts/generate_social_posts.py",
        "Social post generation"
    )
    
    log("=== Night Shift Complete ===\n")

def main():
    """Main daemon loop"""
    log("🤖 Jarvis Local Daemon starting...")
    log("Using model: local-brain (qwen2.5:14b)")
    log("Heartbeat interval: 5 minutes")
    
    last_heartbeat = datetime.now() - timedelta(minutes=6)  # Run immediately
    last_night_shift = None
    
    while True:
        try:
            now = datetime.now()
            
            # Heartbeat every 5 minutes
            if (now - last_heartbeat).total_seconds() >= 300:
                heartbeat_check()
                last_heartbeat = now
            
            # Night shift once per night (2:00am)
            if now.hour == 2 and (not last_night_shift or last_night_shift.date() != now.date()):
                night_shift()
                last_night_shift = now
            
            # Sleep for 60 seconds
            time.sleep(60)
            
        except KeyboardInterrupt:
            log("🛑 Daemon stopped by user")
            break
        except Exception as e:
            log(f"❌ Error in main loop: {str(e)}")
            time.sleep(60)  # Sleep and continue

if __name__ == "__main__":
    main()
