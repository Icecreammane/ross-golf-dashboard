#!/usr/bin/env python3
"""
Future Ross Voice Messages

Generates voice messages from future versions of Ross using TTS.
"Yo current Ross, this is 2027 Ross. You made it bro."

Uses OpenAI TTS (Onyx voice - Ross's preference from jarvis_voice.py)
"""

import json
import urllib.request
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / "clawd"
TIMELINES_FILE = WORKSPACE / "multiverse" / "timelines.json"
VOICES_DIR = WORKSPACE / "multiverse" / "voices"
OLLAMA_URL = "http://localhost:11434/api/generate"

VOICES_DIR.mkdir(parents=True, exist_ok=True)

def call_local_ai(prompt, temperature=0.8):
    """Generate message content with local AI"""
    try:
        data = json.dumps({
            "model": "qwen2.5:14b",
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(
            OLLAMA_URL,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response")
    except Exception as e:
        print(f"AI error: {e}")
        return None

def generate_voice_message(timeline_type, timepoint, prediction_data):
    """
    Generate a voice message from future Ross
    
    timeline_type: current_pace, optimized, beast_mode, etc.
    timepoint: 1_year, 5_years, etc.
    prediction_data: the actual prediction dict
    """
    
    time_labels = {
        "1_month": "1 month",
        "3_months": "3 months",
        "6_months": "6 months",
        "1_year": "1 year",
        "2_years": "2 years",
        "5_years": "5 years",
        "10_years": "10 years"
    }
    
    time_label = time_labels.get(timepoint, timepoint)
    income = prediction_data.get('side_income', 0)
    situation = prediction_data.get('life_situation', '')
    achievements = prediction_data.get('achievements', [])
    happiness = prediction_data.get('happiness', 0)
    regret = prediction_data.get('regret_level', 0)
    
    timeline_names = {
        "current_pace": "keeping the same pace",
        "optimized": "following all the AI recommendations",
        "beast_mode": "going ALL IN",
        "chaos": "quitting your job and forcing yourself to make it",
        "safe": "playing it safe"
    }
    
    path_description = timeline_names.get(timeline_type, "this path")
    
    prompt = f"""You are Ross from {time_label} in the future, sending a voice message to current Ross (February 2026).

YOUR FUTURE STATE ({time_label} from now, {path_description.upper()} timeline):
- Making ${income}/month from freelancing/business
- Life situation: {situation}
- Achievements: {', '.join(achievements) if achievements else 'steady progress'}
- Happiness: {happiness}/100
- Regret level: {regret}/100

Write a 30-60 second voice message to current Ross. Be REAL and specific:
- Reference actual numbers (${income}/month)
- Mention specific achievements
- Give advice based on what you learned
- Be encouraging but honest about challenges
- Sound like Ross (direct, real, action-oriented)
- End with something motivating

Make it conversational - this is a voice message, not an essay. Use "yo", "bro", contractions, etc.

IMPORTANT: Just write the message text, no labels or formatting."""

    print(f"  🎤 Generating message: {timeline_type} / {time_label}...")
    
    message = call_local_ai(prompt, temperature=0.8)
    
    if message:
        # Clean up any formatting the AI added
        message = message.strip().replace('"', '').replace("'", "")
        # Remove any "Future Ross:" or similar labels
        if ':' in message[:30]:
            message = message.split(':', 1)[1].strip()
        
        return message
    
    return None

def generate_all_voice_messages():
    """Generate voice messages from all timeline/timepoint combinations"""
    
    print("="*70)
    print("🎤 FUTURE ROSS VOICE MESSAGES")
    print("="*70)
    print("\nGenerating voice messages from your future selves...\n")
    
    # Load timelines
    if not TIMELINES_FILE.exists():
        print("❌ Timelines not generated yet")
        print("   Run: python3 ~/clawd/scripts/timeline_generator.py")
        return
    
    with open(TIMELINES_FILE) as f:
        data = json.load(f)
    
    timelines = data.get('timelines', {})
    
    all_messages = {}
    
    # Generate messages for key timepoints
    key_timepoints = ['1_year', '5_years', '10_years']
    
    for timeline_id, timeline_data in timelines.items():
        timeline_name = timeline_data.get('name', timeline_id)
        predictions = timeline_data.get('predictions', [])
        
        print(f"\n{timeline_name} Timeline:")
        
        timeline_messages = {}
        
        for pred in predictions:
            timepoint = pred.get('timepoint')
            if timepoint in key_timepoints:
                message = generate_voice_message(timeline_id, timepoint, pred)
                if message:
                    timeline_messages[timepoint] = {
                        "text": message,
                        "income": pred.get('side_income', 0),
                        "happiness": pred.get('happiness', 0),
                        "generated_at": datetime.now().isoformat()
                    }
                    print(f"  ✅ {timepoint.replace('_', ' ')}")
                    print(f"     Preview: {message[:80]}...")
        
        all_messages[timeline_id] = timeline_messages
    
    # Save all messages
    output_file = VOICES_DIR / "messages.json"
    with open(output_file, 'w') as f:
        json.dump(all_messages, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✅ VOICE MESSAGES GENERATED")
    print(f"{'='*70}")
    print(f"\n💾 Saved to: {output_file}")
    print(f"\n📝 Generated {sum(len(m) for m in all_messages.values())} messages")
    print("\n🎤 To hear them, you'd need OpenAI TTS API")
    print("   (Text versions saved and ready to display)")
    
    return all_messages

def show_message(timeline, timepoint):
    """Display a specific voice message"""
    
    messages_file = VOICES_DIR / "messages.json"
    if not messages_file.exists():
        print("No messages generated yet")
        return
    
    with open(messages_file) as f:
        all_messages = json.load(f)
    
    timeline_messages = all_messages.get(timeline, {})
    message_data = timeline_messages.get(timepoint)
    
    if message_data:
        print("\n" + "="*70)
        print(f"🎤 MESSAGE FROM FUTURE ROSS ({timepoint.replace('_', ' ')})")
        print("="*70)
        print(f"\n{message_data['text']}\n")
        print("="*70)
        print(f"(From {timeline} timeline, making ${message_data['income']}/month)")
    else:
        print(f"No message for {timeline} / {timepoint}")

def main():
    """CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Future Ross Voice Messages")
        print("\nCommands:")
        print("  generate              - Generate all voice messages")
        print("  show <timeline> <time> - Show specific message")
        print("\nExamples:")
        print("  generate")
        print("  show beast_mode 5_years")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "generate":
        generate_all_voice_messages()
    
    elif command == "show":
        if len(sys.argv) < 4:
            print("Usage: show <timeline> <timepoint>")
            print("\nTimelines: current_pace, optimized, beast_mode, chaos, safe")
            print("Timepoints: 1_year, 5_years, 10_years")
        else:
            timeline = sys.argv[2]
            timepoint = sys.argv[3]
            show_message(timeline, timepoint)
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
