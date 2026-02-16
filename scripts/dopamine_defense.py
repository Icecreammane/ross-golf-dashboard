#!/usr/bin/env python3
"""
Dopamine Defense System - Interrupt doom scrolling and re-engage with quick wins.

Monitors idle periods and sends Telegram interventions to redirect attention
to productive micro-tasks.
"""

import json
import random
import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# Import activity tracker functions
import sys
sys.path.insert(0, str(Path(__file__).parent))
from activity_tracker import (
    get_idle_status, 
    record_interaction, 
    get_daily_summary,
    format_time_duration,
    CST
)

# Paths
WORKSPACE = Path.home() / "clawd"
DATA_DIR = WORKSPACE / "data"
QUICK_WINS_FILE = DATA_DIR / "quick_wins.json"
DEFENSE_STATE_FILE = DATA_DIR / "dopamine_defense_state.json"
HEARTBEAT_STATE = WORKSPACE / "memory" / "heartbeat-state.json"

# Configuration
INTERRUPT_COOLDOWN_MINUTES = 60  # Don't spam - wait 1 hour between interrupts


def load_quick_wins():
    """Load quick win tasks from JSON."""
    if not QUICK_WINS_FILE.exists():
        return {"quick_wins": [], "last_suggested": None, "suggestion_history": []}
    
    with open(QUICK_WINS_FILE, 'r') as f:
        return json.load(f)


