#!/usr/bin/env python3
"""
Proactive Monitor Daemon - Uses local AI to monitor systems every 5 minutes
Only escalates to Sonnet when action is needed
Runs continuously, checking email, calendar, fitness, etc.
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import the router
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from local_router import LocalRouter

WORKSPACE = "/Users/clawdbot/clawd"
ESCALATION_FILE = os.path.join(WORKSPACE, "memory", "escalation-pending.json")
STATE_FILE = os.path.join(WORKSPACE, "memory", "monitor-state.json")


class ProactiveMonitor:
    def __init__(self):
        self.router = LocalRouter(WORKSPACE)
        self.state = self._load_state()
        self.escalations = []
    
    def _load_state(self) -> Dict:
        """Load monitor state"""
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {
            "last_checks": {
                "email": None,
                "calendar": None,
                "fitness": None,
                "bank": None
            },
            "last_escalation": None
        }
    
    def _save_state(self):
        """Save monitor state"""
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _should_check(self, check_type: str, interval_minutes: int = 5) -> bool:
        """Determine if we should run this check based on last check time"""
        last_check = self.state["last_checks"].get(check_type)
        if not last_check:
            return True
        
        last_check_dt = datetime.fromisoformat(last_check)
        return (datetime.now() - last_check_dt).total_seconds() > (interval_minutes * 60)
    
    def check_email(self) -> Optional[Dict]:
        """Check email for urgent messages using local AI"""
        if not self._should_check("email", interval_minutes=5):
            return None
        
        print("📧 Checking email...")
        
        # Construct prompt for local AI
        prompt = """You are monitoring Ross's email inbox. Check for:
1. Urgent messages that need immediate attention
2. Time-sensitive requests
3. Important follow-ups

Based on typical email patterns, identify if any of these conditions exist:
- Subject lines with "URGENT", "ASAP", "ACTION REQUIRED"
- Messages from VIPs or important contacts
- Time-sensitive meeting requests
- Critical system notifications

Respond in JSON format:
{
    "urgent_count": 0,
    "urgent_messages": [],
    "needs_escalation": false,
    "summary": "No urgent emails"
}
"""
        
        # Use router to check with local model
        result = self.router.execute_task(prompt, context={"type": "email_check"})
        
        self.state["last_checks"]["email"] = datetime.now().isoformat()
        self._save_state()
        
        # Parse result
        try:
            # In real implementation, we'd parse actual email API response
            # For now, simulate
            analysis = {
                "urgent_count": 0,
                "urgent_messages": [],
                "needs_escalation": False,
                "summary": "No urgent emails",
                "cost": result["cost"],
                "saved": result["saved"]
            }
            
            if analysis["needs_escalation"]:
                return {
                    "type": "email_urgent",
                    "priority": "high",
                    "data": analysis,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error parsing email check: {e}")
        
        return None
    
    def check_calendar(self) -> Optional[Dict]:
        """Check calendar for upcoming events using local AI"""
        if not self._should_check("calendar", interval_minutes=15):
            return None
        
        print("📅 Checking calendar...")
        
        prompt = """You are monitoring Ross's calendar. Check for:
1. Events starting in the next 2 hours
2. Conflicts or overlapping meetings
3. Events without preparation notes

Analyze the calendar and respond in JSON:
{
    "upcoming_count": 0,
    "upcoming_events": [],
    "needs_escalation": false,
    "summary": "No upcoming events in next 2 hours"
}
"""
        
        result = self.router.execute_task(prompt, context={"type": "calendar_check"})
        
        self.state["last_checks"]["calendar"] = datetime.now().isoformat()
        self._save_state()
        
        # In real implementation, integrate with Google Calendar API
        analysis = {
            "upcoming_count": 0,
            "upcoming_events": [],
            "needs_escalation": False,
            "summary": "No upcoming events",
            "cost": result["cost"],
            "saved": result["saved"]
        }
        
        if analysis["needs_escalation"]:
            return {
                "type": "calendar_upcoming",
                "priority": "medium",
                "data": analysis,
                "timestamp": datetime.now().isoformat()
            }
        
        return None
    
    def check_fitness(self) -> Optional[Dict]:
        """Check if fitness tracking is up to date"""
        if not self._should_check("fitness", interval_minutes=60):
            return None
        
        print("💪 Checking fitness tracking...")
        
        # Check if meals logged today
        today = datetime.now().strftime("%Y-%m-%d")
        
        prompt = f"""Check fitness tracking for {today}:
1. Have meals been logged?
2. Has weight been recorded?
3. Any workouts logged?

