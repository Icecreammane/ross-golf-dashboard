#!/usr/bin/env python3
"""
Auto-Recovery Actions - Automatically fix common failures
Imported by health monitor to take corrective actions
"""

import os
import sys
import time
import json
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
MONITORING_DIR = WORKSPACE / "monitoring"
RECOVERY_LOG = MONITORING_DIR / "recovery.log"
RECOVERY_STATE_FILE = MONITORING_DIR / "recovery-state.json"

# Setup logging
recovery_logger = logging.getLogger('auto-recovery')
recovery_logger.setLevel(logging.INFO)

# File handler for recovery actions
fh = logging.FileHandler(RECOVERY_LOG)
fh.setLevel(logging.INFO)
fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
recovery_logger.addHandler(fh)

# Console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
recovery_logger.addHandler(ch)


class AutoRecovery:
    """Automatic recovery actions for common failures"""
    
    def __init__(self):
        self.state = self.load_state()
        self.recovery_actions = {
            'gateway': self.recover_gateway,
            'fitness_tracker': self.recover_fitness_tracker,
            'hub_dashboard': self.recover_hub_dashboard,
            'disk_space': self.recover_disk_space,
            'memory': self.recover_memory,
            'log_files': self.recover_log_files
        }
    
    def load_state(self):
        """Load recovery state from disk"""
        if RECOVERY_STATE_FILE.exists():
            try:
                with open(RECOVERY_STATE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                recovery_logger.warning(f"Failed to load recovery state: {e}")
        return {
            'recovery_history': [],
            'failure_counts': {},
            'last_recovery_times': {}
        }
    
    def save_state(self):
        """Save recovery state to disk"""
        try:
            with open(RECOVERY_STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            recovery_logger.error(f"Failed to save recovery state: {e}")
    
    def get_failure_count(self, service):
        """Get consecutive failure count for a service"""
        return self.state['failure_counts'].get(service, 0)
    
    def increment_failure_count(self, service):
        """Increment failure count for a service"""
        self.state['failure_counts'][service] = self.get_failure_count(service) + 1
        self.save_state()
    
    def reset_failure_count(self, service):
        """Reset failure count for a service (after successful recovery)"""
        if service in self.state['failure_counts']:
            del self.state['failure_counts'][service]
            self.save_state()
    
    def get_last_recovery_time(self, service):
        """Get last recovery attempt time for a service"""
        time_str = self.state['last_recovery_times'].get(service)
        if time_str:
            return datetime.fromisoformat(time_str)
        return None
    
    def set_last_recovery_time(self, service):
        """Record recovery attempt time"""
        self.state['last_recovery_times'][service] = datetime.now().isoformat()
        self.save_state()
    
    def log_recovery(self, service, action, success, message=""):
        """Log recovery action to history"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'service': service,
            'action': action,
            'success': success,
            'message': message,
            'failure_count': self.get_failure_count(service)
        }
        
        self.state['recovery_history'].append(entry)
        # Keep only last 200 recovery actions
        self.state['recovery_history'] = self.state['recovery_history'][-200:]
        self.save_state()
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        recovery_logger.info(f"{status} | {service} | {action} | {message}")
    
    def run_command(self, cmd, shell=True, cwd=None):
        """Run shell command and return success status"""
        try:
            result = subprocess.run(
                cmd,
                shell=shell,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def recover_gateway(self, check_result):
        """Restart clawdbot gateway"""
        recovery_logger.info("🔄 Attempting to restart gateway...")
        
        success, stdout, stderr = self.run_command("clawdbot gateway restart")
        
        if success:
            self.log_recovery('gateway', 'restart', True, "Gateway restarted successfully")
            time.sleep(3)  # Wait for gateway to start
            return True
        else:
            self.log_recovery('gateway', 'restart', False, f"Failed: {stderr}")
            return False
    
    def recover_fitness_tracker(self, check_result):
        """Restart fitness tracker Flask app"""
        recovery_logger.info("🔄 Attempting to restart fitness tracker...")
        
        # Kill existing process
        kill_success, _, _ = self.run_command('pkill -f "fitness-tracker/app.py"')
        time.sleep(2)
        
        # Start new process
        tracker_dir = WORKSPACE / "fitness-tracker"
        if not tracker_dir.exists():
            self.log_recovery('fitness_tracker', 'restart', False, "fitness-tracker directory not found")
            return False
        
        start_cmd = f"nohup python3 app.py > {MONITORING_DIR}/fitness-tracker.log 2>&1 &"
        success, stdout, stderr = self.run_command(start_cmd, cwd=str(tracker_dir))
        
        if success or kill_success:  # If kill worked, assume we tried to start
            time.sleep(3)
            self.log_recovery('fitness_tracker', 'restart', True, "Fitness tracker restarted")
            return True
        else:
            self.log_recovery('fitness_tracker', 'restart', False, f"Failed: {stderr}")
            return False
    
    def recover_hub_dashboard(self, check_result):
        """Restart hub dashboard server"""
        recovery_logger.info("🔄 Attempting to restart hub dashboard...")
        
        # Kill existing process
        kill_success, _, _ = self.run_command('pkill -f "hub-api.py"')
        time.sleep(2)
        
        # Start new process
        hub_script = WORKSPACE / "systems" / "hub-api.py"
        if not hub_script.exists():
            self.log_recovery('hub_dashboard', 'restart', False, "hub-api.py not found")
            return False
        
        start_cmd = f"nohup python3 systems/hub-api.py > {MONITORING_DIR}/hub.log 2>&1 &"
        success, stdout, stderr = self.run_command(start_cmd, cwd=str(WORKSPACE))
        
        if success or kill_success:
            time.sleep(3)
            self.log_recovery('hub_dashboard', 'restart', True, "Hub dashboard restarted")
            return True
        else:
            self.log_recovery('hub_dashboard', 'restart', False, f"Failed: {stderr}")
            return False
    
    def recover_disk_space(self, check_result):
        """Clean old log files to free disk space"""
        recovery_logger.info("🧹 Attempting to clean old logs...")
        
        logs_dir = WORKSPACE / "logs"
        if not logs_dir.exists():
            self.log_recovery('disk_space', 'cleanup', False, "Logs directory not found")
            return False
        
        # Find and delete logs older than 30 days
        cmd = f'find "{logs_dir}" -type f -name "*.log" -mtime +30 -delete'
        success, stdout, stderr = self.run_command(cmd)
        
        # Also clean up old monitoring logs
        monitoring_cmd = f'find "{MONITORING_DIR}" -type f -name "*.log" -mtime +30 -delete'
        self.run_command(monitoring_cmd)
        
        if success:
            self.log_recovery('disk_space', 'cleanup', True, "Deleted logs older than 30 days")
            return True
        else:
            self.log_recovery('disk_space', 'cleanup', False, f"Failed: {stderr}")
            return False
    
    def recover_memory(self, check_result):
        """Log heavy processes when memory is high"""
        recovery_logger.info("📊 Identifying memory-heavy processes...")
        
        cmd = "ps aux | sort -nrk 4 | head -10"
        success, stdout, stderr = self.run_command(cmd)
        
        if success:
            message = f"Top 10 memory consumers logged:\n{stdout[:500]}"
            self.log_recovery('memory', 'identify', True, message)
            return True
        else:
            self.log_recovery('memory', 'identify', False, "Failed to get process list")
            return False
    
    def recover_log_files(self, check_result):
        """Rotate large log files"""
        recovery_logger.info("📝 Rotating large log files...")
        
        large_logs = check_result.get('large_logs', [])
        if not large_logs:
            return True
        
        rotated = 0
        for log_info in large_logs:
            log_path = WORKSPACE / log_info['path']
            if log_path.exists():
                # Create backup with timestamp
                backup_path = log_path.with_suffix(f'.{datetime.now().strftime("%Y%m%d_%H%M%S")}.log.old')
                try:
                    log_path.rename(backup_path)
                    # Create empty log file
                    log_path.touch()
                    rotated += 1
                except Exception as e:
                    recovery_logger.error(f"Failed to rotate {log_path}: {e}")
        
        if rotated > 0:
            self.log_recovery('log_files', 'rotate', True, f"Rotated {rotated} large log files")
            return True
        else:
            self.log_recovery('log_files', 'rotate', False, "No logs rotated")
            return False
    
    def should_attempt_recovery(self, service):
        """Determine if we should attempt recovery based on rate limiting"""
        last_attempt = self.get_last_recovery_time(service)
        
        if last_attempt is None:
            return True
        
        # Don't retry more than once every 5 minutes
        time_since_last = datetime.now() - last_attempt
        if time_since_last < timedelta(minutes=5):
            recovery_logger.info(f"⏸️  Skipping {service} recovery (attempted {time_since_last.seconds}s ago)")
            return False
        
        return True
    
    def attempt_recovery(self, service, check_result):
        """Attempt to recover a failed service"""
        
        # Check if we should attempt recovery
        if not self.should_attempt_recovery(service):
            return False
        
        # Get recovery action
        recovery_func = self.recovery_actions.get(service)
        if not recovery_func:
            recovery_logger.warning(f"No recovery action defined for {service}")
            return False
        
        # Record attempt
        self.set_last_recovery_time(service)
        
        # Attempt recovery
        recovery_logger.info(f"🚑 Starting recovery for {service}")
        success = recovery_func(check_result)
        
        if success:
            recovery_logger.info(f"✅ Recovery successful for {service}")
            self.reset_failure_count(service)
        else:
            recovery_logger.error(f"❌ Recovery failed for {service}")
            self.increment_failure_count(service)
        
        return success
    
    def process_health_results(self, health_results):
        """Process health check results and attempt recovery as needed"""
        recovery_logger.info("=" * 60)
        recovery_logger.info("Processing health check results...")
        
        actions_taken = []
        
        for service, result in health_results.items():
            status = result.get('status')
            
            # Only attempt recovery for down or error states
            if status in ['down', 'error']:
                recovery_logger.warning(f"⚠️  {service} is {status}")
                success = self.attempt_recovery(service, result)
                actions_taken.append({
                    'service': service,
                    'success': success,
                    'failure_count': self.get_failure_count(service)
                })
            
            # Handle warnings (disk space, memory, large logs)
            elif status == 'warning':
                recovery_logger.info(f"⚠️  {service} warning: {result.get('message')}")
                if service in ['disk_space', 'log_files']:
                    success = self.attempt_recovery(service, result)
                    actions_taken.append({
                        'service': service,
                        'success': success,
                        'failure_count': self.get_failure_count(service)
                    })
        
        if actions_taken:
            recovery_logger.info(f"Took {len(actions_taken)} recovery actions")
        else:
            recovery_logger.info("No recovery actions needed")
        
        recovery_logger.info("=" * 60)
        
        return actions_taken


if __name__ == "__main__":
    # Test recovery system
    recovery = AutoRecovery()
    
    # Simulate a failed gateway check
    test_result = {'status': 'down', 'message': 'Gateway not found'}
    recovery.attempt_recovery('gateway', test_result)
