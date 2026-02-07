#!/usr/bin/env python3
"""
Smart Context Detection System
Detects Ross's current context and adapts communication style accordingly.

Usage:
    from systems.smart_context import get_current_context, should_use_voice
    
    context = get_current_context()
    # Returns: 'work', 'morning', 'evening', 'weekend', 'night'
    
    use_voice = should_use_voice(user_sent_voice=False)
    # Returns: True/False based on context + user input type
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Literal

# Configuration
WORKSPACE = Path.home() / "clawd"
STATE_FILE = WORKSPACE / "memory" / "context-state.json"
TIMEZONE = "America/Chicago"  # Ross's timezone

# Context definitions
WORK_DAYS = [0, 1, 2, 3, 4]  # Monday-Friday
WORK_START = 9  # 9 AM
WORK_END = 17   # 5 PM
MORNING_END = 10  # Before 10 AM = morning
EVENING_START = 17  # After 5 PM = evening
NIGHT_START = 22  # After 10 PM = night

ContextType = Literal['work', 'morning', 'evening', 'weekend', 'night']


def get_current_time() -> datetime:
    """Get current time in Ross's timezone."""
    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(TIMEZONE)
    except ImportError:
        # Fallback for Python < 3.9
        import pytz
        tz = pytz.timezone(TIMEZONE)
    
    return datetime.now(tz)


def get_current_context() -> ContextType:
    """
    Detect Ross's current context based on time.
    
    Returns:
        - 'work': Weekday, 9am-5pm
        - 'morning': Weekday/weekend, before 10am
        - 'evening': Weekday/weekend, 5pm-10pm
        - 'night': Any day, after 10pm
        - 'weekend': Saturday/Sunday, 10am-5pm
    """
    now = get_current_time()
    hour = now.hour
    weekday = now.weekday()
    
    # Night takes priority (any day)
    if hour >= NIGHT_START or hour < 6:
        return 'night'
    
    # Weekday logic
    if weekday in WORK_DAYS:
        if WORK_START <= hour < WORK_END:
            return 'work'
        elif hour < MORNING_END:
            return 'morning'
        else:
            return 'evening'
    
    # Weekend logic
    else:
        if hour < MORNING_END:
            return 'morning'
        elif hour < EVENING_START:
            return 'weekend'
        else:
            return 'evening'


def should_use_voice(user_sent_voice: bool = False, context: ContextType = None) -> bool:
    """
    Determine if Jarvis should respond with voice.
    
    Rules:
    - Work hours: Never use voice (text only)
    - User sent voice: Always respond with voice
    - Morning/evening: Use voice by default
    - Weekend: Use voice by default
    - Night: Text only (don't wake anyone)
    
    Args:
        user_sent_voice: Did the user send a voice message?
        context: Override context detection (optional)
    
    Returns:
        True if should use voice, False otherwise
    """
    if context is None:
        context = get_current_context()
    
    # User sent voice = always respond with voice (mirror their preference)
    if user_sent_voice:
        return True
    
    # Work hours or night = text only
    if context in ['work', 'night']:
        return False
    
    # Morning, evening, weekend = voice by default
    return True


def get_communication_style(context: ContextType = None) -> Dict[str, any]:
    """
    Get recommended communication style for current context.
    
    Returns:
        Dictionary with:
        - use_voice: bool
        - be_concise: bool
        - greeting_style: str
        - response_length: str ('brief', 'normal', 'detailed')
    """
    if context is None:
        context = get_current_context()
    
    styles = {
        'work': {
            'use_voice': False,
            'be_concise': True,
            'greeting_style': 'minimal',  # "Got it" vs "Good morning Ross!"
            'response_length': 'brief',
            'explanation': 'Work hours - text only, ultra concise'
        },
        'morning': {
            'use_voice': True,
            'be_concise': False,
            'greeting_style': 'warm',  # "Good morning Ross!"
            'response_length': 'normal',
            'explanation': 'Morning - voice + friendly tone'
        },
        'evening': {
            'use_voice': True,
            'be_concise': False,
            'greeting_style': 'casual',
            'response_length': 'normal',
            'explanation': 'Evening - voice + relaxed tone'
        },
        'weekend': {
            'use_voice': True,
            'be_concise': False,
            'greeting_style': 'casual',
            'response_length': 'detailed',
            'explanation': 'Weekend - voice + more detailed responses'
        },
        'night': {
            'use_voice': False,
            'be_concise': True,
            'greeting_style': 'quiet',
            'response_length': 'brief',
            'explanation': 'Late night - text only, brief responses'
        }
    }
    
    return styles.get(context, styles['work'])


def save_context_state(user_sent_voice: bool = False, jarvis_used_voice: bool = False):
    """
    Save current context state to JSON file for tracking/debugging.
    
    Args:
        user_sent_voice: Did user send voice this interaction?
        jarvis_used_voice: Did Jarvis respond with voice?
    """
    now = get_current_time()
    context = get_current_context()
    style = get_communication_style(context)
    
    state = {
        'timestamp': now.isoformat(),
        'context': context,
        'user_sent_voice': user_sent_voice,
        'jarvis_used_voice': jarvis_used_voice,
        'recommended_style': style,
        'hour': now.hour,
        'weekday': now.strftime('%A')
    }
    
    # Ensure directory exists
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Load history if exists
    history = []
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                history = data.get('history', [])
        except (json.JSONDecodeError, KeyError):
            history = []
    
    # Keep last 100 states
    history.append(state)
    history = history[-100:]
    
    # Save with current state + history
    output = {
        'current': state,
        'history': history,
        'last_updated': now.isoformat()
    }
    
    with open(STATE_FILE, 'w') as f:
        json.dump(output, f, indent=2)


def get_context_summary() -> str:
    """
    Get human-readable summary of current context.
    Useful for debugging or showing Ross what's detected.
    """
    now = get_current_time()
    context = get_current_context()
    style = get_communication_style(context)
    
    return f"""🤖 **Smart Context Detection**
📅 {now.strftime('%A, %B %d, %Y')}
⏰ {now.strftime('%I:%M %p %Z')}

**Detected Context:** {context.upper()}
**Use Voice:** {'Yes' if style['use_voice'] else 'No'}
**Style:** {style['response_length'].capitalize()} responses, {style['greeting_style']} greeting
**Reason:** {style['explanation']}
"""


# CLI interface for testing
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--summary':
        print(get_context_summary())
    elif len(sys.argv) > 1 and sys.argv[1] == '--test-voice':
        user_voice = sys.argv[2].lower() == 'true' if len(sys.argv) > 2 else False
        result = should_use_voice(user_sent_voice=user_voice)
        print(f"User sent voice: {user_voice}")
        print(f"Should use voice: {result}")
        print(f"Context: {get_current_context()}")
    else:
        # Default: show current context
        print(get_context_summary())
        
        # Save state
        save_context_state()
        print(f"\n✅ State saved to: {STATE_FILE}")
