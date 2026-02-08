#!/usr/bin/env python3
"""
Action Guardrails
Safety system for autonomous actions
Approval levels, dry run mode, emergency brake
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
GUARDRAILS_CONFIG = WORKSPACE / "memory" / "action_guardrails.json"

class ActionGuardrails:
    """Guardrail system for autonomous actions"""
    
    def __init__(self):
        self.config_file = GUARDRAILS_CONFIG
        self.load_config()
    
    def load_config(self):
        """Load guardrails configuration"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.config = json.load(f)
        else:
            self.config = self.initialize_config()
            self.save_config()
    
    def initialize_config(self):
        """Initialize default guardrails"""
        return {
            "version": "1.0",
            "dry_run_mode": False,
            "emergency_brake": False,
            "action_levels": {
                # Level 1: Auto-execute (safe operations)
                "level_1": {
                    "auto_execute": True,
                    "notify_after": True,
                    "actions": [
                        "memory_commit",
                        "reminder_send",
                        "health_check"
                    ]
                },
                # Level 2: Notify then execute
                "level_2": {
                    "auto_execute": True,
                    "notify_before": True,
                    "notify_after": False,
                    "actions": [
                        "streak_warning",
                        "protein_reminder",
                        "task_queue_populate"
                    ]
                },
                # Level 3: Ask first (requires approval)
                "level_3": {
                    "auto_execute": False,
                    "require_approval": True,
                    "actions": [
                        "git_push",
                        "file_delete",
                        "config_change"
                    ]
                }
            },
            "rate_limits": {
                "global_budget": 50,  # Max actions per hour
                "per_action_budget": 10,  # Max per action type per hour
                "current_hour_count": 0,
                "hour_reset_time": None
            },
            "blocked_actions": [],
            "pending_approvals": []
        }
    
    def save_config(self):
        """Save configuration"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_action_level(self, action_id):
        """Get approval level for action"""
        for level_name, level_config in self.config["action_levels"].items():
            if action_id in level_config["actions"]:
                return level_name, level_config
        
        # Default to level 3 (safest) if unknown
        return "level_3", self.config["action_levels"]["level_3"]
    
    def can_execute(self, action_id, context=None):
        """
        Check if action can execute
        
        Returns: (can_execute: bool, reason: str, level: str)
        """
        # Check emergency brake
        if self.config["emergency_brake"]:
            return False, "emergency_brake_active", None
        
        # Check if action is blocked
        if action_id in self.config["blocked_actions"]:
            return False, "action_blocked", None
        
        # Check dry run mode
        if self.config["dry_run_mode"]:
            return False, "dry_run_mode", None
        
        # Check rate limits
        if not self._check_rate_limit(action_id):
            return False, "rate_limit_exceeded", None
        
        # Get action level
        level_name, level_config = self.get_action_level(action_id)
        
        # Check if auto-execute allowed
        if level_config.get("require_approval", False):
            # Check for pending approval
            if not self._has_approval(action_id, context):
                return False, "approval_required", level_name
        
        return True, "approved", level_name
    
    def _check_rate_limit(self, action_id):
        """Check if within rate limits"""
        limits = self.config["rate_limits"]
        
        # Check if hour has reset
        if limits["hour_reset_time"]:
            reset_time = datetime.fromisoformat(limits["hour_reset_time"])
            if datetime.now() > reset_time:
                # Reset counters
                limits["current_hour_count"] = 0
                limits["hour_reset_time"] = (datetime.now() + timedelta(hours=1)).isoformat()
        else:
            limits["hour_reset_time"] = (datetime.now() + timedelta(hours=1)).isoformat()
        
        # Check global budget
        if limits["current_hour_count"] >= limits["global_budget"]:
            return False
        
        return True
    
    def _has_approval(self, action_id, context):
        """Check if action has pending approval"""
        for approval in self.config["pending_approvals"]:
            if approval["action_id"] == action_id:
                if approval.get("approved", False):
                    # Remove from pending
                    self.config["pending_approvals"].remove(approval)
                    self.save_config()
                    return True
        
        return False
    
    def log_action_attempt(self, action_id, allowed, reason, context=None):
        """Log action attempt"""
        if allowed:
            # Increment counters
            self.config["rate_limits"]["current_hour_count"] += 1
            self.save_config()
    
    def request_approval(self, action_id, description, context=None):
        """Request approval for action"""
        approval_request = {
            "action_id": action_id,
            "description": description,
            "context": context or {},
            "requested_at": datetime.now().isoformat(),
            "approved": False
        }
        
        self.config["pending_approvals"].append(approval_request)
        self.save_config()
        
        return approval_request
    
    def approve_action(self, action_id):
        """Approve a pending action"""
        for approval in self.config["pending_approvals"]:
            if approval["action_id"] == action_id:
                approval["approved"] = True
                approval["approved_at"] = datetime.now().isoformat()
                self.save_config()
                return True
        
        return False
    
    def deny_action(self, action_id):
        """Deny and remove pending action"""
        self.config["pending_approvals"] = [
            a for a in self.config["pending_approvals"]
            if a["action_id"] != action_id
        ]
        self.save_config()
    
    def set_dry_run(self, enabled=True):
        """Enable/disable dry run mode"""
        self.config["dry_run_mode"] = enabled
        self.save_config()
        
        return enabled
    
    def set_emergency_brake(self, enabled=True):
        """Enable/disable emergency brake"""
        self.config["emergency_brake"] = enabled
        self.save_config()
        
        return enabled
    
    def block_action(self, action_id):
        """Block a specific action permanently"""
        if action_id not in self.config["blocked_actions"]:
            self.config["blocked_actions"].append(action_id)
            self.save_config()
    
    def unblock_action(self, action_id):
        """Unblock an action"""
        if action_id in self.config["blocked_actions"]:
            self.config["blocked_actions"].remove(action_id)
            self.save_config()
    
    def get_status(self):
        """Get guardrail status"""
        limits = self.config["rate_limits"]
        
        return {
            "dry_run_mode": self.config["dry_run_mode"],
            "emergency_brake": self.config["emergency_brake"],
            "actions_this_hour": limits["current_hour_count"],
            "global_budget": limits["global_budget"],
            "pending_approvals": len(self.config["pending_approvals"]),
            "blocked_actions": len(self.config["blocked_actions"])
        }
    
    def generate_report(self):
        """Generate human-readable report"""
        status = self.get_status()
        
        report = []
        report.append("=" * 70)
        report.append("🛡️  ACTION GUARDRAILS STATUS")
        report.append("=" * 70)
        report.append("")
        
        # Mode status
        if status["emergency_brake"]:
            report.append("🚨 EMERGENCY BRAKE: ACTIVE (all actions blocked)")
        elif status["dry_run_mode"]:
            report.append("🧪 DRY RUN MODE: Active (simulating only)")
        else:
            report.append("✅ Normal operation")
        
        report.append("")
        
        # Rate limits
        report.append("📊 Rate Limits:")
        report.append(f"   Actions this hour: {status['actions_this_hour']}/{status['global_budget']}")
        
        remaining = status['global_budget'] - status['actions_this_hour']
        if remaining < 10:
            report.append(f"   ⚠️  Only {remaining} actions remaining this hour")
        
        report.append("")
        
        # Pending approvals
        if status["pending_approvals"] > 0:
            report.append(f"⏳ Pending approvals: {status['pending_approvals']}")
            for approval in self.config["pending_approvals"]:
                report.append(f"   • {approval['action_id']}: {approval['description']}")
            report.append("")
        
        # Blocked actions
        if status["blocked_actions"] > 0:
            report.append(f"🚫 Blocked actions: {status['blocked_actions']}")
            for action in self.config["blocked_actions"]:
                report.append(f"   • {action}")
            report.append("")
        
        # Action levels
        report.append("🔒 Action Levels:")
        report.append("   Level 1 (Auto-execute): Safe operations")
        for action in self.config["action_levels"]["level_1"]["actions"]:
            report.append(f"      • {action}")
        
        report.append("   Level 2 (Notify + execute): Warnings")
        for action in self.config["action_levels"]["level_2"]["actions"]:
            report.append(f"      • {action}")
        
        report.append("   Level 3 (Approval required): Dangerous")
        for action in self.config["action_levels"]["level_3"]["actions"]:
            report.append(f"      • {action}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def test_guardrails():
    """Test guardrail system"""
    guardrails = ActionGuardrails()
    
    print("=" * 70)
    print("🛡️  ACTION GUARDRAILS TEST")
    print("=" * 70)
    print()
    
    # Test different action levels
    test_actions = [
        ("memory_commit", "Commit memory files"),
        ("streak_warning", "Send streak warning"),
        ("git_push", "Push to GitHub"),
        ("unknown_action", "Some unknown action")
    ]
    
    for action_id, description in test_actions:
        can_execute, reason, level = guardrails.can_execute(action_id)
        
        print(f"Action: {action_id}")
        print(f"  Level: {level or 'unknown'}")
        print(f"  Can execute: {'YES ✅' if can_execute else 'NO ❌'}")
        print(f"  Reason: {reason}")
        print()
    
    # Test dry run mode
    print("Testing dry run mode...")
    guardrails.set_dry_run(True)
    can_execute, reason, _ = guardrails.can_execute("memory_commit")
    print(f"  Dry run enabled: {can_execute} (reason: {reason})")
    
    guardrails.set_dry_run(False)
    print()
    
    # Show status
    print(guardrails.generate_report())


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        guardrails = ActionGuardrails()
        
        if action == "test":
            test_guardrails()
        
        elif action == "status":
            print(guardrails.generate_report())
        
        elif action == "dry-run":
            enabled = guardrails.set_dry_run(True)
            print(f"Dry run mode: {'ON' if enabled else 'OFF'}")
        
        elif action == "normal":
            enabled = guardrails.set_dry_run(False)
            print(f"Dry run mode: {'OFF' if not enabled else 'ON'}")
        
        elif action == "brake":
            enabled = guardrails.set_emergency_brake(True)
            print("🚨 EMERGENCY BRAKE ACTIVATED")
        
        elif action == "release":
            enabled = guardrails.set_emergency_brake(False)
            print("✅ Emergency brake released")
        
        else:
            print(f"Unknown action: {action}")
    
    else:
        guardrails = ActionGuardrails()
        print(guardrails.generate_report())


if __name__ == "__main__":
    main()
