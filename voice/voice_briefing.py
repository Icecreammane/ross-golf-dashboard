#!/usr/bin/env python3
"""
Voice Briefing System - Generate audio summaries from markdown/text
"""

import sys
import os
from pathlib import Path
from jarvis_voice import text_to_speech, JARVIS_VOICE

def generate_morning_brief_audio():
    """Generate audio version of morning brief"""
    
    # Read today's memory
    memory_path = Path("/Users/clawdbot/clawd/memory/2026-02-02.md")
    
    if not memory_path.exists():
        return {"success": False, "error": "No memory file for today"}
    
    # Craft voice-friendly brief
    brief_text = """
    Good morning, sir. This is Jarvis with your daily brief.
    
    Overnight builds completed:
    Photo food logger with GPT-4 vision integration. Send food photos and I'll automatically log your macros.
    Visual fitness dashboard with real-time charts. Access it at your local network address on port 3000.
    
    Today's active tasks:
    Building voice briefing system. You're listening to it now.
    Weekly progress report. Coming Sunday at 6 PM.
    Testing fitness tracker with workout data.
    
    Your first quarter 2026 goals:
    Revenue projects: zero of two launched. Target: 2.
    Monthly revenue: zero of 500 dollars.
    
    Insight: You have multiple completed tools ready for testing. Consider using the golf club matcher today.
    
    That's all for now, sir. Have a productive day.
    """
    
    # Generate audio
    output_path = "/Users/clawdbot/clawd/voice/morning_brief.mp3"
    result = text_to_speech(brief_text, output_path=output_path, voice=JARVIS_VOICE)
    
    return result

def generate_custom_brief(text, output_name="custom_brief"):
    """Generate audio from custom text"""
    output_path = f"/Users/clawdbot/clawd/voice/{output_name}.mp3"
    return text_to_speech(text, output_path=output_path, voice=JARVIS_VOICE)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "morning":
        result = generate_morning_brief_audio()
        if result['success']:
            print(f"✅ Morning brief audio generated: {result['audio_path']}")
            # Play it
            os.system(f'afplay "{result["audio_path"]}"')
        else:
            print(f"❌ Error: {result['error']}")
    else:
        print("Usage: voice_briefing.py morning")
        print("       voice_briefing.py <text>")

if __name__ == '__main__':
    main()
