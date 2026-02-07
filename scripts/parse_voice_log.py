#!/usr/bin/env python3
"""
Voice Log Parser - Jarvis
Parses voice messages and extracts actionable data
- Food logs: "Ate chicken breast 8oz"
- Workout logs: "Bench press 225x5"
- Wins: "Hit a new PR today"
- General notes: anything else
"""

import re
import json
from datetime import datetime
from pathlib import Path

def parse_food_log(text):
    """Parse food-related voice messages"""
    # Look for food keywords
    food_keywords = ['ate', 'eating', 'had', 'meal', 'breakfast', 'lunch', 'dinner', 'snack']
    
    if any(keyword in text.lower() for keyword in food_keywords):
        return {
            'type': 'food',
            'description': text,
            'timestamp': datetime.now().isoformat(),
            'needs_macro_lookup': True
        }
    return None

def parse_workout_log(text):
    """Parse workout-related voice messages"""
    # Look for exercise patterns: "bench press 225x5" or "squats 315 for 8 reps"
    exercise_pattern = r'(\w+(?:\s+\w+)?)\s+(\d+)(?:x|for\s+)(\d+)'
    
    workout_keywords = ['workout', 'lifted', 'press', 'squat', 'deadlift', 'curl', 'row', 'pull', 'push']
    
    if any(keyword in text.lower() for keyword in workout_keywords):
        match = re.search(exercise_pattern, text, re.IGNORECASE)
        if match:
            exercise = match.group(1)
            weight = int(match.group(2))
            reps = int(match.group(3))
            return {
                'type': 'workout',
                'exercise': exercise,
                'weight': weight,
                'reps': reps,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'type': 'workout',
                'description': text,
                'timestamp': datetime.now().isoformat(),
                'needs_parsing': True
            }
    return None

def parse_win(text):
    """Parse wins/accomplishments"""
    win_keywords = ['won', 'win', 'pr', 'personal record', 'accomplished', 'finished', 'completed', 'hit']
    
    if any(keyword in text.lower() for keyword in win_keywords):
        return {
            'type': 'win',
            'description': text,
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d')
        }
    return None

def parse_voice_message(text):
    """Parse voice message and categorize"""
    text = text.strip()
    
    # Try each parser
    result = parse_food_log(text) or parse_workout_log(text) or parse_win(text)
    
    if result:
        return result
    else:
        # Generic note
        return {
            'type': 'note',
            'content': text,
            'timestamp': datetime.now().isoformat()
        }

def save_parsed_log(data):
    """Save parsed data to appropriate location"""
    log_dir = Path.home() / "clawd" / "voice_logs"
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{data['type']}_{timestamp}.json"
    
    with open(log_dir / filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    return log_dir / filename

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 parse_voice_log.py 'voice message text'")
        sys.exit(1)
    
    text = " ".join(sys.argv[1:])
    result = parse_voice_message(text)
    print(json.dumps(result, indent=2))
    
    filepath = save_parsed_log(result)
    print(f"\n✅ Saved to: {filepath}")
