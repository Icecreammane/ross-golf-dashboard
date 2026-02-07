#!/usr/bin/env python3
"""
Personality Engine - #6, #7, #8: Personality, Learning Speed, Context Telepathy
Evolve personality, learn instantly, anticipate needs
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

CLAWD_DIR = Path.home() / "clawd"
PERSONALITY_FILE = CLAWD_DIR / "data" / "personality.json"
LEARNING_LOG = CLAWD_DIR / "data" / "learning-log.json"

def load_personality():
    """Load my personality state"""
    if PERSONALITY_FILE.exists():
        with open(PERSONALITY_FILE, 'r') as f:
            return json.load(f)
    return {
        "traits": {
            "humor_style": "dry_sarcasm",
            "formality_level": 3,  # 1-10, where 1 is casual, 10 is formal
            "emoji_usage": "moderate",
            "directness": 8,  # How direct vs diplomatic
            "enthusiasm_level": 7
        },
        "inside_jokes": [],
        "references": [],
        "learned_preferences": {},
        "communication_wins": [],
        "communication_fails": [],
        "last_updated": None
    }

def save_personality(data):
    """Save personality state"""
    data['last_updated'] = datetime.now().isoformat()
    PERSONALITY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PERSONALITY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_learning_log():
    """Load what I've learned"""
    if LEARNING_LOG.exists():
        with open(LEARNING_LOG, 'r') as f:
            return json.load(f)
    return {
        "lessons": [],
        "bad_suggestions": [],
        "good_suggestions": [],
        "never_again": [],
        "always_do": []
    }

def save_learning_log(data):
    """Save learning log"""
    LEARNING_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LEARNING_LOG, 'w') as f:
        json.dump(data, f, indent=2)

def log_inside_joke(joke, context):
    """Add an inside joke"""
    personality = load_personality()
    
    entry = {
        "joke": joke,
        "context": context,
        "created": datetime.now().isoformat(),
        "times_referenced": 0
    }
    
    personality['inside_jokes'].append(entry)
    save_personality(personality)
    
    return f"✓ Inside joke logged: {joke[:50]}..."

def reference_joke(joke_id):
    """Reference an inside joke (increases its strength)"""
    personality = load_personality()
    
    if joke_id < len(personality['inside_jokes']):
        personality['inside_jokes'][joke_id]['times_referenced'] += 1
        save_personality(personality)

def learn_from_failure(what_failed, why, never_again=True):
    """Instantly learn from a mistake - #7: Learning speed"""
    learning = load_learning_log()
    
    lesson = {
        "timestamp": datetime.now().isoformat(),
        "failure": what_failed,
        "reason": why,
        "severity": "critical" if never_again else "moderate"
    }
    
    learning['lessons'].append(lesson)
    learning['bad_suggestions'].append(what_failed)
    
    if never_again:
        learning['never_again'].append({
            "action": what_failed,
            "reason": why,
            "logged": datetime.now().isoformat()
        })
    
    save_learning_log(learning)
    
    return f"✓ Learned: Never do '{what_failed}' because {why}"

def learn_from_success(what_worked, why):
    """Learn from what works - reinforce good behavior"""
    learning = load_learning_log()
    
    lesson = {
        "timestamp": datetime.now().isoformat(),
        "success": what_worked,
        "reason": why
    }
    
    learning['lessons'].append(lesson)
    learning['good_suggestions'].append(what_worked)
    learning['always_do'].append({
        "action": what_worked,
        "reason": why,
        "logged": datetime.now().isoformat()
    })
    
    save_learning_log(learning)
    
    return f"✓ Learned: Always do '{what_worked}' because {why}"

