#!/usr/bin/env python3
"""
Night Shift: Intelligence Brief
Analyzes fitness data, calendar, and generates insights
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
OUTPUT_DIR = WORKSPACE / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def analyze_fitness_data():
    """Analyze fitness patterns"""
    fitness_file = WORKSPACE / "data" / "fitness_data.json"
    
    if not fitness_file.exists():
        return "No fitness data available"
    
    with open(fitness_file) as f:
        data = json.load(f)
    
    workouts = data.get("workouts", [])
    nutrition = data.get("nutrition", [])
    
    summary = f"""**Fitness Data:**
- Total workouts logged: {len(workouts)}
- Total meals logged: {len(nutrition)}
- Recent workout: {workouts[-1]['raw_text'] if workouts else 'None'}
- Recent meal: {nutrition[-1]['raw_text'] if nutrition else 'None'}
"""
    return summary

def check_calendar():
    """Check upcoming calendar events"""
    calendar_file = WORKSPACE / "calendar" / "upcoming-events.md"
    
    if calendar_file.exists():
        with open(calendar_file) as f:
            content = f.read()
        return f"**Calendar:**\n{content[:500]}"
    
    return "**Calendar:** No upcoming events file found"

def analyze_goals_progress():
    """Analyze progress on goals"""
    goals_file = WORKSPACE / "GOALS.md"
    
    if not goals_file.exists():
        return "No goals file found"
    
    with open(goals_file) as f:
        goals = f.read()
    
    # Simple analysis - just read first 500 chars
    return f"**Goals Context:**\n{goals[:500]}..."

def scan_opportunities():
    """Placeholder for Reddit opportunity scanning"""
    return """**Opportunity Scan:**
- Reddit monitoring coming soon
- Will track: r/Fitness, r/SideProject, r/Entrepreneur
- Looking for: "need help with X" posts matching your solutions
"""

def generate_brief():
    """Generate complete intelligence brief"""
    
    brief = f"""# Intelligence Brief - {datetime.now().strftime('%Y-%m-%d')}

Generated at: {datetime.now().strftime('%I:%M %p')}

## Summary
Your overnight intelligence report combining fitness, calendar, goals, and opportunities.

---

## Fitness & Health

{analyze_fitness_data()}

---

## Calendar & Schedule

{check_calendar()}

---

## Goals Progress

{analyze_goals_progress()}

---

## Opportunities

{scan_opportunities()}

---

## Recommendations

**Today's Focus:**
1. Check calendar for any prep needed
2. Log workout if training today
3. Review goals progress weekly
4. Monitor for opportunities in target communities

**Quick Wins:**
- [ ] Update fitness tracker with today's activity
- [ ] Check Reddit for 5 minutes (opportunity scan)
- [ ] Review goals alignment

---

*This brief runs automatically every night. Feedback? Update the night shift scripts.*
"""
    
    output_file = OUTPUT_DIR / f"intelligence-brief-{datetime.now().strftime('%Y%m%d')}.md"
    with open(output_file, "w") as f:
        f.write(brief)
    
    return output_file

def main():
    print("📊 Night Shift: Intelligence Brief")
    print("=" * 50)
    
    print("\nAnalyzing fitness data...")
    print("Checking calendar...")
    print("Reviewing goals...")
    print("Scanning opportunities...")
    
    brief_file = generate_brief()
    print(f"\n✅ Brief: {brief_file}")
    
    print("\n✨ Intelligence brief complete!")
    
    return {"brief": str(brief_file)}

if __name__ == "__main__":
    main()
