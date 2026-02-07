#!/usr/bin/env python3
"""
Weekly Progress Report Generator
Runs every Sunday at 6pm - summarizes the week's progress
"""

import json
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def load_fitness_data():
    """Load fitness tracker data"""
    data_path = Path("/Users/clawdbot/clawd/fitness-tracker/fitness_data.json")
    if data_path.exists():
        with open(data_path, 'r') as f:
            return json.load(f)
    return None

def load_memory_files():
    """Load this week's memory files"""
    memory_dir = Path("/Users/clawdbot/clawd/memory")
    today = datetime.now()
    week_files = []
    
    for i in range(7):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        file_path = memory_dir / f"{date_str}.md"
        
        if file_path.exists():
            with open(file_path, 'r') as f:
                week_files.append({
                    'date': date_str,
                    'content': f.read()
                })
    
    return week_files

def analyze_week():
    """Analyze this week's data and generate report"""
    
    fitness_data = load_fitness_data()
    memory_files = load_memory_files()
    
    # Calculate fitness stats
    one_week_ago = datetime.now() - timedelta(days=7)
    week_timestamp = one_week_ago.timestamp()
    
    report = {
        'week_ending': datetime.now().strftime("%Y-%m-%d"),
        'fitness': {},
        'builds': [],
        'goals': {},
        'insights': []
    }
    
    if fitness_data:
        # Workouts this week
        week_workouts = [w for w in fitness_data.get('workouts', []) 
                         if w['timestamp'] > week_timestamp]
        report['fitness']['workouts'] = len(week_workouts)
        
        # Weight change
        weight_logs = fitness_data.get('weight_logs', [])
        week_weights = [w for w in weight_logs if w['timestamp'] > week_timestamp]
        if week_weights:
            week_start = week_weights[0]['weight']
            week_end = week_weights[-1]['weight']
            report['fitness']['weight_change'] = round(week_end - week_start, 1)
        
        # Nutrition tracking
        food_logs = fitness_data.get('food_logs', [])
        week_food = [f for f in food_logs if f['timestamp'] > week_timestamp]
        report['fitness']['days_tracked'] = len(set(f['date'] for f in week_food))
        
        # Average macros
        if week_food:
            avg_cals = sum(f.get('calories', 0) for f in week_food) / len(week_food)
            avg_protein = sum(f.get('protein', 0) for f in week_food) / len(week_food)
            report['fitness']['avg_daily_calories'] = round(avg_cals)
            report['fitness']['avg_daily_protein'] = round(avg_protein)
    
    # Extract builds from memory
    for memory in memory_files:
        content = memory['content'].lower()
        if 'completed' in content or 'built' in content or 'shipped' in content:
            # This is a simplified extraction - could be more sophisticated
            report['builds'].append({
                'date': memory['date'],
                'note': 'See detailed logs'
            })
    
    return report

