#!/usr/bin/env python3
"""
Build Status Updater
Updates ~/clawd/logs/build-status.json to drive the Live Build Dashboard

Usage:
    from systems.build_status_updater import BuildStatus
    
    # Start a new build
    build = BuildStatus.create_build(
        title="New Feature Build",
        tasks=["Task 1", "Task 2", "Task 3"],
        priority="high",
        assigned_to="Jarvis",
        notes="Building cool stuff"
    )
    
    # Update progress
    build.update_task("Task 1", status="complete", progress=100)
    build.update_progress()
    
    # Mark complete
    build.complete()
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict
import hashlib

WORKSPACE = Path.home() / "clawd"
STATUS_FILE = WORKSPACE / "logs" / "build-status.json"


class BuildStatus:
    """Manage build status for the Live Build Dashboard."""
    
    def __init__(self, build_id: str, data: Dict):
        self.build_id = build_id
        self.data = data
    
    @classmethod
    def create_build(
        cls,
        title: str,
        tasks: List[str],
        priority: str = "medium",
        assigned_to: str = "Jarvis",
        notes: str = "",
        eta_hours: float = 2.0
    ) -> 'BuildStatus':
        """
        Create a new build and add to active builds.
        
        Args:
            title: Build title
            tasks: List of task names
            priority: 'high', 'medium', or 'low'
            assigned_to: Who's working on it
            notes: Additional context
            eta_hours: Estimated hours to completion
        
        Returns:
            BuildStatus instance
        """
        # Generate unique ID
        build_id = hashlib.md5(f"{title}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        now = datetime.now()
        eta = now + timedelta(hours=eta_hours)
        
        build_data = {
            'id': build_id,
            'title': title,
            'status': 'in_progress',
            'priority': priority,
            'started': now.isoformat(),
            'eta': eta.isoformat(),
            'progress': 0,
            'tasks': [
                {
                    'name': task,
                    'status': 'pending',
                    'progress': 0,
                    'deliverable': None
                }
                for task in tasks
            ],
            'assigned_to': assigned_to,
            'notes': notes
        }
        
        # Load current status
        status_data = _load_status()
        
        # Add to active builds
        status_data['active_builds'].append(build_data)
        status_data['last_updated'] = now.isoformat()
        
        # Save
        _save_status(status_data)
        
        return cls(build_id, build_data)
    
    @classmethod
    def get_build(cls, build_id: str) -> Optional['BuildStatus']:
        """Get existing build by ID."""
        status_data = _load_status()
        
        for build in status_data['active_builds']:
            if build['id'] == build_id:
                return cls(build_id, build)
        
        return None
    
    def update_task(
        self,
        task_name: str,
        status: str = None,
        progress: int = None,
        deliverable: str = None
    ):
        """
        Update a specific task.
        
        Args:
            task_name: Name of the task to update
            status: 'pending', 'in_progress', 'complete', 'failed'
            progress: 0-100
            deliverable: Path to deliverable file
        """
        for task in self.data['tasks']:
            if task['name'] == task_name:
                if status:
                    task['status'] = status
                if progress is not None:
                    task['progress'] = progress
                if deliverable:
                    task['deliverable'] = deliverable
                break
        
        self.update_progress()
        self._save()
    
    def update_progress(self):
        """Recalculate overall progress from tasks."""
        if not self.data['tasks']:
            return
        
        total_progress = sum(task['progress'] for task in self.data['tasks'])
        self.data['progress'] = total_progress // len(self.data['tasks'])
        
        self._save()
    
    def complete(self):
        """Mark build as complete and move to completed list."""
        self.data['status'] = 'complete'
        self.data['progress'] = 100
        self.data['completed'] = datetime.now().isoformat()
        
        status_data = _load_status()
        
        # Remove from active
        status_data['active_builds'] = [
            b for b in status_data['active_builds'] 
            if b['id'] != self.build_id
        ]
        
        # Add to completed (keep last 10)
        if 'completed_builds' not in status_data:
            status_data['completed_builds'] = []
        
        status_data['completed_builds'].insert(0, self.data)
        status_data['completed_builds'] = status_data['completed_builds'][:10]
        
        status_data['last_updated'] = datetime.now().isoformat()
        _save_status(status_data)
    
    def pause(self):
        """Pause the build."""
        self.data['status'] = 'paused'
        self._save()
    
    def resume(self):
        """Resume a paused build."""
        self.data['status'] = 'in_progress'
        self._save()
    
    def fail(self, reason: str = ""):
        """Mark build as failed."""
        self.data['status'] = 'failed'
        if reason:
            self.data['failure_reason'] = reason
        self._save()
    
    def _save(self):
        """Save changes to status file."""
        status_data = _load_status()
        
        # Update this build in active list
        for i, build in enumerate(status_data['active_builds']):
            if build['id'] == self.build_id:
                status_data['active_builds'][i] = self.data
                break
        
        status_data['last_updated'] = datetime.now().isoformat()
        _save_status(status_data)


def _load_status() -> Dict:
    """Load current status file."""
    if not STATUS_FILE.exists():
        return {
            'last_updated': datetime.now().isoformat(),
            'active_builds': [],
            'completed_builds': [],
            'queued_builds': []
        }
    
    try:
        return json.loads(STATUS_FILE.read_text())
    except json.JSONDecodeError:
        return {
            'last_updated': datetime.now().isoformat(),
            'active_builds': [],
            'completed_builds': [],
            'queued_builds': []
        }


def _save_status(data: Dict):
    """Save status file."""
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(data, indent=2))


# CLI for testing
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        # Create demo build
        build = BuildStatus.create_build(
            title="Demo Build System",
            tasks=["Setup", "Build Core", "Test", "Deploy"],
            priority="high",
            assigned_to="Demo Agent",
            notes="Testing the build status system"
        )
        
        print(f"✅ Created build: {build.build_id}")
        print(f"   Title: {build.data['title']}")
        print(f"   Tasks: {len(build.data['tasks'])}")
        
        # Update first task
        build.update_task("Setup", status="complete", progress=100)
        print("✅ Completed: Setup")
        
        # Update second task
        build.update_task("Build Core", status="in_progress", progress=50)
        print("🔄 In progress: Build Core (50%)")
        
        print(f"\n📊 Overall progress: {build.data['progress']}%")
        print(f"📄 View at: http://10.0.0.18:8080/dashboard/builds.html")
    
    else:
        print("Usage:")
        print("  python3 build-status-updater.py --demo")
