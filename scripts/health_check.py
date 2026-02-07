#!/usr/bin/env python3
"""
System Health Check - Quick diagnostics for daemon
"""

import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/Users/clawdbot/clawd")
ALERT_FILE = WORKSPACE / "monitoring" / "alert-pending.json"

def check_disk_space():
    """Check disk usage"""
    total, used, free = shutil.disk_usage("/")
    percent_used = (used / total) * 100
    return percent_used < 90, f"Disk: {percent_used:.1f}% used"

def check_gateway():
    """Check if gateway is running"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "clawdbot"],
            capture_output=True
        )
        return result.returncode == 0, "Gateway: running" if result.returncode == 0 else "Gateway: stopped"
    except:
        return False, "Gateway: check failed"

def check_fitness_tracker():
    """Check if fitness Flask app is running"""
    try:
        result = subprocess.run(
            ["lsof", "-i", ":3000"],
            capture_output=True
        )
        return result.returncode == 0, "Fitness tracker: running" if result.returncode == 0 else "Fitness tracker: stopped"
    except:
        return False, "Fitness tracker: check failed"

def main():
    checks = [
        check_disk_space(),
        check_gateway(),
        check_fitness_tracker()
    ]
    
    alerts = []
    for ok, message in checks:
        print(message)
        if not ok:
            alerts.append({
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
    
    # Write alerts if any exist
    if alerts:
        ALERT_FILE.parent.mkdir(exist_ok=True)
        with open(ALERT_FILE, "w") as f:
            json.dump(alerts, f, indent=2)
    
    return len(alerts) == 0

if __name__ == "__main__":
    exit(0 if main() else 1)
