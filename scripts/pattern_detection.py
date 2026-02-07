#!/usr/bin/env python3
"""
Pattern Detection - Finds Ross's productivity patterns
Tracks: energy levels, productive hours, workout→output correlation, decision quality
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/Users/clawdbot/clawd")
MEMORY_DIR = WORKSPACE / "memory"
LEARNING_DATA = MEMORY_DIR / "learning_data.json"
PATTERN_DATA = MEMORY_DIR / "pattern_data.json"

def load_pattern_data():
    """Load existing pattern data"""
    if PATTERN_DATA.exists():
        with open(PATTERN_DATA) as f:
            return json.load(f)
    
    return {
        "activity_by_hour": {},
        "productive_hours": [],
        "energy_patterns": [],
        "workout_correlation": [],
        "decision_quality_by_hour": {},
        "insights": []
    }

def log_activity_with_context(hour, activity_type, energy_level=None, productivity=None):
    """Log activity with context for pattern analysis"""
    data = load_pattern_data()
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "hour": hour,
        "type": activity_type,
        "energy": energy_level,
        "productivity": productivity
    }
    
    # Track by hour
    hour_key = str(hour)
    if hour_key not in data["activity_by_hour"]:
        data["activity_by_hour"][hour_key] = []
    data["activity_by_hour"][hour_key].append(entry)
    
    # Save
    with open(PATTERN_DATA, "w") as f:
        json.dump(data, f, indent=2)

def analyze_productive_hours():
    """Find Ross's most productive hours"""
    data = load_pattern_data()
    
    # Count high-productivity activities by hour
    productivity_by_hour = defaultdict(list)
    
    for hour, activities in data["activity_by_hour"].items():
        for activity in activities:
            if activity.get("productivity"):
                productivity_by_hour[int(hour)].append(activity["productivity"])
    
    # Calculate average productivity per hour
    avg_productivity = {}
    for hour, scores in productivity_by_hour.items():
        if scores:
            avg_productivity[hour] = sum(scores) / len(scores)
    
    # Find top 3 hours
    if avg_productivity:
        top_hours = sorted(avg_productivity.items(), key=lambda x: x[1], reverse=True)[:3]
        return [hour for hour, score in top_hours]
    
    return []

def analyze_energy_patterns():
    """Find when Ross has highest energy"""
    data = load_pattern_data()
    
    energy_by_hour = defaultdict(list)
    
    for hour, activities in data["activity_by_hour"].items():
        for activity in activities:
            if activity.get("energy"):
                energy_by_hour[int(hour)].append(activity["energy"])
    
    # Calculate average energy per hour
    avg_energy = {}
    for hour, levels in energy_by_hour.items():
        if levels:
            avg_energy[hour] = sum(levels) / len(levels)
    
    # Find peak energy hours
    if avg_energy:
        peak_hours = sorted(avg_energy.items(), key=lambda x: x[1], reverse=True)[:3]
        return [(hour, energy) for hour, energy in peak_hours]
    
    return []

def detect_workout_correlation():
    """Check if workouts correlate with productivity"""
    # Read fitness data
    fitness_file = WORKSPACE / "data" / "fitness_data.json"
    if not fitness_file.exists():
        return None
    
    with open(fitness_file) as f:
        fitness = json.load(f)
    
    workouts = fitness.get("workouts", [])
    
    # Simple heuristic: days with workouts vs days without
    workout_days = set()
    for workout in workouts:
        timestamp = workout.get("timestamp", "")
        if timestamp:
            date = datetime.fromisoformat(timestamp).date()
            workout_days.add(date)
    
    insight = {
        "total_workout_days": len(workout_days),
        "correlation": "Needs more data (track productivity on workout vs non-workout days)"
    }
    
    return insight

def generate_insights():
    """Generate actionable insights from patterns"""
    insights = []
    
    # Productive hours
    productive_hours = analyze_productive_hours()
    if productive_hours:
        hours_str = ", ".join([f"{h}:00" for h in productive_hours])
        insights.append({
            "type": "productive_hours",
            "insight": f"Most productive hours: {hours_str}",
            "recommendation": "Schedule deep work (coding, writing) during these windows",
            "confidence": 0.7
        })
    
    # Energy patterns
    energy_peaks = analyze_energy_patterns()
    if energy_peaks:
        peak_hour = energy_peaks[0][0]
        insights.append({
            "type": "energy_pattern",
            "insight": f"Peak energy at {peak_hour}:00",
            "recommendation": "Tackle hardest problems during this hour",
            "confidence": 0.6
        })
    
    # Workout correlation
    workout_insight = detect_workout_correlation()
    if workout_insight:
        insights.append({
            "type": "workout_correlation",
            "insight": f"Workouts logged: {workout_insight['total_workout_days']} days",
            "recommendation": "Continue tracking to find workout→productivity patterns",
            "confidence": 0.5
        })
    
    # Save insights
    data = load_pattern_data()
    data["insights"] = insights
    
    with open(PATTERN_DATA, "w") as f:
        json.dump(data, f, indent=2)
    
    return insights

def get_schedule_recommendations():
    """Get optimal schedule based on patterns"""
    insights = generate_insights()
    
    recommendations = {
        "deep_work": [],
        "meetings": [],
        "breaks": [],
        "workouts": []
    }
    
    for insight in insights:
        if insight["type"] == "productive_hours":
            # Extract hours from insight text
            recommendations["deep_work"].append(insight["recommendation"])
        elif insight["type"] == "energy_pattern":
            recommendations["breaks"].append("Take breaks during low-energy periods")
    
    return recommendations

def main():
    """CLI for pattern detection"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 pattern_detection.py analyze     - Analyze patterns")
        print("  python3 pattern_detection.py recommend   - Get schedule recommendations")
        print("  python3 pattern_detection.py log <hour>  - Log activity for current hour")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze":
        print("🔍 Analyzing patterns...\n")
        insights = generate_insights()
        
        if not insights:
            print("Not enough data yet. Keep logging activity!")
        else:
            for insight in insights:
                conf = int(insight["confidence"] * 100)
                print(f"📊 {insight['insight']}")
                print(f"   → {insight['recommendation']}")
                print(f"   Confidence: {conf}%\n")
    
    elif command == "recommend":
        print("📅 Optimal Schedule Recommendations:\n")
        recs = get_schedule_recommendations()
        
        for category, items in recs.items():
            if items:
                print(f"{category.replace('_', ' ').title()}:")
                for item in items:
                    print(f"  • {item}")
                print()
    
    elif command == "log":
        hour = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().hour
        log_activity_with_context(hour, "work", energy_level=7, productivity=8)
        print(f"✅ Logged activity for {hour}:00")

if __name__ == "__main__":
    main()
