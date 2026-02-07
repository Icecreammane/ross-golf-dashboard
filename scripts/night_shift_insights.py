#!/usr/bin/env python3
"""
Night Shift: Personal Insights
Analyzes memory files, finds patterns, tracks goal progress
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
MEMORY_DIR = WORKSPACE / "memory"
OUTPUT_DIR = WORKSPACE / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def analyze_daily_logs():
    """Analyze recent daily memory logs"""
    if not MEMORY_DIR.exists():
        return "No memory directory found"
    
    daily_logs = sorted(MEMORY_DIR.glob("202*.md"), reverse=True)[:7]
    
    if not daily_logs:
        return "No daily logs found"
    
    summary = f"**Recent Activity:** {len(daily_logs)} daily logs found\n"
    for log in daily_logs[:3]:
        date = log.stem
        size = log.stat().st_size
        summary += f"- {date}: {size} bytes\n"
    
    return summary

def check_wins():
    """Check daily wins tracking"""
    wins_file = MEMORY_DIR / "daily-wins.json"
    
    if not wins_file.exists():
        return "No wins tracked yet"
    
    with open(wins_file) as f:
        wins = json.load(f)
    
    recent_wins = wins[-5:] if wins else []
    
    summary = f"**Total Wins Logged:** {len(wins)}\n\n"
    if recent_wins:
        summary += "**Recent Wins:**\n"
        for win in recent_wins:
            date = win.get('date', 'Unknown')
            text = win.get('win', 'No description')
            summary += f"- {date}: {text}\n"
    
    return summary

def analyze_goals_progress():
    """Analyze goal progress over time"""
    goals_file = WORKSPACE / "GOALS.md"
    
    if not goals_file.exists():
        return "No goals file"
    
    with open(goals_file) as f:
        goals = f.read()
    
    # Count checkboxes
    total_items = goals.count('[ ]') + goals.count('[x]')
    completed = goals.count('[x]')
    
    if total_items > 0:
        progress = (completed / total_items) * 100
        return f"""**Goal Progress:**
- Total items: {total_items}
- Completed: {completed}
- Progress: {progress:.1f}%
"""
    
    return "No trackable goals found"

def find_patterns():
    """Find patterns in activity (placeholder for now)"""
    return """**Pattern Analysis:**
*Coming soon: ML-powered pattern detection*

**What we'll track:**
- Best productive hours
- Workout → energy correlation
- Win logging → momentum
- Calendar density → stress levels
- Sleep → next-day performance

**For now:**
- Manually review your daily logs
- Look for what precedes good days
- Note energy patterns
- Track decision quality by time of day
"""

def generate_insights():
    """Generate personal insights report"""
    
    report = f"""# Personal Insights - {datetime.now().strftime('%Y-%m-%d')}

Generated at: {datetime.now().strftime('%I:%M %p')}

## Summary

Your weekly patterns, progress, and performance insights.

---

## Activity Overview

{analyze_daily_logs()}

---

## Wins & Progress

{check_wins()}

{analyze_goals_progress()}

---

## Patterns & Correlations

{find_patterns()}

---

## This Week's Focus

**High-Level Goals:**
- Review GOALS.md weekly
- Log wins daily (builds momentum)
- Track what triggers productive days
- Monitor energy levels

**Quick Reflection Questions:**
- What made this week successful?
- What patterns emerged?
- What should I do more/less of?
- Am I moving toward my goals?

---

## Recommendations

**Daily Habits:**
- [ ] Log at least 1 win per day
- [ ] Review tomorrow's calendar before bed
- [ ] Note energy levels (helps find patterns)

**Weekly Habits:**
- [ ] Review goal progress (Sunday evening)
- [ ] Reflect on patterns
- [ ] Plan next week's priorities

**Monthly Habits:**
- [ ] Deep reflection on progress
- [ ] Update GOALS.md if priorities changed
- [ ] Celebrate completed milestones

---

*This report will get smarter over time as we log more data and detect patterns.*
"""
    
    output_file = OUTPUT_DIR / f"personal-insights-{datetime.now().strftime('%Y%m%d')}.md"
    with open(output_file, "w") as f:
        f.write(report)
    
    return output_file

def main():
    print("🧠 Night Shift: Personal Insights")
    print("=" * 50)
    
    print("\nAnalyzing daily logs...")
    print("Checking wins...")
    print("Reviewing goals...")
    print("Finding patterns...")
    
    insights_file = generate_insights()
    print(f"\n✅ Insights: {insights_file}")
    
    print("\n✨ Personal insights complete!")
    
    return {"insights": str(insights_file)}

if __name__ == "__main__":
    main()
