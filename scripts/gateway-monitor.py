#!/usr/bin/env python3
"""
Gateway Stability Monitor
Monitors gateway process and auto-restarts if it crashes or becomes unresponsive
"""

import subprocess
import time
import os
import signal
import sys
from datetime import datetime
from pathlib import Path

class GatewayMonitor:
    def __init__(self):
        self.log_file = Path.home() / '.clawdbot' / 'logs' / 'monitor.log'
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.gateway_pid = None
        self.restart_count = 0
        self.last_restart = None
        self.health_check_interval = 30  # seconds
        self.max_restarts_per_hour = 5
    
    def log(self, msg):
        """Log to file and stdout"""
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] {msg}"
        print(log_line)
        with open(self.log_file, 'a') as f:
            f.write(log_line + '\n')
    
    def get_gateway_pid(self):
        """Get current gateway PID"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'clawdbot-gateway'],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                return int(result.stdout.strip().split()[0])
        except:
            pass
        return None
    
    def is_gateway_alive(self):
        """Check if gateway process is still running"""
        pid = self.get_gateway_pid()
        if not pid:
            return False
        
        try:
            os.kill(pid, 0)  # Signal 0 checks if process exists
            return True
        except:
            return False
    
    def is_gateway_responsive(self):
        """Health check: Can we talk to the gateway?"""
        try:
            # Try to reach gateway status
            result = subprocess.run(
                ['curl', '-s', '--max-time', '5', 'http://localhost:7001/health'],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def restart_gateway(self):
        """Restart the gateway"""
        timestamp = datetime.now()
        
        # Check restart rate limit
        if self.last_restart:
            time_since_restart = (timestamp - self.last_restart).total_seconds()
            if time_since_restart < 3600:  # Within an hour
                if self.restart_count >= self.max_restarts_per_hour:
                    self.log(f"⚠️  RATE LIMITED: {self.restart_count} restarts in last hour")
                    return False
        
        self.log(f"🔄 RESTARTING gateway (attempt #{self.restart_count + 1})")
        
        try:
            # Stop current process if it exists
            pid = self.get_gateway_pid()
            if pid:
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
            
            # Restart via clawdbot
            result = subprocess.run(
                ['clawdbot', 'gateway', 'restart'],
                capture_output=True,
                timeout=30
            )
            
            time.sleep(3)  # Wait for restart
            
            if self.is_gateway_alive():
                self.log("✅ Gateway restarted successfully")
                self.restart_count += 1
                self.last_restart = timestamp
                return True
            else:
                self.log("❌ Gateway restart failed")
                return False
        
        except Exception as e:
            self.log(f"❌ Restart error: {e}")
            return False
    
    def monitor_loop(self):
        """Main monitoring loop"""
        self.log("🚀 Gateway Monitor started")
        
        check_count = 0
        while True:
            try:
                check_count += 1
                
                # Full health check every 10 iterations, simple check otherwise
                if check_count % 10 == 0:
                    is_alive = self.is_gateway_alive()
                    is_responsive = self.is_gateway_responsive() if is_alive else False
                else:
                    is_alive = self.is_gateway_alive()
                    is_responsive = is_alive  # Assume responsive if alive
                
                if not is_alive:
                    self.log("⚠️  Gateway process not found")
                    self.restart_gateway()
                elif not is_responsive:
                    self.log("⚠️  Gateway not responding to health check")
                    self.restart_gateway()
                else:
                    # All good (silent)
                    pass
                
                time.sleep(self.health_check_interval)
            
            except KeyboardInterrupt:
                self.log("👋 Monitor shutdown")
                sys.exit(0)
            except Exception as e:
                self.log(f"Monitor error: {e}")
                time.sleep(self.health_check_interval)


def main():
    monitor = GatewayMonitor()
    monitor.monitor_loop()


if __name__ == '__main__':
    main()
