#!/usr/bin/env python3
"""
Intervention Engine - Real-time monitoring and intervention triggering
Runs as background process or called during heartbeats
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from accountability.predictor import ProcrastinationPredictor
from accountability.pattern_tracker import PatternTracker

class InterventionEngine:
    def __init__(self, workspace_root: str = "/Users/clawdbot/clawd"):
        self.workspace = Path(workspace_root)
        self.predictor = ProcrastinationPredictor(workspace_root)
        self.tracker = PatternTracker(workspace_root)
        
        self.state_file = self.workspace / "memory" / "patterns" / "intervention-state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.intervention_log = self.workspace / "memory" / "patterns" / "interventions.jsonl"
    
    def _load_state(self) -> Dict[str, Any]:
        """Load intervention state"""
        if not self.state_file.exists():
            return {
                "last_intervention_time": None,
                "last_check_time": None,
                "total_interventions": 0,
                "successful_interventions": 0
            }
        
        with open(self.state_file, "r") as f:
            return json.load(f)
    
    def _save_state(self, state: Dict[str, Any]):
        """Save intervention state"""
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)
    
    def check_and_intervene(
        self,
        scheduled_task: Optional[str] = None,
        force: bool = False
    ) -> Optional[str]:
        """
        Check if intervention is needed and generate message
        
        Args:
            scheduled_task: Current task Ross should be working on
            force: Force intervention regardless of rules
        
        Returns:
            Intervention message if needed, None otherwise
        """
        state = self._load_state()
        
        # Get prediction
        prediction = self.predictor.predict_procrastination()
        
        # Parse last intervention time
        last_intervention = None
        if state.get("last_intervention_time"):
            last_intervention = datetime.fromisoformat(state["last_intervention_time"])
        
        # Decide if we should intervene
        should_send = force or self.predictor.should_intervene(prediction, last_intervention)
        
        if not should_send:
            # Update check time
            state["last_check_time"] = datetime.now().isoformat()
            self._save_state(state)
            return None
        
        # Generate intervention
        message = self.predictor.generate_intervention(prediction, scheduled_task)
        
        if not message:
            return None
        
        # Log intervention
        intervention_entry = {
            "timestamp": int(datetime.now().timestamp()),
            "datetime": datetime.now().isoformat(),
            "risk_level": prediction["risk_level"],
            "confidence": prediction["confidence"],
            "scheduled_task": scheduled_task,
            "message": message,
            "prediction": prediction
        }
        
        with open(self.intervention_log, "a") as f:
            f.write(json.dumps(intervention_entry) + "\n")
        
        # Update state
        state["last_intervention_time"] = datetime.now().isoformat()
        state["last_check_time"] = datetime.now().isoformat()
        state["total_interventions"] += 1
        self._save_state(state)
        
        return message
    
    def log_intervention_outcome(
        self,
        successful: bool,
        notes: Optional[str] = None
    ):
        """
        Log whether the intervention worked
        
        Args:
            successful: Did Ross complete the task after intervention?
            notes: Additional context
        """
        state = self._load_state()
        
        if successful:
            state["successful_interventions"] += 1
        
        # Log outcome
        outcome_entry = {
            "timestamp": int(datetime.now().timestamp()),
            "datetime": datetime.now().isoformat(),
            "successful": successful,
            "notes": notes,
            "success_rate": state["successful_interventions"] / state["total_interventions"] if state["total_interventions"] > 0 else 0
        }
        
        outcome_file = self.workspace / "memory" / "patterns" / "intervention-outcomes.jsonl"
        with open(outcome_file, "a") as f:
            f.write(json.dumps(outcome_entry) + "\n")
        
        self._save_state(state)
    
    def get_effectiveness_stats(self) -> Dict[str, Any]:
        """Get intervention effectiveness statistics"""
        state = self._load_state()
        
        total = state.get("total_interventions", 0)
        successful = state.get("successful_interventions", 0)
        
        return {
            "total_interventions": total,
            "successful_interventions": successful,
            "success_rate": successful / total if total > 0 else 0,
            "last_intervention": state.get("last_intervention_time"),
            "last_check": state.get("last_check_time")
        }
    
    def get_status_report(self) -> str:
        """Generate human-readable status report"""
        stats = self.get_effectiveness_stats()
        prediction = self.predictor.predict_procrastination()
        
        report = "# Intervention Engine Status\n\n"
        
        report += f"**Current Risk**: {prediction['risk_level'].upper()} "
        report += f"({prediction['confidence']*100:.0f}% confidence)\n\n"
        
        report += "## Effectiveness Stats\n\n"
        report += f"- Total interventions: {stats['total_interventions']}\n"
        report += f"- Successful: {stats['successful_interventions']}\n"
        report += f"- Success rate: {stats['success_rate']*100:.0f}%\n"
        
        if stats['last_intervention']:
            last = datetime.fromisoformat(stats['last_intervention'])
            report += f"- Last intervention: {last.strftime('%Y-%m-%d %I:%M %p')}\n"
        
        return report


# Heartbeat integration function
def heartbeat_check(scheduled_task: Optional[str] = None) -> Optional[str]:
    """
    Called during heartbeats to check if intervention needed
    
    Returns intervention message or None
    """
    engine = InterventionEngine()
    return engine.check_and_intervene(scheduled_task)


# CLI interface
if __name__ == "__main__":
    import sys
    
    engine = InterventionEngine()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            task = sys.argv[2] if len(sys.argv) > 2 else None
            message = engine.check_and_intervene(task)
            if message:
                print(message)
            else:
                print("✅ No intervention needed")
        
        elif command == "status":
            print(engine.get_status_report())
        
        elif command == "success":
            notes = sys.argv[2] if len(sys.argv) > 2 else None
            engine.log_intervention_outcome(True, notes)
            print("✅ Logged successful intervention")
        
        elif command == "failure":
            notes = sys.argv[2] if len(sys.argv) > 2 else None
            engine.log_intervention_outcome(False, notes)
            print("❌ Logged failed intervention")
        
        else:
            print("Unknown command. Use: check, status, success, failure")
    else:
        print(engine.get_status_report())
