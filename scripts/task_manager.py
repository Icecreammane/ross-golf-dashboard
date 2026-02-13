#!/usr/bin/env python3
"""
Task Manager - Move tasks between Kanban columns
"""

import json
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / "clawd"
KANBAN_FILE = WORKSPACE / "data" / "kanban.json"

def load_kanban():
    with open(KANBAN_FILE) as f:
        return json.load(f)

def save_kanban(kanban):
    with open(KANBAN_FILE, 'w') as f:
        json.dump(kanban, f, indent=2)
    # Regenerate dashboard
    import subprocess
    subprocess.run([sys.executable, str(WORKSPACE / "scripts" / "daily_task_generator.py")], 
                   capture_output=True)

def move_task(task_id, to_column):
    """Move a task to a different column"""
    kanban = load_kanban()
    
    # Find and remove task
    task = None
    for column in ['todo', 'in_progress', 'done']:
        for i, t in enumerate(kanban[column]):
            if t['id'] == task_id:
                task = kanban[column].pop(i)
                break
        if task:
            break
    
    if not task:
        print(f"❌ Task {task_id} not found")
        return False
    
    # Update status and timestamp
    task['status'] = to_column
    if to_column == 'in_progress' and 'started_at' not in task:
        task['started_at'] = datetime.now().isoformat()
    if to_column == 'done':
        task['completed_at'] = datetime.now().isoformat()
    
    # Add to new column
    kanban[to_column].append(task)
    
    save_kanban(kanban)
    print(f"✅ Moved task to {to_column}: {task['title']}")
    return True

def list_tasks():
    """List all tasks"""
    kanban = load_kanban()
    
    print("\n📋 TO DO:")
    for task in kanban['todo']:
        print(f"  [{task['id']}] {task['title']} ({task['priority']})")
    
    print("\n⚡ IN PROGRESS:")
    for task in kanban['in_progress']:
        print(f"  [{task['id']}] {task['title']}")
    
    print("\n✅ DONE:")
    for task in kanban['done'][:5]:  # Show last 5
        print(f"  [{task['id']}] {task['title']}")

def start_task(task_id):
    """Move task to in_progress"""
    return move_task(task_id, 'in_progress')

def complete_task(task_id):
    """Move task to done"""
    return move_task(task_id, 'done')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  task_manager.py list")
        print("  task_manager.py start <task_id>")
        print("  task_manager.py complete <task_id>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list':
        list_tasks()
    elif command == 'start' and len(sys.argv) > 2:
        start_task(sys.argv[2])
    elif command == 'complete' and len(sys.argv) > 2:
        complete_task(sys.argv[2])
    else:
        print("Unknown command")
        sys.exit(1)
