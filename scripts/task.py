#!/usr/bin/env python3
"""
Task Queue Manager - Manage TODO.md from command line
Usage:
  python3 task.py list              # Show all tasks
  python3 task.py add "Task name"   # Add new task
  python3 task.py done N            # Mark task N as done
  python3 task.py priority          # Show high priority only
"""

import os
import sys
from datetime import datetime

TODO_PATH = os.path.expanduser("~/clawd/TODO.md")

def read_todo():
    """Read and parse TODO.md"""
    if not os.path.exists(TODO_PATH):
        return []
    
    with open(TODO_PATH) as f:
        return f.readlines()

def write_todo(lines):
    """Write back to TODO.md"""
    with open(TODO_PATH, 'w') as f:
        f.writelines(lines)
    
    # Update timestamp
    for i, line in enumerate(lines):
        if line.startswith("**Updated:**"):
            lines[i] = f"**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M CST')}\n"
            break
    
    with open(TODO_PATH, 'w') as f:
        f.writelines(lines)

def list_tasks(priority_only=False):
    """List all tasks with numbers"""
    lines = read_todo()
    
    task_num = 1
    current_section = ""
    
    print("\n📋 TODO LIST")
    print("━" * 50)
    
    for line in lines:
        if line.startswith("## ") and not line.startswith("## Completed"):
            current_section = line.strip()[3:]
            if priority_only and "High Priority" not in current_section:
                continue
            print(f"\n{current_section}")
        
        if line.strip().startswith("- [ ]"):
            task = line.strip()[6:]
            print(f"  [{task_num}] {task}")
            task_num += 1
        
        elif line.strip().startswith("- [x]") and not priority_only:
            task = line.strip()[6:]
            print(f"  [✓] {task}")
    
    print()

def add_task(task_description):
    """Add a new task to high priority"""
    lines = read_todo()
    
    # Find high priority section
    insert_idx = None
    for i, line in enumerate(lines):
        if "## High Priority" in line:
            # Find first blank line after section header
            for j in range(i+1, len(lines)):
                if lines[j].strip() == "":
                    insert_idx = j
                    break
            break
    
    if insert_idx is None:
        print("❌ Couldn't find High Priority section")
        return
    
    # Insert new task
    new_task = f"- [ ] **{task_description}** — Added {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    lines.insert(insert_idx, new_task)
    
    write_todo(lines)
    print(f"✅ Added: {task_description}")

def mark_done(task_number):
    """Mark a task as complete"""
    lines = read_todo()
    
    task_count = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("- [ ]"):
            task_count += 1
            if task_count == task_number:
                # Move to completed section
                task = line.strip()[6:]
                lines[i] = f"- [x] {task} — Completed {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                
                # Find completed section
                completed_idx = None
                for j, cline in enumerate(lines):
                    if "## Completed" in cline:
                        completed_idx = j + 2
                        break
                
                if completed_idx:
                    # Move task to completed
                    completed_task = lines.pop(i)
                    lines.insert(completed_idx, completed_task)
                
                write_todo(lines)
                print(f"✅ Completed: {task}")
                return
    
    print(f"❌ Task {task_number} not found")

def main():
    if len(sys.argv) < 2:
        list_tasks()
        return
    
    command = sys.argv[1].lower()
    
    if command in ["list", "ls", "l"]:
        list_tasks()
    
    elif command in ["priority", "p", "pri"]:
        list_tasks(priority_only=True)
    
    elif command in ["add", "a"]:
        if len(sys.argv) < 3:
            print("❌ Usage: task.py add \"Task description\"")
            return
        task = " ".join(sys.argv[2:])
        add_task(task)
    
    elif command in ["done", "d", "complete", "c"]:
        if len(sys.argv) < 3:
            print("❌ Usage: task.py done <number>")
            return
        try:
            task_num = int(sys.argv[2])
            mark_done(task_num)
        except ValueError:
            print("❌ Invalid task number")
    
    else:
        print("❌ Unknown command. Usage:")
        print("  task.py list          # Show all tasks")
        print("  task.py priority      # High priority only")
        print("  task.py add \"Task\"    # Add new task")
        print("  task.py done N        # Complete task N")

if __name__ == "__main__":
    main()
