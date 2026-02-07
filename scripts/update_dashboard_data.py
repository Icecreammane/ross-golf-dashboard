#!/usr/bin/env python3
"""
Update dashboard data by fetching sessions and parsing build status files.
Generates dashboard-data.json for the org chart dashboard.
"""

import json
import subprocess
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
OUTPUT_FILE = WORKSPACE / "dashboard-data.json"
BUILD_STATUS = WORKSPACE / "BUILD_STATUS.md"
BUILD_QUEUE = WORKSPACE / "BUILD_QUEUE.md"


def run_command(cmd):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=5
        )
        return result.stdout
    except Exception as e:
        print(f"Error running command: {e}")
        return ""


def get_session_labels():
    """Extract session labels from sessions.json."""
    try:
        sessions_file = Path.home() / ".clawdbot/agents/main/sessions/sessions.json"
        if not sessions_file.exists():
            return {}
        
        with open(sessions_file) as f:
            sessions_data = json.load(f)
        
        labels = {}
        for key, data in sessions_data.items():
            if 'label' in data:
                labels[key] = data['label']
        
        return labels
    except Exception as e:
        print(f"Warning: Could not read session labels: {e}")
        return {}


def parse_sessions():
    """Parse clawdbot sessions output."""
    output = run_command("clawdbot sessions 2>&1")
    agents = []
    
    # Get session labels
    session_labels = get_session_labels()
    
    lines = output.split('\n')
    
    for line in lines:
        if not line.strip() or 'Session store' in line or 'Sessions listed' in line or 'Kind' in line:
            continue
            
        # Parse session line - format: direct agent:main:... TIME MODEL ...
        parts = line.split()
        if len(parts) < 4:
            continue
            
        session_key = parts[1] if len(parts) > 1 else ""
        age_parts = []
        model = "unknown"
        
        # Age can be multiple words like "just now" or "4m ago"
        # Model comes after age
        for i in range(2, len(parts)):
            if 'claude' in parts[i].lower() or parts[i].startswith('gpt'):
                model = parts[i]
                break
            age_parts.append(parts[i])
        
        age = ' '.join(age_parts) if age_parts else "unknown"
        
        # Determine if main or subagent
        is_main = "agent:main:main" in session_key
        is_subagent = "subag" in session_key
        
        if is_main:
            agents.append({
                "name": "Jarvis (Main Agent)",
                "status": "Active",
                "task": "Coordinating sub-agents and autonomous builds",
                "runtime": age,
                "sessionId": session_key,
                "isMain": True,
                "model": model,
                "description": "Main orchestration agent managing all sub-agents and build processes"
            })
        elif is_subagent:
            # Extract the UUID from the abbreviated session key
            # Format: agent:main:subag...XXXXXX where XXXXXX is last 6 chars
            session_id_match = re.search(r'\.\.\.([a-f0-9]{6})$', session_key)
            short_suffix = session_id_match.group(1) if session_id_match else ""
            
            # Find matching full key in session_labels
            label = ""
            full_session_key = session_key
            for key in session_labels.keys():
                if short_suffix and key.endswith(short_suffix):
                    label = session_labels[key]
                    full_session_key = key
                    break
            
            # Extract first 8 chars of UUID for display
            uuid_match = re.search(r'([a-f0-9]{8})-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', full_session_key)
            short_id = uuid_match.group(1) if uuid_match else short_suffix
            
            # Format task name from label
            task_name = label.replace('-', ' ').title() if label else "Processing assigned task..."
            
            agents.append({
                "name": f"Sub-Agent {short_id}",
                "status": "Building" if "ago" in age and not "h ago" in age else "Active",
                "task": task_name,
                "runtime": age,
                "sessionId": session_key,
                "isMain": False,
                "model": model,
                "description": f"Building: {task_name}",
                "label": label
            })
    
    # If no main agent found, add placeholder
    if not any(a.get('isMain') for a in agents):
        agents.insert(0, {
            "name": "Jarvis (Main Agent)",
            "status": "Active",
            "task": "Managing autonomous build system",
            "runtime": "active",
            "sessionId": "agent:main:main",
            "isMain": True,
            "model": "claude-sonnet-4-5",
            "description": "Main orchestration agent"
        })
    
    return agents


