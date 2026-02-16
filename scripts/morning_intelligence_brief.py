#!/usr/bin/env python3
"""
Morning Intelligence Brief
Comprehensive daily intelligence delivered at 7:30am

Includes:
- Weather + outfit suggestion
- Calendar overview (meetings, conflicts)
- Urgent emails flagged
- Macro targets for the day
- Top priority task
- Format: 5-bullet executive summary
"""

import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Config
DATA_DIR = Path("/Users/clawdbot/clawd/data")
CONFIG_FILE = Path("/Users/clawdbot/clawd/morning-config.json")

def get_weather() -> Dict:
    """Get Nashville weather"""
    # Placeholder - integrate with weather API
    return {
        "temp": 45,
        "conditions": "Cloudy",
        "high": 52,
        "low": 38,
        "outfit_suggestion": "Light jacket, jeans"
    }

def get_calendar_overview() -> Dict:
    """Get today's calendar events"""
    # Placeholder - integrate with Google Calendar
    return {
        "events_count": 3,
        "events": [
            {"time": "9:00 AM", "title": "Team standup", "duration": "30 min"},
            {"time": "2:00 PM", "title": "Coffee with Sarah", "duration": "1 hr"},
            {"time": "4:00 PM", "title": "Gym", "duration": "1.5 hrs"}
        ],
        "conflicts": [],
        "free_blocks": ["10:00 AM - 2:00 PM", "after 5:30 PM"]
    }

def check_urgent_emails() -> Dict:
    """Check for urgent/important emails"""
    # Placeholder - integrate with Gmail API
    return {
        "urgent_count": 2,
        "urgent_emails": [
            {"from": "client@example.com", "subject": "Urgent: Project deadline", "importance": "high"},
            {"from": "boss@company.com", "subject": "Meeting today?", "importance": "medium"}
        ]
    }

def get_macro_targets() -> Dict:
    """Get daily macro targets from fitness tracker"""
    try:
        # Query FitTrack Pro API
        response = requests.get("http://localhost:3000/api/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            goals = data.get("goals", {})
            today = data.get("today", {})
            return {
                "calories": goals.get("calories", 2200),
                "protein": goals.get("protein", 200),
                "current_calories": today.get("calories", 0),
                "current_protein": today.get("protein", 0)
            }
    except:
        pass
    
    # Fallback
    return {
        "calories": 2200,
        "protein": 200,
        "current_calories": 0,
        "current_protein": 0
    }

def get_top_priority() -> str:
    """Get top priority task from config"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            priorities = config.get("priorities", {}).get("today", [])
            if priorities:
                return priorities[0]
    
    return "Review your task list and set priorities"

def generate_brief() -> str:
    """Generate morning intelligence brief"""
    weather = get_weather()
    calendar = get_calendar_overview()
    emails = check_urgent_emails()
    macros = get_macro_targets()
    priority = get_top_priority()
    
    # Format brief
    brief = f"""
🌅 **Morning Intelligence Brief**  
📅 {datetime.now().strftime('%A, %B %d, %Y')}

**1. Weather & Dress Code**
🌡️ {weather['temp']}°F, {weather['conditions']} (High: {weather['high']}°F)
👔 Suggestion: {weather['outfit_suggestion']}

**2. Calendar Overview**
📅 {calendar['events_count']} events today:
"""
    
    for event in calendar['events'][:3]:
        brief += f"   • {event['time']} - {event['title']} ({event['duration']})\n"
    
    if calendar['free_blocks']:
        brief += f"   🟢 Free: {', '.join(calendar['free_blocks'])}\n"
    
    brief += f"""
**3. Email Intelligence**
📧 {emails['urgent_count']} urgent messages requiring attention:
"""
    
    for email in emails['urgent_emails'][:2]:
        brief += f"   • {email['from']}: {email['subject']}\n"
    
    brief += f"""
**4. Fitness Targets**
🎯 Calories: {macros['calories']} target | Protein: {macros['protein']}g goal
💪 Start strong: Hit protein at breakfast

**5. Top Priority**
⭐ **{priority}**

---
Have a productive day! 🚀
    """
    
    return brief.strip()

def main():
    """Generate and print brief"""
    brief = generate_brief()
    print(brief)
    
    # Save to file
    output_file = DATA_DIR / "morning_brief_latest.txt"
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(brief)
    
    print(f"\n✅ Brief saved to {output_file}")

if __name__ == "__main__":
    main()
