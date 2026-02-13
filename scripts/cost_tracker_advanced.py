#!/usr/bin/env python3
"""
Advanced Cost Tracker - Per-workflow API cost analysis
Tracks every AI API call with detailed breakdowns
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path.home() / "clawd"
COST_LOG = WORKSPACE / "data" / "api_costs.json"
DASHBOARD_FILE = WORKSPACE / "dashboard" / "costs.html"

# Pricing per million tokens
MODEL_COSTS = {
    # Local (free)
    'local-fast': {'input': 0, 'output': 0},
    'local-brain': {'input': 0, 'output': 0},
    'local-smart': {'input': 0, 'output': 0},
    
    # Anthropic
    'claude-haiku-4-5': {'input': 0.25, 'output': 1.25},
    'claude-sonnet-4-5': {'input': 3.00, 'output': 15.00},
    'claude-opus-4-5': {'input': 15.00, 'output': 75.00},
    
    # OpenAI
    'gpt-4o': {'input': 2.50, 'output': 10.00},
    'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
    'gpt-5.2': {'input': 5.00, 'output': 20.00},
    
    # Google
    'gemini-3-flash-preview': {'input': 0.00, 'output': 0.00},  # Free tier
}

def log_api_call(model, workflow, input_tokens, output_tokens, metadata=None):
    """Log an API call with costs"""
    COST_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing log
    try:
        with open(COST_LOG) as f:
            log = json.load(f)
    except:
        log = {'calls': []}
    
    # Calculate cost
    if model in MODEL_COSTS:
        input_cost = (input_tokens / 1_000_000) * MODEL_COSTS[model]['input']
        output_cost = (output_tokens / 1_000_000) * MODEL_COSTS[model]['output']
        total_cost = input_cost + output_cost
    else:
        # Unknown model, estimate high
        total_cost = ((input_tokens + output_tokens) / 1_000_000) * 10.0
    
    # Add entry
    entry = {
        'timestamp': datetime.now().isoformat(),
        'model': model,
        'workflow': workflow,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'total_tokens': input_tokens + output_tokens,
        'cost': round(total_cost, 4),
        'metadata': metadata or {}
    }
    
    log['calls'].append(entry)
    
    # Keep last 10,000 calls
    if len(log['calls']) > 10000:
        log['calls'] = log['calls'][-10000:]
    
    with open(COST_LOG, 'w') as f:
        json.dump(log, f, indent=2)
    
    return total_cost

def get_costs_by_period(days=1):
    """Get costs for last N days"""
    try:
        with open(COST_LOG) as f:
            log = json.load(f)
    except:
        return {'total': 0, 'by_workflow': {}, 'by_model': {}, 'by_day': {}, 'call_count': 0}
    
    cutoff = datetime.now() - timedelta(days=days)
    
    total = 0
    by_workflow = defaultdict(float)
    by_model = defaultdict(float)
    by_day = defaultdict(float)
    
    for call in log['calls']:
        call_time = datetime.fromisoformat(call['timestamp'])
        if call_time < cutoff:
            continue
        
        cost = call['cost']
        total += cost
        by_workflow[call['workflow']] += cost
        by_model[call['model']] += cost
        
        day = call_time.strftime('%Y-%m-%d')
        by_day[day] += cost
    
    return {
        'total': round(total, 2),
        'by_workflow': dict(by_workflow),
        'by_model': dict(by_model),
        'by_day': dict(by_day),
        'call_count': len([c for c in log['calls'] if datetime.fromisoformat(c['timestamp']) >= cutoff])
    }

def generate_cost_dashboard():
    """Generate HTML cost dashboard"""
    DASHBOARD_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Get data
    today = get_costs_by_period(1)
    week = get_costs_by_period(7)
    month = get_costs_by_period(30)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Cost Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
            background: linear-gradient(135deg, #ff006e, #ffa500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #888;
            font-size: 14px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto 40px auto;
        }}
        .stat-card {{
            background: #1a1a1a;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: 700;
            color: #00ff88;
        }}
        .stat-label {{
            font-size: 12px;
            color: #888;
            margin-top: 8px;
            text-transform: uppercase;
        }}
        .alert {{
            background: #2a1a1a;
            border-left: 4px solid #ff4d4d;
            padding: 16px;
            margin-bottom: 30px;
            max-width: 1400px;
            margin-left: auto;
            margin-right: auto;
        }}
        .charts {{
            max-width: 1400px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}
        .chart-card {{
            background: #1a1a1a;
            border-radius: 12px;
            padding: 20px;
        }}
        .chart-title {{
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 20px;
        }}
        canvas {{
            max-height: 300px;
        }}
        @media (max-width: 900px) {{
            .charts {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>💰 API Cost Dashboard</h1>
        <div class="subtitle">Real-time cost tracking · Updated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">${today['total']}</div>
            <div class="stat-label">Today</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${week['total']}</div>
            <div class="stat-label">Last 7 Days</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${month['total']}</div>
            <div class="stat-label">Last 30 Days</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${round(month['total'] / 30, 2)}/day</div>
            <div class="stat-label">Daily Average</div>
        </div>
    </div>
"""
    
    # Alert if spending is high
    if week['total'] > 250:
        html += f"""
    <div class="alert">
        ⚠️ <strong>High spending alert:</strong> You've spent ${week['total']} in the last 7 days. 
        This projects to ${round(week['total'] * 4.3, 2)}/month. Consider routing more tasks to cheaper models.
    </div>
"""
    
    # Charts
    html += """
    <div class="charts">
        <div class="chart-card">
            <div class="chart-title">Cost by Workflow (Last 7 Days)</div>
            <canvas id="workflowChart"></canvas>
        </div>
        <div class="chart-card">
            <div class="chart-title">Cost by Model (Last 7 Days)</div>
            <canvas id="modelChart"></canvas>
        </div>
        <div class="chart-card">
            <div class="chart-title">Daily Spending Trend</div>
            <canvas id="trendChart"></canvas>
        </div>
    </div>
    
    <script>
"""
    
    # Workflow chart data
    workflow_labels = list(week['by_workflow'].keys())[:10]
    workflow_values = [week['by_workflow'][w] for w in workflow_labels]
    
    html += f"""
        // Workflow chart
        new Chart(document.getElementById('workflowChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(workflow_labels)},
                datasets: [{{
                    label: 'Cost ($)',
                    data: {json.dumps(workflow_values)},
                    backgroundColor: 'rgba(0, 255, 136, 0.8)'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ ticks: {{ color: '#888' }}, grid: {{ color: '#2a2a2a' }} }},
                    x: {{ ticks: {{ color: '#888' }}, grid: {{ display: false }} }}
                }}
            }}
        }});
"""
    
    # Model chart data
    model_labels = list(week['by_model'].keys())
    model_values = [week['by_model'][m] for m in model_labels]
    
    html += f"""
        // Model chart
        new Chart(document.getElementById('modelChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(model_labels)},
                datasets: [{{
                    data: {json.dumps(model_values)},
                    backgroundColor: ['#ff006e', '#ffa500', '#00d4ff', '#00ff88', '#8338ec']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ color: '#888' }} }}
                }}
            }}
        }});
"""
    
    # Trend chart
    days = sorted(month['by_day'].keys())[-14:]  # Last 14 days
    day_values = [month['by_day'].get(d, 0) for d in days]
    
    html += f"""
        // Trend chart
        new Chart(document.getElementById('trendChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(days)},
                datasets: [{{
                    label: 'Daily Cost ($)',
                    data: {json.dumps(day_values)},
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ ticks: {{ color: '#888' }}, grid: {{ color: '#2a2a2a' }} }},
                    x: {{ ticks: {{ color: '#888' }}, grid: {{ display: false }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    with open(DASHBOARD_FILE, 'w') as f:
        f.write(html)
    
    return str(DASHBOARD_FILE)

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  cost_tracker_advanced.py log <model> <workflow> <input_tokens> <output_tokens>")
        print("  cost_tracker_advanced.py report [days]")
        print("  cost_tracker_advanced.py dashboard")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'log' and len(sys.argv) >= 6:
        model = sys.argv[2]
        workflow = sys.argv[3]
        input_tokens = int(sys.argv[4])
        output_tokens = int(sys.argv[5])
        cost = log_api_call(model, workflow, input_tokens, output_tokens)
        print(f"✅ Logged: ${cost:.4f} ({model} for {workflow})")
    
    elif command == 'report':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        data = get_costs_by_period(days)
        print(f"\n📊 Cost Report (Last {days} Days)")
        print(f"=" * 50)
        print(f"Total: ${data['total']}")
        print(f"\nBy Workflow:")
        for workflow, cost in sorted(data['by_workflow'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {workflow}: ${cost:.2f}")
        print(f"\nBy Model:")
        for model, cost in sorted(data['by_model'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {model}: ${cost:.2f}")
    
    elif command == 'dashboard':
        path = generate_cost_dashboard()
        print(f"✅ Dashboard generated: {path}")
        data = get_costs_by_period(7)
        print(f"\n📊 Last 7 Days: ${data['total']}")
    
    else:
        print("Unknown command")
        sys.exit(1)

if __name__ == '__main__':
    main()
