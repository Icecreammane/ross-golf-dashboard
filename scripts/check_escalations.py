#!/usr/bin/env python3
"""
Check Escalations - Read escalation file created by proactive_monitor.py
Called during Sonnet's heartbeat to handle items that need human attention
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional

WORKSPACE = "/Users/clawdbot/clawd"
ESCALATION_FILE = os.path.join(WORKSPACE, "memory", "escalation-pending.json")


def load_escalations() -> Optional[Dict]:
    """Load pending escalations if they exist"""
    if not os.path.exists(ESCALATION_FILE):
        return None
    
    try:
        with open(ESCALATION_FILE, 'r') as f:
            data = json.load(f)
        
        # Check if escalations are recent (within last hour)
        timestamp = datetime.fromisoformat(data["timestamp"])
        age_minutes = (datetime.now() - timestamp).total_seconds() / 60
        
        if age_minutes > 60:
            # Stale escalations, ignore
            print(f"⚠️  Escalations are {age_minutes:.0f} minutes old, ignoring")
            return None
        
        return data
    except Exception as e:
        print(f"Error loading escalations: {e}")
        return None


def format_escalation_message(escalations: Dict) -> str:
    """Format escalations into a readable message"""
    if not escalations or escalations["total_count"] == 0:
        return None
    
    lines = [
        f"🔔 **Proactive Monitor Alert** ({escalations['total_count']} items)",
        ""
    ]
    
    # Group by priority
    for priority in ["high", "medium", "low"]:
        items = [e for e in escalations["escalations"] if e["priority"] == priority]
        if items:
            emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[priority]
            lines.append(f"{emoji} **{priority.upper()} PRIORITY:**")
            
            for item in items:
                item_type = item["type"].replace("_", " ").title()
                summary = item["data"].get("summary", "No summary")
                lines.append(f"   • {item_type}: {summary}")
            
            lines.append("")
    
    # Add timestamp
    timestamp = datetime.fromisoformat(escalations["timestamp"])
    lines.append(f"_Checked at {timestamp.strftime('%I:%M %p')}_")
    
    return "\n".join(lines)


def clear_escalations():
    """Clear the escalation file after handling"""
    if os.path.exists(ESCALATION_FILE):
        os.remove(ESCALATION_FILE)
        print("✅ Cleared escalation file")


def main():
    """Main function - check and display escalations"""
    escalations = load_escalations()
    
    if not escalations:
        print("ESCALATION_CHECK: None")
        return
    
    message = format_escalation_message(escalations)
    
    if message:
        print("ESCALATION_CHECK: Found")
        print("\n" + message)
        
        # Don't auto-clear - let Sonnet decide when to clear after handling
    else:
        print("ESCALATION_CHECK: None")


if __name__ == "__main__":
    main()
