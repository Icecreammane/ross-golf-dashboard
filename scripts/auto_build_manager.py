#!/usr/bin/env python3
"""
Auto Build Manager - The Autonomous Build Orchestrator

This script is called during heartbeats to:
1. Monitor BUILD_QUEUE.md for pending tasks
2. Auto-spawn sub-agents when nothing is building
3. Track build progress and update status files
4. Handle completions and failures
5. Notify Ross of important events

Usage:
    python3 auto_build_manager.py [--check|--monitor|--complete LABEL|--fail LABEL]
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
BUILD_QUEUE = WORKSPACE / "BUILD_QUEUE.md"
BUILD_STATUS = WORKSPACE / "BUILD_STATUS.md"
ACTIVE_BUILDS = WORKSPACE / "subagents" / "active.json"
SPAWN_SCRIPT = WORKSPACE / "scripts" / "spawn_agent.py"


def load_active_builds():
    """Load active builds from JSON"""
    if not ACTIVE_BUILDS.exists():
        return {"active": [], "completed": []}
    
    try:
        with open(ACTIVE_BUILDS, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"active": [], "completed": []}


def save_active_builds(data):
    """Save active builds to JSON"""
    ACTIVE_BUILDS.parent.mkdir(exist_ok=True)
    with open(ACTIVE_BUILDS, 'w') as f:
        json.dump(data, f, indent=2)


def parse_build_queue():
    """
    Parse BUILD_QUEUE.md and extract tasks.
    Returns dict with 'building', 'queue', and 'completed' lists.
    """
    if not BUILD_QUEUE.exists():
        return {"building": [], "queue": [], "completed": []}
    
    content = BUILD_QUEUE.read_text()
    
    # Parse sections
    building = []
    queue = []
    completed = []
    
    current_section = None
    current_task = None
    
    for line in content.split('\n'):
        # Detect sections
        if '## 🔴 Priority (Building Now)' in line:
            current_section = 'building'
        elif '## 🟡 Active Queue (Next Up)' in line:
            current_section = 'queue'
        elif '## 🟢 Completed (Last 7 Days)' in line:
            current_section = 'completed'
        elif '## 📋 Task Details' in line:
            current_section = 'details'
        
        # Parse task lines
        if current_section in ['building', 'queue', 'completed']:
            # Match task format: - [ ] Task name - ...
            match = re.match(r'^- \[([ x])\] (.+?)(?:\s*-\s*(.+))?$', line.strip())
            if match:
                checked = match.group(1) == 'x'
                task_name = match.group(2).strip()
                details = match.group(3).strip() if match.group(3) else ""
                
                task = {
                    "name": task_name,
                    "checked": checked,
                    "details": details,
                    "section": current_section
                }
                
                # Extract metadata from details
                if 'Priority:' in details:
                    priority_match = re.search(r'Priority:\s*(\w+)', details)
                    if priority_match:
                        task['priority'] = priority_match.group(1)
                
                if 'Added:' in details:
                    time_match = re.search(r'Added:\s*([^\-]+)', details)
                    if time_match:
                        task['added'] = time_match.group(1).strip()
                
                if 'Sub-agent:' in details:
                    agent_match = re.search(r'Sub-agent:\s*([^\)]+)', details)
                    if agent_match:
                        task['agent'] = agent_match.group(1).strip()
                
                if current_section == 'building':
                    building.append(task)
                elif current_section == 'queue':
                    queue.append(task)
                elif current_section == 'completed':
                    completed.append(task)
    
    return {
        "building": building,
        "queue": queue,
        "completed": completed
    }


def check_queue():
    """Check queue and return next task to build (if any)"""
    queue_data = parse_build_queue()
    active_builds = load_active_builds()
    
    # Check if anything is currently building
    if queue_data['building'] or active_builds['active']:
        return None  # Already building something
    
    # Get next high-priority task from queue
    for task in queue_data['queue']:
        if task.get('priority') == 'High':
            return task
    
    # No high priority? Check for medium during off-hours (10pm-6am)
    now = datetime.now()
    if now.hour >= 22 or now.hour < 6:
        for task in queue_data['queue']:
            if task.get('priority') == 'Medium':
                return task
    
    return None


def spawn_builder(task):
    """Spawn sub-agent for task"""
    task_name = task['name']
    
    # Generate agent label from task name
    label = re.sub(r'[^a-z0-9]+', '-', task_name.lower()).strip('-')
    
    # Read task details from BUILD_QUEUE.md Task Details section
    task_spec = extract_task_spec(task_name)
    
    print(f"🚀 Spawning builder: {label}")
    print(f"   Task: {task_name}")
    print(f"   Priority: {task.get('priority', 'Unknown')}")
    
    # Use spawn_agent.py to create sub-agent
    spawn_cmd = f"python3 {SPAWN_SCRIPT} --label {label} --task '{task_spec}'"
    
    # Execute spawn (this will create the sub-agent)
    result = os.system(spawn_cmd)
    
    if result == 0:
        # Update BUILD_QUEUE.md - move task to building
        move_task_to_building(task_name, label)
        
        # Update BUILD_STATUS.md
        update_build_status()
        
        print(f"✅ Builder spawned successfully: {label}")
        return True
    else:
        print(f"❌ Failed to spawn builder for: {task_name}")
        return False


def extract_task_spec(task_name):
    """Extract full task specification from BUILD_QUEUE.md Task Details section"""
    if not BUILD_QUEUE.exists():
        return f"Build: {task_name}"
    
    content = BUILD_QUEUE.read_text()
    
    # Find task details section
    details_match = re.search(
        rf'### {re.escape(task_name)}\n(.*?)(?=\n###|\n##|$)',
        content,
        re.DOTALL
    )
    
    if details_match:
        return details_match.group(1).strip()
    else:
        return f"Build: {task_name}\n\nNo detailed specification found. Use best judgment."


def move_task_to_building(task_name, agent_label):
    """Move task from queue to building section in BUILD_QUEUE.md"""
    if not BUILD_QUEUE.exists():
        return
    
    content = BUILD_QUEUE.read_text()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Find and remove task from queue section
    task_pattern = rf'- \[ \] {re.escape(task_name)}.*?\n'
    content = re.sub(task_pattern, '', content)
    
    # Add to building section
    building_section = '## 🔴 Priority (Building Now)'
    building_entry = f"- [ ] {task_name} - Status: Building (Sub-agent: {agent_label}) - Started: {now}\n"
    
    content = content.replace(
        building_section,
        f"{building_section}\n{building_entry}"
    )
    
    # Update timestamp
    content = re.sub(
        r'\*Last updated:.*?\*',
        f'*Last updated: {now}*',
        content
    )
    
    BUILD_QUEUE.write_text(content)


def update_build_status():
    """Update BUILD_STATUS.md with current state"""
    queue_data = parse_build_queue()
    active_builds = load_active_builds()
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    status_content = f"""# Build Status - Live

