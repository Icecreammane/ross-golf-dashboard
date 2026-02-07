#!/usr/bin/env python3
"""
Morning Brief Generator - Compile overnight work and today's priorities
Usage: python3 morning-brief.py
"""

import os
import json
from datetime import datetime, timedelta
import glob

WORKSPACE = os.path.expanduser("~/clawd")

def read_file_safe(path):
    """Safely read a file, return empty string if not found"""
    try:
        with open(path, 'r') as f:
            return f.read()
    except:
        return ""

def get_overnight_work():
    """Check what was built overnight"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Check for new projects
    projects = []
    project_dir = os.path.join(WORKSPACE, "projects")
    if os.path.exists(project_dir):
        for proj in os.listdir(project_dir):
            if proj.startswith(yesterday) or proj.startswith(today):
                proj_path = os.path.join(project_dir, proj)
                if os.path.isdir(proj_path):
                    # Read HANDOFF.md or README.md
                    handoff = read_file_safe(os.path.join(proj_path, "HANDOFF.md"))
                    readme = read_file_safe(os.path.join(proj_path, "README.md"))
                    
                    projects.append({
                        "name": proj,
                        "path": proj_path,
                        "has_handoff": bool(handoff),
                        "has_readme": bool(readme)
                    })
    
    return projects

def get_today_priorities():
    """Extract today's priorities from TODO.md"""
    todo_path = os.path.join(WORKSPACE, "TODO.md")
    if not os.path.exists(todo_path):
        return []
    
    with open(todo_path) as f:
        lines = f.readlines()
    
    priorities = []
    in_high_priority = False
    
    for line in lines:
        if "## High Priority" in line:
            in_high_priority = True
            continue
        elif line.startswith("##"):
            in_high_priority = False
        
        if in_high_priority and line.strip().startswith("- [ ]"):
            # Extract task
            task = line.strip()[6:].split("—")[0].strip()
            priorities.append(task)
    
    return priorities[:3]  # Top 3

def get_system_alerts():
    """Check for any system alerts"""
    alerts = []
    
    # Check health log
    health_log = os.path.join(WORKSPACE, "monitoring/health.log")
    if os.path.exists(health_log):
        with open(health_log) as f:
            lines = f.readlines()
            for line in lines[-10:]:  # Last 10 lines
                if "ERROR" in line or "CRITICAL" in line or "DOWN" in line:
                    alerts.append(line.strip())
    
    return alerts

def generate_brief():
    """Generate the morning brief"""
    print("\n☀️ Good morning, sir.\n")
    
    # Overnight work
    projects = get_overnight_work()
    if projects:
        print("🛠️  BUILT LAST NIGHT:")
        for proj in projects:
            print(f"  • {proj['name']}")
            print(f"    Location: {proj['path']}")
            if proj['has_handoff']:
                print(f"    📖 See HANDOFF.md for testing instructions")
        print()
    else:
        print("🛠️  BUILT LAST NIGHT:")
        print("  No new projects (working on infrastructure upgrades)")
        print()
    
    # Today's priorities
    priorities = get_today_priorities()
    if priorities:
        print("📋 TODAY'S PRIORITIES:")
        for i, priority in enumerate(priorities, 1):
            print(f"  {i}. {priority}")
        print()
    
    # Alerts
    alerts = get_system_alerts()
    if alerts:
        print("🔔 ALERTS:")
        for alert in alerts:
            print(f"  ⚠️  {alert}")
        print()
    else:
        print("🔔 ALERTS:")
        print("  All systems operational ✅")
        print()
    
    # Footer
    print("━" * 50)
    print(f"⏰ {datetime.now().strftime('%A, %B %d %Y — %I:%M %p %Z')}")
    print()

if __name__ == "__main__":
    generate_brief()
