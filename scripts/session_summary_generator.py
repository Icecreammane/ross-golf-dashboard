#!/usr/bin/env python3
"""
Session Summary Generator - Auto-update SESSION_SUMMARY.md

Run this at the END of each major session to capture what was built,
decisions made, and context for next session.

Usage:
    python3 session_summary_generator.py
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
MEMORY_DIR = WORKSPACE / "memory"
SESSION_SUMMARY = WORKSPACE / "SESSION_SUMMARY.md"
DEPLOYMENTS = WORKSPACE / "DEPLOYMENTS.md"

def read_recent_memory():
    """Read last 2 days of memory logs"""
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    logs = []
    for date in [yesterday, today]:
        log_file = MEMORY_DIR / f"{date.strftime('%Y-%m-%d')}.md"
        if log_file.exists():
            logs.append(log_file.read_text())
    
    return "\n\n".join(logs)

def extract_key_info(memory_content):
    """Extract deployments, builds, decisions from memory"""
    # Look for common patterns
    deployments = []
    builds = []
    decisions = []
    
    lines = memory_content.split('\n')
    for i, line in enumerate(lines):
        # Detect URLs
        if 'http://' in line or 'https://' in line:
            deployments.append(line.strip())
        
        # Detect builds/ships
        if any(keyword in line.lower() for keyword in ['shipped', 'built', 'deployed', 'created']):
            builds.append(line.strip())
        
        # Detect decisions
        if any(keyword in line.lower() for keyword in ['decided', 'decision:', 'ross:', 'key decision']):
            decisions.append(line.strip())
    
    return {
        'deployments': deployments[:5],  # Top 5
        'builds': builds[:10],
        'decisions': decisions[:5]
    }

def generate_summary():
    """Generate SESSION_SUMMARY.md from recent memory"""
    memory = read_recent_memory()
    info = extract_key_info(memory)
    
    # Read current deployments
    deployments_content = ""
    if DEPLOYMENTS.exists():
        deployments_content = DEPLOYMENTS.read_text()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M CST")
    
    summary = f"""# SESSION SUMMARY - Last Session Briefing

**Generated:** {timestamp}
**Auto-updated:** End of major sessions

## 🚀 RECENT DEPLOYMENTS

{deployments_content if deployments_content else "No deployments tracked yet. See DEPLOYMENTS.md"}

## 🔨 WHAT WE BUILT RECENTLY

"""
    
    if info['builds']:
        for build in info['builds'][:10]:
            summary += f"- {build}\n"
    else:
        summary += "- (Review memory logs for details)\n"
    
    summary += f"""

## 💡 KEY DECISIONS

"""
    
    if info['decisions']:
        for decision in info['decisions'][:5]:
            summary += f"- {decision}\n"
    else:
        summary += "- (Review memory logs for decisions)\n"
    
    summary += f"""

## 📋 ACTIVE PROJECTS

### Check these files for status:
- `GOALS.md` - Current objectives
- `DEPLOYMENTS.md` - All live URLs
- `memory/{datetime.now().strftime('%Y-%m-%d')}.md` - Today's activity
- `TASK_QUEUE.md` - Pending tasks

## ✅ SESSION START CHECKLIST

1. ✅ Read this file (SESSION_SUMMARY.md)
2. ✅ Check current date/time
3. ✅ Read DEPLOYMENTS.md for live URLs
4. ✅ Read yesterday + today memory logs
5. ✅ Run memory_search if user asks about past work

---

**This file is auto-updated. Read it at the start of EVERY session.**
**Last updated:** {timestamp}
"""
    
    SESSION_SUMMARY.write_text(summary)
    print(f"✅ SESSION_SUMMARY.md updated: {timestamp}")
    print(f"   - {len(info['builds'])} builds captured")
    print(f"   - {len(info['decisions'])} decisions captured")
    print(f"   - {len(info['deployments'])} URLs found")

if __name__ == "__main__":
    generate_summary()
