#!/usr/bin/env python3
"""
Voice Command Handler

Receives voice messages from Telegram, transcribes them, and executes commands.

Commands:
- "Log workout: [description]"
- "Add win: [description]"  
- "Create task: [description]"
- "Check progress"
- "What's on the list?"
- "Generate tasks"

Uses Whisper API for transcription (or local Whisper if available).
"""

import json
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / "clawd"

def transcribe_voice(audio_file_path):
    """
    Transcribe voice message
    
    TODO: Integrate with Whisper API or local Whisper
    For now, returns mock transcription for testing
    """
    # Mock transcription for testing
    return "Log workout chest day 90 minutes felt great"

def parse_intent(transcription):
    """Parse voice command intent and extract data"""
    
    text_lower = transcription.lower()
    
    if text_lower.startswith("log workout"):
        # Extract workout details
        details = transcription[len("log workout"):].strip().lstrip(":")
        return {
            "command": "log_workout",
            "details": details
        }
    
    elif text_lower.startswith("add win"):
        # Extract win details
        details = transcription[len("add win"):].strip().lstrip(":")
        return {
            "command": "add_win",
            "details": details
        }
    
    elif text_lower.startswith("create task"):
        # Extract task details
        details = transcription[len("create task"):].strip().lstrip(":")
        return {
            "command": "create_task",
            "details": details
        }
    
    elif "check progress" in text_lower:
        return {
            "command": "check_progress"
        }
    
    elif "what" in text_lower and "list" in text_lower:
        return {
            "command": "list_tasks"
        }
    
    elif "generate task" in text_lower:
        return {
            "command": "generate_tasks"
        }
    
    else:
        return {
            "command": "unknown",
            "transcription": transcription
        }

def execute_command(intent):
    """Execute the parsed command"""
    
    command = intent.get("command")
    
    if command == "log_workout":
        # Log workout
        details = intent.get("details", "No details")
        
        # Append to today's memory log
        today = datetime.now().strftime("%Y-%m-%d")
        memory_file = WORKSPACE / "memory" / f"{today}.md"
        
        with open(memory_file, 'a') as f:
            timestamp = datetime.now().strftime("%I:%M%p")
            f.write(f"\n## {timestamp} - Workout (Voice Logged)\n")
            f.write(f"{details}\n")
        
        return {
            "success": True,
            "message": f"✅ Workout logged: {details}",
            "details": details
        }
    
    elif command == "add_win":
        # Log daily win
        details = intent.get("details", "No details")
        
        today = datetime.now().strftime("%Y-%m-%d")
        memory_file = WORKSPACE / "memory" / f"{today}.md"
        
        with open(memory_file, 'a') as f:
            timestamp = datetime.now().strftime("%I:%M%p")
            f.write(f"\n## {timestamp} - Daily Win (Voice Logged)\n")
            f.write(f"🏆 {details}\n")
        
        return {
            "success": True,
            "message": f"🏆 Win logged: {details}",
            "details": details
        }
    
    elif command == "create_task":
        # Add task to queue
        details = intent.get("details", "No details")
        
        task_queue = WORKSPACE / "TASK_QUEUE.md"
        
        with open(task_queue, 'a') as f:
            f.write(f"- [ ] {details} (added via voice)\n")
        
        return {
            "success": True,
            "message": f"✅ Task added: {details}",
            "details": details
        }
    
    elif command == "check_progress":
        # Return progress summary
        return {
            "success": True,
            "message": "📊 Checking progress... (Would show goals, wins, tasks here)",
            "data": {"placeholder": "progress_data"}
        }
    
    elif command == "list_tasks":
        # Return task list
        return {
            "success": True,
            "message": "📋 Fetching task list... (Would list pending tasks here)",
            "data": {"placeholder": "task_list"}
        }
    
    elif command == "generate_tasks":
        # Trigger task generation
        return {
            "success": True,
            "message": "🤖 Generating tasks from goals...",
            "trigger": "task_generation"
        }
    
    else:
        return {
            "success": False,
            "message": f"❓ I didn't understand: '{intent.get('transcription')}'",
            "transcription": intent.get("transcription")
        }

def handle_voice_message(audio_file_path):
    """Main handler for voice messages"""
    
    # 1. Transcribe
    transcription = transcribe_voice(audio_file_path)
    
    # 2. Parse intent
    intent = parse_intent(transcription)
    
    # 3. Execute command
    result = execute_command(intent)
    
    return {
        "transcription": transcription,
        "intent": intent,
        "result": result
    }

def main():
    """Test voice handler"""
    
    # Test with mock audio
    result = handle_voice_message("/path/to/mock/audio.ogg")
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
