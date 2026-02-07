#!/usr/bin/env python3
"""
Security Logger - API Action Tracking
Logs all external API calls for audit trail
"""

import os
import json
from datetime import datetime

LOG_DIR = os.path.expanduser("~/clawd/security-logs")
API_LOG = os.path.join(LOG_DIR, "api-actions.log")
DAILY_LOG = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.md")

def log_api_action(service, action, trigger_source, details, status="success"):
    """
    Log an API action to both the master log and daily markdown log.
    
    Args:
        service: API service name (e.g., 'google_calendar', 'spotify')
        action: What was done (e.g., 'create_event', 'delete_playlist')
        trigger_source: What triggered it (e.g., 'user_command', 'heartbeat', 'external_fetch')
        details: Additional context (dict or string)
        status: 'success', 'denied', 'failed'
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Master log (append-only)
    log_entry = {
        "timestamp": timestamp,
        "service": service,
        "action": action,
        "trigger_source": trigger_source,
        "details": details,
        "status": status
    }
    
    with open(API_LOG, 'a') as f:
        f.write(json.dumps(log_entry) + "\n")
    
    # Daily markdown log (human-readable)
    emoji = "✅" if status == "success" else "❌" if status == "failed" else "⚠️"
    details_str = json.dumps(details) if isinstance(details, dict) else str(details)
    
    daily_entry = f"{emoji} **{timestamp}** | {service} | `{action}` | Trigger: {trigger_source}\n"
    if details_str:
        daily_entry += f"   └─ {details_str}\n"
    daily_entry += "\n"
    
    # Create/append to daily log
    if not os.path.exists(DAILY_LOG):
        with open(DAILY_LOG, 'w') as f:
            f.write(f"# Security Log - {datetime.now().strftime('%Y-%m-%d')}\n\n")
    
    with open(DAILY_LOG, 'a') as f:
        f.write(daily_entry)
    
    return log_entry

def log_denied_action(service, action, reason, source="external"):
    """
    Log a denied/suspicious action attempt.
    """
    return log_api_action(
        service=service,
        action=action,
        trigger_source=source,
        details={"denial_reason": reason},
        status="denied"
    )

def get_todays_actions():
    """
    Return today's API actions as a list.
    """
    if not os.path.exists(API_LOG):
        return []
    
    today = datetime.now().strftime("%Y-%m-%d")
    actions = []
    
    with open(API_LOG, 'r') as f:
        for line in f:
            entry = json.loads(line.strip())
            if entry['timestamp'].startswith(today):
                actions.append(entry)
    
    return actions

if __name__ == "__main__":
    # Test the logger
    log_api_action(
        service="test_service",
        action="test_action",
        trigger_source="manual_test",
        details={"message": "Security logger initialized"}
    )
    print(f"✅ Security logger initialized")
    print(f"📝 Logs at: {LOG_DIR}")
