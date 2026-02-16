#!/usr/bin/env python3
"""
Auto-logging system for Jarvis - Write conversations to daily memory files
Usage: python3 auto_log.py "Your log entry here" [--type decision|preference|task|insight]
"""

import sys
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
MEMORY_DIR = WORKSPACE / "memory"

def get_today_file():
    """Get path to today's memory file"""
    today = datetime.now().strftime("%Y-%m-%d")
    return MEMORY_DIR / f"{today}.md"

def log_entry(content, entry_type="general"):
    """Log an entry to today's memory file"""
    MEMORY_DIR.mkdir(exist_ok=True)
    
    today_file = get_today_file()
    timestamp = datetime.now().strftime("%H:%M")
    
    # Format based on type
    if entry_type == "decision":
        header = f"## 🎯 Decision - {timestamp}"
    elif entry_type == "preference":
        header = f"## 💡 Preference - {timestamp}"
    elif entry_type == "task":
        header = f"## ✅ Task - {timestamp}"
    elif entry_type == "insight":
        header = f"## 🧠 Insight - {timestamp}"
    else:
        header = f"## 📝 {timestamp}"
    
    entry = f"\n{header}\n{content}\n"
    
    # Append to file (create if doesn't exist)
    if not today_file.exists():
        # Create new file with header
        date_str = datetime.now().strftime("%B %d, %Y")
        today_file.write_text(f"# Daily Log - {date_str}\n\n")
    
    with open(today_file, "a") as f:
        f.write(entry)
    
    print(f"✅ Logged to {today_file.name}")
    return today_file

def log_decision(decision_text, context=""):
    """Quick log for decisions"""
    from scripts.learning_loop import log_decision as ll_log
    
    # Log to daily file
    log_entry(f"**Decision:** {decision_text}\n**Context:** {context}", "decision")
    
    # Also log to learning loop for pattern tracking
    ll_log(decision_text, context)

def log_preference(preference_text):
    """Quick log for preferences"""
    log_entry(f"**Preference:** {preference_text}", "preference")

def log_task_completion(task_name, notes=""):
    """Quick log for completed tasks"""
    content = f"**Completed:** {task_name}"
    if notes:
        content += f"\n**Notes:** {notes}"
    log_entry(content, "task")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 auto_log.py 'Your log entry' [--type decision|preference|task|insight]")
        sys.exit(1)
    
    content = sys.argv[1]
    entry_type = "general"
    
    if len(sys.argv) > 2 and sys.argv[2] == "--type":
        entry_type = sys.argv[3] if len(sys.argv) > 3 else "general"
    
    log_entry(content, entry_type)

if __name__ == "__main__":
    main()