def get_swot_analysis():
    """Get Jarvis SWOT analysis"""
    try:
        result = subprocess.run(
            ['python3', '/Users/clawdbot/clawd/scripts/jarvis_swot.py', 'json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"Error getting SWOT: {e}")
    return None

def format_report_html(report):
    """Format report as mobile-friendly HTML"""
    
    fitness = report['fitness']
    swot = get_swot_analysis()
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Progress - {report['week_ending']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            padding: 16px;
            line-height: 1.6;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 32px;
            border-radius: 16px;
            margin-bottom: 24px;
            text-align: center;
        }}
        .header h1 {{ font-size: 28px; color: white; margin-bottom: 8px; }}
        .header .week {{ font-size: 14px; opacity: 0.9; }}
        .section {{
            background: #1a1a1a;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }}
        .section h2 {{
            font-size: 20px;
            color: #667eea;
            margin-bottom: 16px;
        }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }}
        .stat {{
            background: #2a2a2a;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat .value {{
            font-size: 32px;
            font-weight: bold;
            color: #4ade80;
            margin-bottom: 4px;
        }}
        .stat .label {{
            font-size: 12px;
            color: #888;
            text-transform: uppercase;
        }}
        .insight {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
        }}
        .swot-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }}
        .swot-box {{
            background: #2a2a2a;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid;
        }}
        .swot-box.strengths {{ border-color: #4ade80; }}
        .swot-box.weaknesses {{ border-color: #f59e0b; }}
        .swot-box.opportunities {{ border-color: #3b82f6; }}
        .swot-box.threats {{ border-color: #ef4444; }}
        .swot-box h3 {{
            font-size: 16px;
            margin-bottom: 12px;
            color: #e0e0e0;
        }}
        .swot-box ul {{
            list-style: none;
            padding: 0;
        }}
        .swot-box li {{
            padding: 6px 0;
            font-size: 14px;
            color: #a3a3a3;
        }}
        .swot-box li::before {{
            content: '• ';
            color: inherit;
        }}
        .actions {{
            background: #2a2a2a;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
            border-left: 4px solid #667eea;
        }}
        .actions h3 {{
            font-size: 16px;
            margin-bottom: 12px;
            color: #667eea;
        }}
        .actions ol {{
            padding-left: 20px;
            color: #a3a3a3;
        }}
        .actions li {{
            padding: 4px 0;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Weekly Progress Report</h1>
            <div class="week">Week ending {report['week_ending']}</div>
        </div>
        
        <div class="section">
            <h2>💪 Fitness</h2>
            <div class="stat-grid">
                <div class="stat">
                    <div class="value">{fitness.get('workouts', 0)}</div>
                    <div class="label">Workouts</div>
                </div>
                <div class="stat">
                    <div class="value">{fitness.get('days_tracked', 0)}</div>
                    <div class="label">Days Tracked</div>
                </div>
                <div class="stat">
                    <div class="value">{fitness.get('weight_change', 'N/A')}</div>
                    <div class="label">Weight Change (lbs)</div>
                </div>
                <div class="stat">
                    <div class="value">{fitness.get('avg_daily_protein', 0)}g</div>
                    <div class="label">Avg Protein</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🛠️ Builds Completed</h2>
            <p>This week: {len(report['builds'])} major projects shipped</p>
        </div>
        
        <div class="insight">
            <strong>💡 Insight</strong><br>
            Consistent tracking builds momentum. Keep logging daily.
        </div>"""
    
    # Add SWOT analysis if available
    if swot:
        html += f"""
        <div class="section">
            <h2>🤖 Jarvis SWOT Analysis</h2>
            
            <div class="swot-grid">
                <div class="swot-box strengths">
                    <h3>💪 Strengths</h3>
                    <ul>
                        {''.join(f'<li>{s}</li>' for s in swot['strengths'])}
                    </ul>
                </div>
                
                <div class="swot-box weaknesses">
                    <h3>⚠️ Weaknesses</h3>
                    <ul>
                        {''.join(f'<li>{w}</li>' for w in swot['weaknesses'])}
                    </ul>
                </div>
                
                <div class="swot-box opportunities">
                    <h3>🚀 Opportunities</h3>
                    <ul>
                        {''.join(f'<li>{o}</li>' for o in swot['opportunities'][:5])}
                    </ul>
                </div>
                
                <div class="swot-box threats">
                    <h3>🛡️ Threats</h3>
                    <ul>
                        {''.join(f'<li>{t}</li>' for t in swot['threats'][:4])}
                    </ul>
                </div>
            </div>
            
            <div class="actions">
                <h3>📊 Recommended Actions This Week:</h3>
                <ol>
                    <li>Prioritize semantic memory implementation</li>
                    <li>Increase proactive check-ins (if underutilized)</li>
                    <li>Gather more feedback on suggestions</li>
                    <li>Log daily memories consistently</li>
                    <li>Build next priority tool from opportunities list</li>
                </ol>
            </div>
        </div>"""
    
    html += """
    </div>
</body>
</html>"""
    
    return html

def format_report_text(report):
    """Format report as plain text for Telegram"""
    
    fitness = report['fitness']
    swot = get_swot_analysis()
    
    text = f"""📊 **Weekly Progress Report**
Week ending {report['week_ending']}

💪 **Fitness:**
• {fitness.get('workouts', 0)} workouts completed
• {fitness.get('days_tracked', 0)} days of nutrition tracked
• Weight change: {fitness.get('weight_change', 'N/A')} lbs
• Avg protein: {fitness.get('avg_daily_protein', 0)}g/day

🛠️ **Builds:**
{len(report['builds'])} major projects shipped this week

💡 **Insight:**
Consistent tracking builds momentum. Keep logging daily.
"""
    
    # Add SWOT analysis
    if swot:
        text += f"""
🤖 **Jarvis SWOT Analysis:**

💪 **Strengths:**
{chr(10).join(f"• {s}" for s in swot['strengths'][:3])}

⚠️ **Weaknesses:**
{chr(10).join(f"• {w}" for w in swot['weaknesses'][:3])}

🚀 **Top Opportunities:**
{chr(10).join(f"• {o}" for o in swot['opportunities'][:3])}

📊 **This Week's Focus:**
• {swot['opportunities'][0] if swot['opportunities'] else 'Continue building momentum'}
"""
    
    return text

def main():
    report = analyze_week()
    
    # Generate HTML
    html = format_report_html(report)
    html_path = "/Users/clawdbot/clawd/reports/weekly_progress.html"
    with open(html_path, 'w') as f:
        f.write(html)
    
    # Generate text
    text = format_report_text(report)
    
    print(text)
    print(f"\nHTML report: {html_path}")

if __name__ == '__main__':
    main()
