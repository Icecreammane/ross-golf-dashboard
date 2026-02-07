#!/usr/bin/env python3
"""
Alert Aggregator - Collect all monitor outputs and send consolidated alerts
Only sends messages when something genuinely needs attention
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MONITORING_DIR = Path(__file__).parent
STATE_FILE = MONITORING_DIR / 'state' / 'alert-state.json'
LOG_FILE = MONITORING_DIR / 'logs' / 'alerts.log'


def log_message(message):
    """Log to alerts.log"""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")


def run_monitor(script_name):
    """Run a monitor script and capture output"""
    script_path = MONITORING_DIR / script_name
    
    if not script_path.exists():
        log_message(f"Monitor not found: {script_name}")
        return None
    
    try:
        result = subprocess.run(
            ['python3', str(script_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            log_message(f"Invalid JSON from {script_name}: {result.stdout[:200]}")
            return None
    
    except subprocess.TimeoutExpired:
        log_message(f"Monitor timeout: {script_name}")
        return None
    except Exception as e:
        log_message(f"Monitor error {script_name}: {str(e)}")
        return None


def load_state():
    """Load alert state to track what we've already alerted on"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        'last_alert': None,
        'alerted_issues': []
    }


def save_state(state):
    """Save alert state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def format_alert_message(alerts):
    """Format alerts into a clear, actionable message"""
    if not alerts:
        return None
    
    count = len(alerts)
    
    if count == 1:
        alert = alerts[0]
        return f"🚨 {alert['title']}\n{alert['message']}"
    
    # Multiple alerts - create numbered list
    header = f"🚨 {count} things need attention:\n\n"
    items = []
    
    for i, alert in enumerate(alerts, 1):
        items.append(f"{i}. {alert['title']}: {alert['message']}")
    
    return header + '\n'.join(items)


def should_alert(alert_key, state):
    """Determine if we should send this alert (avoid spam)"""
    # If we've already alerted on this in the last hour, skip
    alerted = state.get('alerted_issues', [])
    
    for prev in alerted:
        if prev['key'] == alert_key:
            # Check timestamp
            prev_time = datetime.fromisoformat(prev['timestamp'])
            if (datetime.now() - prev_time).total_seconds() < 3600:
                return False  # Already alerted recently
    
    return True


def aggregate_alerts():
    """Run all monitors and aggregate alerts"""
    log_message("=== Starting monitoring check ===")
    
    state = load_state()
    alerts = []
    
    # Run email monitor
    email_result = run_monitor('monitor-email.py')
    if email_result and email_result.get('urgent_count', 0) > 0:
        count = email_result['urgent_count']
        top = email_result.get('top_urgent', [])
        
        alert_key = f"email:{count}"
        if should_alert(alert_key, state):
            message = f"{count} urgent email(s)"
            if top:
                subjects = [e['subject'][:50] for e in top]
                message += f"\n• " + "\n• ".join(subjects)
            
            alerts.append({
                'key': alert_key,
                'title': '📧 Urgent Email',
                'message': message,
                'severity': 'medium'
            })
            log_message(f"Alert: {count} urgent emails")
    
    # Run health monitor
    health_result = run_monitor('monitor-health.py')
    if health_result and health_result.get('alerts'):
        for alert in health_result['alerts']:
            alert_key = f"health:{alert['service']}"
            
            if should_alert(alert_key, state):
                severity = alert.get('severity', 'warning')
                icon = '🔴' if severity == 'critical' else '⚠️'
                
                alerts.append({
                    'key': alert_key,
                    'title': f"{icon} {alert['service'].title()}",
                    'message': alert['message'],
                    'severity': severity
                })
                log_message(f"Alert: {alert['message']}")
    
    # Sort by severity (critical first)
    alerts.sort(key=lambda a: 0 if a['severity'] == 'critical' else 1)
    
    # Send alert if needed
    if alerts:
        message = format_alert_message(alerts)
        send_alert_to_ross(message)
        
        # Update state
        state['last_alert'] = datetime.now().isoformat()
        state['alerted_issues'] = [
            {
                'key': a['key'],
                'timestamp': datetime.now().isoformat()
            }
            for a in alerts
        ]
        save_state(state)
        
        log_message(f"Sent alert with {len(alerts)} issue(s)")
        return {'status': 'alerted', 'count': len(alerts)}
    else:
        log_message("All checks passed - no alerts needed")
        return {'status': 'ok', 'count': 0}


def send_alert_to_ross(message):
    """Send alert message to Ross via Clawdbot"""
    # Use clawdbot message command to send to Ross
    try:
        # This will send to the main Telegram chat with Ross
        subprocess.run(
            ['clawdbot', 'message', 'send', '--channel', 'telegram', 
             '--target', '8412148376', '--message', message],
            timeout=30,
            check=True
        )
        log_message(f"Alert sent to Ross")
    except subprocess.CalledProcessError as e:
        log_message(f"Failed to send alert: {e}")
    except Exception as e:
        log_message(f"Error sending alert: {str(e)}")


if __name__ == '__main__':
    result = aggregate_alerts()
    print(json.dumps(result, indent=2))
    
    # Exit code indicates if alerts were sent
    sys.exit(0)
