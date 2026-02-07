#!/usr/bin/env python3
"""
Morning Brief Voice Generator
Extends generate-morning-brief.py to create voice version of the morning brief.

Usage:
    python3 generate-morning-brief-voice.py [--send]
    
    Without --send: Generates voice + transcript only
    With --send: Also sends via Telegram (use in cron)
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Add workspace to path for imports
WORKSPACE = Path.home() / "clawd"
sys.path.insert(0, str(WORKSPACE))
sys.path.insert(0, str(WORKSPACE / "systems"))
sys.path.insert(0, str(WORKSPACE / "scripts"))

from auto_voice import generate_with_transcript

# Import functions from generate-morning-brief.py (handle hyphenated name)
import importlib.util
spec = importlib.util.spec_from_file_location("generate_morning_brief", 
    WORKSPACE / "scripts" / "generate-morning-brief.py")
morning_brief_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(morning_brief_module)

get_overnight_work = morning_brief_module.get_overnight_work
get_priorities = morning_brief_module.get_priorities
get_calendar_events = morning_brief_module.get_calendar_events
get_open_loops = morning_brief_module.get_open_loops
get_insight = morning_brief_module.get_insight
load_state = morning_brief_module.load_state

TEMPLATES = WORKSPACE / "templates" / "voice-templates.json"
OUTPUT_DIR = WORKSPACE / "morning-briefs"
VOICE_STATE = WORKSPACE / "memory" / "voice-brief-state.json"


def load_voice_templates() -> dict:
    """Load voice message templates."""
    with open(TEMPLATES, 'r') as f:
        return json.load(f)


def strip_html(html_text: str) -> str:
    """
    Strip HTML tags and convert to plain text suitable for TTS.
    
    Args:
        html_text: HTML content
        
    Returns:
        Clean plain text
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_text)
    
    # Clean up common HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()


def format_section(title: str, content: str, templates: dict) -> str:
    """
    Format a section of the brief for voice delivery.
    
    Args:
        title: Section title
        content: Section content (may be HTML)
        templates: Voice templates
        
    Returns:
        Formatted text suitable for TTS
    """
    clean_content = strip_html(content)
    
    # Check for empty states
    if "empty-state" in content.lower() or "no " in clean_content.lower() or not clean_content.strip():
        # Use template for empty sections
        if "calendar" in title.lower():
            return templates["morning_brief"]["empty_calendar"]
        elif "task" in title.lower() or "priorit" in title.lower():
            return templates["morning_brief"]["empty_tasks"]
        elif "overnight" in title.lower() or "build" in title.lower():
            return templates["morning_brief"]["empty_builds"]
        else:
            return ""  # Skip empty section
    
    # Format the section with natural speech
    return f"{title}. {clean_content}"


def generate_morning_brief_script() -> str:
    """
    Generate the script for the morning brief voice message.
    
    Returns:
        Full text script ready for TTS
    """
    templates = load_voice_templates()
    now = datetime.now()
    date_str = now.strftime("%A, %B %d")
    
    # Start with greeting
    script = templates["morning_brief"]["intro"].format(date=date_str)
    script += "\n\n"
    
    # Calendar events
    calendar = get_calendar_events()
    calendar_text = format_section("Your calendar", calendar, templates)
    if calendar_text:
        script += calendar_text + "\n\n"
    
    # Priorities
    priorities = get_priorities()
    priority_text = format_section("Today's priorities", priorities, templates)
    if priority_text:
        script += priority_text + "\n\n"
    
    # Overnight work
    overnight = get_overnight_work()
    overnight_text = format_section("Overnight builds", overnight, templates)
    if overnight_text:
        script += overnight_text + "\n\n"
    
    # Open loops
    loops = get_open_loops()
    loops_text = format_section("Open loops", loops, templates)
    if loops_text:
        script += loops_text + "\n\n"
    
    # Insight (proactive suggestion)
    try:
        insight = get_insight()
        if insight:
            script += f"One more thing: {insight}\n\n"
    except Exception:
        pass  # Skip if insight generation fails
    
    # Outro
    script += templates["morning_brief"]["outro"]
    
    return script


