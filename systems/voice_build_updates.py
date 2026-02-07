#!/usr/bin/env python3
"""
Voice Build Update Generator
Monitors build completions and generates voice summaries for major milestones.

Usage:
    # Check for updates and generate voice notifications
    python3 voice-build-updates.py
    
    # Run in cron (checks every 15 min, respects work hours)
    */15 * * * * cd ~/clawd && python3 systems/voice-build-updates.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Add workspace to path
WORKSPACE = Path.home() / "clawd"
sys.path.insert(0, str(WORKSPACE / "systems"))

from auto_voice import generate_with_transcript
from smart_context import get_current_context, should_use_voice

BUILD_STATUS = WORKSPACE / "logs" / "build-status.json"
VOICE_TEMPLATES = WORKSPACE / "templates" / "voice-templates.json"
NOTIFICATION_STATE = WORKSPACE / "memory" / "build-voice-notifications.json"
OUTPUT_DIR = WORKSPACE / "build-notifications"


def load_templates() -> dict:
    """Load voice message templates."""
    with open(VOICE_TEMPLATES, 'r') as f:
        return json.load(f)


def load_notification_state() -> dict:
    """Load notification state to avoid duplicates."""
    if NOTIFICATION_STATE.exists():
        with open(NOTIFICATION_STATE, 'r') as f:
            return json.load(f)
    return {"notified_builds": [], "last_check": None}


def save_notification_state(state: dict):
    """Save notification state."""
    NOTIFICATION_STATE.parent.mkdir(parents=True, exist_ok=True)
    with open(NOTIFICATION_STATE, 'w') as f:
        json.dump(state, f, indent=2)


def load_build_status() -> dict:
    """Load current build status."""
    if not BUILD_STATUS.exists():
        return {"completed_builds": [], "active_builds": []}
    
    with open(BUILD_STATUS, 'r') as f:
        return json.load(f)


def should_notify_now() -> bool:
    """
    Check if we should send notifications right now based on context.
    
    Returns:
        True if it's appropriate to send voice notifications
    """
    context = get_current_context()
    
    # Never during work hours or late night
    if context in ['work', 'night']:
        return False
    
    # OK during morning, evening, weekend
    return True


def format_build_completion(build: dict, templates: dict) -> str:
    """
    Format build completion announcement for voice.
    
    Args:
        build: Build data from build-status.json
        templates: Voice templates
        
    Returns:
        Voice script text
    """
    title = build.get("title", "Unknown Build")
    
    # Extract key features/deliverables
    tasks = build.get("tasks", [])
    deliverables = [
        task.get("deliverable") for task in tasks 
        if task.get("deliverable") and task.get("status") == "complete"
    ]
    
    if deliverables:
        # Format deliverables
        key_features = f"Deliverables include: {', '.join([Path(d).name for d in deliverables[:3]])}."
    else:
        key_features = "All tasks completed successfully."
    
    # Determine location
    location = deliverables[0] if deliverables else "your workspace"
    
    # Use template
    template = templates["build_updates"]["completed"]
    message = template.format(
        system_name=title,
        key_features=key_features,
        location=location
    )
    
    return message


def format_build_milestone(build: dict, templates: dict) -> str:
    """
    Format build milestone announcement for voice.
    
    Args:
        build: Build data
        templates: Voice templates
        
    Returns:
        Voice script text
    """
    title = build.get("title", "Unknown Build")
    progress = build.get("progress", 0)
    
    # Determine current task
    tasks = build.get("tasks", [])
    current_task = None
    for task in tasks:
        if task.get("status") == "in_progress":
            current_task = task.get("name")
            break
    
    if current_task:
        milestone_description = f"now working on {current_task}"
    else:
        milestone_description = "making steady progress"
    
    template = templates["build_updates"]["milestone"]
    message = template.format(
        system_name=title,
        milestone_description=milestone_description,
        progress=progress
    )
    
    return message


def check_for_new_completions() -> List[Dict]:
    """
    Check for builds that completed since last check.
    
    Returns:
        List of newly completed builds
    """
    state = load_notification_state()
    notified_ids = set(state.get("notified_builds", []))
    
    build_data = load_build_status()
    completed = build_data.get("completed_builds", [])
    
    # Find new completions
    new_completions = []
    for build in completed:
        build_id = build.get("id")
        if build_id and build_id not in notified_ids:
            new_completions.append(build)
    
    return new_completions


def check_for_milestones() -> List[Dict]:
    """
    Check for active builds that hit significant milestones (50%, 75%).
    
    Returns:
        List of builds at milestones
    """
    state = load_notification_state()
    notified_milestones = set(state.get("notified_milestones", []))
    
    build_data = load_build_status()
    active = build_data.get("active_builds", [])
    
    milestone_builds = []
    for build in active:
        build_id = build.get("id")
        progress = build.get("progress", 0)
        
        # Check for 50% and 75% milestones
        for threshold in [50, 75]:
            milestone_key = f"{build_id}:{threshold}"
            if progress >= threshold and milestone_key not in notified_milestones:
                build["milestone_threshold"] = threshold
                milestone_builds.append(build)
                break  # Only one milestone per build per check
    
    return milestone_builds


def generate_notifications():
    """
    Main function: Check for updates and generate voice notifications.
    """
    # Check context - should we notify now?
    if not should_notify_now():
        context = get_current_context()
        print(f"⏸️  Skipping notifications during {context} time")
        return
    
    state = load_notification_state()
    templates = load_templates()
    
    # Check for new completions
    new_completions = check_for_new_completions()
    
    if new_completions:
        print(f"🎉 Found {len(new_completions)} new build completion(s)")
        
        for build in new_completions:
            build_id = build.get("id")
            title = build.get("title", "Unknown Build")
            
            print(f"\n📢 Generating notification for: {title}")
            
            # Generate voice script
            script = format_build_completion(build, templates)
            
            # Generate voice
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename_base = f"build-complete-{build_id}-{timestamp}"
            
            try:
                OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                
                audio_path, transcript_path = generate_with_transcript(
                    text=script,
                    output_dir=OUTPUT_DIR,
                    filename_base=filename_base,
                    voice="onyx",
                    model="tts-1-hd",
                    format="opus",
                    speed=1.0,
                    log_purpose="build_completion"
                )
                
                print(f"✅ Voice notification generated: {audio_path}")
                
                # Mark as notified
                if "notified_builds" not in state:
                    state["notified_builds"] = []
                state["notified_builds"].append(build_id)
                
                # TODO: Auto-send via Telegram
                # For now, just log the path for manual sending
                print(f"📱 Ready to send: {audio_path}")
                
            except Exception as e:
                print(f"❌ Error generating voice: {e}")
    
    # Check for milestones (optional - can be noisy)
    # Uncomment if Ross wants milestone notifications
    # milestones = check_for_milestones()
    # if milestones:
    #     print(f"🎯 Found {len(milestones)} build milestone(s)")
    #     for build in milestones:
    #         # Similar logic to completions
    #         pass
    
    # Update state
    state["last_check"] = datetime.now().isoformat()
    save_notification_state(state)
    
    if not new_completions:
        print("✓ No new build updates")


def list_pending_notifications():
    """List notifications that haven't been sent yet."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    notifications = sorted(OUTPUT_DIR.glob("*.opus"))
    
    if not notifications:
        print("No pending notifications")
        return
    
    print(f"\n📬 {len(notifications)} pending notification(s):\n")
    for notif in notifications:
        # Parse filename
        timestamp = notif.stem.split('-')[-2:]
        print(f"  • {notif.name}")
        
        # Show transcript preview
        transcript = notif.with_suffix('.txt')
        if transcript.exists():
            with open(transcript, 'r') as f:
                lines = f.readlines()
                preview = lines[3] if len(lines) > 3 else ""
                print(f"    {preview.strip()[:80]}...")
        print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate voice build update notifications")
    parser.add_argument("--list", action="store_true", help="List pending notifications")
    parser.add_argument("--force", action="store_true", help="Ignore context/time restrictions")
    args = parser.parse_args()
    
    if args.list:
        list_pending_notifications()
    else:
        # Override context check if forced
        if args.force:
            original_should_notify = should_notify_now
            globals()['should_notify_now'] = lambda: True
        
        generate_notifications()
