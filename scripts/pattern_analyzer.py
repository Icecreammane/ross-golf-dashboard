#!/usr/bin/env python3
"""
Pattern Analyzer - #4: Pattern intuition, not just analysis
Learn Ross's behavioral patterns and predict future behavior
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

CLAWD_DIR = Path.home() / "clawd"
PATTERNS_FILE = CLAWD_DIR / "data" / "behavioral-patterns.json"
FITNESS_DATA = CLAWD_DIR / "fitness-tracker" / "fitness_data.json"

def load_patterns():
    """Load learned behavioral patterns"""
    if PATTERNS_FILE.exists():
        with open(PATTERNS_FILE, 'r') as f:
            return json.load(f)
    return {
        "patterns": [],
        "correlations": {},
        "predictions": {},
        "confidence_scores": {},
        "last_analysis": None
    }

def save_patterns(data):
    """Save learned patterns"""
    data['last_analysis'] = datetime.now().isoformat()
    PATTERNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PATTERNS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def analyze_workout_patterns():
    """Analyze workout behavior patterns"""
    if not Path(FITNESS_DATA).exists():
        return []
    
    with open(FITNESS_DATA, 'r') as f:
        data = json.load(f)
    
    workouts = data.get('workouts', [])
    patterns_found = []
    
    # Pattern: Day of week preferences
    day_counts = defaultdict(int)
    for workout in workouts[-30:]:  # Last 30 workouts
        date = datetime.strptime(workout['date'], '%Y-%m-%d')
        day_counts[date.strftime('%A')] += 1
    
    if day_counts:
        best_day = max(day_counts, key=day_counts.get)
        patterns_found.append({
            "type": "workout_day_preference",
            "pattern": f"Ross works out most on {best_day}s",
            "confidence": min(day_counts[best_day] / 10, 0.95),
            "data": dict(day_counts)
        })
    
    # Pattern: Workout frequency
    if len(workouts) >= 14:
        recent_workouts = len([w for w in workouts if (datetime.now() - datetime.strptime(w['date'], '%Y-%m-%d')).days <= 14])
        avg_per_week = (recent_workouts / 2)
        
        patterns_found.append({
            "type": "workout_frequency",
            "pattern": f"Ross averages {avg_per_week:.1f} workouts per week",
            "confidence": 0.8,
            "data": {"workouts_last_14_days": recent_workouts, "avg_weekly": avg_per_week}
        })
    
    return patterns_found

def analyze_food_logging_patterns():
    """Analyze food logging behavior"""
    if not Path(FITNESS_DATA).exists():
        return []
    
    with open(FITNESS_DATA, 'r') as f:
        data = json.load(f)
    
    food_logs = data.get('food_logs', [])
    patterns_found = []
    
    # Pattern: Days of week with best tracking
    day_counts = defaultdict(int)
    for log in food_logs[-60:]:  # Last 60 logs
        date = datetime.strptime(log['date'], '%Y-%m-%d')
        day_counts[date.strftime('%A')] += 1
    
    if day_counts:
        worst_day = min(day_counts, key=day_counts.get) if day_counts else None
        if worst_day:
            patterns_found.append({
                "type": "logging_weakness",
                "pattern": f"Food logging drops off on {worst_day}s",
                "confidence": 0.75,
                "data": dict(day_counts),
                "actionable": f"Proactive reminder on {worst_day} mornings"
            })
    
    # Pattern: Logging consistency
    dates_logged = set(log['date'] for log in food_logs[-21:])
    consistency_rate = len(dates_logged) / 21 if food_logs else 0
    
    patterns_found.append({
        "type": "logging_consistency",
        "pattern": f"Ross logs food {consistency_rate:.0%} of days",
        "confidence": 0.85,
        "data": {"days_logged": len(dates_logged), "days_tracked": 21, "rate": consistency_rate}
    })
    
    return patterns_found

def find_correlations():
    """Find correlations between behaviors"""
    correlations = {}
    
    # Example: Sleep → Gym attendance (would need sleep data)
    # Example: Weekend → Lower logging (can analyze from existing data)
    
    if not Path(FITNESS_DATA).exists():
        return correlations
    
    with open(FITNESS_DATA, 'r') as f:
        data = json.load(f)
    
    food_logs = data.get('food_logs', [])
    workouts = data.get('workouts', [])
    
    # Correlation: Workout day → More protein logged
    workout_dates = set(w['date'] for w in workouts[-30:])
    workout_day_protein = []
    non_workout_day_protein = []
    
    for log in food_logs[-90:]:
        if log['date'] in workout_dates:
            workout_day_protein.append(log.get('protein', 0))
        else:
            non_workout_day_protein.append(log.get('protein', 0))
    
    if workout_day_protein and non_workout_day_protein:
        avg_workout = sum(workout_day_protein) / len(workout_day_protein)
        avg_non_workout = sum(non_workout_day_protein) / len(non_workout_day_protein)
        
        if abs(avg_workout - avg_non_workout) > 20:
            correlations['workout_protein'] = {
                "pattern": f"Ross eats {avg_workout:.0f}g protein on workout days vs {avg_non_workout:.0f}g on rest days",
                "confidence": 0.70,
                "data": {"workout_day_avg": avg_workout, "rest_day_avg": avg_non_workout}
            }
    
    return correlations

def generate_predictions():
    """Generate behavioral predictions"""
    patterns = load_patterns()
    predictions = {}
    
    # Prediction: Will Ross work out today?
    today_name = datetime.now().strftime('%A')
    workout_patterns = [p for p in patterns.get('patterns', []) if p['type'] == 'workout_day_preference']
    
    if workout_patterns:
        day_data = workout_patterns[0].get('data', {})
        today_count = day_data.get(today_name, 0)
        max_count = max(day_data.values()) if day_data else 1
        probability = (today_count / max_count) if max_count > 0 else 0.5
        
        predictions['workout_today'] = {
            "prediction": "likely" if probability > 0.7 else "possible" if probability > 0.4 else "unlikely",
            "confidence": probability,
            "reasoning": f"Based on {today_name} workout history ({today_count} times)"
        }
    
    # Prediction: Will Ross log food today?
    logging_patterns = [p for p in patterns.get('patterns', []) if p['type'] == 'logging_consistency']
    if logging_patterns:
        rate = logging_patterns[0].get('data', {}).get('rate', 0.5)
        predictions['will_log_food'] = {
            "prediction": "likely" if rate > 0.75 else "possible" if rate > 0.5 else "needs_reminder",
            "confidence": rate,
            "reasoning": f"Historical logging rate: {rate:.0%}"
        }
    
    return predictions

def analyze():
    """Run full pattern analysis"""
    print("🧠 Analyzing Ross's behavioral patterns...")
    
    patterns_data = load_patterns()
    
    # Collect patterns
    workout_patterns = analyze_workout_patterns()
    food_patterns = analyze_food_logging_patterns()
    
    all_patterns = workout_patterns + food_patterns
    patterns_data['patterns'] = all_patterns
    
    # Find correlations
    correlations = find_correlations()
    patterns_data['correlations'] = correlations
    
    # Generate predictions
    predictions = generate_predictions()
    patterns_data['predictions'] = predictions
    
    save_patterns(patterns_data)
    
    print(f"✓ Found {len(all_patterns)} patterns")
    print(f"✓ Found {len(correlations)} correlations")
    print(f"✓ Generated {len(predictions)} predictions")
    
    return patterns_data

def print_report():
    """Print human-readable pattern report"""
    data = load_patterns()
    
    print("\n" + "="*60)
    print("BEHAVIORAL PATTERN ANALYSIS")
    print("="*60 + "\n")
    
    print("🔍 PATTERNS DETECTED:")
    for pattern in data.get('patterns', []):
        conf = int(pattern['confidence'] * 100)
        print(f"  [{conf}%] {pattern['pattern']}")
        if 'actionable' in pattern:
            print(f"       → Action: {pattern['actionable']}")
    
    print("\n🔗 CORRELATIONS:")
    for name, corr in data.get('correlations', {}).items():
        conf = int(corr['confidence'] * 100)
        print(f"  [{conf}%] {corr['pattern']}")
    
    print("\n🔮 PREDICTIONS:")
    for name, pred in data.get('predictions', {}).items():
        conf = int(pred['confidence'] * 100)
        print(f"  [{conf}%] {name}: {pred['prediction']}")
        print(f"       → {pred['reasoning']}")
    
    print("\n" + "="*60 + "\n")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 pattern_analyzer.py analyze  # Run full analysis")
        print("  python3 pattern_analyzer.py report   # Print current patterns")
        print("  python3 pattern_analyzer.py predict  # Get predictions")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze":
        analyze()
        print_report()
    elif command == "report":
        print_report()
    elif command == "predict":
        data = load_patterns()
        print(json.dumps(data.get('predictions', {}), indent=2))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
