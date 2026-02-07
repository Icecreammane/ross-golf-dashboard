#!/usr/bin/env python3
"""
Autonomous Build Queue Manager

Manages the build queue, spawns sub-agents, tracks progress, generates reports.
Core orchestration system for autonomous operations.
"""

import json
import os
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from build_scheduler import BuildScheduler, BuildTask, Priority

class SubAgent:
    """Represents a spawned sub-agent working on a task"""
    def __init__(self, task_id: str, pid: Optional[int] = None):
        self.task_id = task_id
        self.pid = pid
        self.started_at = datetime.now()
        self.status = "running"
        self.output_log = f"autonomous/logs/subagent_{task_id}_{int(time.time())}.log"
    
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "pid": self.pid,
            "started_at": self.started_at.isoformat(),
            "status": self.status,
            "output_log": self.output_log,
            "runtime_minutes": (datetime.now() - self.started_at).total_seconds() / 60
        }

class AutonomousQueue:
    """Main queue manager for autonomous operations"""
    
    def __init__(self):
        self.scheduler = BuildScheduler()
        self.active_agents: List[SubAgent] = []
        self.max_concurrent = 3
        self.state_file = "autonomous/data/queue_state.json"
        self.load_state()
    
    def load_state(self):
        """Load active agent state"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                # Rebuild active agents (check if still running)
                for agent_data in data.get("active_agents", []):
                    agent = SubAgent(agent_data["task_id"], agent_data.get("pid"))
                    agent.started_at = datetime.fromisoformat(agent_data["started_at"])
                    agent.status = agent_data["status"]
                    agent.output_log = agent_data["output_log"]
                    
                    # Verify agent is actually running
                    if agent.pid and self._is_process_alive(agent.pid):
                        self.active_agents.append(agent)
                    else:
                        agent.status = "stopped"
    
    def save_state(self):
        """Save active agent state"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        data = {
            "last_updated": datetime.now().isoformat(),
            "active_agents": [a.to_dict() for a in self.active_agents]
        }
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _is_process_alive(self, pid: int) -> bool:
        """Check if a process is still running"""
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    
    def add_to_queue(self, title: str, description: str, estimated_hours: float,
                     category: str, priority: Priority, dependencies: List[str] = None,
                     auto_approve: bool = False) -> str:
        """Add a new task to the build queue"""
        task_id = f"task_{int(time.time())}_{len(self.scheduler.tasks)}"
        task = BuildTask(
            id=task_id,
            title=title,
            description=description,
            estimated_hours=estimated_hours,
            category=category,
            priority=priority,
            dependencies=dependencies,
            auto_approve=auto_approve
        )
        self.scheduler.add_task(task)
        
        # Log to memory
        self._log_queue_action(f"Added task: {title} ({estimated_hours}h, {category})")
        return task_id
    
    def spawn_builder(self, task: BuildTask) -> Optional[SubAgent]:
        """Spawn a sub-agent to work on a task"""
        if len(self.active_agents) >= self.max_concurrent:
            return None
        
        # Check system resources before spawning
        if not self._check_system_resources():
            self._log_queue_action("⚠️ System resources high, delaying spawn")
            return None
        
        # Create sub-agent
        agent = SubAgent(task.id)
        
        # Log to file
        os.makedirs(os.path.dirname(agent.output_log), exist_ok=True)
        
        # Build sub-agent command
        prompt = self._build_subagent_prompt(task)
        
        # For now, we log the intent - actual spawning would use clawdbot API
        self._log_subagent_spawn(task, agent, prompt)
        
        self.active_agents.append(agent)
        task.status = "in_progress"
        self.scheduler.save_queue()
        self.save_state()
        
        return agent
    
    def _build_subagent_prompt(self, task: BuildTask) -> str:
        """Build the prompt for a sub-agent"""
        return f"""You are a sub-agent spawned to complete a specific build task.

**Task ID:** {task.id}
**Title:** {task.title}
**Category:** {task.category}
**Estimated Time:** {task.estimated_hours} hours

**Description:**
{task.description}

**Your Mission:**
Complete this task autonomously. When done:
1. Test thoroughly
2. Update documentation
3. Log what you built
4. Report completion with summary

**Guidelines:**
- Work systematically
- Test as you build
- Document changes
- Be thorough, not rushed
- Ask if you hit blockers

Begin now."""
    
    def _log_subagent_spawn(self, task: BuildTask, agent: SubAgent, prompt: str):
        """Log sub-agent spawn details"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task.id,
            "title": task.title,
            "agent_log": agent.output_log,
            "prompt": prompt
        }
        
        log_file = "autonomous/logs/subagent_spawns.jsonl"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def _check_system_resources(self) -> bool:
        """Check if system has resources available"""
        try:
            # Check disk space
            import shutil
            stat = shutil.disk_usage('/')
            disk_percent = (stat.used / stat.total) * 100
            
            if disk_percent > 80:
                return False
            
            # Could add memory/CPU checks here
            return True
        except:
            return True  # Assume OK if we can't check
    
    def track_progress(self) -> List[Dict]:
        """Track progress of active sub-agents"""
        progress = []
        
        for agent in self.active_agents:
            task = next((t for t in self.scheduler.tasks if t.id == agent.task_id), None)
            if not task:
                continue
            
            runtime = (datetime.now() - agent.started_at).total_seconds() / 3600  # hours
            
            status = {
                "task_id": task.id,
                "title": task.title,
                "runtime_hours": round(runtime, 2),
                "estimated_hours": task.estimated_hours,
                "progress_percent": min(100, (runtime / task.estimated_hours) * 100),
                "status": agent.status,
                "log_file": agent.output_log
            }
            progress.append(status)
        
        return progress
    
    def generate_morning_report(self) -> Dict:
        """Generate morning report of overnight work"""
        # Get completed tasks from last 8 hours
        cutoff = datetime.now() - timedelta(hours=8)
        
        completed = []
        in_progress = []
        
        for task in self.scheduler.tasks:
            task_time = datetime.fromisoformat(task.created_at)
            
            if task.status == "completed" and task_time >= cutoff:
                completed.append({
                    "title": task.title,
                    "category": task.category,
                    "hours": task.estimated_hours
                })
            elif task.status == "in_progress":
                # Find agent
                agent = next((a for a in self.active_agents if a.task_id == task.id), None)
                if agent:
                    runtime = (datetime.now() - agent.started_at).total_seconds() / 3600
                    in_progress.append({
                        "title": task.title,
                        "runtime_hours": round(runtime, 2),
                        "estimated_hours": task.estimated_hours
                    })
        
        stats = self.scheduler.get_stats()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "completed_overnight": completed,
            "in_progress": in_progress,
            "queue_stats": stats,
            "total_hours_shipped": sum(t["hours"] for t in completed)
        }
        
        # Save report
        report_file = f"autonomous/logs/morning_report_{datetime.now().strftime('%Y-%m-%d')}.json"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def _log_queue_action(self, message: str):
        """Log queue management actions"""
        log_file = "autonomous/logs/queue_actions.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    
    def schedule_builds(self):
        """Schedule builds for current time window"""
        tasks = self.scheduler.get_next_scheduled_tasks(limit=5)
        
        for task in tasks:
            if len(self.active_agents) >= self.max_concurrent:
                break
            
            if task.auto_approve or task.category in ["Performance optimization", "Bug fixes", "Documentation"]:
                # Auto-spawn for approved categories
                agent = self.spawn_builder(task)
                if agent:
                    self._log_queue_action(f"Auto-spawned: {task.title}")

def main():
    """CLI interface"""
    import sys
    
    queue = AutonomousQueue()
    
    if len(sys.argv) < 2:
        print("Usage: autonomous_queue.py [command]")
        print("Commands: add, spawn, progress, report, schedule")
        return
    
    command = sys.argv[1]
    
    if command == "add":
        # Example: add "Task title" "Description" 2.5 "Performance optimization" high
        if len(sys.argv) < 7:
            print("Usage: add <title> <description> <hours> <category> <priority>")
            return
        
        title = sys.argv[2]
        desc = sys.argv[3]
        hours = float(sys.argv[4])
        category = sys.argv[5]
        priority_str = sys.argv[6].upper()
        priority = Priority[priority_str]
        
        task_id = queue.add_to_queue(title, desc, hours, category, priority)
        print(f"✅ Added task: {task_id}")
    
    elif command == "progress":
        progress = queue.track_progress()
        if progress:
            print("\n🏗️ Active Builds:\n")
            for p in progress:
                print(f"• {p['title']}")
                print(f"  Runtime: {p['runtime_hours']:.1f}h / {p['estimated_hours']}h ({p['progress_percent']:.0f}%)")
                print(f"  Log: {p['log_file']}\n")
        else:
            print("No active builds")
    
    elif command == "report":
        report = queue.generate_morning_report()
        print("\n🚀 Morning Report:\n")
        print(f"Completed overnight: {len(report['completed_overnight'])}")
        print(f"Total hours shipped: {report['total_hours_shipped']:.1f}h\n")
        
        if report['completed_overnight']:
            print("✅ Shipped:")
            for task in report['completed_overnight']:
                print(f"  • {task['title']} ({task['category']})")
        
        if report['in_progress']:
            print("\n🏗️ In Progress:")
            for task in report['in_progress']:
                print(f"  • {task['title']} ({task['runtime_hours']:.1f}h / {task['estimated_hours']}h)")
    
    elif command == "schedule":
        queue.schedule_builds()
        print("✅ Scheduled builds for current window")

if __name__ == "__main__":
    main()
