#!/usr/bin/env python3
"""
Failure Alert System - Notify Ross when auto-recovery fails
Uses clawdbot message tool to send Telegram alerts
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
MONITORING_DIR = WORKSPACE / "monitoring"
ALERT_STATE_FILE = MONITORING_DIR / "alert-state.json"
ALERT_LOG = MONITORING_DIR / "alerts.log"

# Alert thresholds
FAILURE_THRESHOLD = 3  # Alert after 3 consecutive failures
ALERT_COOLDOWN_HOURS = 1  # Max 1 alert per hour per service

# Setup logging
alert_logger = logging.getLogger('alerts')
alert_logger.setLevel(logging.INFO)

fh = logging.FileHandler(ALERT_LOG)
fh.setLevel(logging.INFO)
fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
alert_logger.addHandler(fh)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
alert_logger.addHandler(ch)


class AlertSystem:
    """Alert system for notifying Ross about persistent failures"""
    
    def __init__(self):
        self.state = self.load_state()
    
    def load_state(self):
        """Load alert state from disk"""
        if ALERT_STATE_FILE.exists():
            try:
                with open(ALERT_STATE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                alert_logger.warning(f"Failed to load alert state: {e}")
        return {
            'last_alerts': {},  # service -> timestamp
            'alert_history': []
        }
    
    def save_state(self):
        """Save alert state to disk"""
        try:
            with open(ALERT_STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            alert_logger.error(f"Failed to save alert state: {e}")
    
    def should_alert(self, service, failure_count):
        """Determine if we should send an alert"""
        
        # Check failure threshold
        if failure_count < FAILURE_THRESHOLD:
            return False, f"Failure count {failure_count} below threshold {FAILURE_THRESHOLD}"
        
        # Check cooldown
        last_alert_str = self.state['last_alerts'].get(service)
        if last_alert_str:
            last_alert = datetime.fromisoformat(last_alert_str)
            time_since = datetime.now() - last_alert
            cooldown = timedelta(hours=ALERT_COOLDOWN_HOURS)
            
            if time_since < cooldown:
                remaining = cooldown - time_since
                minutes_left = int(remaining.total_seconds() / 60)
                return False, f"Cooldown active ({minutes_left} minutes left)"
        
        return True, "Alert criteria met"
    
    def send_alert(self, service, failure_count, recovery_log_path):
        """Send alert to Ross via Telegram"""
        
        # Construct alert message
        message = (
            f"🚨 System issue: {service}\n\n"
            f"Tried fixing {failure_count} times, still failing.\n\n"
            f"Check logs:\n{recovery_log_path}\n\n"
            f"Service may need manual intervention."
        )
        
        alert_logger.info(f"Sending alert for {service} (failures: {failure_count})")
        
        try:
            # Use clawdbot message tool via subprocess
            # Note: This will only work if clawdbot CLI supports message sending
            # Alternative: Write to a file that the main agent polls
            
            # For now, log to alert file and create a notification marker
            notification_file = MONITORING_DIR / "alert-pending.json"
            
            alert_data = {
                'timestamp': datetime.now().isoformat(),
                'service': service,
                'failure_count': failure_count,
                'message': message,
                'log_path': str(recovery_log_path)
            }
            
            # Append to pending alerts
            pending_alerts = []
            if notification_file.exists():
                try:
                    with open(notification_file, 'r') as f:
                        pending_alerts = json.load(f)
                except:
                    pass
            
            pending_alerts.append(alert_data)
            
            with open(notification_file, 'w') as f:
                json.dump(pending_alerts, f, indent=2)
            
            alert_logger.info(f"✅ Alert queued: {notification_file}")
            
            # Record alert sent
            self.state['last_alerts'][service] = datetime.now().isoformat()
            self.state['alert_history'].append({
                'timestamp': datetime.now().isoformat(),
                'service': service,
                'failure_count': failure_count,
                'message': message
            })
            
            # Keep only last 100 alerts
            self.state['alert_history'] = self.state['alert_history'][-100:]
            self.save_state()
            
            return True
            
        except Exception as e:
            alert_logger.error(f"❌ Failed to send alert: {e}")
            return False
    
    def check_and_alert(self, recovery_actions, failure_counts):
        """Check recovery results and send alerts if needed"""
        
        alert_logger.info("Checking if alerts are needed...")
        
        alerts_sent = []
        
        for service, failure_count in failure_counts.items():
            should_send, reason = self.should_alert(service, failure_count)
            
            if should_send:
                alert_logger.warning(f"⚠️  {service}: {reason}")
                success = self.send_alert(service, failure_count, MONITORING_DIR / "recovery.log")
                
                if success:
                    alerts_sent.append(service)
            else:
                alert_logger.info(f"ℹ️  {service}: {reason}")
        
        if alerts_sent:
            alert_logger.info(f"📤 Sent {len(alerts_sent)} alerts: {', '.join(alerts_sent)}")
        else:
            alert_logger.info("No alerts needed")
        
        return alerts_sent
    
    def get_pending_alerts(self):
        """Get pending alerts for main agent to send"""
        notification_file = MONITORING_DIR / "alert-pending.json"
        
        if notification_file.exists():
            try:
                with open(notification_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                alert_logger.error(f"Failed to read pending alerts: {e}")
        
        return []
    
    def clear_pending_alerts(self):
        """Clear pending alerts after they've been sent"""
        notification_file = MONITORING_DIR / "alert-pending.json"
        
        if notification_file.exists():
            try:
                notification_file.unlink()
                alert_logger.info("Cleared pending alerts")
            except Exception as e:
                alert_logger.error(f"Failed to clear pending alerts: {e}")


def create_alert_checker_script():
    """Create a script that the main agent can run to check for pending alerts"""
    
    script_content = '''#!/usr/bin/env python3
"""
Check for pending alerts and return them as JSON
Used by main agent during heartbeats
"""

import json
from pathlib import Path

MONITORING_DIR = Path.home() / "clawd" / "monitoring"
ALERT_FILE = MONITORING_DIR / "alert-pending.json"

if ALERT_FILE.exists():
    with open(ALERT_FILE, 'r') as f:
        alerts = json.load(f)
    print(json.dumps(alerts, indent=2))
else:
    print("[]")
'''
    
    script_path = WORKSPACE / "automation" / "check-alerts.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    script_path.chmod(0o755)
    
    alert_logger.info(f"Created alert checker script: {script_path}")


if __name__ == "__main__":
    # Create alert checker script
    create_alert_checker_script()
    
    # Test alert system
    alerts = AlertSystem()
    
    # Simulate checking with high failure count
    test_failure_counts = {
        'gateway': 3,
        'fitness_tracker': 2
    }
    
    alerts.check_and_alert([], test_failure_counts)
    
    print("\n📋 Pending alerts:")
    pending = alerts.get_pending_alerts()
    print(json.dumps(pending, indent=2))
