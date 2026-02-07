#!/usr/bin/env python3
"""
Proactive Agent - Jarvis's autonomous messaging system
Checks conditions and sends proactive messages to Ross when needed
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Paths
CLAWD_DIR = Path.home() / "clawd"
STATE_FILE = CLAWD_DIR / "data" / "proactive-state.json"
FITNESS_DATA = CLAWD_DIR / "fitness-tracker" / "fitness_data.json"
MEMORY_DIR = CLAWD_DIR / "memory"

def load_state():
    """Load proactive agent state"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "last_checks": {},
        "last_messages": {},
        "message_count_today": 0,
        "last_reset": datetime.now().strftime('%Y-%m-%d')
    }

def save_state(state):
    """Save proactive agent state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def reset_daily_counters(state):
    """Reset daily message counters"""
    today = datetime.now().strftime('%Y-%m-%d')
    if state.get('last_reset') != today:
        state['message_count_today'] = 0
        state['last_reset'] = today
    return state

def should_throttle(state):
    """Check if we should throttle messages (max 5 proactive messages/day)"""
    state = reset_daily_counters(state)
    return state['message_count_today'] >= 5

def can_send_message(state, message_type, cooldown_hours=4):
    """Check if we can send a specific message type (with cooldown)"""
    last_sent = state['last_messages'].get(message_type)
    if not last_sent:
        return True
    
    last_time = datetime.fromisoformat(last_sent)
    cooldown = timedelta(hours=cooldown_hours)
    return datetime.now() - last_time > cooldown

def send_message(message, message_type, state):
    """Send a message to Ross via Telegram"""
    # This gets called by the system, which routes to Telegram automatically
    print(f"[PROACTIVE] {message}")
    
    # Update state
    state['last_messages'][message_type] = datetime.now().isoformat()
    state['message_count_today'] += 1
    save_state(state)
    
    return message

def check_food_logging(state):
    """Check if food has been logged today"""
    now = datetime.now()
    
    # Only check between 2pm-8pm CST
    if now.hour < 14 or now.hour >= 20:
        return None
    
    # Check if already messaged about this today
    if not can_send_message(state, 'food_reminder', cooldown_hours=6):
        return None
    
    # Load fitness data
    if not FITNESS_DATA.exists():
        return None
    
    with open(FITNESS_DATA, 'r') as f:
        data = json.load(f)
    
    today = now.strftime('%Y-%m-%d')
    today_logs = [log for log in data.get('food_logs', []) if log.get('date') == today]
    
    # If no food logged yet and it's past 2pm
    if not today_logs and now.hour >= 14:
        return send_message(
            "🍽️ No food logged yet today. Hit those macros, boss! (200g protein, 2650 cal)",
            'food_reminder',
            state
        )
    
    return None

def check_workout_logging(state):
    """Check if workout has been logged today"""
    now = datetime.now()
    
    # Only check in the evening (7pm-9pm CST)
    if now.hour < 19 or now.hour >= 21:
        return None
    
    # Skip weekends (Ross might not work out)
    if now.weekday() >= 5:
        return None
    
    # Check if already messaged about this today
    if not can_send_message(state, 'workout_reminder', cooldown_hours=24):
        return None
    
    # Load fitness data
    if not FITNESS_DATA.exists():
        return None
    
    with open(FITNESS_DATA, 'r') as f:
        data = json.load(f)
    
    today = now.strftime('%Y-%m-%d')
    today_workouts = [w for w in data.get('workouts', []) if w.get('date') == today]
    
    # If no workout logged and it's evening
    if not today_workouts:
        return send_message(
            "💪 No workout logged today. Rest day, or should I expect a late session?",
            'workout_reminder',
            state
        )
    
    return None

def check_morning_wins(state):
    """Check if morning priorities are being hit"""
    now = datetime.now()
    
    # Only check at 11am CST (mid-morning check-in)
    if now.hour != 11:
        return None
    
    # Check if already messaged about this today
    if not can_send_message(state, 'morning_wins', cooldown_hours=24):
        return None
    
    return send_message(
        "☀️ Morning check: Any quick wins so far today? (Even small ones count)",
        'morning_wins',
        state
    )

def check_evening_reflection(state):
    """Evening reflection prompt"""
    now = datetime.now()
    
    # Only check at 8pm CST (evening check-in time)
    if now.hour != 20:
        return None
    
    # Check if already messaged about this today
    if not can_send_message(state, 'evening_reflection', cooldown_hours=24):
        return None
    
    return send_message(
        "🌙 Evening check-in! How was your day? Any wins to log? 🏆",
        'evening_reflection',
        state
    )

def check_goal_progress(state):
    """Weekly goal progress check"""
    now = datetime.now()
    
    # Only on Sundays at 5pm
    if now.weekday() != 6 or now.hour != 17:
        return None
    
    # Check if already messaged this week
    if not can_send_message(state, 'goal_progress', cooldown_hours=168):  # 1 week
        return None
    
    return send_message(
        "📊 Weekly check: How'd we do on goals this week? Weekly report coming at 6pm.",
        'goal_progress',
        state
    )

def run_checks():
    """Run all proactive checks"""
    state = load_state()
    
    # Check if we should throttle (max 5 messages/day)
    if should_throttle(state):
        return
    
    # Run all checks (order matters - most important first)
    checks = [
        check_evening_reflection,  # 8pm daily
        check_food_logging,        # 2pm-8pm
        check_workout_logging,     # 7pm-9pm weekdays
        check_morning_wins,        # 11am
        check_goal_progress,       # Sunday 5pm
    ]
    
    for check in checks:
        message = check(state)
        if message:
            # Only send one proactive message per run
            break

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        state = load_state()
        print(json.dumps(state, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == 'reset':
        state = {"last_checks": {}, "last_messages": {}, "message_count_today": 0, "last_reset": datetime.now().strftime('%Y-%m-%d')}
        save_state(state)
        print("State reset")
    else:
        run_checks()

if __name__ == "__main__":
    main()
