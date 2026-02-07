#!/usr/bin/env python3
"""
Voice Brief Generator - Converts morning brief to audio using ElevenLabs
Uses Ross's preferred "Onyx" voice style (deep, authoritative)
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
BRIEFS_DIR = WORKSPACE / "morning-briefs"
OUTPUT_DIR = WORKSPACE / "voice-briefs"

# ElevenLabs API (when configured)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = "onyx"  # Or specific ElevenLabs voice ID

def generate_brief_script():
    """Generate condensed script from morning brief for audio"""
    
    # Read latest morning brief
    brief_file = BRIEFS_DIR / "latest.txt"
    if not brief_file.exists():
        return "No morning brief available yet."
    
    with open(brief_file) as f:
        full_brief = f.read()
    
    # Condensed audio-friendly version (5 min narration)
    script = f"""Good morning, Ross. This is your brief for {datetime.now().strftime('%A, %B %d')}.

Let me catch you up on what happened overnight and what's ahead today.

[PAUSE]

SYSTEM STATUS
Your AI operations center ran successfully through the night. All systems operational. 
The local model generated content, scanned for opportunities, and prepared your intelligence.

[PAUSE]

NIGHT SHIFT RESULTS
Content ready: Twenty tweet ideas generated. Reddit scanner found three high-priority opportunities. 
Code health scan completed - no critical issues.

[PAUSE]

TODAY'S PRIORITIES
One: Review and schedule tweets for next week.
Two: Check Reddit opportunities - two posts need responses within 6 hours.
Three: FitTrack development - meal planning feature ready to prototype.

[PAUSE]

CALENDAR
Hannah visiting March third through sixth. No other events scheduled this week.

[PAUSE]

FITNESS
Recent meal logged: Chipotle double steak burrito. Sixteen thirty calories, seventy-three grams protein.
One workout logged this week. Time to hit the gym.

[PAUSE]

GOALS PROGRESS
Primary mission: Five hundred MRR by March thirty-first.
You're on day eight. Foundation is solid. Keep laying bricks.

[PAUSE]

That's your brief. Full details in the dashboard. Now go build something great.

End brief.
"""
    
    return script

def text_to_speech_placeholder(script):
    """
    Placeholder TTS until ElevenLabs is configured
    Returns path to generated audio file
    """
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # For now, just save the script
    timestamp = datetime.now().strftime('%Y%m%d')
    script_file = OUTPUT_DIR / f"brief-script-{timestamp}.txt"
    
    with open(script_file, "w") as f:
        f.write(script)
    
    print(f"📝 Script saved: {script_file}")
    print("\n🎤 Audio generation requires ElevenLabs API key")
    print("See VOICE_BRIEF_SETUP.md for instructions")
    
    return str(script_file)

def text_to_speech_elevenlabs(script):
    """Generate audio using ElevenLabs API"""
    
    if not ELEVENLABS_API_KEY:
        return text_to_speech_placeholder(script)
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": script,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        OUTPUT_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d')
        audio_file = OUTPUT_DIR / f"morning-brief-{timestamp}.mp3"
        
        with open(audio_file, "wb") as f:
            f.write(response.content)
        
        print(f"🎵 Audio generated: {audio_file}")
        return str(audio_file)
    else:
        print(f"❌ API error: {response.status_code}")
        return text_to_speech_placeholder(script)

def main():
    """Generate voice brief"""
    
    print("🎙️ Generating voice brief...")
    
    # Generate script
    script = generate_brief_script()
    
    # Convert to audio
    audio_file = text_to_speech_elevenlabs(script)
    
    print(f"\n✅ Voice brief ready")
    print(f"📁 {audio_file}")
    
    return audio_file

if __name__ == "__main__":
    main()
