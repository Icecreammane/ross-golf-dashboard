#!/usr/bin/env python3
"""
Setup cron jobs for Hinge Auto-Pilot
Runs 2x per day: 8am and 7pm CST
"""

import subprocess
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
SCRIPT_PATH = WORKSPACE / "scripts" / "hinge_auto_swipe.py"

def setup_cron():
    """Setup cron jobs using Clawdbot"""
    
    print("⏰ Setting up Hinge Auto-Pilot automation...")
    print()
    
    # Morning session: 8:00 AM CST
    morning_cron = f"0 8 * * * cd {WORKSPACE} && /usr/local/bin/python3 {SCRIPT_PATH} --max-profiles 15"
    
    # Evening session: 7:00 PM CST
    evening_cron = f"0 19 * * * cd {WORKSPACE} && /usr/local/bin/python3 {SCRIPT_PATH} --max-profiles 15"
    
    print("📋 Cron jobs to add:")
    print()
    print("Morning session (8:00 AM CST):")
    print(morning_cron)
    print()
    print("Evening session (7:00 PM CST):")
    print(evening_cron)
    print()
    print("=" * 70)
    print("⚠️  MANUAL SETUP REQUIRED")
    print("=" * 70)
    print()
    print("To add these cron jobs:")
    print("1. Run: crontab -e")
    print("2. Add the two lines above")
    print("3. Save and exit")
    print()
    print("Or ask your assistant to set them up for you!")
    print()


if __name__ == "__main__":
    setup_cron()
