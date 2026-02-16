#!/usr/bin/env python3
"""
Hinge Notification Handler
Checks for pending notifications and sends them via Telegram
"""

import json
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
NOTIFICATION_FILE = WORKSPACE / "data" / "pending_notification.txt"


def check_and_send_notifications():
    """Check for pending notifications and return message to send"""
    
    if not NOTIFICATION_FILE.exists():
        return None
    
    # Read notification
    with open(NOTIFICATION_FILE, 'r') as f:
        content = f.read().strip()
    
    # Delete file
    NOTIFICATION_FILE.unlink()
    
    # Parse notification
    if content.startswith('HINGE_MATCH:'):
        message = content.replace('HINGE_MATCH:', '').strip()
        return message
    
    return None


if __name__ == "__main__":
    msg = check_and_send_notifications()
    if msg:
        print("📱 Notification to send:")
        print(msg)
    else:
        print("✅ No pending notifications")
