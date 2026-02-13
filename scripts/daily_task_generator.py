#!/usr/bin/env python3
"""
Daily Task Generator - Generates 4-5 tasks every morning based on GOALS.md
Inspired by AI automation video analysis
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
GOALS_FILE = WORKSPACE / "GOALS.md"
TASKS_FILE = WORKSPACE / "data" / "daily_tasks.json"
KANBAN_FILE = WORKSPACE / "data" / "kanban.json"

def load_goals():
    """Read GOALS.md"""
    if not GOALS_FILE.exists():
        return "No goals file found"
    with open(GOALS_FILE) as f:
        return f.read()

def load_recent_progress():
    """Check what was done recently"""
    memory_dir = WORKSPACE / "memory"
    recent_files = []
    
    # Get last 3 days of memory
    for i in range(3):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        log_file = memory_dir / f"{date}.md"
        if log_file.exists():
            with open(log_file) as f:
                recent_files.append(f"## {date}\n{f.read()[:1000]}")
    
    return "\n\n".join(recent_files)

def generate_tasks_with_ai(goals, recent_progress):
    """Use AI to generate 4-5 specific, actionable tasks"""
    from openai import OpenAI
    import sys
    sys.path.insert(0, str(WORKSPACE / "scripts"))
    from jarvis_helpers import smart_route, log_cost
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Use smart routing to pick best model
    model = smart_route("Generate 4-5 daily tasks based on goals and recent progress")
    
    prompt = f"""Based on these goals and recent progress, generate 4-5 specific, actionable tasks for today.

## Goals:
{goals}

## Recent Progress:
{recent_progress}

Requirements:
- Each task should take 30-120 minutes
- Tasks should move goals forward measurably
- Be specific (not "work on X", but "build Y feature for X")
- Mix of different goal areas
- Prioritize highest-impact items

