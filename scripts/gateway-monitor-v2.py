#!/usr/bin/env python3
"""
Gateway Monitor v2 - Aggressive Health Checking
Restarts gateway if it becomes unresponsive
"""

import subprocess
import time
import os
from datetime import datetime

LOG_FILE = os.path.expanduser("~/.clawdbot/logs/gateway-monitor.log")

def log(msg):
    """Log to file and print"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def is_gateway_alive():
    """Check if gateway responds to health check"""
    try:
        result = subprocess.run(
            ['curl', '-s', '--max-time', '3', 'http://127.0.0.1:18789/'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def restart_gateway():
    """Restart the gateway"""
    log("🔴 DETECTED: Gateway unresponsive - RESTARTING NOW")
    try:
        subprocess.run(['/Users/clawdbot/.npm-global/bin/clawdbot', 'gateway', 'restart'], timeout=30, capture_output=True)
        time.sleep(3)
        
        if is_gateway_alive():
            log("🟢 SUCCESS: Gateway restarted and online")
            return True
        else:
            log("⚠️  WARNING: Gateway restart completed but not yet responding")
            return False
    except Exception as e:
        log(f"❌ ERROR during restart: {e}")
        return False

# Create log directory
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

log("=" * 60)
log("🚀 Gateway Monitor v2 STARTED")
log("=" * 60)

check_count = 0
while True:
    try:
        check_count += 1
        
        if is_gateway_alive():
            # Gateway is healthy - silent
            if check_count % 10 == 0:
                log(f"✅ Health check #{check_count}: Gateway OK")
        else:
            # Gateway is down!
            restart_gateway()
        
        # Check every 10 seconds (more aggressive than before)
        time.sleep(10)
    
    except KeyboardInterrupt:
        log("👋 Monitor stopped by user")
        break
    except Exception as e:
        log(f"Monitor error: {e}")
        time.sleep(10)
