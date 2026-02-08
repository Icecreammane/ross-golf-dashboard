#!/usr/bin/env python3
"""
Autonomous Actions System
Event-driven actions without waiting for triggers
Actually autonomous, not just scheduled
"""

import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import sys

WORKSPACE = Path.home() / "clawd"
ACTION_LOG = WORKSPACE / "memory" / "autonomous_actions.json"

# Add scripts to path
sys.path.append(str(WORKSPACE / "scripts"))

class AutonomousActions:
    """Event-driven autonomous action system"""
    
    def __init__(self):
        self.log_file = ACTION_LOG
        self.load_log()
        
        # Define autonomous actions
        self.actions = [
            {
                "id": "auto_commit_memory",
                "check": self.check_uncommitted_memory,
                "action": self.commit_memory_updates,
                "cooldown_minutes": 30
            },
            {
                "id": "protein_warning",
                "check": self.check_protein_lag,
                "action": self.send_protein_reminder,
                "cooldown_minutes": 120
            },
            {
                "id": "streak_protection",
                "check": self.check_streak_danger,
                "action": self.protect_streaks,
                "cooldown_minutes": 60
            },
            {
                "id": "task_queue_empty",
                "check": self.check_empty_queue,
                "action": self.populate_queue,
                "cooldown_minutes": 240
            }
        ]
    
    def load_log(self):
        """Load action log"""
        if self.log_file.exists():
            with open(self.log_file) as f:
                self.log = json.load(f)
        else:
            self.log = {
                "version": "1.0",
                "actions_taken": [],
                "last_action_times": {}
            }
    
    def save_log(self):
        """Save action log"""
        self.log_file.parent.mkdir(exist_ok=True)
        with open(self.log_file, 'w') as f:
            json.dump(self.log, f, indent=2)
    
    def can_act(self, action_id, cooldown_minutes):
        """Check if action is off cooldown"""
        if action_id not in self.log["last_action_times"]:
            return True
        
        last_action = datetime.fromisoformat(self.log["last_action_times"][action_id])
        now = datetime.now()
        
        minutes_since = (now - last_action).total_seconds() / 60
        
        return minutes_since >= cooldown_minutes
    
    def log_action(self, action_id, result, details=None):
        """Log an autonomous action"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_id": action_id,
            "result": result,
            "details": details or {}
        }
        
        self.log["actions_taken"].append(entry)
        self.log["last_action_times"][action_id] = datetime.now().isoformat()
        
        # Keep only last 100 actions
        if len(self.log["actions_taken"]) > 100:
            self.log["actions_taken"] = self.log["actions_taken"][-100:]
        
        self.save_log()
    
    # ========== CHECK FUNCTIONS ==========
    
    def check_uncommitted_memory(self):
        """Check if memory files have uncommitted changes"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", "memory/"],
                cwd=WORKSPACE,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            changes = result.stdout.strip()
            
            if changes:
                # Check if changes are just memory updates
                lines = changes.split('\n')
                memory_changes = [l for l in lines if 'memory/' in l]
                
                if memory_changes:
                    return {"should_act": True, "files": len(memory_changes)}
            
            return {"should_act": False}
            
        except Exception as e:
            return {"should_act": False, "error": str(e)}
    
    def check_protein_lag(self):
        """Check if protein logging is lagging"""
        try:
            from win_streak import WinStreakAmplifier
            ws = WinStreakAmplifier()
            
            protein_data = ws.data["categories"]["protein"]
            last_win = protein_data.get("last_win_date")
            
            if last_win:
                last_date = datetime.fromisoformat(last_win).date()
                today = datetime.now().date()
                
                # If protein not logged today and it's past 8pm
                if last_date < today and datetime.now().hour >= 20:
                    return {"should_act": True, "streak": protein_data["current_streak"]}
            
            return {"should_act": False}
            
        except Exception as e:
            return {"should_act": False, "error": str(e)}
    
    def check_streak_danger(self):
        """Check if any streaks are in danger"""
        try:
            from win_streak import WinStreakAmplifier
            ws = WinStreakAmplifier()
            
            today = datetime.now().date()
            at_risk = []
            
            for cat_name, cat_data in ws.data["categories"].items():
                if cat_data["current_streak"] >= 3:  # Only care about 3+ day streaks
                    last_win = cat_data.get("last_win_date")
                    if last_win:
                        last_date = datetime.fromisoformat(last_win).date()
                        if last_date < today:
                            at_risk.append({
                                "category": cat_name,
                                "name": cat_data["name"],
                                "streak": cat_data["current_streak"]
                            })
            
            if at_risk and datetime.now().hour >= 21:  # After 9pm
                return {"should_act": True, "at_risk": at_risk}
            
            return {"should_act": False}
            
        except Exception as e:
            return {"should_act": False, "error": str(e)}
    
    def check_empty_queue(self):
        """Check if task queue is empty"""
        try:
            task_queue = WORKSPACE / "TASK_QUEUE.md"
            
            if not task_queue.exists():
                return {"should_act": True, "reason": "no_file"}
            
            with open(task_queue) as f:
                content = f.read()
            
            # Count active tasks
            active_tasks = len([line for line in content.split('\n') 
                              if line.strip().startswith('- [ ]')])
            
            if active_tasks <= 2:  # Very low
                return {"should_act": True, "current_count": active_tasks}
            
            return {"should_act": False}
            
        except Exception as e:
            return {"should_act": False, "error": str(e)}
    
    # ========== ACTION FUNCTIONS ==========
    
    def commit_memory_updates(self, check_result):
        """Automatically commit memory file updates"""
        try:
            # Use safe_git wrapper for security
            from safe_git import SafeGit
            git = SafeGit()
            
            # Stage memory files
            add_result = git.safe_add(["memory/"])
            
            if not add_result["success"]:
                return {
                    "success": False,
                    "reason": "staging_failed",
                    "error": add_result.get("reason")
                }
            
            # Commit with auto flag
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            commit_result = git.safe_commit(
                f"chore: auto-update memory files ({timestamp})",
                auto=True
            )
            
            if not commit_result["success"]:
                return {
                    "success": False,
                    "reason": commit_result.get("reason"),
                    "error": commit_result.get("error")
                }
            
            return {
                "success": True,
                "files_committed": check_result.get("files", 0),
                "commit_hash": commit_result.get("output", "")[:8]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_protein_reminder(self, check_result):
        """Send protein reminder"""
        streak = check_result.get("streak", 0)
        message = f"⚠️ Protein not logged today. {streak} day streak at risk!"
        
        # This would send via Telegram in production
        # For now, just log it
        print(message)
        
        return {"success": True, "message": message}
    
    def protect_streaks(self, check_result):
        """Send streak protection warning"""
        at_risk = check_result.get("at_risk", [])
        
        if not at_risk:
            return {"success": False, "reason": "no_streaks_at_risk"}
        
        streaks_text = ", ".join([f"{s['name']} ({s['streak']} days)" for s in at_risk])
        message = f"🚨 Streaks at risk: {streaks_text}"
        
        # This would send via Telegram in production
        print(message)
        
        return {"success": True, "streaks_warned": len(at_risk)}
    
    def populate_queue(self, check_result):
        """Add tasks to queue from GOALS.md"""
        try:
            goals_file = WORKSPACE / "GOALS.md"
            task_queue = WORKSPACE / "TASK_QUEUE.md"
            
            if not goals_file.exists():
                return {"success": False, "reason": "no_goals_file"}
            
            # This would call autonomous_check.py or similar
            # For now, just log
            print("Would populate task queue from GOALS.md")
            
            return {"success": True, "action": "queue_populate_triggered"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== MAIN LOOP ==========
    
    def run_cycle(self):
        """Run one cycle of autonomous actions"""
        actions_taken = []
        
        for action_config in self.actions:
            action_id = action_config["id"]
            cooldown = action_config["cooldown_minutes"]
            
            # Check if on cooldown
            if not self.can_act(action_id, cooldown):
                continue
            
            # Run check
            check_result = action_config["check"]()
            
            if check_result.get("should_act", False):
                # Take action
                action_result = action_config["action"](check_result)
                
                if action_result.get("success", False):
                    self.log_action(action_id, "success", action_result)
                    actions_taken.append({
                        "action_id": action_id,
                        "result": action_result
                    })
        
        return actions_taken
    
    def get_status(self):
        """Get current status"""
        status = {
            "total_actions": len(self.log["actions_taken"]),
            "recent_actions": self.log["actions_taken"][-10:],
            "cooldowns": {}
        }
        
        # Check cooldown status for each action
        for action_config in self.actions:
            action_id = action_config["id"]
            cooldown = action_config["cooldown_minutes"]
            
            if action_id in self.log["last_action_times"]:
                last_action = datetime.fromisoformat(self.log["last_action_times"][action_id])
                now = datetime.now()
                minutes_since = (now - last_action).total_seconds() / 60
                minutes_until = max(0, cooldown - minutes_since)
                
                status["cooldowns"][action_id] = {
                    "ready": minutes_until == 0,
                    "minutes_until_ready": int(minutes_until)
                }
            else:
                status["cooldowns"][action_id] = {"ready": True, "minutes_until_ready": 0}
        
        return status


def test_autonomous_actions():
    """Test autonomous actions"""
    aa = AutonomousActions()
    
    print("=" * 70)
    print("🤖 AUTONOMOUS ACTIONS TEST")
    print("=" * 70)
    print()
    
    # Run cycle
    print("🔄 Running action cycle...")
    actions_taken = aa.run_cycle()
    
    if actions_taken:
        print(f"✅ {len(actions_taken)} actions taken:")
        for action in actions_taken:
            print(f"   • {action['action_id']}: {action['result']}")
    else:
        print("  ℹ️  No actions needed")
    
    print()
    
    # Show status
    status = aa.get_status()
    print(f"📊 Total autonomous actions: {status['total_actions']}")
    print()
    
    print("⏱️  Action cooldowns:")
    for action_id, cooldown in status["cooldowns"].items():
        if cooldown["ready"]:
            print(f"   ✅ {action_id}: Ready")
        else:
            print(f"   ⏰ {action_id}: {cooldown['minutes_until_ready']} min until ready")
    
    print()
    print("=" * 70)


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_autonomous_actions()
    elif len(sys.argv) > 1 and sys.argv[1] == "run":
        aa = AutonomousActions()
        actions = aa.run_cycle()
        if actions:
            print(f"Took {len(actions)} actions")
        else:
            print("No actions needed")
    else:
        aa = AutonomousActions()
        status = aa.get_status()
        print(f"Total actions: {status['total_actions']}")
        for action_id, cooldown in status["cooldowns"].items():
            status_text = "Ready" if cooldown["ready"] else f"{cooldown['minutes_until_ready']}m"
            print(f"  {action_id}: {status_text}")


if __name__ == "__main__":
    main()
