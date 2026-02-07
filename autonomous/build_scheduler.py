#!/usr/bin/env python3
"""
Time-Based Build Scoping System

Categorizes builds by time windows and matches them to Ross's availability.
Produces build_queue.json with scheduled work.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

class TimeWindow(Enum):
    QUICK_WIN = "quick_win"  # 1-2 hrs: Weeknight sessions (7pm-11pm)
    OVERNIGHT = "overnight"  # 4-6 hrs: Sleep window (11pm-7am)
    WORK_HOURS = "work_hours"  # 8 hrs: Office time (9am-5pm)
    WEEKEND = "weekend"  # 8-12 hrs: Saturday/Sunday

class Priority(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    BACKLOG = 1

class BuildTask:
    def __init__(self, id: str, title: str, description: str, 
                 estimated_hours: float, category: str, priority: Priority,
                 dependencies: List[str] = None, auto_approve: bool = False):
        self.id = id
        self.title = title
        self.description = description
        self.estimated_hours = estimated_hours
        self.category = category
        self.priority = priority
        self.dependencies = dependencies or []
        self.auto_approve = auto_approve
        self.created_at = datetime.now().isoformat()
        self.scheduled_for = None
        self.status = "queued"
        
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "estimated_hours": self.estimated_hours,
            "category": self.category,
            "priority": self.priority.value,
            "dependencies": self.dependencies,
            "auto_approve": self.auto_approve,
            "created_at": self.created_at,
            "scheduled_for": self.scheduled_for,
            "status": self.status
        }
    
    @staticmethod
    def from_dict(data):
        task = BuildTask(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            estimated_hours=data["estimated_hours"],
            category=data["category"],
            priority=Priority(data["priority"]),
            dependencies=data.get("dependencies", []),
            auto_approve=data.get("auto_approve", False)
        )
        task.created_at = data["created_at"]
        task.scheduled_for = data.get("scheduled_for")
        task.status = data.get("status", "queued")
        return task

class BuildScheduler:
    def __init__(self, queue_file="autonomous/data/build_queue.json"):
        self.queue_file = queue_file
        self.tasks: List[BuildTask] = []
        self.load_queue()
    
    def load_queue(self):
        """Load existing build queue"""
        if os.path.exists(self.queue_file):
            with open(self.queue_file, 'r') as f:
                data = json.load(f)
                self.tasks = [BuildTask.from_dict(t) for t in data.get("tasks", [])]
    
    def save_queue(self):
        """Save build queue to disk"""
        os.makedirs(os.path.dirname(self.queue_file), exist_ok=True)
        data = {
            "last_updated": datetime.now().isoformat(),
            "tasks": [t.to_dict() for t in self.tasks]
        }
        with open(self.queue_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_task(self, task: BuildTask) -> str:
        """Add a task to the queue"""
        self.tasks.append(task)
        self.save_queue()
        return task.id
    
    def get_time_window(self, estimated_hours: float) -> TimeWindow:
        """Determine appropriate time window for a task"""
        if estimated_hours <= 2:
            return TimeWindow.QUICK_WIN
        elif estimated_hours <= 6:
            return TimeWindow.OVERNIGHT
        elif estimated_hours <= 8:
            return TimeWindow.WORK_HOURS
        else:
            return TimeWindow.WEEKEND
    
    def get_available_tasks(self, time_window: TimeWindow) -> List[BuildTask]:
        """Get tasks appropriate for a given time window"""
        available = []
        
        for task in self.tasks:
            if task.status != "queued":
                continue
            
            # Check dependencies
            if task.dependencies:
                deps_complete = all(
                    any(t.id == dep_id and t.status == "completed" for t in self.tasks)
                    for dep_id in task.dependencies
                )
                if not deps_complete:
                    continue
            
            # Match time window
            task_window = self.get_time_window(task.estimated_hours)
            
            # Quick wins can run in any window
            # Longer tasks need their specific windows
            if time_window == TimeWindow.QUICK_WIN:
                if task_window == TimeWindow.QUICK_WIN:
                    available.append(task)
            elif time_window == TimeWindow.OVERNIGHT:
                if task_window in [TimeWindow.QUICK_WIN, TimeWindow.OVERNIGHT]:
                    available.append(task)
            elif time_window == TimeWindow.WORK_HOURS:
                if task_window != TimeWindow.WEEKEND:
                    available.append(task)
            else:  # WEEKEND
                available.append(task)
        
        # Sort by priority score (priority * effort)
        available.sort(key=lambda t: t.priority.value * (1 / t.estimated_hours), reverse=True)
        return available
    
    def calculate_priority_score(self, task: BuildTask) -> float:
        """Calculate priority score: impact × (1/effort)"""
        return task.priority.value * (1 / task.estimated_hours)
    
    def schedule_tasks(self, time_window: TimeWindow, available_hours: float) -> List[BuildTask]:
        """Schedule tasks for a given time window"""
        available_tasks = self.get_available_tasks(time_window)
        scheduled = []
        remaining_hours = available_hours
        
        for task in available_tasks:
            if task.estimated_hours <= remaining_hours:
                task.scheduled_for = time_window.value
                scheduled.append(task)
                remaining_hours -= task.estimated_hours
                
                if remaining_hours < 1:  # Less than 1 hour left
                    break
        
        self.save_queue()
        return scheduled
    
    def get_current_time_window(self) -> Optional[TimeWindow]:
        """Determine current time window based on time of day"""
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()  # 0=Monday, 6=Sunday
        
        # Weekend (Saturday/Sunday)
        if day_of_week >= 5:
            return TimeWindow.WEEKEND
        
        # Weekday time windows
        if 23 <= hour or hour < 7:  # 11pm-7am
            return TimeWindow.OVERNIGHT
        elif 9 <= hour < 17:  # 9am-5pm
            return TimeWindow.WORK_HOURS
        elif 19 <= hour < 23:  # 7pm-11pm
            return TimeWindow.QUICK_WIN
        
        return None
    
    def get_next_scheduled_tasks(self, limit: int = 5) -> List[BuildTask]:
        """Get next tasks to execute"""
        current_window = self.get_current_time_window()
        if not current_window:
            return []
        
        scheduled = self.get_available_tasks(current_window)
        return scheduled[:limit]
    
    def complete_task(self, task_id: str, success: bool = True):
        """Mark a task as completed"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = "completed" if success else "failed"
                self.save_queue()
                break
    
    def get_stats(self) -> Dict:
        """Get queue statistics"""
        total = len(self.tasks)
        queued = sum(1 for t in self.tasks if t.status == "queued")
        completed = sum(1 for t in self.tasks if t.status == "completed")
        failed = sum(1 for t in self.tasks if t.status == "failed")
        
        return {
            "total": total,
            "queued": queued,
            "completed": completed,
            "failed": failed,
            "completion_rate": completed / total if total > 0 else 0
        }