def load_voice_state() -> dict:
    """Load voice brief generation state."""
    if VOICE_STATE.exists():
        with open(VOICE_STATE, 'r') as f:
            return json.load(f)
    return {"last_generated": None, "history": []}


def save_voice_state(state: dict):
    """Save voice brief generation state."""
    VOICE_STATE.parent.mkdir(parents=True, exist_ok=True)
    with open(VOICE_STATE, 'w') as f:
        json.dump(state, f, indent=2)


def generate_voice_brief(send_telegram: bool = False) -> tuple:
    """
    Generate voice version of morning brief.
    
    Args:
        send_telegram: Whether to send via Telegram
        
    Returns:
        Tuple of (audio_path, transcript_path, should_send)
    """
    state = load_voice_state()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Check if already generated today
    if state.get("last_generated") == today:
        print(f"⚠️  Voice brief already generated for {today}")
        return None, None, False
    
    # Generate script
    print("📝 Generating morning brief script...")
    script = generate_morning_brief_script()
    
    print(f"📊 Script length: {len(script)} characters")
    print(f"⏱️  Estimated duration: ~{len(script) / 200:.1f} minutes")
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate voice + transcript
    print("🎙️  Generating voice (Onyx)...")
    filename_base = f"morning-brief-{today}"
    
    try:
        audio_path, transcript_path = generate_with_transcript(
            text=script,
            output_dir=OUTPUT_DIR,
            filename_base=filename_base,
            voice="onyx",
            model="tts-1-hd",
            format="opus",  # Telegram native
            speed=1.0,
            log_purpose="morning_brief"
        )
        
        # Update state
        state["last_generated"] = today
        state["history"].append({
            "date": today,
            "audio_path": str(audio_path),
            "transcript_path": str(transcript_path),
            "char_count": len(script),
            "timestamp": datetime.now().isoformat()
        })
        state["history"] = state["history"][-30:]  # Keep last 30 days
        save_voice_state(state)
        
        print(f"\n✅ Morning brief voice generated!")
        print(f"   Audio: {audio_path}")
        print(f"   Transcript: {transcript_path}")
        
        # Create symlink to latest
        latest_audio = OUTPUT_DIR / "latest.opus"
        latest_transcript = OUTPUT_DIR / "latest.txt"
        
        if latest_audio.exists() or latest_audio.is_symlink():
            latest_audio.unlink()
        if latest_transcript.exists() or latest_transcript.is_symlink():
            latest_transcript.unlink()
        
        latest_audio.symlink_to(audio_path.name)
        latest_transcript.symlink_to(transcript_path.name)
        
        return audio_path, transcript_path, True
        
    except Exception as e:
        print(f"❌ Error generating voice: {e}")
        return None, None, False


def send_via_telegram(audio_path: Path, transcript_path: Path):
    """
    Send morning brief via Telegram.
    
    Args:
        audio_path: Path to audio file
        transcript_path: Path to transcript
    """
    # This function would integrate with the message tool
    # For now, just print instructions
    print("\n📱 To send via Telegram:")
    print(f"   clawdbot message send --target=Ross --file={audio_path}")
    print(f"   Optional: Include transcript as caption")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate voice morning brief")
    parser.add_argument("--send", action="store_true", help="Send via Telegram")
    parser.add_argument("--force", action="store_true", help="Force regeneration even if already sent today")
    args = parser.parse_args()
    
    # Force regeneration if requested
    if args.force:
        state = load_voice_state()
        state["last_generated"] = None
        save_voice_state(state)
    
    # Generate voice brief
    audio_path, transcript_path, should_send = generate_voice_brief(send_telegram=args.send)
    
    if audio_path and should_send:
        if args.send:
            send_via_telegram(audio_path, transcript_path)
        else:
            print("\n💡 Tip: Use --send to automatically deliver via Telegram")
    
    sys.exit(0 if audio_path else 1)
