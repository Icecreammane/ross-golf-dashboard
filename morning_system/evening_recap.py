#!/usr/bin/env python3
"""
Evening Recap - Log wins, learnings, and update decision patterns
Feeds into tomorrow's optimization
"""

import json
from datetime import datetime

def create_template_recap():
    """Create a template for evening recap"""
    
    recap = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "template": {
            "wins_today": [
                {"win": "Example: Shipped meal planner", "impact": "Saves 30 min daily on meal planning"},
                {"win": "Example: Built NBA projections model", "impact": "Ready to test on 2/11 slate"}
            ],
            "workouts_completed": [
                {"workout": "Leg Day", "exercises": 5, "duration_min": 65, "notes": "Heavy day, felt strong"}
            ],
            "nutrition": {
                "goal": "200g protein",
                "actual": "TBD - log at end of day",
                "status": "ON_TRACK or MISSED"
            },
            "priorities_completed": {
                "priority_1": False,  # Update at end of day
                "priority_2": False,
                "priority_3": False
            },
            "learnings": [
                "What worked today?",
                "What didn't work?",
                "What surprised you?",
                "What would you do differently?"
            ],
            "tomorrow_adjustments": [
                "Example: Need more morning focus time",
                "Example: That meal didn't fill me up - swap next time"
            ]
        }
    }
    
    return recap

def save_recap_template():
    """Save template for daily use"""
    
    template = create_template_recap()
    
    with open("/Users/clawdbot/clawd/morning_system/evening_recap_template.json", "w") as f:
        json.dump(template, f, indent=2)
    
    print("✅ Evening recap template created")
    print("\nInstructions:")
    print("1. Fill out wins_today, workouts_completed, nutrition")
    print("2. Mark priorities_completed (true/false)")
    print("3. Write 2-3 learnings")
    print("4. Suggest 1-2 adjustments for tomorrow")
    print("\nSave as: ~/clawd/morning_system/recap_{YYYY-MM-DD}.json")
    print("\nI'll use it to optimize tomorrow's brief!\n")

if __name__ == "__main__":
    save_recap_template()
