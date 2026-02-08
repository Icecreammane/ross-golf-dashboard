#!/usr/bin/env python3
"""
Smart Reminders
Time-based proactive check-ins to prevent dropped balls
"""

import json
from datetime import datetime, time
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
STATE_FILE = WORKSPACE / "memory" / "reminder_state.json"

class SmartReminders:
    """Time-based reminders that actually help"""
    
    def __init__(self):
        self.state_file = STATE_FILE
        self.load_state()
        
        # Define reminders (time, check, message)
        self.reminders = [
            {
                "time": "21:00",  # 9:00pm
                "id": "protein_check",
                "check": self.check_protein,
                "message_template": "Protein check: Currently at {current}g. Need {needed}g more to hit {target}g target."
            },
            {
                "time": "22:00",  # 10:00pm
                "id": "task_prep",
                "check": self.check_task_prep,
                "message_template": "Task list ready for tomorrow? {info}"
            },
            {
                "time": "22:30",  # 10:30pm
                "id": "workout_check",
                "check": self.check_workout,
                "message_template": "Workout logged today? {info}"
            },
            {
                "time": "23:00",  # 11:00pm
                "id": "streak_check",
                "check": self.check_streaks,
                "message_template": "⚠️ Streaks at risk: {streaks_at_risk}"
            }
        ]
    
    def load_state(self):
        """Load reminder state"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {
                "last_reminders": {},
                "snoozed": {}
            }
    
    def save_state(self):
        """Save reminder state"""
        self.state_file.parent.mkdir(exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def should_remind(self, reminder_id, reminder_time):
        """Check if we should send this reminder"""
        today = datetime.now().date().isoformat()
        
        # Check if already sent today
        if reminder_id in self.state["last_reminders"]:
            last_sent = self.state["last_reminders"][reminder_id]
            if last_sent.startswith(today):
                return False
        
        # Check if snoozed
        if reminder_id in self.state["snoozed"]:
            snooze_until = datetime.fromisoformat(self.state["snoozed"][reminder_id])
            if datetime.now() < snooze_until:
                return False
        
        # Check if current time is within 5 min of reminder time
        now = datetime.now().time()
        reminder_time_obj = datetime.strptime(reminder_time, "%H:%M").time()
        
        # Create datetime objects for comparison
        now_dt = datetime.combine(datetime.now().date(), now)
        reminder_dt = datetime.combine(datetime.now().date(), reminder_time_obj)
        
        diff = abs((now_dt - reminder_dt).total_seconds())
        
        return diff <= 300  # Within 5 minutes
    
    def mark_sent(self, reminder_id):
        """Mark reminder as sent"""
        self.state["last_reminders"][reminder_id] = datetime.now().isoformat()
        self.save_state()
    
    def check_protein(self):
        """Check protein intake"""
        try:
            # Load today's food logs
            fitness_file = WORKSPACE / "fitness-tracker" / "fitness_data.json"
            if not fitness_file.exists():
                return None
            
            with open(fitness_file) as f:
                data = json.load(f)
            
            today = datetime.now().date().isoformat()
            todays_logs = [
                log for log in data.get("food_logs", [])
                if log.get("date") == today
            ]
            
            current_protein = sum(log.get("protein", 0) for log in todays_logs)
            target = data.get("settings", {}).get("daily_protein", 200)
            
            if current_protein < target:
                needed = target - current_protein
                return {
                    "should_remind": True,
                    "current": int(current_protein),
                    "needed": int(needed),
                    "target": target
                }
            
            return {"should_remind": False}
            
        except Exception as e:
            print(f"Error checking protein: {e}")
            return None
    
    def check_task_prep(self):
        """Check if tomorrow's tasks are ready"""
        try:
            task_queue = WORKSPACE / "TASK_QUEUE.md"
            if not task_queue.exists():
                return {"should_remind": True, "info": "No task queue found"}
            
            with open(task_queue) as f:
                content = f.read()
            
            # Count active tasks
            active_tasks = len([line for line in content.split('\n') if line.strip().startswith('- [ ]')])
            
            if active_tasks == 0:
                return {"should_remind": True, "info": "Queue is empty - add tomorrow's tasks"}
            else:
                return {"should_remind": False, "info": f"{active_tasks} tasks ready"}
            
        except Exception as e:
            return None
    
    def check_workout(self):
        """Check if workout logged today"""
        try:
            from win_streak import WinStreakAmplifier
            ws = WinStreakAmplifier()
            
            workout_data = ws.data["categories"]["workout"]
            last_win = workout_data.get("last_win_date")
            
            if last_win:
                last_date = datetime.fromisoformat(last_win).date()
                today = datetime.now().date()
                
                if last_date < today:
                    return {"should_remind": True, "info": "No workout logged yet today"}
                else:
                    return {"should_remind": False, "info": f"Workout logged! {workout_data['current_streak']} day streak"}
            else:
                return {"should_remind": True, "info": "No workouts logged yet"}
            
        except Exception as e:
            return None
    
    def check_streaks(self):
        """Check which streaks are at risk"""
        try:
            from win_streak import WinStreakAmplifier
            ws = WinStreakAmplifier()
            
            at_risk = []
            today = datetime.now().date()
            
            for cat_name, cat_data in ws.data["categories"].items():
                if cat_data["current_streak"] > 0:
                    last_win = cat_data.get("last_win_date")
                    if last_win:
                        last_date = datetime.fromisoformat(last_win).date()
                        if last_date < today:
                            name = cat_data["name"]
                            streak = cat_data["current_streak"]
                            at_risk.append(f"{name} ({streak} day streak)")
            
            if at_risk:
                return {"should_remind": True, "streaks_at_risk": ", ".join(at_risk)}
            else:
                return {"should_remind": False}
            
        except Exception as e:
            return None
    
    def check_all(self):
        """Check all reminders and return ones that should fire"""
        reminders_to_send = []
        
        for reminder in self.reminders:
            if not self.should_remind(reminder["id"], reminder["time"]):
                continue
            
            # Run the check function
            result = reminder["check"]()
            
            if result and result.get("should_remind", False):
                # Format message
                message = reminder["message_template"].format(**result)
                
                reminders_to_send.append({
                    "id": reminder["id"],
                    "message": message,
                    "data": result
                })
                
                # Mark as sent
                self.mark_sent(reminder["id"])
        
        return reminders_to_send
    
    def get_status(self):
        """Get reminder status"""
        now = datetime.now()
        status = {
            "current_time": now.strftime("%I:%M %p"),
            "upcoming": [],
            "sent_today": []
        }
        
        today = now.date().isoformat()
        
        for reminder in self.reminders:
            reminder_time = datetime.strptime(reminder["time"], "%H:%M").time()
            reminder_dt = datetime.combine(now.date(), reminder_time)
            
            # Check if sent today
            if reminder["id"] in self.state["last_reminders"]:
                last_sent = self.state["last_reminders"][reminder["id"]]
                if last_sent.startswith(today):
                    status["sent_today"].append({
                        "id": reminder["id"],
                        "time": reminder["time"],
                        "sent_at": last_sent
                    })
                    continue
            
            # Check if upcoming
            if now < reminder_dt:
                minutes_until = int((reminder_dt - now).total_seconds() / 60)
                status["upcoming"].append({
                    "id": reminder["id"],
                    "time": reminder["time"],
                    "minutes_until": minutes_until
                })
        
        return status


def main():
    """Check reminders"""
    reminders = SmartReminders()
    
    # Check for reminders to send
    to_send = reminders.check_all()
    
    if to_send:
        print("=" * 70)
        print("🔔 SMART REMINDERS")
        print("=" * 70)
        print()
        
        for reminder in to_send:
            print(f"⏰ {reminder['id'].upper()}")
            print(f"   {reminder['message']}")
            print()
    else:
        # Show status
        status = reminders.get_status()
        print(f"✅ No reminders at {status['current_time']}")
        
        if status["sent_today"]:
            print(f"\n📬 Sent today: {len(status['sent_today'])}")
        
        if status["upcoming"]:
            print(f"\n⏳ Upcoming:")
            for rem in status["upcoming"]:
                print(f"   {rem['id']} at {rem['time']} ({rem['minutes_until']} min)")


if __name__ == "__main__":
    main()
