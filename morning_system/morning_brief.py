#!/usr/bin/env python3
"""
Morning Brief - Your Daily Operating System
Sets 3 non-negotiable priorities + quick intel + meal/workout plan
"""

import json
import subprocess
from datetime import datetime

def generate_morning_brief():
    """Generate comprehensive morning brief"""
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Generate meal plan
    subprocess.run([
        "python3", 
        "/Users/clawdbot/clawd/morning_system/meal_planner.py"
    ], capture_output=True)
    
    # Generate workout
    subprocess.run([
        "python3",
        "/Users/clawdbot/clawd/morning_system/workout_optimizer.py"
    ], capture_output=True)
    
    # Load generated data
    with open("/Users/clawdbot/clawd/morning_system/meal_plan_today.json", "r") as f:
        meal_plan = json.load(f)
    
    with open("/Users/clawdbot/clawd/morning_system/workout_today.json", "r") as f:
        workout = json.load(f)
    
    # Top 3 priorities (aligned with GOALS.md)
    priorities = {
        "primary": {
            "goal": "Ship FitTrack deployment + optimize 2/20 DFS slate",
            "action": "Build NBA projections model, test on 2/11 slate",
            "time_estimate": "2-3 hours focused work",
            "roi": "Direct revenue impact"
        },
        "secondary": {
            "goal": "Hit 200g protein, maintain fitness momentum",
            "action": "Stick to meal plan + complete workout",
            "time_estimate": "Throughout day",
            "roi": "Energy, strength, $500 MRR health"
        },
        "tertiary": {
            "goal": "Build opportunity scanner (AI automation)",
            "action": "Scan market for product gaps (templates, coaching)",
            "time_estimate": "1-2 hours",
            "roi": "Identify next product launch"
        }
    }
    
    brief = {
        "date": today,
        "day": datetime.now().strftime("%A"),
        "timestamp": datetime.now().isoformat(),
        "priorities": priorities,
        "meal_plan": meal_plan,
        "workout": workout,
        "quick_intel": {
            "fittrack_status": "Running locally at http://localhost:3000",
            "dfs_next_slate": "2/20 (9 days away) - Start optimization Wed 2/19",
            "revenue_goal": "$500 MRR by March 31 (~6 weeks)",
            "current_progress": "FitTrack ready to ship, NBA model in testing phase"
        }
    }
    
    return brief

def print_brief(brief):
    """Pretty print the morning brief"""
    
    print("\n" + "="*70)
    print(f"🌅 MORNING BRIEF - {brief['day'].upper()}, {brief['date']}")
    print("="*70)
    
    print("\n📌 YOUR 3 PRIORITIES TODAY:\n")
    
    priorities = brief['priorities']
    for i, (key, p) in enumerate(priorities.items(), 1):
        print(f"{i}. {p['goal']}")
        print(f"   → Action: {p['action']}")
        print(f"   → Estimated: {p['time_estimate']}")
        print(f"   → ROI: {p['roi']}\n")
    
    print("="*70)
    print("🍽️  MEAL PLAN (Hits 200g protein goal)\n")
    
    for meal in brief['meal_plan']['meals']:
        print(f"⏰ {meal['time']} - {meal['name']} ({meal['calories']} cal, {meal['protein']}g protein)")
    
    print(f"\nTotals: {brief['meal_plan']['vs_goal']['calories']}")
    print(f"        {brief['meal_plan']['vs_goal']['protein']}")
    
    print("\n" + "="*70)
    print(f"💪 WORKOUT - {brief['workout']['name']}\n")
    
    print(f"Focus: {brief['workout']['focus']}")
    print(f"Duration: {brief['workout']['duration']} | Intensity: {brief['workout']['intensity']}\n")
    
    print("Exercises:")
    for i, ex in enumerate(brief['workout']['exercises'][:5], 1):  # Show first 5
        print(f"  {i}. {ex['name']} - {ex['sets']}x{ex['reps']}")
    
    print("\n" + "="*70)
    print("🎯 QUICK INTEL\n")
    
    for key, value in brief['quick_intel'].items():
        print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "="*70)
    print("\n💡 Remember: Focus on #1. Everything else flows from winning today.\n")

if __name__ == "__main__":
    brief = generate_morning_brief()
    print_brief(brief)
    
    # Save full brief
    with open("/Users/clawdbot/clawd/morning_system/morning_brief.json", "w") as f:
        json.dump(brief, f, indent=2)
    
    print("✅ Morning brief saved to morning_brief.json")