def main():
    """CLI interface for build scheduler"""
    import sys
    
    scheduler = BuildScheduler()
    
    if len(sys.argv) < 2:
        print("Usage: build_scheduler.py [command]")
        print("Commands: list, schedule, stats, next")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        print("\n📋 Build Queue:\n")
        for task in scheduler.tasks:
            status_icon = {"queued": "⏳", "completed": "✅", "failed": "❌"}.get(task.status, "❓")
            print(f"{status_icon} [{task.id}] {task.title}")
            print(f"   {task.estimated_hours}h | {task.category} | Priority: {task.priority.value}")
            print(f"   {task.description}\n")
    
    elif command == "schedule":
        current = scheduler.get_current_time_window()
        if current:
            print(f"\n⏰ Current window: {current.value}\n")
            tasks = scheduler.get_next_scheduled_tasks()
            for task in tasks:
                print(f"• {task.title} ({task.estimated_hours}h)")
        else:
            print("No active time window")
    
    elif command == "stats":
        stats = scheduler.get_stats()
        print("\n📊 Queue Statistics:\n")
        print(f"Total tasks: {stats['total']}")
        print(f"Queued: {stats['queued']}")
        print(f"Completed: {stats['completed']}")
        print(f"Failed: {stats['failed']}")
        print(f"Completion rate: {stats['completion_rate']:.1%}")
    
    elif command == "next":
        tasks = scheduler.get_next_scheduled_tasks(3)
        if tasks:
            print("\n🎯 Next tasks:\n")
            for i, task in enumerate(tasks, 1):
                print(f"{i}. {task.title} ({task.estimated_hours}h)")
        else:
            print("No tasks available for current time window")

if __name__ == "__main__":
    main()