def save_quick_wins(data):
    """Save quick wins data."""
    with open(QUICK_WINS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def load_defense_state():
    """Load dopamine defense system state."""
    if not DEFENSE_STATE_FILE.exists():
        return {
            "last_interrupt": None,
            "interrupts_sent": [],
            "responses_received": [],
            "success_rate": 0.0
        }
    
    with open(DEFENSE_STATE_FILE, 'r') as f:
        return json.load(f)


def save_defense_state(data):
    """Save dopamine defense state."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DEFENSE_STATE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def get_next_quick_win():
    """
    Select next quick win task (rotate to avoid repetition).
    
    Returns:
        dict: Quick win task or None if no tasks available
    """
    wins_data = load_quick_wins()
    quick_wins = wins_data.get("quick_wins", [])
    
    if not quick_wins:
        return None
    
    # Get suggestion history (last 3)
    history = wins_data.get("suggestion_history", [])[-3:]
    
    # Filter out recently suggested tasks
    available = [w for w in quick_wins if w["id"] not in history]
    
    # If all have been suggested recently, reset
    if not available:
        available = quick_wins
        history = []
    
    # Pick random from available
    selected = random.choice(available)
    
    # Update history
    history.append(selected["id"])
    wins_data["suggestion_history"] = history[-5:]  # Keep last 5
    wins_data["last_suggested"] = selected["id"]
    
    save_quick_wins(wins_data)
    
    return selected


def should_send_interrupt():
    """
    Determine if we should send an interrupt now.
    
    Checks:
    - Is user idle >20 min?
    - Is it work hours?
    - Has enough time passed since last interrupt?
    
    Returns:
        tuple: (should_send, reason)
    """
    idle_status = get_idle_status()
    
    # Not idle enough
    if not idle_status["should_interrupt"]:
        if not idle_status["work_hours"]:
            return False, "Outside work hours"
        if not idle_status["is_idle"]:
            return False, f"Not idle enough ({idle_status['minutes_idle']}m < 20m)"
        return False, "Unknown reason"
    
    # Check cooldown
    state = load_defense_state()
    if state["last_interrupt"]:
        last_interrupt = datetime.fromisoformat(state["last_interrupt"])
        now = datetime.now(CST)
        minutes_since = (now - last_interrupt).total_seconds() / 60
        
        if minutes_since < INTERRUPT_COOLDOWN_MINUTES:
            return False, f"Cooldown active ({int(minutes_since)}m < {INTERRUPT_COOLDOWN_MINUTES}m)"
    
    return True, "Ready to interrupt"


def send_interrupt_message(quick_win, idle_minutes):
    """
    Generate interrupt message content.
    
    Args:
        quick_win: Selected quick win task
        idle_minutes: How long user has been idle
    
    Returns:
        str: Formatted message
    """
    messages = [
        f"🎯 Working on something? Or stuck?\n\nYou've been quiet for {int(idle_minutes)} minutes.\n\nHere's a quick win: **{quick_win['task']}**\n\n⏱️ ~{quick_win['estimated_minutes']} minutes",
        
        f"⚡ Catch you scrolling?\n\n{int(idle_minutes)}m of silence detected.\n\nQuick productive reset: **{quick_win['task']}**\n\n({quick_win['estimated_minutes']} min • {quick_win['category']})",
        
        f"🔄 Time for a dopamine upgrade!\n\nIdle for {int(idle_minutes)}m — let's redirect that energy.\n\n**Quick win:** {quick_win['task']}\n\n✅ Just {quick_win['estimated_minutes']} minutes",
        
        f"💡 Noticed you've been away for {int(idle_minutes)}m.\n\nWant a quick productive win?\n\n**{quick_win['task']}**\n\n⏰ {quick_win['estimated_minutes']} minutes • Worth it!"
    ]
    
    return random.choice(messages)


def record_interrupt_sent(quick_win, message):
    """Record that an interrupt was sent."""
    now = datetime.now(CST)
    state = load_defense_state()
    
    interrupt_record = {
        "timestamp": now.isoformat(),
        "quick_win_id": quick_win["id"],
        "quick_win_task": quick_win["task"],
        "message": message,
        "response_received": None,
        "response_time_minutes": None
    }
    
    state["last_interrupt"] = now.isoformat()
    state["interrupts_sent"].append(interrupt_record)
    
    # Keep only last 30 days
    cutoff = (now - timedelta(days=30)).isoformat()
    state["interrupts_sent"] = [i for i in state["interrupts_sent"] if i["timestamp"] > cutoff]
    
    save_defense_state(state)


def record_response_received():
    """Record that user responded (re-engaged)."""
    now = datetime.now(CST)
    state = load_defense_state()
    
    # Find last interrupt without response
    for interrupt in reversed(state["interrupts_sent"]):
        if interrupt["response_received"] is None:
            interrupt_time = datetime.fromisoformat(interrupt["timestamp"])
            response_time = (now - interrupt_time).total_seconds() / 60
            
            interrupt["response_received"] = now.isoformat()
            interrupt["response_time_minutes"] = round(response_time, 1)
            
            state["responses_received"].append({
                "interrupt_timestamp": interrupt["timestamp"],
                "response_timestamp": now.isoformat(),
                "response_time_minutes": round(response_time, 1)
            })
            
            break
    
    # Calculate success rate
    total_interrupts = len(state["interrupts_sent"])
    total_responses = len([i for i in state["interrupts_sent"] if i["response_received"]])
    state["success_rate"] = round(total_responses / total_interrupts, 2) if total_interrupts > 0 else 0.0
    
    save_defense_state(state)


def check_and_interrupt():
    """
    Main function: Check if interrupt needed and return message.
    
    Returns:
        dict: Result with message to send (or None)
    """
    should_send, reason = should_send_interrupt()
    
    if not should_send:
        return {
            "should_interrupt": False,
            "reason": reason,
            "message": None
        }
    
    # Get quick win
    quick_win = get_next_quick_win()
    if not quick_win:
        return {
            "should_interrupt": False,
            "reason": "No quick wins available",
            "message": None
        }
    
    # Get idle status for message
    idle_status = get_idle_status()
    
    # Generate message
    message = send_interrupt_message(quick_win, idle_status["minutes_idle"])
    
    # Record interrupt
    record_interrupt_sent(quick_win, message)
    
    return {
        "should_interrupt": True,
        "reason": f"Idle {idle_status['minutes_idle']}m in work hours",
        "message": message,
        "quick_win": quick_win,
        "idle_minutes": idle_status["minutes_idle"]
    }


def get_defense_stats():
    """Get dopamine defense system statistics."""
    state = load_defense_state()
    
    total_interrupts = len(state["interrupts_sent"])
    responded_interrupts = len([i for i in state["interrupts_sent"] if i["response_received"]])
    
    avg_response_time = None
    if responded_interrupts > 0:
        response_times = [i["response_time_minutes"] for i in state["interrupts_sent"] if i["response_time_minutes"]]
        avg_response_time = round(sum(response_times) / len(response_times), 1)
    
    return {
        "total_interrupts": total_interrupts,
        "successful_engagements": responded_interrupts,
        "success_rate": state["success_rate"],
        "avg_response_time_minutes": avg_response_time,
        "last_interrupt": state["last_interrupt"]
    }


def generate_evening_report():
    """
    Generate evening check-in report with activity summary.
    
    Returns:
        str: Formatted report
    """
    summary = get_daily_summary()
    stats = get_defense_stats()
    
    active_time = format_time_duration(summary["estimated_active_minutes"])
    idle_time = format_time_duration(summary["total_idle_minutes"])
    productivity = int(summary["productivity_score"] * 100)
    
    report = f"""📊 **Today's Dopamine Defense Report**

⏱️ **Time Breakdown:**
• Building: {active_time}
• Idle periods: {idle_time}
• Productivity score: {productivity}%

🎯 **Interventions:**
• Interrupts sent: {stats['total_interrupts']}
• Successful re-engagements: {stats['successful_engagements']}
• Success rate: {int(stats['success_rate'] * 100)}%
"""
    
    if stats['avg_response_time_minutes']:
        report += f"• Avg response time: {format_time_duration(stats['avg_response_time_minutes'])}\n"
    
    # Add insight
    if productivity >= 70:
        report += "\n✨ Strong focus today! Keep that momentum."
    elif productivity >= 50:
        report += "\n💪 Solid day. A few scroll sessions, but you stayed productive."
    else:
        report += "\n🎯 Tomorrow's a fresh start. Let's catch those scroll sessions earlier."
    
    return report


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            result = check_and_interrupt()
            print(json.dumps(result, indent=2))
            
            if result["should_interrupt"]:
                print("\n📨 MESSAGE TO SEND:")
                print(result["message"])
        
        elif command == "record_response":
            record_response_received()
            print("✅ Response recorded")
        
        elif command == "stats":
            stats = get_defense_stats()
            print(json.dumps(stats, indent=2))
        
        elif command == "report":
            report = generate_evening_report()
            print(report)
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: dopamine_defense.py [check|record_response|stats|report]")
    else:
        # Default: check and show what would happen
        result = check_and_interrupt()
        print(json.dumps(result, indent=2))
