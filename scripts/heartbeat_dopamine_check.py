#!/usr/bin/env python3
"""
Heartbeat Dopamine Defense Integration

Simple wrapper for calling from agent heartbeat handlers.
Returns message to send to Ross if intervention needed, or None.
"""

import json
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from dopamine_defense import check_and_interrupt


def heartbeat_check():
    """
    Run dopamine defense check during heartbeat.
    
    Returns:
        dict with 'send_message' (bool) and 'message' (str or None)
    """
    result = check_and_interrupt()
    
    return {
        "send_message": result["should_interrupt"],
        "message": result.get("message"),
        "reason": result.get("reason"),
        "idle_minutes": result.get("idle_minutes", 0)
    }


if __name__ == "__main__":
    # Run check and output JSON for easy parsing
    result = heartbeat_check()
    
    # Output JSON
    print(json.dumps(result, indent=2))
    
    # Exit code: 0 = no action, 1 = send message
    sys.exit(1 if result["send_message"] else 0)