Return ONLY valid JSON (no markdown, no explanation):
{{
  "tasks": [
    {{
      "title": "Task description",
      "goal": "Which goal this advances",
      "priority": "high/medium/low",
      "estimated_minutes": 60,
      "type": "code/research/content/admin"
    }}
  ]
}}"""

    response = client.chat.completions.create(
        model=model,  # Use routed model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    # Log cost for tracking
    log_cost(
        model=model,
        workflow="daily-task-generation",
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens
    )
    
    # Parse response
    text = response.choices[0].message.content.strip()
    if text.startswith('```'):
        lines = text.split('\n')
        text = '\n'.join([l for l in lines if not l.startswith('```')])
        text = text.strip()
        if text.startswith('json'):
            text = text[4:].strip()
    
    return json.loads(text)

def save_tasks(tasks_data):
    """Save generated tasks"""
    TASKS_FILE.parent.mkdir(exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Load existing tasks
    try:
        with open(TASKS_FILE) as f:
            all_tasks = json.load(f)
    except:
        all_tasks = {}
    
    # Add today's tasks
    all_tasks[today] = {
        'generated_at': datetime.now().isoformat(),
        'tasks': tasks_data['tasks']
    }
    
    with open(TASKS_FILE, 'w') as f:
        json.dump(all_tasks, f, indent=2)
    
    return today

def update_kanban(tasks_data, date):
    """Update Kanban board"""
    KANBAN_FILE.parent.mkdir(exist_ok=True)
    
    # Load existing kanban
    try:
        with open(KANBAN_FILE) as f:
            kanban = json.load(f)
    except:
        kanban = {
            'todo': [],
            'in_progress': [],
            'done': []
        }
    
    # Add today's tasks to TODO
    for task in tasks_data['tasks']:
        kanban['todo'].append({
            'id': f"{date}_{len(kanban['todo'])}",
            'date': date,
            'title': task['title'],
            'goal': task['goal'],
            'priority': task['priority'],
            'estimated_minutes': task['estimated_minutes'],
            'type': task['type'],
            'status': 'todo',
            'created_at': datetime.now().isoformat()
        })
    
    with open(KANBAN_FILE, 'w') as f:
        json.dump(kanban, f, indent=2)

def generate_dashboard():
    """Generate HTML dashboard"""
    dashboard_file = WORKSPACE / "dashboard" / "kanban.html"
    dashboard_file.parent.mkdir(exist_ok=True)
    
    # Load kanban data
    try:
        with open(KANBAN_FILE) as f:
            kanban = json.load(f)
    except:
        kanban = {'todo': [], 'in_progress': [], 'done': []}
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jarvis Mission Control</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0a0a0a;
            color: #fff;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        h1 {{
            font-size: 36px;
            background: linear-gradient(135deg, #00d4ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #888;
            font-size: 14px;
        }}
        .kanban {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        .column {{
            background: #1a1a1a;
            border-radius: 12px;
            padding: 20px;
        }}
        .column-header {{
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 2px solid #2a2a2a;
        }}
        .todo {{ border-top: 4px solid #00d4ff; }}
        .in-progress {{ border-top: 4px solid #ffa500; }}
        .done {{ border-top: 4px solid #00ff88; }}
        .task-card {{
            background: #0a0a0a;
            border: 1px solid #2a2a2a;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            cursor: move;
        }}
        .task-title {{
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .task-meta {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 8px;
        }}
        .tag {{
            font-size: 11px;
            padding: 4px 8px;
            border-radius: 4px;
            background: #2a2a2a;
        }}
        .priority-high {{ background: #ff4d4d; color: #fff; }}
        .priority-medium {{ background: #ffa500; color: #000; }}
        .priority-low {{ background: #00d4ff; color: #000; }}
        .task-goal {{
            font-size: 12px;
            color: #888;
            margin-top: 8px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            max-width: 1400px;
            margin: 0 auto 30px auto;
        }}
        .stat-card {{
            background: #1a1a1a;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: 700;
            color: #00ff88;
        }}
        .stat-label {{
            font-size: 12px;
            color: #888;
            margin-top: 4px;
        }}
        @media (max-width: 900px) {{
            .kanban {{ grid-template-columns: 1fr; }}
            .stats {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Jarvis Mission Control</h1>
        <div class="subtitle">AI-Generated Daily Tasks · Updated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{len(kanban['todo'])}</div>
            <div class="stat-label">To Do</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(kanban['in_progress'])}</div>
            <div class="stat-label">In Progress</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(kanban['done'])}</div>
            <div class="stat-label">Completed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{round(len(kanban['done']) / max(len(kanban['todo']) + len(kanban['in_progress']) + len(kanban['done']), 1) * 100)}%</div>
            <div class="stat-label">Progress</div>
        </div>
    </div>
    
    <div class="kanban">
        <div class="column todo">
            <div class="column-header">📋 To Do</div>
"""
    
    for task in kanban['todo']:
        html += f"""
            <div class="task-card">
                <div class="task-title">{task['title']}</div>
                <div class="task-meta">
                    <span class="tag priority-{task['priority']}">{task['priority'].upper()}</span>
                    <span class="tag">{task['type']}</span>
                    <span class="tag">{task['estimated_minutes']} min</span>
                </div>
                <div class="task-goal">🎯 {task['goal']}</div>
            </div>
"""
    
    html += """
        </div>
        <div class="column in-progress">
            <div class="column-header">⚡ In Progress</div>
"""
    
    for task in kanban['in_progress']:
        html += f"""
            <div class="task-card">
                <div class="task-title">{task['title']}</div>
                <div class="task-meta">
                    <span class="tag priority-{task['priority']}">{task['priority'].upper()}</span>
                    <span class="tag">{task['type']}</span>
                    <span class="tag">{task['estimated_minutes']} min</span>
                </div>
                <div class="task-goal">🎯 {task['goal']}</div>
            </div>
"""
    
    html += """
        </div>
        <div class="column done">
            <div class="column-header">✅ Done</div>
"""
    
    for task in kanban['done']:
        html += f"""
            <div class="task-card">
                <div class="task-title">{task['title']}</div>
                <div class="task-meta">
                    <span class="tag priority-{task['priority']}">{task['priority'].upper()}</span>
                    <span class="tag">{task['type']}</span>
                </div>
                <div class="task-goal">🎯 {task['goal']}</div>
            </div>
"""
    
    html += """
        </div>
    </div>
</body>
</html>
"""
    
    with open(dashboard_file, 'w') as f:
        f.write(html)
    
    return str(dashboard_file)

def main():
    print("🤖 Jarvis Daily Task Generator")
    print("=" * 50)
    
    # Load goals and context
    print("📖 Reading GOALS.md...")
    goals = load_goals()
    
    print("🔍 Checking recent progress...")
    recent_progress = load_recent_progress()
    
    # Generate tasks
    print("🧠 Generating today's tasks with AI...")
    tasks_data = generate_tasks_with_ai(goals, recent_progress)
    
    # Save tasks
    print(f"💾 Saving {len(tasks_data['tasks'])} tasks...")
    date = save_tasks(tasks_data)
    
    # Update Kanban
    print("📊 Updating Kanban board...")
    update_kanban(tasks_data, date)
    
    # Generate dashboard
    print("🎨 Generating dashboard...")
    dashboard_path = generate_dashboard()
    
    print("\n✅ Tasks generated successfully!")
    print(f"\n📋 Today's Tasks ({date}):")
    for i, task in enumerate(tasks_data['tasks'], 1):
        print(f"\n{i}. {task['title']}")
        print(f"   Goal: {task['goal']}")
        print(f"   Priority: {task['priority']} | Time: {task['estimated_minutes']} min | Type: {task['type']}")
    
    print(f"\n🌐 Dashboard: file://{dashboard_path}")
    print(f"📂 Tasks file: {TASKS_FILE}")
    print(f"📂 Kanban file: {KANBAN_FILE}")

if __name__ == '__main__':
    main()
