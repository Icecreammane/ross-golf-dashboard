#!/usr/bin/env python3
"""
Remote Gateway Restart
Allows restarting the gateway via Telegram command
Usage: /restart-gateway
"""

import subprocess
import sys
from datetime import datetime

def restart_gateway():
    """Restart the Clawdbot gateway"""
    timestamp = datetime.now().isoformat()
    
    print(f"[{timestamp}] 🔄 Remote gateway restart initiated...")
    
    try:
        # Restart gateway
        result = subprocess.run(
            ['clawdbot', 'gateway', 'restart'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ Gateway restart command sent successfully")
            return True
        else:
            print(f"⚠️  Gateway restart returned code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        print("❌ Restart command timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == '__main__':
    success = restart_gateway()
    sys.exit(0 if success else 1)
