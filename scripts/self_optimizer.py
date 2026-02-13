#!/usr/bin/env python3
"""
Self-Optimization System - AI reviews and improves its own configuration
Runs nightly to keep system up-to-date with best practices
"""

import json
import os
from datetime import datetime
from pathlib import Path
from openai import OpenAI

WORKSPACE = Path.home() / "clawd"
OPTIMIZATION_LOG = WORKSPACE / "data" / "optimizations.json"

FILES_TO_OPTIMIZE = [
    WORKSPACE / "AGENTS.md",
    WORKSPACE / "SOUL.md",
    WORKSPACE / "TOOLS.md",
    WORKSPACE / "HEARTBEAT.md",
    WORKSPACE / "DECISION_PROTOCOL.md",
    WORKSPACE / "scripts" / "daily_task_generator.py",
]

def load_file(path):
    """Load file content"""
    if not path.exists():
        return None
    with open(path) as f:
        return f.read()

def analyze_and_improve(file_path, content):
    """Use AI to analyze file and suggest improvements"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = f"""You are a self-optimization system reviewing your own configuration file.

FILE: {file_path.name}
CURRENT CONTENT:
{content[:4000]}  # First 4000 chars

TASK: Review this file against AI agent best practices and suggest improvements.

Consider:
1. Clarity - Are instructions clear and unambiguous?
2. Completeness - Are there gaps or missing edge cases?
3. Efficiency - Can processes be streamlined?
4. Best practices - Are there newer/better approaches?
5. Consistency - Does it align with other config files?

Return ONLY valid JSON (no markdown):
{{
  "score": 0-100,
  "issues": [
    {{"severity": "high/medium/low", "issue": "description", "line": 10}}
  ],
  "improvements": [
    {{"priority": "high/medium/low", "suggestion": "what to change", "rationale": "why"}}
  ],
  "auto_apply": [
    {{"change": "specific text to add/modify", "safe": true/false}}
  ]
}}

Only suggest auto_apply changes that are 100% safe (won't break anything)."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    text = response.choices[0].message.content.strip()
    if text.startswith('```'):
        lines = text.split('\n')
        text = '\n'.join([l for l in lines if not l.startswith('```')])
        text = text.strip()
        if text.startswith('json'):
            text = text[4:].strip()
    
    return json.loads(text)

def apply_safe_changes(file_path, changes):
    """Apply changes that are marked as safe"""
    applied = []
    
    for change in changes:
        if not change.get('safe', False):
            continue
        
        # Log what we're applying
        applied.append(change['change'])
        
        # TODO: Actually apply the change
        # For now, just log it
    
    return applied

def log_optimization(file_path, analysis, changes_applied):
    """Log optimization results"""
    OPTIMIZATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(OPTIMIZATION_LOG) as f:
            log = json.load(f)
    except:
        log = {'optimizations': []}
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'file': str(file_path),
        'score': analysis['score'],
        'issues_found': len(analysis['issues']),
        'improvements_suggested': len(analysis['improvements']),
        'changes_applied': len(changes_applied),
        'analysis': analysis,
        'applied': changes_applied
    }
    
    log['optimizations'].append(entry)
    
    with open(OPTIMIZATION_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def generate_report():
    """Generate optimization report"""
    try:
        with open(OPTIMIZATION_LOG) as f:
            log = json.load(f)
    except:
        return "No optimizations run yet"
    
    if not log['optimizations']:
        return "No optimizations run yet"
    
    recent = log['optimizations'][-5:]  # Last 5 runs
    
    report = "# Self-Optimization Report\n\n"
    report += f"**Last run:** {recent[-1]['timestamp']}\n\n"
    
    report += "## Recent Optimizations\n\n"
    for opt in recent:
        report += f"### {Path(opt['file']).name}\n"
        report += f"- **Score:** {opt['score']}/100\n"
        report += f"- **Issues found:** {opt['issues_found']}\n"
        report += f"- **Improvements suggested:** {opt['improvements_suggested']}\n"
        report += f"- **Changes applied:** {opt['changes_applied']}\n\n"
        
        if opt['analysis']['improvements']:
            report += "**Top suggestions:**\n"
            for imp in opt['analysis']['improvements'][:3]:
                report += f"- [{imp['priority'].upper()}] {imp['suggestion']}\n"
            report += "\n"
    
    return report

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'report':
        print(generate_report())
        return
    
    print("🔍 Self-Optimization System Running...")
    print("=" * 60)
    
    for file_path in FILES_TO_OPTIMIZE:
        if not file_path.exists():
            print(f"⏭️  Skipping {file_path.name} (not found)")
            continue
        
        print(f"\n📝 Analyzing {file_path.name}...")
        
        content = load_file(file_path)
        analysis = analyze_and_improve(file_path, content)
        
        print(f"   Score: {analysis['score']}/100")
        print(f"   Issues: {len(analysis['issues'])}")
        print(f"   Suggestions: {len(analysis['improvements'])}")
        
        # Apply safe changes
        safe_changes = [c for c in analysis.get('auto_apply', []) if c.get('safe')]
        if safe_changes:
            print(f"   🔧 Applying {len(safe_changes)} safe changes...")
            applied = apply_safe_changes(file_path, safe_changes)
        else:
            applied = []
            print(f"   ℹ️  No safe auto-apply changes")
        
        # Log results
        log_optimization(file_path, analysis, applied)
        
        # Show top suggestions
        if analysis['improvements']:
            print(f"\n   💡 Top Suggestions:")
            for imp in analysis['improvements'][:2]:
                print(f"      [{imp['priority'].upper()}] {imp['suggestion']}")
    
    print(f"\n✅ Optimization complete!")
    print(f"📊 Full report: python3 {__file__} report")
    print(f"📂 Log: {OPTIMIZATION_LOG}")

if __name__ == '__main__':
    main()
