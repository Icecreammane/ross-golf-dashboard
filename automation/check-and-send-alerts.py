#!/usr/bin/env python3
"""
Check for pending auto-recovery alerts and return them for the main agent to send.
Called during heartbeats to deliver alerts to Ross.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

MONITORING_DIR = Path.home() / "clawd" / "monitoring"
ALERT_FILE = MONITORING_DIR / "alert-pending.json"

def check_alerts():
    """Check for pending alerts and return them"""
    
    if not ALERT_FILE.exists():
        return []
    
    try:
        with open(ALERT_FILE, 'r') as f:
            alerts = json.load(f)
        
        if not alerts:
            return []
        
        # Return alert messages
        return alerts
        
    except Exception as e:
        print(f"Error reading alerts: {e}", file=sys.stderr)
        return []

def clear_alerts():
    """Clear pending alerts after they've been sent"""
    
    if ALERT_FILE.exists():
        try:
            ALERT_FILE.unlink()
            print("Cleared pending alerts", file=sys.stderr)
        except Exception as e:
            print(f"Error clearing alerts: {e}", file=sys.stderr)

def format_alert_for_telegram(alert):
    """Format alert message for Telegram"""
    
    message = alert.get('message', 'Unknown error')
    
    # Add timestamp
    timestamp = alert.get('timestamp', 'Unknown time')
    try:
        dt = datetime.fromisoformat(timestamp)
        time_str = dt.strftime('%I:%M %p')
    except:
        time_str = timestamp
    
    formatted = f"**Auto-Recovery Alert** ({time_str})\n\n{message}"
    
    return formatted

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Check for auto-recovery alerts')
    parser.add_argument('--format', choices=['json', 'text'], default='text',
                       help='Output format')
    parser.add_argument('--clear', action='store_true',
                       help='Clear alerts after reading')
    
    args = parser.parse_args()
    
    alerts = check_alerts()
    
    if not alerts:
        print("No pending alerts")
        sys.exit(0)
    
    if args.format == 'json':
        print(json.dumps(alerts, indent=2))
    else:
        print(f"Found {len(alerts)} pending alert(s):\n")
        for i, alert in enumerate(alerts, 1):
            print(f"Alert {i}:")
            print(format_alert_for_telegram(alert))
            print()
    
    if args.clear:
        clear_alerts()