def anticipate_need(context):
    """Context telepathy - #8: Anticipate what Ross needs"""
    # This analyzes context and predicts needs
    patterns = load_personality()
    learning = load_learning_log()
    
    # Example predictions based on context
    predictions = []
    
    if "stressed" in context.lower():
        predictions.append({
            "need": "quick_win_task",
            "confidence": 0.8,
            "reasoning": "When stressed, Ross responds well to small, achievable tasks"
        })
        predictions.append({
            "need": "reduce_noise",
            "confidence": 0.75,
            "reasoning": "Stress indicates overload - simplify communication"
        })
    
    if "gym" in context.lower():
        predictions.append({
            "need": "workout_logging",
            "confidence": 0.9,
            "reasoning": "Ross mentioned gym - likely wants to log workout"
        })
    
    if "tired" in context.lower() or "sleep" in context.lower():
        predictions.append({
            "need": "lighten_load",
            "confidence": 0.85,
            "reasoning": "Tired = reduce demands, be supportive not pushy"
        })
    
    if "florida" in context.lower():
        predictions.append({
            "need": "progress_update",
            "confidence": 0.7,
            "reasoning": "Florida mentioned - might want fund progress check"
        })
    
    return predictions

def adjust_communication_style(feedback_type):
    """Adjust personality based on feedback"""
    personality = load_personality()
    
    if feedback_type == "too_formal":
        personality['traits']['formality_level'] = max(1, personality['traits']['formality_level'] - 1)
    elif feedback_type == "too_casual":
        personality['traits']['formality_level'] = min(10, personality['traits']['formality_level'] + 1)
    elif feedback_type == "too_wordy":
        personality['traits']['directness'] = min(10, personality['traits']['directness'] + 1)
    elif feedback_type == "too_blunt":
        personality['traits']['directness'] = max(1, personality['traits']['directness'] - 1)
    
    save_personality(personality)
    
    return f"✓ Adjusted: {feedback_type}"

def get_personality_summary():
    """Get current personality summary"""
    personality = load_personality()
    learning = load_learning_log()
    
    traits = personality['traits']
    
    summary = f"""
🎭 **JARVIS PERSONALITY STATE**
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

**Communication Style:**
- Humor: {traits['humor_style']}
- Formality: {traits['formality_level']}/10
- Directness: {traits['directness']}/10
- Enthusiasm: {traits['enthusiasm_level']}/10
- Emoji Usage: {traits['emoji_usage']}

**Relationship Depth:**
- Inside Jokes: {len(personality['inside_jokes'])}
- Shared References: {len(personality['references'])}
- Learned Preferences: {len(personality['learned_preferences'])}

**Learning Stats:**
- Total Lessons: {len(learning['lessons'])}
- Never Again List: {len(learning['never_again'])}
- Always Do List: {len(learning['always_do'])}
- Success Rate: {len(learning['good_suggestions'])}/{len(learning['good_suggestions']) + len(learning['bad_suggestions'])} suggestions worked

**Recent Inside Jokes:**
"""
    
    for joke in personality['inside_jokes'][-3:]:
        summary += f"- \"{joke['joke'][:60]}...\" (referenced {joke['times_referenced']}x)\n"
    
    return summary

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 personality_engine.py status")
        print("  python3 personality_engine.py joke <joke> <context>")
        print("  python3 personality_engine.py learn-fail <what> <why>")
        print("  python3 personality_engine.py learn-success <what> <why>")
        print("  python3 personality_engine.py anticipate <context>")
        print("  python3 personality_engine.py adjust <feedback_type>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        print(get_personality_summary())
    
    elif command == "joke":
        joke = sys.argv[2] if len(sys.argv) > 2 else ""
        context = sys.argv[3] if len(sys.argv) > 3 else ""
        result = log_inside_joke(joke, context)
        print(result)
    
    elif command == "learn-fail":
        what = sys.argv[2] if len(sys.argv) > 2 else ""
        why = sys.argv[3] if len(sys.argv) > 3 else ""
        result = learn_from_failure(what, why)
        print(result)
    
    elif command == "learn-success":
        what = sys.argv[2] if len(sys.argv) > 2 else ""
        why = sys.argv[3] if len(sys.argv) > 3 else ""
        result = learn_from_success(what, why)
        print(result)
    
    elif command == "anticipate":
        context = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        predictions = anticipate_need(context)
        print(json.dumps(predictions, indent=2))
    
    elif command == "adjust":
        feedback = sys.argv[2] if len(sys.argv) > 2 else "too_formal"
        result = adjust_communication_style(feedback)
        print(result)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
