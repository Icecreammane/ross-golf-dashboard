#!/usr/bin/env python3
"""
Task Queue Auto-Generator
Reads GOALS.md hourly and generates priority tasks when queue is low
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE = Path("/Users/clawdbot/clawd")
GOALS_FILE = WORKSPACE / "GOALS.md"
QUEUE_FILE = WORKSPACE / "data" / "task-queue.json"
LOG_FILE = WORKSPACE / "logs" / "task-generator.log"

# Priority scoring
PRIORITY_WEIGHTS = {
    "revenue": 100,
    "infrastructure": 50,
    "personal": 25,
    "manual": 200  # Manual tasks always highest priority
}

def log(message):
    """Append to log file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    
    with open(LOG_FILE, "a") as f:
        f.write(log_line)
    
    print(log_line.strip())

def load_goals():
    """Parse GOALS.md and extract actionable items"""
    if not GOALS_FILE.exists():
        log("ERROR: GOALS.md not found")
        return []
    
    with open(GOALS_FILE) as f:
        content = f.read()
    
    goals = []
    
    # Extract revenue tasks (highest priority)
    revenue_patterns = [
        r"Ship (\d+) revenue products \((.*?)\)",
        r"\*\*Quick wins first:\*\* (.*?)(?=\n|$)",
        r"\*\*Build recurring:\*\* (.*?)(?=\n|$)",
        r"Anything that generates revenue within (\d+) days"
    ]
    
    for pattern in revenue_patterns:
        matches = re.findall(pattern, content)
        if matches:
            for match in matches:
                if isinstance(match, tuple):
                    match = " ".join(str(m) for m in match)
                goals.append({
                    "type": "revenue",
                    "raw": match
                })
    
    # Extract infrastructure tasks
    infra_section = re.search(r"### High Priority.*?### Medium Priority", content, re.DOTALL)
    if infra_section:
        lines = infra_section.group(0).split("\n")
        for line in lines:
            if line.strip().startswith("-"):
                task = line.strip("- ").strip()
                if task and not task.startswith("###"):
                    goals.append({
                        "type": "infrastructure",
                        "raw": task
                    })
    
    # Extract personal goals
    personal_patterns = [
        r"Hit daily macros \((.*?)\)",
        r"Start Florida Fund \(\$(.*?) goal.*?\)",
        r"Win fantasy championship"
    ]
    
    for pattern in personal_patterns:
        matches = re.findall(pattern, content)
        if matches:
            for match in matches:
                goals.append({
                    "type": "personal",
                    "raw": match if isinstance(match, str) else " ".join(match)
                })
    
    log(f"Extracted {len(goals)} goals from GOALS.md")
    return goals

def generate_tasks_from_goals(goals, count=5):
    """Convert goals into specific, actionable tasks"""
    tasks = []
    
    # Revenue tasks
    revenue_goals = [g for g in goals if g["type"] == "revenue"]
    if revenue_goals:
        tasks.append({
            "id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_1",
            "title": "Ship Golf Coaching MVP",
            "description": "Build $29/mo golf coaching subscription - landing page, payment, basic content",
            "priority": PRIORITY_WEIGHTS["revenue"],
            "type": "revenue",
            "context": "Quick win product from GOALS - targets $500 MRR",
            "created": datetime.now().isoformat(),
            "source": "auto-generated"
        })
        
        tasks.append({
            "id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_2",
            "title": "Launch Notion Templates Store",
            "description": "Create 3-5 Notion templates, set up Gumroad, launch at $19-29",
            "priority": PRIORITY_WEIGHTS["revenue"],
            "type": "revenue",
            "context": "Quick win product from GOALS - passive income",
            "created": datetime.now().isoformat(),
            "source": "auto-generated"
        })
    
    # Infrastructure tasks
    infra_goals = [g for g in goals if g["type"] == "infrastructure"]
    if infra_goals and len(tasks) < count:
        # Pick most relevant from parsed goals
        for goal in infra_goals[:2]:
            tasks.append({
                "id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(tasks)+1}",
                "title": goal["raw"][:50],
                "description": goal["raw"],
                "priority": PRIORITY_WEIGHTS["infrastructure"],
                "type": "infrastructure",
                "context": "From GOALS.md high priority builds",
                "created": datetime.now().isoformat(),
                "source": "auto-generated"
            })
    
    # Personal tasks
    personal_goals = [g for g in goals if g["type"] == "personal"]
    if personal_goals and len(tasks) < count:
        tasks.append({
            "id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(tasks)+1}",
            "title": "Fitness Tracker Automation",
            "description": "Build automation for daily macro tracking (200g protein, 2200 cal target)",
            "priority": PRIORITY_WEIGHTS["personal"],
            "type": "personal",
            "context": "Ross uses daily - high engagement",
            "created": datetime.now().isoformat(),
            "source": "auto-generated"
        })
    
    return tasks[:count]

def load_queue():
    """Load existing task queue, preserve manual tasks"""
    if not QUEUE_FILE.exists():
        log("No existing queue found, starting fresh")
        return []
    
    try:
        with open(QUEUE_FILE) as f:
            data = json.load(f)
            return data.get("tasks", [])
    except Exception as e:
        log(f"ERROR loading queue: {e}")
        return []

def save_queue(tasks):
    """Save task queue to JSON"""
    data = {
        "last_updated": datetime.now().isoformat(),
        "task_count": len(tasks),
        "tasks": tasks
    }
    
    with open(QUEUE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    
    log(f"Saved {len(tasks)} tasks to queue")

def should_generate_tasks(current_tasks):
    """Check if we need to generate new tasks"""
    active_tasks = [t for t in current_tasks if not t.get("completed", False)]
    
    if len(active_tasks) == 0:
        log("Queue empty - generating tasks")
        return True
    
    if len(active_tasks) < 3:
        log(f"Queue low ({len(active_tasks)} tasks) - generating more")
        return True
    
    log(f"Queue healthy ({len(active_tasks)} active tasks) - no generation needed")
    return False

def merge_tasks(existing, new_tasks):
    """Merge new tasks with existing, preserving manual additions"""
    # Keep all existing tasks (manual or completed)
    merged = existing.copy()
    
    # Add new tasks if they don't duplicate existing ones
    existing_titles = {t["title"].lower() for t in existing}
    
    for task in new_tasks:
        if task["title"].lower() not in existing_titles:
            merged.append(task)
            log(f"Added new task: {task['title']}")
    
    # Sort by priority (highest first)
    merged.sort(key=lambda t: t.get("priority", 0), reverse=True)
    
    return merged

def main():
    """Main execution"""
    log("=== Task Queue Generator Started ===")
    
    # Load current queue
    current_tasks = load_queue()
    log(f"Current queue: {len(current_tasks)} tasks")
    
    # Check if generation needed
    if not should_generate_tasks(current_tasks):
        log("=== No generation needed, exiting ===")
        return
    
    # Load goals and generate tasks
    goals = load_goals()
    if not goals:
        log("ERROR: No goals extracted, exiting")
        return
    
    new_tasks = generate_tasks_from_goals(goals, count=5)
    log(f"Generated {len(new_tasks)} new tasks")
    
    # Merge with existing
    merged_tasks = merge_tasks(current_tasks, new_tasks)
    
    # Save queue
    save_queue(merged_tasks)
    
    log("=== Task Queue Generator Complete ===")

if __name__ == "__main__":
    main()
