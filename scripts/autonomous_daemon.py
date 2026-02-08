#!/usr/bin/env python3
"""
Autonomous Daemon - Tier 1 of the Jarvis autonomous system

Runs 24/7, monitors files/logs/system state, makes simple decisions,
escalates to Sonnet when needed via signal files.

This is the always-on intelligence that makes Jarvis truly autonomous.
"""

import os
import sys
import time
import json
import hashlib
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE = Path.home() / "clawd"
ESCALATIONS = WORKSPACE / "escalations"
STATE_FILE = WORKSPACE / "daemon_state.json"
LOG_FILE = WORKSPACE / "logs" / "daemon.log"

# Ensure directories exist
ESCALATIONS.mkdir(exist_ok=True)
LOG_FILE.parent.mkdir(exist_ok=True)

class DaemonState:
    """Persistent state for the daemon"""
    def __init__(self):
        self.data = self.load()
    
    def load(self):
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                return json.load(f)
        return {
            "started": datetime.now().isoformat(),
            "last_check": None,
            "file_hashes": {},
            "last_escalation": None,
            "checks_run": 0
        }
    
    def save(self):
        with open(STATE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def update_check(self):
        self.data["last_check"] = datetime.now().isoformat()
        self.data["checks_run"] += 1
        self.save()
    
    def get_file_hash(self, filepath):
        """Get stored hash for a file"""
        return self.data["file_hashes"].get(str(filepath))
    
    def set_file_hash(self, filepath, hash_value):
        """Store hash for a file"""
        self.data["file_hashes"][str(filepath)] = hash_value
        self.save()

def log(message, level="INFO"):
    """Log to both file and stdout"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] [{level}] {message}"
    print(log_msg)
    with open(LOG_FILE, 'a') as f:
        f.write(log_msg + "\n")

def file_hash(filepath):
    """Quick hash of file contents"""
    if not Path(filepath).exists():
        return None
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def try_local_analysis(signal_type, data):
    """Try to handle signal with local model before escalating"""
    try:
        import subprocess
        result = subprocess.run(
            ['python3', str(WORKSPACE / 'scripts' / 'local_analyzer.py'), signal_type],
            input=json.dumps({"type": signal_type, "data": data}),
            capture_output=True,
            text=True,
            timeout=120  # 2 min max for local model
        )
        
        if result.returncode == 0 and result.stdout:
            response = json.loads(result.stdout)
            if response.get("handled"):
                log(f"Local model handled: {signal_type} - {response.get('action_taken')}")
                return True
        
        return False
    except Exception as e:
        log(f"Local analysis failed: {e}", "WARN")
        return False

def write_signal(signal_type, data, priority="medium"):
    """Write an escalation signal for Sonnet to handle (after local analysis fails)"""
    signal_id = f"{int(time.time())}_{signal_type}"
    signal_file = ESCALATIONS / f"{signal_id}.json"
    
    signal = {
        "type": signal_type,
        "priority": priority,
        "created": datetime.now().isoformat(),
        "data": data
    }
    
    with open(signal_file, 'w') as f:
        json.dump(signal, f, indent=2)
    
    log(f"Signal written for Sonnet: {signal_type} (priority: {priority})")

def check_goals_md(state):
    """Monitor GOALS.md for changes"""
    goals_file = WORKSPACE / "GOALS.md"
    if not goals_file.exists():
        return
    
    current_hash = file_hash(goals_file)
    stored_hash = state.get_file_hash(goals_file)
    
    if stored_hash and current_hash != stored_hash:
        log("GOALS.md changed - checking for new objectives")
        
        # Read goals to see if there are new high-priority items
        with open(goals_file) as f:
            content = f.read()
        
        # Try local model analysis first
        if not try_local_analysis("goals_updated", {"goals_content": content}):
            # Local model escalated or failed, write signal
            if "URGENT" in content.upper() or "HIGH PRIORITY" in content.upper():
                write_signal(
                    "goals_updated",
                    {"message": "High-priority goals detected in GOALS.md"},
                    priority="high"
                )
            else:
                log("Goals updated, local model handled it")
    
    state.set_file_hash(goals_file, current_hash)

def check_task_queue(state):
    """Monitor TASK_QUEUE.md and execute simple tasks"""
    queue_file = WORKSPACE / "TASK_QUEUE.md"
    if not queue_file.exists():
        return
    
    current_hash = file_hash(queue_file)
    stored_hash = state.get_file_hash(queue_file)
    
    if stored_hash and current_hash != stored_hash:
        log("TASK_QUEUE.md changed - checking for work")
        
        with open(queue_file) as f:
            content = f.read()
        
        # Count pending tasks (lines starting with "- [ ]")
        pending = content.count("- [ ]")
        
        if pending > 10:
            # Try local analysis first
            if not try_local_analysis("task_queue_growing", {"pending_tasks": pending, "queue_content": content}):
                write_signal(
                    "task_queue_growing",
                    {"pending_tasks": pending, "message": "Task backlog growing, may need attention"},
                    priority="medium"
                )
    
    state.set_file_hash(queue_file, current_hash)

def check_memory_files(state):
    """Monitor memory directory for activity"""
    memory_dir = WORKSPACE / "memory"
    if not memory_dir.exists():
        return
    
    # Check today's log file
    today = datetime.now().strftime("%Y-%m-%d")
    today_file = memory_dir / f"{today}.md"
    
    if today_file.exists():
        current_hash = file_hash(today_file)
        stored_hash = state.get_file_hash(today_file)
        
        if stored_hash and current_hash != stored_hash:
            log(f"Today's memory log updated: {today}.md")
            # Just track changes, no escalation needed for routine updates
        
        state.set_file_hash(today_file, current_hash)

def check_system_health():
    """Simple system health checks"""
    issues = []
    
    # Check disk space
    import shutil
    usage = shutil.disk_usage(WORKSPACE)
    percent_used = (usage.used / usage.total) * 100
    
    if percent_used > 90:
        issues.append(f"Disk usage at {percent_used:.1f}%")
    
    # Check if gateway is running
    import subprocess
    try:
        result = subprocess.run(['pgrep', '-f', 'clawdbot'], 
                               capture_output=True, timeout=5)
        if result.returncode != 0:
            issues.append("Gateway process not found")
    except:
        pass
    
    if issues:
        write_signal(
            "system_health",
            {"issues": issues},
            priority="high"
        )

def check_for_empty_task_queue():
    """If task queue is empty, signal that new tasks should be generated"""
    queue_file = WORKSPACE / "TASK_QUEUE.md"
    if not queue_file.exists():
        return
    
    with open(queue_file) as f:
        content = f.read()
    
    # Count pending tasks
    pending = content.count("- [ ]")
    
    # If less than 3 pending tasks, try local generation first
    if pending < 3:
        log(f"Task queue low ({pending} tasks) - trying local generation")
        if not try_local_analysis("generate_tasks", {"current_tasks": pending}):
            # Local model couldn't generate, escalate
            write_signal(
                "generate_tasks",
                {"current_tasks": pending, "message": "Task queue needs replenishment"},
                priority="low"
            )

def run_check_cycle(state):
    """Run one complete check cycle"""
    log("Running check cycle...")
    
    try:
        check_goals_md(state)
        check_task_queue(state)
        check_memory_files(state)
        check_for_empty_task_queue()
        
        # System health check every 10 cycles (less frequent)
        if state.data["checks_run"] % 10 == 0:
            check_system_health()
        
        state.update_check()
        log(f"Check cycle complete (#{state.data['checks_run']})")
        
    except Exception as e:
        log(f"Error in check cycle: {e}", "ERROR")

def main():
    """Main daemon loop"""
    log("=== Autonomous Daemon Starting ===")
    log(f"Workspace: {WORKSPACE}")
    log(f"Escalations: {ESCALATIONS}")
    log(f"PID: {os.getpid()}")
    
    state = DaemonState()
    log(f"State loaded: {state.data['checks_run']} previous checks")
    
    # Initial check
    run_check_cycle(state)
    
    # Main loop: check every 5 minutes
    CHECK_INTERVAL = 300  # 5 minutes
    
    try:
        while True:
            time.sleep(CHECK_INTERVAL)
            run_check_cycle(state)
    except KeyboardInterrupt:
        log("Daemon stopped by user")
    except Exception as e:
        log(f"Fatal error: {e}", "ERROR")
        # Write crash signal
        write_signal(
            "daemon_crashed",
            {"error": str(e), "pid": os.getpid()},
            priority="urgent"
        )
        raise

if __name__ == "__main__":
    main()
