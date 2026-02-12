#!/usr/bin/env python3
"""
Workout Optimizer - Prescribes daily training based on recent history
Learns what works and suggests progressions
"""

import json
from datetime import datetime, timedelta

def get_recent_workouts():
    """Pull last 7 workouts from fitness tracker"""
    try:
        with open("/Users/clawdbot/clawd/fitness-tracker/fitness_data.json", "r") as f:
            data = json.load(f)
        return data.get("workouts", [])[-7:]
    except:
        return []

def generate_workout_plan():
    """Prescribe today's workout based on recent history"""
    
    recent = get_recent_workouts()
    today = datetime.now()
    days_since_last = None
    
    if recent:
        last_workout = datetime.fromisoformat(recent[-1]["date"] + "T00:00:00")
        days_since_last = (today - last_workout).days
    
    # Workout rotation (4-day split)
    day_of_week = today.weekday()  # 0=Mon, 6=Sun
    
    workouts = {
        0: {  # Monday - Legs
            "name": "LEG DAY (Heavy)",
            "focus": "Quad & glute dominant",
            "exercises": [
                {"name": "Squat", "sets": 4, "reps": "6-8", "target": "Heavy"},
                {"name": "Romanian Deadlift", "sets": 3, "reps": "8-10", "target": "Glutes/Hamstring"},
                {"name": "Leg Press", "sets": 3, "reps": "8-10", "target": "Quad"},
                {"name": "Leg Curl", "sets": 3, "reps": "10-12", "target": "Hamstring"},
                {"name": "Calf Raises", "sets": 3, "reps": "12-15", "target": "Calf"},
            ],
            "duration": "60-70 min",
            "intensity": "HIGH"
        },
        1: {  # Tuesday - Upper Push
            "name": "UPPER PUSH (Bench Focus)",
            "focus": "Chest, shoulders, triceps",
            "exercises": [
                {"name": "Bench Press", "sets": 4, "reps": "6-8", "target": "Heavy"},
                {"name": "Incline Dumbbell Press", "sets": 3, "reps": "8-10", "target": "Chest"},
                {"name": "Shoulder Press", "sets": 3, "reps": "8-10", "target": "Shoulders"},
                {"name": "Tricep Dips", "sets": 3, "reps": "8-10", "target": "Triceps"},
                {"name": "Lateral Raises", "sets": 3, "reps": "12-15", "target": "Shoulders"},
            ],
            "duration": "60 min",
            "intensity": "HIGH"
        },
        2: {  # Wednesday - Upper Pull
            "name": "UPPER PULL (Back Focus)",
            "focus": "Back, biceps, rear delts",
            "exercises": [
                {"name": "Deadlift", "sets": 4, "reps": "5-6", "target": "Heavy"},
                {"name": "Barbell Rows", "sets": 4, "reps": "6-8", "target": "Back"},
                {"name": "Pull-ups", "sets": 3, "reps": "8-10", "target": "Lats"},
                {"name": "Barbell Curls", "sets": 3, "reps": "8-10", "target": "Biceps"},
                {"name": "Face Pulls", "sets": 3, "reps": "12-15", "target": "Rear Delts"},
            ],
            "duration": "60 min",
            "intensity": "HIGH"
        },
        3: {  # Thursday - OFF/Active Recovery
            "name": "ACTIVE RECOVERY",
            "focus": "Mobility, stretching, light cardio",
            "exercises": [
                {"name": "5-10 min light cardio (walk/bike)", "sets": 1, "reps": "easy", "target": "Cardio"},
                {"name": "Full body stretching", "sets": 1, "reps": "20 min", "target": "Mobility"},
                {"name": "Foam rolling", "sets": 1, "reps": "10 min", "target": "Recovery"},
            ],
            "duration": "30 min",
            "intensity": "LOW"
        },
        4: {  # Friday - Legs (Repeat)
            "name": "LEG DAY (Variation)",
            "focus": "Hamstring & glute dominant",
            "exercises": [
                {"name": "Hack Squat", "sets": 4, "reps": "8-10", "target": "Quad"},
                {"name": "Leg Curl", "sets": 3, "reps": "8-10", "target": "Hamstring"},
                {"name": "Hip Thrust", "sets": 3, "reps": "10-12", "target": "Glutes"},
                {"name": "Leg Extension", "sets": 3, "reps": "12-15", "target": "Quad"},
            ],
            "duration": "50 min",
            "intensity": "MEDIUM"
        },
        5: {  # Saturday - Upper (Hypertrophy Focus)
            "name": "UPPER HYPERTROPHY",
            "focus": "Volume training, higher reps",
            "exercises": [
                {"name": "Dumbbell Bench Press", "sets": 4, "reps": "8-10", "target": "Chest"},
                {"name": "Machine Rows", "sets": 4, "reps": "8-10", "target": "Back"},
                {"name": "Cable Flyes", "sets": 3, "reps": "10-12", "target": "Chest"},
                {"name": "Lat Pulldown", "sets": 3, "reps": "10-12", "target": "Lats"},
            ],
            "duration": "50 min",
            "intensity": "MEDIUM-HIGH"
        },
        6: {  # Sunday - REST
            "name": "REST DAY",
            "focus": "Recovery, meal prep, planning",
            "exercises": [
                {"name": "Light walk if desired", "sets": 1, "reps": "optional", "target": "Cardio"},
            ],
            "duration": "Flexible",
            "intensity": "REST"
        }
    }
    
    workout = workouts[day_of_week]
    
    # Adjust intensity if not enough rest
    if days_since_last and days_since_last < 1:
        workout["note"] = f"⚠️  Only {days_since_last} day(s) rest - consider backing off if fatigued"
    
    return {
        "date": today.strftime("%Y-%m-%d"),
        "day": today.strftime("%A"),
        **workout,
        "tips": [
            "Warm up 5-10 minutes before lifting",
            "Rest 60-90 seconds between heavy sets",
            "Hit protein goal of 200g today",
            "Stay hydrated throughout workout"
        ]
    }

if __name__ == "__main__":
    workout = generate_workout_plan()
    
    print(f"\n💪 {workout['name']} - {workout['date']}\n")
    print(f"Focus: {workout['focus']}")
    print(f"Duration: {workout['duration']} | Intensity: {workout['intensity']}\n")
    
    print("=" * 60)
    print("EXERCISES:\n")
    
    for i, ex in enumerate(workout["exercises"], 1):
        print(f"{i}. {ex['name']}")
        print(f"   Sets: {ex['sets']} | Reps: {ex['reps']} | Target: {ex['target']}\n")
    
    print("=" * 60)
    print("\n💡 TIPS:\n")
    for tip in workout["tips"]:
        print(f"  • {tip}")
    
    if "note" in workout:
        print(f"\n{workout['note']}")
    
    # Save to file
    with open("/Users/clawdbot/clawd/morning_system/workout_today.json", "w") as f:
        json.dump(workout, f, indent=2)
    
    print("\n✅ Workout plan saved to workout_today.json")
