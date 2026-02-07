#!/usr/bin/env python3
"""
Overnight Execution Framework

Orchestrates autonomous work during sleep hours (11pm-7am).
Spawns sub-agents, monitors progress, generates completion reports.
"""

import json
import os
import sys
from datetime import datetime, time as dt_time
from typing import Dict, List
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from build_scheduler import BuildScheduler, TimeWindow
from autonomous_queue import AutonomousQueue
from context_scheduler import ContextScheduler, Context
from problem_predictor import ProblemPredictor
from pattern_learner import PatternLearner

class OvernightRunner:
    def __init__(self):
        self.queue = AutonomousQueue()
        self.scheduler = BuildScheduler()
        self.context = ContextScheduler()
        self.predictor = ProblemPredictor()
        self.patterns = PatternLearner()
        self.execution_log = "autonomous/logs/overnight_execution.log"
        self.current_session = None
    
    def is_overnight_hours(self) -> bool:
        """Check if it's overnight execution time (11pm-7am)"""
        now = datetime.now()
        return now.hour >= 23 or now.hour < 7
    
    def start_overnight_session(self) -> Dict:
        """Start overnight execution session"""
        if not self.is_overnight_hours():
            return {
                "success": False,
                "reason": "Not overnight hours (11pm-7am)",
                "current_hour": datetime.now().hour
            }
        
        # Set context
        self.context.set_context(Context.SLEEPING, explicit=True)
        
        # Start session
        self.current_session = {
            "session_id": f"overnight_{int(datetime.now().timestamp())}",
            "started_at": datetime.now().isoformat(),
            "phase": "started",
            "tasks_spawned": [],
            "tasks_completed": [],
            "problems_detected": [],
            "problems_fixed": []
        }
        
        self._log("🌙 Overnight session started")
        
        # Run the overnight workflow
        self._run_overnight_workflow()
        
        return {
            "success": True,
            "session_id": self.current_session["session_id"],
            "tasks_queued": len(self.current_session["tasks_spawned"])
        }
    
    def _run_overnight_workflow(self):
        """Execute overnight workflow"""
        # Phase 1: Check for problems (11:00pm)
        self._log("Phase 1: Scanning for problems...")
        self.current_session["phase"] = "scanning"
        
        problems = self.predictor.predict_problems()
        self.current_session["problems_detected"] = [p.id for p in problems]
        self._log(f"Found {len(problems)} potential problems")
        
        # Auto-fix problems
        fixes = self.predictor.auto_fix_problems()
        self.current_session["problems_fixed"] = [f["problem_id"] for f in fixes]
        self._log(f"Auto-fixed {len(fixes)} problems")
        
        # Phase 2: Check patterns and pre-build (11:05pm)
        self._log("Phase 2: Checking patterns...")
        self.current_session["phase"] = "patterns"
        
        suggestions = self.patterns.suggest_pre_builds()
        for suggestion in suggestions:
            if suggestion["confidence"] >= 0.8:
                self._log(f"Pre-building for pattern: {suggestion['description']}")
        
        # Phase 3: Schedule and spawn builds (11:05pm - 6:30am)
        self._log("Phase 3: Scheduling builds...")
        self.current_session["phase"] = "building"
        
        # Get overnight tasks
        overnight_tasks = self.scheduler.get_available_tasks(TimeWindow.OVERNIGHT)
        self._log(f"Found {len(overnight_tasks)} overnight tasks available")
        
        # Respect max concurrent limit for overnight
        max_concurrent = self.context.get_max_concurrent_builds(Context.SLEEPING)
        
        spawned_count = 0
        for task in overnight_tasks[:max_concurrent]:
            if task.auto_approve or task.category in ["Performance optimization", "Bug fixes", "Infrastructure"]:
                agent = self.queue.spawn_builder(task)
                if agent:
                    self.current_session["tasks_spawned"].append(task.id)
                    self._log(f"Spawned: {task.title}")
                    spawned_count += 1
        
        self._log(f"Spawned {spawned_count} build tasks")
        
        # Phase 4: Monitor throughout night (continuous)
        self._log("Phase 4: Monitoring builds...")
        self.current_session["phase"] = "monitoring"
        
        # Check system resources
        if not self.queue._check_system_resources():
            self._log("⚠️ System resources high, throttling")
        
        # Phase 5: Generate completion report (6:30am)
        # This would be triggered by cron
    
    def generate_completion_report(self) -> Dict:
        """Generate overnight completion report"""
        if not self.current_session:
            return {"error": "No active session"}
        
        self._log("Phase 5: Generating completion report...")
        self.current_session["phase"] = "reporting"
        
        # Get progress
        progress = self.queue.track_progress()
        
        # Get completed tasks
        completed = []
        in_progress = []
        
        for task_id in self.current_session["tasks_spawned"]:
            task = next((t for t in self.scheduler.tasks if t.id == task_id), None)
            if not task:
                continue
            
            if task.status == "completed":
                completed.append({
                    "id": task.id,
                    "title": task.title,
                    "category": task.category,
                    "hours": task.estimated_hours
                })
            elif task.status == "in_progress":
                agent = next((a for a in self.queue.active_agents if a.task_id == task_id), None)
                if agent:
                    runtime = (datetime.now() - agent.started_at).total_seconds() / 3600
                    in_progress.append({
                        "id": task.id,
                        "title": task.title,
                        "runtime_hours": round(runtime, 2),
                        "estimated_hours": task.estimated_hours
                    })
        
        report = {
            "session_id": self.current_session["session_id"],
            "started_at": self.current_session["started_at"],
            "completed_at": datetime.now().isoformat(),
            "duration_hours": self._calculate_session_duration(),
            "tasks_spawned": len(self.current_session["tasks_spawned"]),
            "tasks_completed": len(completed),
            "tasks_in_progress": len(in_progress),
            "completed_tasks": completed,
            "in_progress_tasks": in_progress,
            "problems_detected": len(self.current_session["problems_detected"]),
            "problems_fixed": len(self.current_session["problems_fixed"]),
            "total_hours_shipped": sum(t["hours"] for t in completed)
        }
        
        # Save report
        report_file = f"autonomous/logs/overnight_report_{datetime.now().strftime('%Y-%m-%d')}.json"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self._log(f"✅ Completion report generated: {report_file}")
        
        return report
    
    def _calculate_session_duration(self) -> float:
        """Calculate session duration in hours"""
        if not self.current_session:
            return 0.0
        
        started = datetime.fromisoformat(self.current_session["started_at"])
        duration = (datetime.now() - started).total_seconds() / 3600
        return round(duration, 2)
    
    def prepare_morning_brief(self) -> str:
        """Prepare morning brief text"""
        report = self.generate_completion_report()
        
        brief = "🌅 **Overnight Build Report**\n\n"
        
        if report["tasks_completed"] > 0:
            brief += "🚀 **What Shipped Overnight:**\n"
            for task in report["completed_tasks"]:
                brief += f"  ✅ {task['title']} ({task['category']})\n"
            brief += f"\n📊 Total: {report['total_hours_shipped']:.1f} hours of work completed\n\n"
        else:
            brief += "⏳ No tasks completed overnight\n\n"
        
        if report["tasks_in_progress"] > 0:
            brief += "🏗️ **Still Building:**\n"
            for task in report["in_progress_tasks"]:
                progress = (task["runtime_hours"] / task["estimated_hours"]) * 100
                brief += f"  🔨 {task['title']} ({progress:.0f}% complete)\n"
            brief += "\n"
        
        if report["problems_fixed"] > 0:
            brief += f"🔧 **Auto-Fixed:** {report['problems_fixed']} problems detected and resolved\n\n"
        
        # Add pattern suggestions
        suggestions = self.patterns.suggest_pre_builds()
        if suggestions:
            brief += "💡 **Pre-Built Based on Patterns:**\n"
            for sugg in suggestions[:3]:
                brief += f"  • {sugg['description']}\n"
        
        brief += f"\n⏰ Session duration: {report['duration_hours']:.1f} hours"
        
        return brief
    
    def _log(self, message: str):
        """Log overnight execution events"""
        os.makedirs(os.path.dirname(self.execution_log), exist_ok=True)
        with open(self.execution_log, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")

def main():
    """CLI interface and cron entry point"""
    import sys
    
    runner = OvernightRunner()
    
    if len(sys.argv) < 2:
        # No command = run overnight session (for cron)
        if runner.is_overnight_hours():
            result = runner.start_overnight_session()
            print(json.dumps(result, indent=2))
        else:
            print("Not overnight hours")
        return
    
    command = sys.argv[1]
    
    if command == "start":
        result = runner.start_overnight_session()
        print(json.dumps(result, indent=2))
    
    elif command == "report":
        report = runner.generate_completion_report()
        print(json.dumps(report, indent=2))
    
    elif command == "brief":
        brief = runner.prepare_morning_brief()
        print(brief)
    
    elif command == "is-overnight":
        print("yes" if runner.is_overnight_hours() else "no")

if __name__ == "__main__":
    main()
