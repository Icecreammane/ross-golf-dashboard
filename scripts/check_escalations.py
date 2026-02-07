#!/usr/bin/env python3
"""
Escalation Handler for Sonnet
Checks for escalations from local daemon and handles them appropriately.
Called during Sonnet's heartbeats.
"""

import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/Users/clawdbot/clawd")
ESCALATION_FILE = WORKSPACE / "memory" / "escalation-pending.json"
SPAWN_SIGNAL = WORKSPACE / "memory" / "spawn-signal.json"

def check_escalations():
    """Check for pending escalations and return action needed"""
    if not ESCALATION_FILE.exists():
        return None
    
    with open(ESCALATION_FILE) as f:
        escalation = json.load(f)
    
    escalation_type = escalation.get("type")
    
    # Return the escalation data for Sonnet to handle
    result = {
        "type": escalation_type,
        "data": escalation,
        "action": None
    }
    
    if escalation_type == "spawn_ready":
        # Read spawn signal
        if SPAWN_SIGNAL.exists():
            with open(SPAWN_SIGNAL) as f:
                signal = json.load(f)
            result["action"] = "spawn_build"
            result["spawn_data"] = signal
    
    elif escalation_type == "morning_brief":
        result["action"] = "send_morning_brief"
    
    elif escalation_type == "evening_checkin":
        result["action"] = "send_evening_message"
    
    elif escalation_type == "critical_alerts":
        result["action"] = "notify_alerts"
        result["alerts"] = escalation.get("alerts", [])
    
    # Clear escalation file after reading
    ESCALATION_FILE.unlink()
    
    return result

if __name__ == "__main__":
    result = check_escalations()
    if result:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps({"status": "no_escalations"}))
