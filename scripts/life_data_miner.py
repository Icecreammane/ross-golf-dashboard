#!/usr/bin/env python3
"""
Life Data Miner - Extract behavioral patterns from all logged data

Mines:
- Memory files (daily logs, decisions, wins)
- Build logs (what you've shipped)
- Task completions
- Conversation patterns
- Time-of-day activity

Builds your behavioral dataset.
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

WORKSPACE = Path.home() / "clawd"
MEMORY_DIR = WORKSPACE / "memory"
OUTPUT_FILE = WORKSPACE / "god_mode" / "behavioral_data.json"

# Ensure output directory exists
OUTPUT_FILE.parent.mkdir(exist_ok=True)

def extract_timestamp_pattern(content):
    """Extract timestamps from content (e.g., '6:30pm', '18:30')"""
    patterns = []
    
    # Match patterns like "6:30pm" or "18:30"
    time_pattern = r'\b(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)?\b'
    matches = re.findall(time_pattern, content)
    
    for match in matches:
        hour = int(match[0])
        minute = int(match[1])
        meridiem = match[2].lower() if match[2] else None
        
        if meridiem == 'pm' and hour != 12:
            hour += 12
        elif meridiem == 'am' and hour == 12:
            hour = 0
        
        patterns.append(f"{hour:02d}:{minute:02d}")
    
    return patterns

def extract_decisions(content):
    """Extract decisions from content"""
    decisions = []
    
    # Look for decision keywords
    decision_keywords = ['decided', 'chose', 'going with', 'picked', 'selecting']
    lines = content.split('\n')
    
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in decision_keywords):
            decisions.append(line.strip())
    
    return decisions

def extract_wins(content):
    """Extract wins/achievements"""
    wins = []
    
    # Look for win indicators
    win_patterns = [
        r'✅.*',
        r'🏆.*',
        r'[Ww]in:.*',
        r'[Cc]ompleted:.*',
        r'[Ss]hipped:.*',
        r'COMPLETE.*'
    ]
    
    for pattern in win_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        wins.extend(matches)
    
    return wins

def extract_workouts(content):
    """Extract workout data"""
    workouts = []
    
    workout_keywords = ['workout', 'lifted', 'gym', 'exercise', 'chest day', 'leg day', 'bench press']
    lines = content.split('\n')
    
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in workout_keywords):
            workouts.append(line.strip())
    
    return workouts

def extract_energy_indicators(content):
    """Extract energy level indicators"""
    energy_data = {
        "high": 0,
        "medium": 0,
        "low": 0
    }
    
    content_lower = content.lower()
    
    # High energy indicators
    high_energy = ['crushed', 'killing it', 'on fire', 'locked in', 'energy', 'motivated', 'pumped']
    energy_data['high'] = sum(1 for word in high_energy if word in content_lower)
    
    # Low energy indicators
    low_energy = ['tired', 'exhausted', 'burnout', 'drained', 'low energy', 'stuck']
    energy_data['low'] = sum(1 for word in low_energy if word in content_lower)
    
    # If neither, assume medium
    if energy_data['high'] == 0 and energy_data['low'] == 0:
        energy_data['medium'] = 1
    
    return energy_data

def mine_memory_files():
    """Mine all memory files for behavioral data"""
    
    if not MEMORY_DIR.exists():
        return {}
    
    data = {
        "files_processed": 0,
        "time_patterns": defaultdict(int),
        "decisions": [],
        "wins": [],
        "workouts": [],
        "energy_by_date": {},
        "activity_by_hour": defaultdict(int),
        "daily_summaries": {}
    }
    
    # Process all memory markdown files
    for mem_file in sorted(MEMORY_DIR.glob("*.md")):
        if mem_file.name.startswith('.'):
            continue
        
        data["files_processed"] += 1
        
        with open(mem_file) as f:
            content = f.read()
        
        date_str = mem_file.stem  # Filename without extension
        
        # Extract data
        timestamps = extract_timestamp_pattern(content)
        decisions = extract_decisions(content)
        wins = extract_wins(content)
        workouts = extract_workouts(content)
        energy = extract_energy_indicators(content)
        
        # Aggregate time patterns
        for ts in timestamps:
            hour = int(ts.split(':')[0])
            data["activity_by_hour"][hour] += 1
        
        # Store by date
        data["decisions"].extend([{"date": date_str, "text": d} for d in decisions])
        data["wins"].extend([{"date": date_str, "text": w} for w in wins])
        data["workouts"].extend([{"date": date_str, "text": w} for w in workouts])
        data["energy_by_date"][date_str] = energy
        
        # Daily summary
        data["daily_summaries"][date_str] = {
            "decisions": len(decisions),
            "wins": len(wins),
            "workouts": len(workouts),
            "energy": "high" if energy['high'] > energy['low'] else "low" if energy['low'] > 0 else "medium",
            "activity_count": len(timestamps)
        }
    
    # Convert defaultdicts to regular dicts for JSON serialization
    data["time_patterns"] = dict(data["time_patterns"])
    data["activity_by_hour"] = dict(data["activity_by_hour"])
    
    return data

def analyze_patterns(data):
    """Analyze extracted data for patterns"""
    
    patterns = {
        "most_active_hours": [],
        "peak_productivity_time": None,
        "avg_daily_wins": 0,
        "avg_daily_decisions": 0,
        "workout_frequency": 0,
        "high_energy_days": 0,
        "low_energy_days": 0,
        "total_days_tracked": len(data.get("daily_summaries", {}))
    }
    
    # Find most active hours
    activity = data.get("activity_by_hour", {})
    if activity:
        sorted_hours = sorted(activity.items(), key=lambda x: x[1], reverse=True)
        patterns["most_active_hours"] = [f"{h:02d}:00" for h, _ in sorted_hours[:3]]
        patterns["peak_productivity_time"] = f"{sorted_hours[0][0]:02d}:00" if sorted_hours else None
    
    # Calculate averages
    daily_summaries = data.get("daily_summaries", {})
    if daily_summaries:
        total_days = len(daily_summaries)
        total_wins = sum(day.get("wins", 0) for day in daily_summaries.values())
        total_decisions = sum(day.get("decisions", 0) for day in daily_summaries.values())
        
        patterns["avg_daily_wins"] = round(total_wins / total_days, 2) if total_days > 0 else 0
        patterns["avg_daily_decisions"] = round(total_decisions / total_days, 2) if total_days > 0 else 0
        
        # Count energy days
        patterns["high_energy_days"] = sum(1 for day in daily_summaries.values() if day.get("energy") == "high")
        patterns["low_energy_days"] = sum(1 for day in daily_summaries.values() if day.get("energy") == "low")
        
        # Workout frequency
        patterns["workout_frequency"] = len(data.get("workouts", []))
    
    return patterns

def main():
    """Mine and analyze life data"""
    print("🧠 GOD MODE: Data Mining Starting...")
    print(f"📂 Scanning: {MEMORY_DIR}")
    
    # Mine data
    data = mine_memory_files()
    
    print(f"\n✅ Processed {data['files_processed']} memory files")
    print(f"📊 Found:")
    print(f"   • {len(data['decisions'])} decisions")
    print(f"   • {len(data['wins'])} wins")
    print(f"   • {len(data['workouts'])} workouts")
    print(f"   • {len(data['daily_summaries'])} days tracked")
    
    # Analyze patterns
    patterns = analyze_patterns(data)
    data["patterns"] = patterns
    
    print(f"\n🎯 Initial Patterns:")
    print(f"   • Most active hours: {', '.join(patterns['most_active_hours'])}")
    print(f"   • Avg wins/day: {patterns['avg_daily_wins']}")
    print(f"   • Workout frequency: {patterns['workout_frequency']} logged")
    print(f"   • High energy days: {patterns['high_energy_days']}/{patterns['total_days_tracked']}")
    
    # Save data
    data["mined_at"] = datetime.now().isoformat()
    data["version"] = "1.0"
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n💾 Data saved to: {OUTPUT_FILE}")
    print(f"📈 Behavioral dataset ready for analysis")
    
    return data

if __name__ == "__main__":
    main()
