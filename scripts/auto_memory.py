#!/usr/bin/env python3
"""
Automatic Memory System - Pre-query and real-time logging
Runs BEFORE Jarvis responds and AFTER significant exchanges
"""

import json
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_DIR = Path.home() / "clawd" / "memory"
STATE_FILE = MEMORY_DIR / "auto_memory_state.json"

def load_state():
    """Load memory state"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "last_recall_query": None,
        "last_log_time": None,
        "conversation_thread": []
    }

def save_state(state):
    """Save memory state"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def pre_query(user_message):
    """
    Run BEFORE responding to user
    Searches memory and surfaces relevant context
    """
    print("🧠 Running automatic memory recall...")
    
    # 1. Search instant recall
    result = subprocess.run(
        ['python3', str(Path.home() / 'clawd/scripts/instant_recall.py'), user_message],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    relevant_memories = []
    if result.returncode == 0:
        # Parse output for relevant snippets
        lines = result.stdout.split('\n')
        for i, line in enumerate(lines):
            if 'score:' in line or 'relevance:' in line:
                # Capture context around scored items
                context = '\n'.join(lines[max(0, i-2):min(len(lines), i+5)])
                relevant_memories.append(context)
    
    # 2. Load recent memory files
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    recent_context = []
    for date in [today, yesterday]:
        log_file = MEMORY_DIR / f"{date}.md"
        if log_file.exists():
            with open(log_file) as f:
                content = f.read()
                # Extract relevant sections
                if any(keyword in user_message.lower() for keyword in ['fittrack', 'fitness', 'tracker', 'voice', 'logging']):
                    recent_context.append(f"## From {date}:\n{content[:500]}...")
    
    # 3. Check for project mentions
    projects = ['fittrack', 'fitness-tracker', 'golf', 'dashboard']
    mentioned_projects = [p for p in projects if p in user_message.lower()]
    
    # Generate context summary
    context = {
        "relevant_memories": relevant_memories[:3],  # Top 3
        "recent_context": recent_context,
        "mentioned_projects": mentioned_projects,
        "timestamp": datetime.now().isoformat()
    }
    
    # Update state
    state = load_state()
    state['last_recall_query'] = user_message
    state['conversation_thread'].append({
        "message": user_message,
        "timestamp": datetime.now().isoformat(),
        "context_found": len(relevant_memories) + len(recent_context)
    })
    save_state(state)
    
    # Output for Jarvis to see
    print(json.dumps(context, indent=2))
    return context

def post_log(exchange_summary):
    """
    Run AFTER response
    Logs significant details in real-time
    """
    print("📝 Logging conversation to memory...")
    
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = MEMORY_DIR / f"{today}.md"
    
    timestamp = datetime.now().strftime('%H:%M')
    
    # Append to today's log
    entry = f"\n## {timestamp} - {exchange_summary['type']}\n{exchange_summary['content']}\n"
    
    with open(log_file, 'a') as f:
        f.write(entry)
    
    print(f"✅ Logged to {log_file}")
    
    # Update memory index
    subprocess.run(
        ['python3', str(Path.home() / 'clawd/scripts/persistent_memory.py'), '--update'],
        capture_output=True,
        timeout=30
    )
    
    print("✅ Memory index updated")

def main():
    if len(sys.argv) < 2:
        print("Usage: auto_memory.py [pre|post] <data>")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "pre":
        # Pre-query mode
        user_message = sys.argv[2] if len(sys.argv) > 2 else ""
        pre_query(user_message)
    
    elif mode == "post":
        # Post-logging mode
        exchange_data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        post_log(exchange_data)
    
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)

if __name__ == '__main__':
    main()
