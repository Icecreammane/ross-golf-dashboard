#!/usr/bin/env python3
"""
Check for Hinge notifications and send via Telegram
Run this from heartbeat or cron to forward match notifications
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from hinge_notification_handler import check_and_send_notifications

def main():
    """Check for notifications and return message for Telegram"""
    message = check_and_send_notifications()
    
    if message:
        # Print message so it can be captured and sent
        print("SEND_TELEGRAM:" + message)
        return True
    else:
        # No notifications
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