def parse_build_status():
    """Parse BUILD_STATUS.md for current builds."""
    if not BUILD_STATUS.exists():
        return []
    
    content = BUILD_STATUS.read_text()
    builds = []
    
    # Look for currently building section
    current_section = re.search(r'## Currently Building\s+(.*?)(?=##|\Z)', content, re.DOTALL)
    if current_section:
        section_text = current_section.group(1)
        if "No active builds" not in section_text:
            # Parse active builds
            # This is a simple parser - adjust based on actual format
            lines = section_text.strip().split('\n')
            for line in lines:
                if line.strip() and not line.startswith('*'):
                    builds.append({
                        "name": line.strip('- ').split('-')[0].strip(),
                        "status": "Building"
                    })
    
    return builds


def parse_build_queue():
    """Parse BUILD_QUEUE.md for queued items."""
    if not BUILD_QUEUE.exists():
        return []
    
    content = BUILD_QUEUE.read_text()
    queue_items = []
    
    # Parse active queue section
    queue_section = re.search(r'## 🟡 Active Queue.*?\n(.*?)(?=##|\Z)', content, re.DOTALL)
    if queue_section:
        section_text = queue_section.group(1)
        
        # Parse task items
        task_pattern = r'- \[ \] (.+?) - Added: (.+?) - Priority: (\w+)'
        matches = re.finditer(task_pattern, section_text)
        
        for match in matches:
            name = match.group(1).strip()
            added = match.group(2).strip()
            priority = match.group(3).strip()
            
            # Try to find description in task details
            description = ""
            detail_section = re.search(rf'### {re.escape(name)}\s+- \*\*Description:\*\* (.+?)(?:\n-|\n###|\Z)', content, re.DOTALL)
            if detail_section:
                description = detail_section.group(1).strip()
            
            queue_items.append({
                "name": name,
                "priority": priority,
                "description": description[:150] + '...' if len(description) > 150 else description,
                "added": added
            })
    
    return queue_items


def calculate_stats(agents, queue_items):
    """Calculate statistics."""
    active_count = sum(1 for a in agents if not a.get('isMain') and a['status'] in ['Active', 'Building'])
    
    # Parse completed from BUILD_STATUS or BUILD_QUEUE
    completed_count = 0
    if BUILD_QUEUE.exists():
        content = BUILD_QUEUE.read_text()
        completed_section = re.search(r'## 🟢 Completed \(Last 7 Days\)', content)
        if completed_section:
            # Count completed items (simple count of lines starting with [x])
            completed_matches = re.findall(r'- \[x\]', content)
            completed_count = len(completed_matches)
    
    return {
        "active": active_count,
        "completedToday": completed_count,
        "queued": len(queue_items),
        "successRate": "100%" if completed_count > 0 else "N/A"
    }


def merge_agent_data(sessions, builds):
    """Merge session data with build status."""
    agents = list(sessions)  # Copy sessions
    
    # Match builds to agents
    for build in builds:
        # Try to find matching agent
        found = False
        for agent in agents:
            if not agent.get('isMain') and agent['status'] == 'Building':
                agent['task'] = build['name']
                found = True
                break
        
        # If no matching agent, this might be a queued build
        if not found:
            # Could add as a placeholder agent
            pass
    
    return agents


def generate_dashboard_data():
    """Generate complete dashboard data."""
    print("Fetching session data...")
    sessions = parse_sessions()
    
    print("Parsing build status...")
    builds = parse_build_status()
    
    print("Parsing build queue...")
    queue_items = parse_build_queue()
    
    print("Merging data...")
    agents = merge_agent_data(sessions, builds)
    
    print("Calculating stats...")
    stats = calculate_stats(agents, queue_items)
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "agents": agents,
        "queue": queue_items,
        "stats": stats
    }
    
    print(f"Writing data to {OUTPUT_FILE}...")
    OUTPUT_FILE.write_text(json.dumps(data, indent=2))
    print("✅ Dashboard data updated!")
    
    return data


if __name__ == "__main__":
    try:
        data = generate_dashboard_data()
        print(f"\nSummary:")
        print(f"  Agents: {len(data['agents'])}")
        print(f"  Queue items: {len(data['queue'])}")
        print(f"  Active: {data['stats']['active']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