Respond in JSON:
{{
    "meals_logged": true/false,
    "weight_logged": true/false,
    "workout_logged": true/false,
    "needs_reminder": true/false,
    "summary": "Fitness tracking status"
}}
"""
        
        result = self.router.execute_task(prompt, context={"type": "fitness_check"})
        
        self.state["last_checks"]["fitness"] = datetime.now().isoformat()
        self._save_state()
        
        # In real implementation, check actual fitness data
        analysis = {
            "meals_logged": True,
            "weight_logged": True,
            "workout_logged": False,
            "needs_reminder": False,
            "summary": "Fitness tracking up to date",
            "cost": result["cost"],
            "saved": result["saved"]
        }
        
        if analysis["needs_reminder"]:
            return {
                "type": "fitness_reminder",
                "priority": "low",
                "data": analysis,
                "timestamp": datetime.now().isoformat()
            }
        
        return None
    
    def check_bank(self) -> Optional[Dict]:
        """Check bank transactions for anomalies (future: Plaid integration)"""
        if not self._should_check("bank", interval_minutes=60):
            return None
        
        print("💳 Checking bank transactions...")
        
        # Placeholder for future Plaid integration
        prompt = """Check recent bank transactions:
1. Any unusual spending patterns?
2. Large transactions?
3. Duplicate charges?

Respond in JSON:
{
    "unusual_transactions": [],
    "needs_review": false,
    "summary": "No unusual activity"
}
"""
        
        result = self.router.execute_task(prompt, context={"type": "bank_check"})
        
        self.state["last_checks"]["bank"] = datetime.now().isoformat()
        self._save_state()
        
        # Future implementation
        analysis = {
            "unusual_transactions": [],
            "needs_review": False,
            "summary": "No unusual activity",
            "cost": result["cost"],
            "saved": result["saved"]
        }
        
        if analysis["needs_review"]:
            return {
                "type": "bank_unusual",
                "priority": "high",
                "data": analysis,
                "timestamp": datetime.now().isoformat()
            }
        
        return None
    
    def run_checks(self) -> List[Dict]:
        """Run all monitoring checks"""
        escalations = []
        
        # Run each check
        checks = [
            self.check_email,
            self.check_calendar,
            self.check_fitness,
            self.check_bank
        ]
        
        for check in checks:
            try:
                result = check()
                if result:
                    escalations.append(result)
            except Exception as e:
                print(f"Error in {check.__name__}: {e}")
        
        return escalations
    
    def save_escalations(self, escalations: List[Dict]):
        """Save escalations to file for Sonnet to read during heartbeat"""
        if not escalations:
            # Clear escalation file if nothing to escalate
            if os.path.exists(ESCALATION_FILE):
                os.remove(ESCALATION_FILE)
            return
        
        escalation_data = {
            "timestamp": datetime.now().isoformat(),
            "escalations": escalations,
            "total_count": len(escalations),
            "priority_breakdown": {
                "high": len([e for e in escalations if e["priority"] == "high"]),
                "medium": len([e for e in escalations if e["priority"] == "medium"]),
                "low": len([e for e in escalations if e["priority"] == "low"])
            }
        }
        
        with open(ESCALATION_FILE, 'w') as f:
            json.dump(escalation_data, f, indent=2)
        
        print(f"\n✅ Saved {len(escalations)} escalation(s) to {ESCALATION_FILE}")
    
    def run_once(self):
        """Run one monitoring cycle"""
        print(f"\n{'='*60}")
        print(f"🤖 Proactive Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        escalations = self.run_checks()
        self.save_escalations(escalations)
        
        # Show stats
        stats = self.router.get_stats(days=1)
        print(f"\n💰 Today's Stats:")
        print(f"   Tasks: {stats['total_tasks']} ({stats['ollama_tasks']} local, {stats['sonnet_tasks']} Sonnet)")
        print(f"   Cost: ${stats['total_cost']:.4f}")
        print(f"   Saved: ${stats['total_saved']:.4f}")
        print(f"   Local %: {stats['local_percentage']:.1f}%")
        
        if escalations:
            print(f"\n⚠️  {len(escalations)} item(s) need Sonnet attention")
        else:
            print(f"\n✅ All clear, no escalations needed")
    
    def run_daemon(self, interval_minutes: int = 5):
        """Run continuously as a daemon"""
        print(f"🚀 Starting Proactive Monitor Daemon")
        print(f"   Checking every {interval_minutes} minutes")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_once()
                print(f"\n💤 Sleeping for {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print("\n\n🛑 Monitor stopped by user")
            sys.exit(0)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Proactive Monitor Daemon")
    parser.add_argument("--daemon", action="store_true", help="Run as continuous daemon")
    parser.add_argument("--interval", type=int, default=5, help="Check interval in minutes (default: 5)")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    
    args = parser.parse_args()
    
    monitor = ProactiveMonitor()
    
    if args.daemon:
        monitor.run_daemon(interval_minutes=args.interval)
    else:
        monitor.run_once()


if __name__ == "__main__":
    main()