*Updated: {now}*

"""
    
    # Currently Building section
    if queue_data['building'] or active_builds['active']:
        status_content += "## Currently Building\n\n"
        
        for task in queue_data['building']:
            status_content += f"**{task['name']}**\n"
            if 'agent' in task:
                status_content += f"- Sub-agent: {task['agent']}\n"
            if 'added' in task:
                status_content += f"- Started: {task['added']}\n"
            status_content += "\n"
        
        for build in active_builds['active']:
            status_content += f"**{build.get('label', 'Unknown')}**\n"
            status_content += f"- Session: {build.get('sessionKey', 'N/A')}\n"
            status_content += f"- Started: {build.get('started', 'N/A')}\n"
            
            # Calculate progress
            if 'tasks' in build:
                total = len(build['tasks'])
                done = sum(1 for t in build['tasks'] if t.get('status') == 'done')
                progress = int((done / total) * 100) if total > 0 else 0
                status_content += f"- Progress: {progress}% ({done}/{total} tasks)\n"
            
            status_content += "\n"
    else:
        status_content += "## Currently Building\n\n*No active builds*\n\n"
    
    # Queue section
    if queue_data['queue']:
        status_content += "## Queue Position\n\n"
        for i, task in enumerate(queue_data['queue'][:5], 1):
            priority = task.get('priority', 'Unknown')
            status_content += f"{i}. {task['name']} - Priority: {priority}\n"
        status_content += "\n"
    
    # Recent completions
    if queue_data['completed']:
        status_content += "## Recent Completions\n\n"
        for task in queue_data['completed'][:5]:
            status_content += f"- {task['name']}\n"
        status_content += "\n"
    
    BUILD_STATUS.write_text(status_content)


def monitor_builds():
    """Monitor active builds and update status"""
    active_builds = load_active_builds()
    now = datetime.now()
    
    for build in active_builds['active']:
        last_update = datetime.fromisoformat(build.get('lastUpdate', build['started']))
        hours_since_update = (now - last_update).total_seconds() / 3600
        
        # Alert if no update in 4+ hours
        if hours_since_update > 4:
            print(f"⚠️  Build '{build['label']}' has been silent for {hours_since_update:.1f} hours")
            print(f"   Consider checking progress or terminating.")
    
    update_build_status()


def handle_completion(label):
    """Handle build completion"""
    active_builds = load_active_builds()
    
    # Find completed build
    completed_build = None
    for i, build in enumerate(active_builds['active']):
        if build['label'] == label:
            completed_build = active_builds['active'].pop(i)
            break
    
    if not completed_build:
        print(f"⚠️  Build '{label}' not found in active builds")
        return
    
    # Move to completed
    completed_build['completed'] = datetime.now().isoformat()
    active_builds['completed'].append(completed_build)
    
    # Keep only last 20 completed builds
    active_builds['completed'] = active_builds['completed'][-20:]
    
    save_active_builds(active_builds)
    
    # Update BUILD_QUEUE.md - mark as completed
    mark_task_completed(completed_build.get('name', label))
    
    # Update status
    update_build_status()
    
    print(f"✅ Build completed: {label}")
    
    # Check if more tasks in queue
    next_task = check_queue()
    if next_task:
        print(f"🔄 Next task ready: {next_task['name']}")
        print(f"   Starting automatically...")
        spawn_builder(next_task)


def mark_task_completed(task_name):
    """Mark task as completed in BUILD_QUEUE.md"""
    if not BUILD_QUEUE.exists():
        return
    
    content = BUILD_QUEUE.read_text()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Find task in building section
    task_pattern = rf'- \[ \] {re.escape(task_name)}.*?\n'
    
    # Remove from building
    content = re.sub(task_pattern, '', content)
    
    # Add to completed
    completed_section = '## 🟢 Completed (Last 7 Days)'
    completed_entry = f"- [x] {task_name} - Completed: {now}\n"
    
    content = content.replace(
        completed_section,
        f"{completed_section}\n{completed_entry}"
    )
    
    BUILD_QUEUE.write_text(content)


def handle_failure(label, retry_count=0):
    """Handle build failure with retry logic"""
    MAX_RETRIES = 3
    
    print(f"❌ Build failed: {label} (Attempt {retry_count + 1}/{MAX_RETRIES})")
    
    if retry_count < MAX_RETRIES:
        print(f"🔄 Retrying in 5 minutes...")
        # In real implementation, would schedule retry
        # For now, just log the failure
    else:
        print(f"🚨 Build failed after {MAX_RETRIES} attempts. Escalating to Ross.")
        # Mark as failed in queue
        # Notify Ross via Telegram (would need integration)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        # Default: check queue and spawn if needed
        print("🔍 Checking build queue...")
        next_task = check_queue()
        
        if next_task:
            print(f"📋 Found task: {next_task['name']}")
            spawn_builder(next_task)
        else:
            print("✅ No tasks ready to build")
            monitor_builds()
        
        return
    
    action = sys.argv[1]
    
    if action == '--check':
        next_task = check_queue()
        if next_task:
            print(f"Next task: {next_task['name']}")
        else:
            print("No tasks ready")
    
    elif action == '--monitor':
        monitor_builds()
    
    elif action == '--complete' and len(sys.argv) > 2:
        label = sys.argv[2]
        handle_completion(label)
    
    elif action == '--fail' and len(sys.argv) > 2:
        label = sys.argv[2]
        retry = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        handle_failure(label, retry)
    
    else:
        print("Usage: auto_build_manager.py [--check|--monitor|--complete LABEL|--fail LABEL]")
        sys.exit(1)


if __name__ == '__main__':
    main()
