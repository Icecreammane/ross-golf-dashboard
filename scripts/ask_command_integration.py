#!/usr/bin/env python3
"""
Integration helper for /ask command in Clawdbot main agent.

This file provides a simple wrapper that the main agent can call when
it detects a /ask command in Telegram.

Usage in agent:
    from scripts.ask_command_integration import process_ask_command
    
    if message.startswith('/ask'):
        response = process_ask_command(message)
        reply(response)
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path.home() / "clawd" / "scripts"))

from ask_command import handle_ask_command


def process_ask_command(message_text):
    """
    Process /ask command from Telegram message
    
    Args:
        message_text: Full message text including "/ask"
    
    Returns:
        Formatted response string ready to send
    """
    # Strip /ask prefix
    question = message_text.replace('/ask', '', 1).strip()
    
    if not question:
        return """❓ **Usage:** `/ask [your question]`

**Examples:**
• `/ask Which of these 3 opportunities should I pursue?`
• `/ask Should I focus on quick wins or long-term projects?`
• `/ask What's the best ROI option right now?`

💡 I'll analyze based on conversion rates, revenue potential, and effort required."""
    
    # Process with main handler
    try:
        response = handle_ask_command(question)
        return response
    except Exception as e:
        return f"❌ Error processing request: {str(e)}\n\nTry: `python3 ~/clawd/scripts/test_ask_command.py` to diagnose."


# For testing
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Test /ask integration:")
        print("  python3 ask_command_integration.py '/ask Which opportunity?'")
        sys.exit(0)
    
    message = " ".join(sys.argv[1:])
    response = process_ask_command(message)
    print(response)
