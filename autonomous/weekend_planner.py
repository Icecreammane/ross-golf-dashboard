#!/usr/bin/env python3
"""
Weekend Build Planner

Plans and suggests ambitious 8-12 hour projects for weekends.
Friday: Review and suggest
Saturday: Select and execute
Sunday: Ship complete system
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from build_scheduler import BuildScheduler, BuildTask, Priority, TimeWindow

class WeekendPlanner:
    def __init__(self):
        self.scheduler = BuildScheduler()
        self.plan_file = "autonomous/data/weekend_plan.json"
        self.current_plan = None
        self.load_plan()
    
    def load_plan(self):
        """Load current weekend plan"""
        if os.path.exists(self.plan_file):
            with open(self.plan_file, 'r') as f:
                self.current_plan = json.load(f)
    
    def save_plan(self):
        """Save weekend plan"""
        if self.current_plan:
            os.makedirs(os.path.dirname(self.plan_file), exist_ok=True)
            with open(self.plan_file, 'w') as f:
                json.dump(self.current_plan, f, indent=2)
    
    def is_friday_evening(self) -> bool:
        """Check if it's Friday evening (5pm-11pm)"""
        now = datetime.now()
        return now.weekday() == 4 and 17 <= now.hour < 23
    
    def is_weekend(self) -> bool:
        """Check if it's weekend (Saturday/Sunday)"""
        return datetime.now().weekday() in [5, 6]
    
    def generate_weekend_options(self) -> List[Dict]:
        """Generate weekend project options"""
        # Get weekend-appropriate tasks (8-12 hours)
        weekend_tasks = [
            task for task in self.scheduler.tasks
            if task.status == "queued" and 8 <= task.estimated_hours <= 12
        ]
        
        # Sort by priority score
        weekend_tasks.sort(key=lambda t: self.scheduler.calculate_priority_score(t), reverse=True)
        
        options = []
        for task in weekend_tasks[:5]:  # Top 5 options
            options.append({
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "estimated_hours": task.estimated_hours,
                "category": task.category,
                "priority": task.priority.value,
                "priority_score": round(self.scheduler.calculate_priority_score(task), 2),
                "breakdown": self._generate_task_breakdown(task)
            })
        
        return options
    
    def _generate_task_breakdown(self, task: BuildTask) -> List[str]:
        """Generate phase breakdown for a task"""
        # Simple phase breakdown based on category
        phases = {
            "Performance optimization": [
                "Profile and identify bottlenecks",
                "Design optimization approach",
                "Implement optimizations",
                "Test and measure improvements",
                "Document changes"
            ],
            "New features": [
                "Design feature architecture",
                "Build core functionality",
                "Add error handling",
                "Test thoroughly",
                "Write documentation",
                "Deploy and monitor"
            ],
            "Infrastructure": [
                "Plan architecture",
                "Set up core infrastructure",
                "Implement automation",
                "Test and validate",
                "Monitor and document"
            ],
            "Research/analysis": [
                "Gather data and context",
                "Analyze findings",
                "Prototype solutions",
                "Test and validate",
                "Document recommendations"
            ]
        }
        
        category_phases = phases.get(task.category, [
            "Plan and design",
            "Implement core functionality",
            "Test and validate",
            "Polish and document"
        ])
        
        # Estimate time per phase
        hours_per_phase = task.estimated_hours / len(category_phases)
        
        breakdown = []
        for phase in category_phases:
            breakdown.append(f"{phase} ({hours_per_phase:.1f}h)")
        
        return breakdown
    
    def present_friday_options(self) -> str:
        """Present weekend options on Friday evening"""
        options = self.generate_weekend_options()
        
        if not options:
            return "No weekend-sized projects in queue. Consider adding some ambitious builds!"
        
        message = "🎯 **Weekend Build Options**\n\n"
        message += "Ready to tackle something big this weekend? Here are the top candidates:\n\n"
        
        for i, option in enumerate(options, 1):
            message += f"**Option {i}: {option['title']}**\n"
            message += f"⏱️ Estimated: {option['estimated_hours']} hours\n"
            message += f"🎯 Category: {option['category']}\n"
            message += f"📊 Priority: {option['priority']}/5 (score: {option['priority_score']})\n"
            message += f"\n📝 {option['description']}\n"
            message += f"\n**Phase Breakdown:**\n"
            for phase in option['breakdown']:
                message += f"  • {phase}\n"
            message += "\n---\n\n"
        
        message += "Which one interests you? Or should I suggest something else?"
        
        return message
    
    def select_weekend_project(self, task_id: str) -> bool:
        """Select a project for weekend execution"""
        task = next((t for t in self.scheduler.tasks if t.id == task_id), None)
        if not task:
            return False
        
        self.current_plan = {
            "created_at": datetime.now().isoformat(),
            "task_id": task_id,
            "title": task.title,
            "description": task.description,
            "estimated_hours": task.estimated_hours,
            "phases": self._generate_task_breakdown(task),
            "status": "selected",
            "started_at": None,
            "completed_phases": [],
            "current_phase": None
        }
        
        self.save_plan()
        return True
    
    def start_weekend_execution(self) -> Dict:
        """Start weekend project execution"""
        if not self.current_plan:
            return {"success": False, "reason": "No project selected"}
        
        if not self.is_weekend():
            return {"success": False, "reason": "Not weekend"}
        
        self.current_plan["status"] = "in_progress"
        self.current_plan["started_at"] = datetime.now().isoformat()
        self.current_plan["current_phase"] = self.current_plan["phases"][0]
        self.save_plan()
        
        return {
            "success": True,
            "project": self.current_plan["title"],
            "estimated_hours": self.current_plan["estimated_hours"],
            "current_phase": self.current_plan["current_phase"]
        }
    
    def complete_phase(self, phase_name: str) -> Dict:
        """Mark a phase as completed"""
        if not self.current_plan:
            return {"success": False, "reason": "No active plan"}
        
        self.current_plan["completed_phases"].append({
            "phase": phase_name,
            "completed_at": datetime.now().isoformat()
        })
        
        # Move to next phase
        phases = self.current_plan["phases"]
        completed_count = len(self.current_plan["completed_phases"])
        
        if completed_count < len(phases):
            self.current_plan["current_phase"] = phases[completed_count]
        else:
            self.current_plan["current_phase"] = None
            self.current_plan["status"] = "completed"
            
            # Mark task as completed
            self.scheduler.complete_task(self.current_plan["task_id"], success=True)
        
        self.save_plan()
        
        return {
            "success": True,
            "completed_phases": completed_count,
            "total_phases": len(phases),
            "next_phase": self.current_plan["current_phase"],
            "project_complete": self.current_plan["status"] == "completed"
        }
    
    def get_weekend_progress(self) -> Dict:
        """Get current weekend project progress"""
        if not self.current_plan:
            return {"active": False}
        
        completed_count = len(self.current_plan["completed_phases"])
        total_phases = len(self.current_plan["phases"])
        progress_percent = (completed_count / total_phases) * 100
        
        # Calculate time spent
        time_spent = 0
        if self.current_plan.get("started_at"):
            started = datetime.fromisoformat(self.current_plan["started_at"])
            time_spent = (datetime.now() - started).total_seconds() / 3600
        
        return {
            "active": True,
            "project": self.current_plan["title"],
            "status": self.current_plan["status"],
            "progress_percent": round(progress_percent, 1),
            "completed_phases": completed_count,
            "total_phases": total_phases,
            "current_phase": self.current_plan["current_phase"],
            "time_spent_hours": round(time_spent, 1),
            "estimated_hours": self.current_plan["estimated_hours"],
            "on_track": time_spent <= self.current_plan["estimated_hours"] if time_spent > 0 else True
        }
    
    def generate_sunday_summary(self) -> str:
        """Generate Sunday evening project summary"""
        if not self.current_plan:
            return "No weekend project was active"
        
        progress = self.get_weekend_progress()
        
        summary = f"🎉 **Weekend Project Summary**\n\n"
        summary += f"**Project:** {self.current_plan['title']}\n\n"
        
        if progress["status"] == "completed":
            summary += "✅ **Status:** COMPLETED!\n\n"
            summary += f"**Phases completed:** {progress['completed_phases']}/{progress['total_phases']}\n"
            summary += f"**Time spent:** {progress['time_spent_hours']:.1f}h / {progress['estimated_hours']}h\n\n"
            
            if progress["time_spent_hours"] <= progress["estimated_hours"]:
                summary += "🎯 Finished on schedule!\n"
            else:
                summary += f"⏱️ Took {progress['time_spent_hours'] - progress['estimated_hours']:.1f}h extra\n"
            
            summary += "\n**All phases completed:**\n"
            for phase_data in self.current_plan["completed_phases"]:
                summary += f"  ✅ {phase_data['phase']}\n"
        
        elif progress["status"] == "in_progress":
            summary += f"🏗️ **Status:** IN PROGRESS ({progress['progress_percent']:.0f}% complete)\n\n"
            summary += f"**Completed:** {progress['completed_phases']}/{progress['total_phases']} phases\n"
            summary += f"**Current:** {progress['current_phase']}\n"
            summary += f"**Time spent:** {progress['time_spent_hours']:.1f}h / {progress['estimated_hours']}h\n\n"
            
            summary += "**Completed phases:**\n"
            for phase_data in self.current_plan["completed_phases"]:
                summary += f"  ✅ {phase_data['phase']}\n"
            
            summary += "\n**Remaining phases:**\n"
            remaining = self.current_plan["phases"][progress['completed_phases']:]
            for phase in remaining:
                summary += f"  ⏳ {phase}\n"
            
            summary += "\nContinue during the week, or tackle next weekend?"
        
        return summary

def main():
    """CLI interface"""
    import sys
    
    planner = WeekendPlanner()
    
    if len(sys.argv) < 2:
        print("Usage: weekend_planner.py [command]")
        print("Commands: suggest, select, start, progress, complete, summary")
        return
    
    command = sys.argv[1]
    
    if command == "suggest":
        message = planner.present_friday_options()
        print(message)
    
    elif command == "select":
        if len(sys.argv) < 3:
            print("Usage: select <task_id>")
            return
        
        task_id = sys.argv[2]
        if planner.select_weekend_project(task_id):
            print(f"✅ Selected project: {planner.current_plan['title']}")
        else:
            print("❌ Task not found")
    
    elif command == "start":
        result = planner.start_weekend_execution()
        print(json.dumps(result, indent=2))
    
    elif command == "progress":
        progress = planner.get_weekend_progress()
        print(json.dumps(progress, indent=2))
    
    elif command == "complete":
        if len(sys.argv) < 3:
            print("Usage: complete <phase_name>")
            return
        
        phase = sys.argv[2]
        result = planner.complete_phase(phase)
        print(json.dumps(result, indent=2))
    
    elif command == "summary":
        summary = planner.generate_sunday_summary()
        print(summary)

if __name__ == "__main__":
    main()
