#!/usr/bin/env python3
"""
Health Monitor Daemon - Continuous system health checker
Runs every 5 minutes, logs to ~/clawd/monitoring/health.log
"""

import os
import sys
import time
import json
import psutil
import socket
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
WORKSPACE = Path.home() / "clawd"
MONITORING_DIR = WORKSPACE / "monitoring"
HEALTH_LOG = MONITORING_DIR / "health.log"
STATE_FILE = MONITORING_DIR / "health-state.json"
CHECK_INTERVAL = 300  # 5 minutes

# Ensure directories exist
MONITORING_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(HEALTH_LOG),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class HealthMonitor:
    """System health monitoring daemon"""
    
    def __init__(self):
        self.state = self.load_state()
        self.checks = {
            'gateway': self.check_gateway,
            'fitness_tracker': self.check_fitness_tracker,
            'hub_dashboard': self.check_hub_dashboard,
            'disk_space': self.check_disk_space,
            'memory': self.check_memory,
            'log_files': self.check_log_files
        }
    
    def load_state(self):
        """Load previous state from disk"""
        default_state = {
            'last_check': None,
            'check_history': [],
            'failure_counts': {}
        }
        
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_state.update(loaded)
                    return default_state
            except Exception as e:
                logger.warning(f"Failed to load state: {e}")
        
        return default_state
    
    def save_state(self):
        """Save current state to disk"""
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def check_gateway(self):
        """Check if clawdbot-gateway process is running"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmdline = proc.info.get('cmdline') or []
                if any('clawdbot-gateway' in str(arg) for arg in cmdline):
                    return {'status': 'ok', 'pid': proc.info['pid']}
            return {'status': 'down', 'message': 'Gateway process not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def check_fitness_tracker(self):
        """Check if fitness tracker is responding on port 3000"""
        return self._check_port(3000, 'Fitness Tracker')
    
    def check_hub_dashboard(self):
        """Check if hub dashboard is accessible on port 8080"""
        return self._check_port(8080, 'Hub Dashboard')
    
    def _check_port(self, port, service_name):
        """Generic port availability check"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                return {'status': 'ok', 'port': port}
            else:
                return {'status': 'down', 'message': f'{service_name} not responding on port {port}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def check_disk_space(self):
        """Check if disk space is above 10% free"""
        try:
            usage = psutil.disk_usage(str(WORKSPACE))
            percent_free = 100 - usage.percent
            
            if percent_free > 10:
                return {'status': 'ok', 'percent_free': round(percent_free, 2)}
            else:
                return {
                    'status': 'warning',
                    'percent_free': round(percent_free, 2),
                    'message': f'Low disk space: {percent_free:.1f}% free'
                }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def check_memory(self):
        """Check if memory usage is below 90%"""
        try:
            memory = psutil.virtual_memory()
            
            if memory.percent < 90:
                return {'status': 'ok', 'percent_used': round(memory.percent, 2)}
            else:
                return {
                    'status': 'warning',
                    'percent_used': round(memory.percent, 2),
                    'message': f'High memory usage: {memory.percent:.1f}%'
                }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def check_log_files(self):
        """Check if any log files exceed 100MB"""
        try:
            large_logs = []
            logs_dir = WORKSPACE / "logs"
            
            if logs_dir.exists():
                for log_file in logs_dir.rglob("*.log"):
                    size_mb = log_file.stat().st_size / (1024 * 1024)
                    if size_mb > 100:
                        large_logs.append({
                            'path': str(log_file.relative_to(WORKSPACE)),
                            'size_mb': round(size_mb, 2)
                        })
            
            if large_logs:
                return {
                    'status': 'warning',
                    'large_logs': large_logs,
                    'message': f'{len(large_logs)} log file(s) exceed 100MB'
                }
            else:
                return {'status': 'ok'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def run_checks(self):
        """Run all health checks and return results"""
        results = {}
        
        logger.info("=" * 60)
        logger.info("Running health checks...")
        
        for check_name, check_func in self.checks.items():
            try:
                result = check_func()
                results[check_name] = result
                
                status_emoji = {
                    'ok': '✅',
                    'warning': '⚠️',
                    'down': '❌',
                    'error': '🔥'
                }.get(result['status'], '❓')
                
                logger.info(f"{status_emoji} {check_name}: {result['status']}")
                
                if result.get('message'):
                    logger.info(f"   → {result['message']}")
                
            except Exception as e:
                logger.error(f"❌ {check_name}: EXCEPTION - {e}")
                results[check_name] = {'status': 'error', 'message': str(e)}
        
        # Update state
        self.state['last_check'] = datetime.now().isoformat()
        self.state['check_history'].append({
            'timestamp': datetime.now().isoformat(),
            'results': results
        })
        
        # Keep only last 100 checks
        self.state['check_history'] = self.state['check_history'][-100:]
        
        self.save_state()
        
        return results
    
    def run(self):
        """Main daemon loop"""
        logger.info("🚀 Health Monitor Daemon starting...")
        logger.info(f"Workspace: {WORKSPACE}")
        logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
        logger.info(f"Log file: {HEALTH_LOG}")
        
        try:
            while True:
                results = self.run_checks()
                
                # Count failures
                failures = sum(1 for r in results.values() if r['status'] in ['down', 'error'])
                warnings = sum(1 for r in results.values() if r['status'] == 'warning')
                
                logger.info(f"Check complete: {failures} failures, {warnings} warnings")
                logger.info(f"Next check in {CHECK_INTERVAL} seconds")
                logger.info("=" * 60)
                
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("🛑 Health Monitor stopped by user")
        except Exception as e:
            logger.error(f"🔥 Health Monitor crashed: {e}")
            raise


if __name__ == "__main__":
    monitor = HealthMonitor()
    monitor.run()
