#!/usr/bin/env python3
"""
build_status.py - Show current build status

Quick status check for what's building, queued, and completed.
"""

import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
BUILD_STATUS_FILE = WORKSPACE / "BUILD_STATUS.md"
BUILD_QUEUE_FILE = WORKSPACE / "BUILD_QUEUE.md"
PROGRESS_FILE = WORKSPACE / "progress-data.json"


def show_status():
    """Show comprehensive build status"""
    print("🔧 Build Status")
    print("=" * 60)
    
    # Check current build status
    if BUILD_STATUS_FILE.exists():
        with open(BUILD_STATUS_FILE, "r") as f:
            content = f.read()
        
        if "building" in content.lower() or "in progress" in content.lower():
            print("\n🔵 Currently Building:")
            # Extract task name
            for line in content.split("\n"):
                if line.startswith("**Task:**"):
                    task = line.replace("**Task:**", "").strip()
                    print(f"   {task}")
                elif line.startswith("**ETA:**"):
                    eta = line.replace("**ETA:**", "").strip()
                    print(f"   └─ ETA: {eta}")
        else:
            print("\n⚪ No active builds")
    else:
        print("\n⚪ No active builds")
    
    # Check progress data
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r") as f:
                progress = json.load(f)
            
            if progress.get("agents"):
                print("\n📊 Active Agents:")
                for agent_data in progress["agents"].values():
                    state = agent_data.get("state", "Unknown")
                    percent = agent_data.get("percent", 0)
                    task = agent_data.get("task_name", "Unknown")
                    message = agent_data.get("message", "")
                    
                    status_icon = {
                        "Complete": "🟢",
                        "Failed": "🔴",
                        "Testing": "🧪",
                    }.get(state, "🔵")
                    
                    print(f"   {status_icon} {task}")
                    print(f"      └─ {state} ({percent}%): {message}")
        except json.JSONDecodeError:
            pass
    
    # Check queue
    if BUILD_QUEUE_FILE.exists():
        with open(BUILD_QUEUE_FILE, "r") as f:
            content = f.read()
        
        pending = []
        for line in content.split("\n"):
            if line.strip().startswith("- [ ]"):
                task = line.replace("- [ ]", "").strip()
                pending.append(task)
        
        if pending:
            print(f"\n📋 Queue ({len(pending)} pending):")
            for i, task in enumerate(pending[:5], 1):
                # Truncate long tasks
                if len(task) > 60:
                    task = task[:57] + "..."
                print(f"   {i}. {task}")
            
            if len(pending) > 5:
                print(f"   ... and {len(pending) - 5} more")
        else:
            print("\n📋 Queue: Empty")
    else:
        print("\n📋 Queue: No queue file")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    show_status()
