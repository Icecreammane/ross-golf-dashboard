#!/usr/bin/env python3
"""
Email Triage Daemon - Hourly inbox check
Runs every hour via cron
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from email_triage import check_inbox

if __name__ == '__main__':
    check_inbox()
