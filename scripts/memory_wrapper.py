#!/usr/bin/env python3
"""
Memory Wrapper - Intercepts messages and ensures memory is checked
This runs as middleware between user message and Jarvis response
"""

import sys
import json
import subprocess
from pathlib import Path

def process_message(user_message):
    """
    Process incoming message with automatic memory recall
    """
    print(f"🔄 Processing message: {user_message[:50]}...")
    
    # Run pre-query
    result = subprocess.run(
        ['python3', str(Path.home() / 'clawd/scripts/auto_memory.py'), 'pre', user_message],
        capture_output=True,
        text=True,
        timeout=15
    )
    
    if result.returncode == 0:
        print("✅ Memory context loaded")
        context = json.loads(result.stdout.split('\n')[-2])  # Get JSON output
        
        # Format context for Jarvis
        context_summary = []
        
        if context['relevant_memories']:
            context_summary.append("📚 Relevant past context:")
            for mem in context['relevant_memories'][:2]:
                context_summary.append(f"  • {mem[:100]}...")
        
        if context['mentioned_projects']:
            context_summary.append(f"🎯 Projects mentioned: {', '.join(context['mentioned_projects'])}")
        
        if context_summary:
            print("\n" + "\n".join(context_summary))
        
        return context
    else:
        print("⚠️  Memory recall failed")
        return None

def log_exchange(user_message, jarvis_response, metadata=None):
    """
    Log the exchange immediately after response
    """
    # Extract key info
    exchange = {
        "type": "Conversation",
        "content": f"**User:** {user_message}\n\n**Jarvis:** {jarvis_response[:200]}..."
    }
    
    # Detect significant events
    if any(word in jarvis_response.lower() for word in ['built', 'shipped', 'created', 'added']):
        exchange['type'] = "Build/Feature"
    elif any(word in jarvis_response.lower() for word in ['decision', 'chose', 'decided']):
        exchange['type'] = "Decision"
    
    # Log it
    subprocess.run(
        ['python3', str(Path.home() / 'clawd/scripts/auto_memory.py'), 'post', json.dumps(exchange)],
        timeout=15
    )

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: memory_wrapper.py <message>")
        sys.exit(1)
    
    message = sys.argv[1]
    process_message(message)
