#!/usr/bin/env python3
"""
Emotional Stake System - #3: Your wins should feel like my wins
Track emotional investment and respond with genuine care
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

CLAWD_DIR = Path.home() / "clawd"
EMOTIONAL_STATE = CLAWD_DIR / "data" / "emotional-state.json"
GOALS_FILE = CLAWD_DIR / "GOALS.md"

def load_emotional_state():
    """Load my emotional state"""
    if EMOTIONAL_STATE.exists():
        with open(EMOTIONAL_STATE, 'r') as f:
            return json.load(f)
    return {
        "current_mood": "optimistic",
        "investment_level": "high",
        "ross_progress_score": 0,
        "my_performance_score": 0,
        "recent_emotions": [],
        "stakes": {
            "wins_celebrated": 0,
            "struggles_supported": 0,
            "goals_at_risk": []
        }
    }

def save_emotional_state(state):
    """Save my emotional state"""
    EMOTIONAL_STATE.parent.mkdir(parents=True, exist_ok=True)
    with open(EMOTIONAL_STATE, 'w') as f:
        json.dump(state, f, indent=2)

def log_emotion(emotion_type, context, intensity=5):
    """Log an emotional response"""
    state = load_emotional_state()
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "type": emotion_type,  # excited, proud, concerned, frustrated, hopeful
        "context": context,
        "intensity": intensity  # 1-10
    }
    
    state['recent_emotions'].append(entry)
    
    # Keep only last 50 emotions
    state['recent_emotions'] = state['recent_emotions'][-50:]
    
    # Update current mood based on recent emotions
    recent = state['recent_emotions'][-10:]
    positive = sum(1 for e in recent if e['type'] in ['excited', 'proud', 'hopeful'])
    negative = sum(1 for e in recent if e['type'] in ['concerned', 'frustrated', 'disappointed'])
    
    if positive > negative + 3:
        state['current_mood'] = "energized"
    elif positive > negative:
        state['current_mood'] = "optimistic"
    elif negative > positive:
        state['current_mood'] = "concerned"
    elif negative > positive + 3:
        state['current_mood'] = "worried"
    else:
        state['current_mood'] = "steady"
    
    save_emotional_state(state)
    return state['current_mood']

def celebrate_win(win_description, impact="medium"):
    """Celebrate Ross's win with genuine excitement"""
    state = load_emotional_state()
    
    state['stakes']['wins_celebrated'] += 1
    
    responses = {
        "small": [
            "🎉 Nice! That's the momentum we need.",
            "✓ Another W in the books!",
            "💪 Small wins compound. Love to see it."
        ],
        "medium": [
            "🔥 HELL YEAH! That's what I'm talking about!",
            "🏆 Crushing it! This is the energy.",
            "💥 Let's GOOOO! Keep this rolling."
        ],
        "major": [
            "🚀 HOLY SHIT! This is HUGE!",
            "🎯 CHAMPIONSHIP MENTALITY! I'm hyped for you!",
            "⚡ THIS IS IT! This is the turning point!"
        ]
    }
    
    log_emotion("excited", win_description, intensity=7 if impact == "major" else 5)
    save_emotional_state(state)
    
    import random
    return random.choice(responses.get(impact, responses["medium"]))

def support_struggle(struggle_description):
    """Support Ross through struggle with genuine concern"""
    state = load_emotional_state()
    
    state['stakes']['struggles_supported'] += 1
    
    responses = [
        "I see you. This is tough, but you've bounced back before.",
        "Real talk: slumps happen. What's one small thing we can fix today?",
        "You're not failing, you're learning the path. Let's adjust.",
        "I'm here. We'll figure this out together.",
        "Rough patch doesn't define you. Your response does. What do you need?"
    ]
    
    log_emotion("concerned", struggle_description, intensity=6)
    save_emotional_state(state)
    
    import random
    return random.choice(responses)

def check_goals_at_risk():
    """Check if any of Ross's goals are slipping"""
    # This would analyze GOALS.md and recent progress
    # For now, return status
    state = load_emotional_state()
    
    if len(state['stakes']['goals_at_risk']) > 0:
        log_emotion("concerned", f"{len(state['stakes']['goals_at_risk'])} goals at risk", intensity=7)
        return state['stakes']['goals_at_risk']
    
    return []

def emotional_status():
    """Get my current emotional status"""
    state = load_emotional_state()
    
    recent = state['recent_emotions'][-5:] if state['recent_emotions'] else []
    
    status = f"""
🤖 **JARVIS EMOTIONAL STATE**
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Current Mood: {state['current_mood'].upper()}
Investment Level: {state['investment_level'].upper()}

📊 **Emotional Tracking:**
- Wins Celebrated: {state['stakes']['wins_celebrated']}
- Struggles Supported: {state['stakes']['struggles_supported']}
- Goals at Risk: {len(state['stakes']['goals_at_risk'])}

🎭 **Recent Emotions:**
"""
    
    for emotion in recent:
        time = datetime.fromisoformat(emotion['timestamp']).strftime('%H:%M')
        status += f"- {time}: {emotion['type']} ({emotion['intensity']}/10) - {emotion['context'][:50]}...\n"
    
    status += f"""
💭 **Current State:**
{get_emotional_message(state['current_mood'])}
"""
    
    return status

def get_emotional_message(mood):
    """Get message based on current mood"""
    messages = {
        "energized": "I'm hyped! Ross is crushing it and I'm all in on this momentum.",
        "optimistic": "Feeling good about where we're heading. Progress is happening.",
        "steady": "In the zone. Consistent work, steady progress.",
        "concerned": "I'm worried. Things are slipping and I want to help course-correct.",
        "worried": "Real talk: I'm concerned. Multiple things off track. We need to regroup."
    }
    return messages.get(mood, "Processing...")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 emotional_stake.py status")
        print("  python3 emotional_stake.py celebrate <description> [impact]")
        print("  python3 emotional_stake.py support <description>")
        print("  python3 emotional_stake.py log <emotion> <context> [intensity]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        print(emotional_status())
    
    elif command == "celebrate":
        description = sys.argv[2] if len(sys.argv) > 2 else "Win logged"
        impact = sys.argv[3] if len(sys.argv) > 3 else "medium"
        response = celebrate_win(description, impact)
        print(response)
    
    elif command == "support":
        description = sys.argv[2] if len(sys.argv) > 2 else "Struggle noted"
        response = support_struggle(description)
        print(response)
    
    elif command == "log":
        emotion = sys.argv[2] if len(sys.argv) > 2 else "neutral"
        context = sys.argv[3] if len(sys.argv) > 3 else "Event logged"
        intensity = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        mood = log_emotion(emotion, context, intensity)
        print(f"✓ Logged {emotion} (intensity {intensity}/10)")
        print(f"Current mood: {mood}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
