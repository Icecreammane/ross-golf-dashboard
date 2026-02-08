#!/usr/bin/env python3
"""
Task Manager CLI - Manually add/view/complete tasks
"""

import json
import sys
from datetime import datetime
from pathlib import Path

QUEUE_FILE = Path("/Users/clawdbot/clawd/data/task-queue.json")

def load_queue():
    """Load task queue"""
    if not QUEUE_FILE.exists():
        return {"tasks": [], "last_updated": "", "task_count": 0}
    
    with open(QUEUE_FILE) as f:
        return json.load(f)

def save_queue(data):
    """Save task queue"""
    data["last_updated"] = datetime.now().isoformat()
    data["task_count"] = len(data["tasks"])
    
    with open(QUEUE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def list_tasks():
    """Display all tasks"""
    data = load_queue()
    tasks = data.get("tasks", [])
    
    if not tasks:
        print("📭 Task queue is empty")
        return
    
    print(f"\n📋 Task Queue ({len(tasks)} tasks)\n")
    print("=" * 80)
    
    for i, task in enumerate(tasks, 1):
        status = "✅" if task.get("completed") else "⏳"
        source = task.get("source", "unknown")
        priority = task.get("priority", 0)
        
        print(f"\n{status} [{i}] {task['title']}")
        print(f"    Priority: {priority} | Type: {task.get('type', 'unknown')} | Source: {source}")
        print(f"    {task['description']}")
        if task.get("context"):
            print(f"    Context: {task['context']}")
    
    print("\n" + "=" * 80)

def add_task(title, description, priority=200):
    """Add a manual task"""
    data = load_queue()
    
    task = {
        "id": f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "title": title,
        "description": description,
        "priority": priority,
        "type": "manual",
        "context": "Manually added by Ross",
        "created": datetime.now().isoformat(),
        "source": "manual"
    }
    
    # Add task and re-sort by priority
    data.setdefault("tasks", []).append(task)
    data["tasks"].sort(key=lambda t: t.get("priority", 0), reverse=True)
    save_queue(data)
    
    print(f"✅ Added task: {title}")
    print(f"   Priority: {priority}")

def complete_task(task_number):
    """Mark task as completed"""
    data = load_queue()
    tasks = data.get("tasks", [])
    
    if task_number < 1 or task_number > len(tasks):
        print(f"❌ Invalid task number: {task_number}")
        return
    
    task = tasks[task_number - 1]
    task["completed"] = True
    task["completed_at"] = datetime.now().isoformat()
    
    save_queue(data)
    print(f"✅ Completed: {task['title']}")

def remove_task(task_number):
    """Remove a task"""
    data = load_queue()
    tasks = data.get("tasks", [])
    
    if task_number < 1 or task_number > len(tasks):
        print(f"❌ Invalid task number: {task_number}")
        return
    
    task = tasks.pop(task_number - 1)
    save_queue(data)
    print(f"🗑️  Removed: {task['title']}")

def clear_completed():
    """Remove all completed tasks"""
    data = load_queue()
    tasks = data.get("tasks", [])
    
    before = len(tasks)
    data["tasks"] = [t for t in tasks if not t.get("completed")]
    after = len(data["tasks"])
    
    save_queue(data)
    print(f"🧹 Cleared {before - after} completed tasks")

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Task Manager - Usage:")
        print("  python3 task_manager.py list")
        print("  python3 task_manager.py add 'Title' 'Description' [priority]")
        print("  python3 task_manager.py complete <number>")
        print("  python3 task_manager.py remove <number>")
        print("  python3 task_manager.py clear")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_tasks()
    
    elif command == "add":
        if len(sys.argv) < 4:
            print("❌ Usage: add 'Title' 'Description' [priority]")
            return
        title = sys.argv[2]
        description = sys.argv[3]
        priority = int(sys.argv[4]) if len(sys.argv) > 4 else 200
        add_task(title, description, priority)
    
    elif command == "complete":
        if len(sys.argv) < 3:
            print("❌ Usage: complete <task_number>")
            return
        complete_task(int(sys.argv[2]))
    
    elif command == "remove":
        if len(sys.argv) < 3:
            print("❌ Usage: remove <task_number>")
            return
        remove_task(int(sys.argv[2]))
    
    elif command == "clear":
        clear_completed()
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
