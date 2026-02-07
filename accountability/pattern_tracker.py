#!/usr/bin/env python3
"""
Pattern Tracker - Record every action Ross takes
Builds the foundation for predictive accountability
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class PatternTracker:
    def __init__(self, workspace_root: str = "/Users/clawdbot/clawd"):
        self.workspace = Path(workspace_root)
        self.pattern_dir = self.workspace / "memory" / "patterns"
        self.pattern_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_activity_file(self) -> Path:
        """Get today's activity log file"""
        return self.pattern_dir / "daily-activity.jsonl"
    
    def _infer_energy_level(self, duration: int, completed: bool) -> str:
        """Infer energy level from task completion speed"""
        if not completed:
            return "low"
        
        # Quick completion = high energy
        if duration < 900:  # < 15 min
            return "high"
        elif duration < 1800:  # < 30 min
            return "medium"
        else:
            return "low"
    
    def log_action(
        self,
        action: str,
        action_type: str,
        duration: int,
        completed: bool = True,
        context: Optional[Dict[str, Any]] = None,
        energy_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log an action to the pattern tracker
        
        Args:
            action: Name/description of action (e.g., "deploy_fittrack")
            action_type: Category - revenue_task, building, selling, procrastinating, admin
            duration: Time spent in seconds
            completed: Whether task was completed or abandoned
            context: Additional context (mode, task details, etc.)
            energy_level: Override auto-detection (high/medium/low)
        
        Returns:
            The logged entry
        """
        now = datetime.now()
        
        entry = {
            "timestamp": int(now.timestamp()),
            "datetime": now.isoformat(),
            "action": action,
            "type": action_type,
            "duration": duration,
            "completed": completed,
            "energy_level": energy_level or self._infer_energy_level(duration, completed),
            "day_of_week": now.strftime("%A").lower(),
            "time_of_day": self._categorize_time(now.hour),
            "hour": now.hour,
            "context": context or {}
        }
        
        # Append to JSONL file
        activity_file = self._get_activity_file()
        with open(activity_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return entry
    
    def _categorize_time(self, hour: int) -> str:
        """Categorize hour into time of day"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def get_recent_actions(self, hours: int = 24) -> list:
        """Get actions from the last N hours"""
        activity_file = self._get_activity_file()
        if not activity_file.exists():
            return []
        
        cutoff = int(datetime.now().timestamp()) - (hours * 3600)
        actions = []
        
        with open(activity_file, "r") as f:
            for line in f:
                entry = json.loads(line.strip())
                if entry["timestamp"] >= cutoff:
                    actions.append(entry)
        
        return actions
    
    def get_current_streak(self, action_type: str = "revenue_task") -> int:
        """Count consecutive days with completed revenue tasks"""
        # Load all activity
        activity_file = self._get_activity_file()
        if not activity_file.exists():
            return 0
        
        completed_dates = set()
        with open(activity_file, "r") as f:
            for line in f:
                entry = json.loads(line.strip())
                if entry["type"] == action_type and entry["completed"]:
                    date = datetime.fromtimestamp(entry["timestamp"]).date()
                    completed_dates.add(date)
        
        # Count backwards from today
        from datetime import timedelta
        today = datetime.now().date()
        streak = 0
        
        while True:
            check_date = today - timedelta(days=streak)
            if check_date in completed_dates:
                streak += 1
            else:
                break
        
        return streak
    
    def quick_log(self, action: str, minutes: int, action_type: str = "revenue_task"):
        """Quick logging shortcut for common use"""
        return self.log_action(
            action=action,
            action_type=action_type,
            duration=minutes * 60,
            completed=True
        )


# CLI interface for quick logging
if __name__ == "__main__":
    import sys
    
    tracker = PatternTracker()
    
    if len(sys.argv) < 3:
        print("Usage: python pattern_tracker.py <action> <minutes> [type]")
        print("Example: python pattern_tracker.py 'deployed_fittrack' 30 revenue_task")
        sys.exit(1)
    
    action = sys.argv[1]
    minutes = int(sys.argv[2])
    action_type = sys.argv[3] if len(sys.argv) > 3 else "revenue_task"
    
    entry = tracker.quick_log(action, minutes, action_type)
    print(f"✅ Logged: {action} ({minutes}min, {action_type})")
    print(f"   Energy: {entry['energy_level']} | {entry['time_of_day']} | {entry['day_of_week']}")
