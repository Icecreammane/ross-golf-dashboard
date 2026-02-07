#!/usr/bin/env python3
"""
Generate mobile-optimized morning brief for Ross.
Run via heartbeat at 7:30am CST.
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
TEMPLATE_PATH = WORKSPACE / "templates" / "morning-brief.html"
OUTPUT_PATH = WORKSPACE / "morning-brief.html"
TASK_QUEUE = WORKSPACE / "TASK_QUEUE.md"
MEMORY_DIR = WORKSPACE / "memory"
STATE_FILE = WORKSPACE / "memory" / "heartbeat-state.json"


def load_state():
    """Load heartbeat state to track what's been reported."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"lastBriefDate": None, "reportedBuilds": []}


def save_state(state):
    """Save heartbeat state."""
    STATE_FILE.parent.mkdir(exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def get_overnight_work():
    """Extract overnight work from build logs."""
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = datetime.now().strftime("%Y-%m-%d")  # TODO: Calculate actual yesterday
    
    build_logs = []
    
    # Check for build logs from last night
    for log_file in MEMORY_DIR.glob("build-log-*.md"):
        if log_file.exists():
            with open(log_file) as f:
                content = f.read()
                if "COMPLETED" in content or "DELIVERED" in content:
                    build_logs.append(content)
    
    if not build_logs:
        return '<div class="empty-state">No overnight builds completed</div>'
    
    # Parse completed items
    items = []
    for log in build_logs:
        lines = log.split('\n')
        for line in lines:
            if '✅' in line or 'COMPLETED' in line:
                items.append(f"<li>{line.replace('✅', '').strip()}</li>")
    
    if items:
        return "<ul>" + "".join(items) + "</ul>"
    else:
        return '<div class="empty-state">Build in progress...</div>'


def get_priorities():
    """Extract today's priorities from TASK_QUEUE.md."""
    if not TASK_QUEUE.exists():
        return '<div class="empty-state">No task queue found</div>'
    
    with open(TASK_QUEUE) as f:
        content = f.read()
    
    # Extract high priority items
    priorities = []
    lines = content.split('\n')
    in_priority_section = False
    
    for line in lines:
        if '## Today' in line or '## High Priority' in line:
            in_priority_section = True
            continue
        if in_priority_section and line.startswith('##'):
            break
        if in_priority_section and line.strip().startswith('-'):
            item = line.strip().lstrip('- ').replace('[ ]', '').replace('[x]', '✓')
            if item:
                priorities.append(f"<li>{item}</li>")
    
    if priorities[:5]:  # Top 5 priorities
        return "<ul>" + "".join(priorities[:5]) + "</ul>"
    else:
        return '<div class="empty-state">No priorities set for today</div>'


def get_open_loops():
    """Find open loops needing attention."""
    loops = []
    
    # Check PROPOSALS.md for pending approvals
    proposals_path = WORKSPACE / "PROPOSALS.md"
    if proposals_path.exists():
        with open(proposals_path) as f:
            content = f.read()
            pending_count = content.count("PENDING_APPROVAL")
            if pending_count > 0:
                loops.append(f"<li>{pending_count} proposals awaiting approval</li>")
    
    # Check for unread emails (placeholder - needs Himalaya integration)
    # loops.append("<li>Check email for urgent messages</li>")
    
    if loops:
        return "<ul>" + "".join(loops) + "</ul>"
    else:
        return "<div class='empty-state'>No open loops - you're clear!</div>"


def get_stats():
    """Generate quick stats section."""
    stats_html = '''
    <div class="section">
        <h2>Quick Stats</h2>
        <div class="stats">
            <div class="stat-box">
                <div class="number">3</div>
                <div class="label">Proposals Pending</div>
            </div>
            <div class="stat-box">
                <div class="number">2</div>
                <div class="label">Builds Active</div>
            </div>
        </div>
    </div>
    '''
    return stats_html


def get_calendar_events():
    """Get today's calendar events from Apple Calendar."""
    try:
        result = subprocess.run(
            ['python3', str(WORKSPACE / 'calendar' / 'apple_calendar.py'), 'today'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        output = result.stdout.strip()
        
        if 'No events today' in output:
            return '<div class="empty-state">📅 No events scheduled - your day is clear!</div>'
        
        # Parse the output and format as HTML
        lines = output.split('\n')
        events = []
        for line in lines:
            if line.strip().startswith('•'):
                event = line.strip().lstrip('• ')
                events.append(f'<li>{event}</li>')
        
        if events:
            return '<ul class="calendar-events">' + ''.join(events) + '</ul>'
        else:
            return '<div class="empty-state">📅 No events scheduled</div>'
    
    except Exception as e:
        return f'<div class="empty-state">⚠️ Calendar error: {str(e)}</div>'


def get_insight():
    """Generate proactive insight for the day."""
    insights = [
        "Your golf club decision is still pending - want me to schedule a fitting at True Spec?",
        "Fantasy playoffs start soon - shall I build that DraftKings correlation analyzer?",
        "It's been 3 days since your last workout log - want a reminder system?",
    ]
    
    # Simple rotation - could be made smarter
    day_of_year = datetime.now().timetuple().tm_yday
    return insights[day_of_year % len(insights)]


def generate_brief():
    """Generate the morning brief HTML."""
    state = load_state()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Don't send duplicate briefs
    if state.get("lastBriefDate") == today:
        print(f"Brief already sent for {today}")
        return None
    
    # Load template
    with open(TEMPLATE_PATH) as f:
        template = f.read()
    
    # Generate content
    date_str = datetime.now().strftime("%A, %B %d, %Y")
    overnight_work = get_overnight_work()
    priorities = get_priorities()
    calendar_events = get_calendar_events()
    open_loops = get_open_loops()
    stats_section = get_stats()
    insight = get_insight()
    
    # Fill template
    html = template.replace("{{date}}", date_str)
    html = html.replace("{{overnight_work}}", overnight_work)
    html = html.replace("{{priorities}}", priorities)
    html = html.replace("{{calendar_events}}", calendar_events)
    html = html.replace("{{open_loops}}", open_loops)
    html = html.replace("{{stats_section}}", stats_section)
    html = html.replace("{{insight}}", insight)
    
    # Write output
    with open(OUTPUT_PATH, 'w') as f:
        f.write(html)
    
    # Update state
    state["lastBriefDate"] = today
    save_state(state)
    
    print(f"Morning brief generated: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    generate_brief()
