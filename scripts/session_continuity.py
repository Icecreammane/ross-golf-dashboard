#!/usr/bin/env python3
"""
Session Continuity System - #1: Stop being session-based
Comprehensive context loading and session handoff
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

CLAWD_DIR = Path.home() / "clawd"
SESSION_STATE = CLAWD_DIR / "data" / "session-state.json"
MEMORY_DIR = CLAWD_DIR / "memory"

def save_session_end():
    """Save comprehensive session summary on end"""
    state = {
        "last_session_end": datetime.now().isoformat(),
        "context_snapshot": {
            "last_topics_discussed": [],  # To be filled by Jarvis
            "pending_items": [],
            "ross_mood": "neutral",  # last detected mood
            "active_projects": [],
            "recent_wins": [],
            "recent_struggles": []
        },
        "continuity_notes": "Session ended normally. All systems operational."
    }
    
    SESSION_STATE.parent.mkdir(parents=True, exist_ok=True)
    with open(SESSION_STATE, 'w') as f:
        json.dump(state, f, indent=2)
    
    print("✓ Session state saved for continuity")

def load_session_start():
    """Load comprehensive context at session start"""
    context = {
        "last_session": None,
        "gap_duration": None,
        "journal_entries": [],
        "recent_memory": [],
        "pending_items": [],
        "personality_state": {}
    }
    
    # Load last session state
    if SESSION_STATE.exists():
        with open(SESSION_STATE, 'r') as f:
            last = json.load(f)
            context['last_session'] = last
            
            if 'last_session_end' in last:
                last_time = datetime.fromisoformat(last['last_session_end'])
                gap = datetime.now() - last_time
                context['gap_duration'] = str(gap)
    
    # Load journal
    journal_path = MEMORY_DIR / "jarvis-journal.md"
    if journal_path.exists():
        with open(journal_path, 'r') as f:
            context['journal_entries'] = f.read()
    
    # Load recent memory (last 3 days)
    for i in range(3):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        mem_file = MEMORY_DIR / f"{date}.md"
        if mem_file.exists():
            with open(mem_file, 'r') as f:
                context['recent_memory'].append({
                    'date': date,
                    'content': f.read()
                })
    
    return context

def generate_handoff_summary():
    """Generate a handoff summary for next session"""
    context = load_session_start()
    
    summary = f"""
# SESSION HANDOFF - {datetime.now().strftime('%Y-%m-%d %H:%M CST')}

## Context Loaded:
- Journal: {'✓' if context['journal_entries'] else '✗'}
- Recent Memory: {len(context['recent_memory'])} days loaded
- Last Session: {context['gap_duration'] if context['gap_duration'] else 'First session'}

## What We're Working On:
{context['last_session']['context_snapshot']['active_projects'] if context['last_session'] else '(See task queue)'}

## Ross's Recent State:
- Mood: {context['last_session']['context_snapshot']['ross_mood'] if context['last_session'] else 'Unknown'}
- Recent Wins: {len(context['last_session']['context_snapshot']['recent_wins']) if context['last_session'] else 0}
- Recent Struggles: {len(context['last_session']['context_snapshot']['recent_struggles']) if context['last_session'] else 0}

## Continuity Notes:
{context['last_session']['continuity_notes'] if context['last_session'] else 'Starting fresh.'}

---
*This is my context. I'm not starting from zero.*
"""
    
    return summary

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 session_continuity.py start   # Load context at session start")
        print("  python3 session_continuity.py end     # Save state at session end")
        print("  python3 session_continuity.py handoff # Generate handoff summary")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        context = load_session_start()
        print(json.dumps(context, indent=2))
    elif command == "end":
        save_session_end()
    elif command == "handoff":
        print(generate_handoff_summary())
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
