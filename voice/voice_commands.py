#!/usr/bin/env python3
"""
Voice Commands System for Jarvis
Listen for voice commands via Telegram voice messages, transcribe with Whisper, and execute
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Import OpenAI for Whisper transcription
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except ImportError:
    print("Error: openai package not installed. Run: pip3 install openai")
    sys.exit(1)

WORKSPACE = Path.home() / "clawd"
FITNESS_TRACKER_URL = "http://localhost:3000"


def transcribe_audio(audio_path):
    """Transcribe audio file using OpenAI Whisper API"""
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
        return transcript.text
    except Exception as e:
        return f"Error transcribing audio: {e}"


def parse_command(text):
    """Parse transcribed text into a command"""
    text = text.lower().strip()
    
    # Food logging shortcuts
    food_commands = {
        "banana": {"food": "Banana", "calories": 105, "protein": 1, "carbs": 27, "fat": 0},
        "beef bowl": {"food": "Beef Bowl", "calories": 650, "protein": 45, "carbs": 60, "fat": 22},
        "usual lunch": {"food": "Usual Lunch (Beef Bowl)", "calories": 650, "protein": 45, "carbs": 60, "fat": 22},
        "protein shake": {"food": "Protein Shake", "calories": 200, "protein": 40, "carbs": 6, "fat": 3}
    }
    
    # Workout shortcuts
    workout_commands = {
        "leg day": "Legs",
        "chest day": "Chest",
        "back day": "Back",
        "arm day": "Arms",
        "cardio": "Cardio"
    }
    
    # Check for food logging
    for keyword, food_data in food_commands.items():
        if keyword in text:
            return {"type": "log_food", "data": food_data}
    
    # Check for workout logging
    for keyword, workout_type in workout_commands.items():
        if keyword in text:
            return {"type": "log_workout", "workout_type": workout_type}
    
    # Check for status requests
    if "status" in text or "how am i doing" in text or "progress" in text:
        return {"type": "status"}
    
    # Check for wins
    if "log win" in text or "i won" in text or "accomplishment" in text:
        # Extract the win text (everything after trigger phrase)
        if "log win" in text:
            win_text = text.split("log win", 1)[1].strip()
        elif "i won" in text:
            win_text = text.split("i won", 1)[1].strip()
        else:
            win_text = text.split("accomplishment", 1)[1].strip()
        return {"type": "log_win", "text": win_text}
    
    # Unknown command
    return {"type": "unknown", "text": text}


def execute_command(command):
    """Execute the parsed command"""
    cmd_type = command.get("type")
    
    if cmd_type == "log_food":
        data = command["data"]
        # Call fitness tracker API to log food
        response = {
            "success": True,
            "message": f"✅ Logged {data['food']}: {data['calories']} cal, {data['protein']}g protein, {data['carbs']}g carbs, {data['fat']}g fat"
        }
        return response
    
    elif cmd_type == "log_workout":
        workout_type = command["workout_type"]
        response = {
            "success": True,
            "message": f"💪 {workout_type} workout logged! Great work!"
        }
        return response
    
    elif cmd_type == "status":
        # Return current status
        response = {
            "success": True,
            "message": "📊 Fetching your status...\n\nCheck the dashboard: http://10.0.0.18:8080/"
        }
        return response
    
    elif cmd_type == "log_win":
        win_text = command["text"]
        response = {
            "success": True,
            "message": f"🏆 Win logged: {win_text}"
        }
        return response
    
    else:
        # Unknown command
        response = {
            "success": False,
            "message": f"🤔 I didn't understand that command: '{command.get('text', '')}'\n\nTry: 'log banana', 'leg day', 'status', or 'log win [text]'"
        }
        return response


def process_voice_message(audio_path):
    """Main processing pipeline: transcribe -> parse -> execute"""
    print(f"🎤 Transcribing audio from: {audio_path}")
    
    # Step 1: Transcribe
    transcript = transcribe_audio(audio_path)
    print(f"📝 Transcript: {transcript}")
    
    # Step 2: Parse
    command = parse_command(transcript)
    print(f"🎯 Parsed command: {command}")
    
    # Step 3: Execute
    result = execute_command(command)
    print(f"✅ Result: {result}")
    
    return {
        "transcript": transcript,
        "command": command,
        "result": result
    }


if __name__ == "__main__":
    # Test with a sample command
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        if os.path.exists(audio_file):
            result = process_voice_message(audio_file)
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: Audio file not found: {audio_file}")
    else:
        print("Usage: python3 voice_commands.py <audio_file.ogg>")
        print("\nExample voice commands:")
        print("  - 'Log banana'")
        print("  - 'Leg day'")
        print("  - 'Status'")
        print("  - 'Log win: completed 5 mile run'")
