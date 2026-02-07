#!/usr/bin/env python3
"""
Jarvis Voice System - Text-to-Speech using OpenAI TTS
"""

import os
import sys
from pathlib import Path
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Voice options: alloy, echo, fable, onyx, nova, shimmer
JARVIS_VOICE = "onyx"  # Deep, authoritative voice

def text_to_speech(text, output_path=None, voice=JARVIS_VOICE):
    """
    Convert text to speech using OpenAI TTS
    
    Args:
        text: Text to convert to speech
        output_path: Where to save the audio file (defaults to /tmp)
        voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
    
    Returns:
        Path to the generated audio file
    """
    if output_path is None:
        output_path = f"/tmp/jarvis_voice_{hash(text) % 10000}.mp3"
    
    try:
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice=voice,
            input=text
        ) as response:
            response.stream_to_file(output_path)
        
        return {
            'success': True,
            'audio_path': output_path,
            'text': text,
            'voice': voice
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def speak(text, voice=JARVIS_VOICE, play=True):
    """
    Generate speech and optionally play it immediately
    
    Args:
        text: Text to speak
        voice: Voice to use
        play: Whether to play the audio immediately (macOS only)
    
    Returns:
        Result dict with audio_path
    """
    result = text_to_speech(text, voice=voice)
    
    if result['success'] and play:
        # Play audio on macOS
        audio_path = result['audio_path']
        os.system(f'afplay "{audio_path}"')
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: jarvis_voice.py <text> [voice] [--no-play]")
        print("Voices: alloy, echo, fable, onyx, nova, shimmer")
        sys.exit(1)
    
    text = sys.argv[1]
    voice = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else JARVIS_VOICE
    play = '--no-play' not in sys.argv
    
    result = speak(text, voice=voice, play=play)
    
    if result['success']:
        print(f"✅ Audio generated: {result['audio_path']}")
        if play:
            print("🔊 Playing audio...")
    else:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)

if __name__ == '__main__':
    main()
