#!/usr/bin/env python3
"""
Revenue Task Queue
Task management system specifically for revenue-generating work.
Prioritizes by $ per hour * ease multiplier.
"""

import json
import os
import sys
import argparse
from datetime import datetime, date
from pathlib import Path

DATA_FILE = Path.home() / "clawd" / "data" / "revenue-tasks.json"

class RevenueQueue:
    def __init__(self):
        self.data_file = DATA_FILE
        self.data = self._load_data()
        
    def _load_data(self):
        """Load tasks from JSON file"""
        if not self.data_file.exists():
            return {
                "tasks": [],
                "completed": [],
                "stats": {
                    "total_revenue_potential": 0,
                    "total_actual_revenue": 0,
                    "tasks_completed": 0,
                    "avg_completion_time": 0
                }
            }
        
        with open(self.data_file, 'r') as f:
            return json.load(f)
    
    def _save_data(self):
        """Save tasks to JSON file"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def _calculate_priority(self, task):
        """Calculate priority score: ($/hr) * ease_multiplier"""
        revenue = task['revenue_potential']
        time = task['time_required']
        ease = task['ease']
        
        # Calculate $ per hour
        dollars_per_hour = revenue / time if time > 0 else 0
        
        # Apply ease multiplier
        ease_multipliers = {
            'easy': 2.0,
            'medium': 1.0,
            'hard': 0.5
        }
        multiplier = ease_multipliers.get(ease, 1.0)
        
        priority = dollars_per_hour * multiplier
        return priority
    
    def add_task(self, task, revenue, time, ease='medium'):
        """Add a new revenue task"""
        # Get next ID
        existing_ids = [t['id'] for t in self.data['tasks']] + [t['id'] for t in self.data['completed']]
        next_id = max(existing_ids) + 1 if existing_ids else 1
        
        new_task = {
            'id': next_id,
            'task': task,
            'revenue_potential': revenue,
            'time_required': time,
            'ease': ease,
            'status': 'pending',
            'created': str(date.today()),
            'actual_revenue': None
        }
        
        self.data['tasks'].append(new_task)
        self.data['stats']['total_revenue_potential'] += revenue
        self._save_data()
        
        print(f"✅ Added task #{next_id}: {task}")
        print(f"   Revenue potential: ${revenue} | Time: {time}h | Ease: {ease}")
        priority = self._calculate_priority(new_task)
        print(f"   Priority score: {priority:.1f}")
    
    def list_tasks(self):
        """List all tasks sorted by priority"""
        if not self.data['tasks']:
            print("📭 No pending tasks. Add some with 'revenue-queue add'")
            return
        
        # Sort by priority
        tasks = sorted(self.data['tasks'], 
                      key=lambda t: self._calculate_priority(t), 
                      reverse=True)
        
        print(f"\n{'='*70}")
        print("REVENUE TASK QUEUE (sorted by priority)")
        print(f"{'='*70}\n")
        
        for task in tasks:
            priority = self._calculate_priority(task)
            dollars_per_hour = task['revenue_potential'] / task['time_required']
            
            print(f"#{task['id']} [{priority:.0f} pts] {task['task']}")
            print(f"    💰 ${task['revenue_potential']} | ⏱️  {task['time_required']}h | "
                  f"📊 ${dollars_per_hour:.0f}/hr | 🎯 {task['ease']}")
            print()
        
        print(f"Total potential revenue: ${self.data['stats']['total_revenue_potential']}")
        print(f"Completed tasks: {self.data['stats']['tasks_completed']}")
        print(f"Actual revenue earned: ${self.data['stats']['total_actual_revenue']}\n")
    
    def next_task(self):
        """Show the highest priority task"""
        if not self.data['tasks']:
            print("📭 No pending tasks!")
            return
        
        # Get highest priority task
        next_task = max(self.data['tasks'], key=lambda t: self._calculate_priority(t))
        priority = self._calculate_priority(next_task)
        
        print(f"\n{'='*70}")
        print("YOUR NEXT TASK:")
        print(f"{'='*70}\n")
        print(f"#{next_task['id']} {next_task['task']}")
        print(f"\n💰 Revenue potential: ${next_task['revenue_potential']}")
        print(f"⏱️  Time required: {next_task['time_required']}h")
        print(f"🎯 Ease: {next_task['ease']}")
        print(f"📊 Priority score: {priority:.0f}")
        print(f"\n$ per hour: ${next_task['revenue_potential'] / next_task['time_required']:.0f}")
        print(f"\n{'='*70}")
        print("Ready to ship? 🚀\n")
    
    def suggest(self, available_hours):
        """Suggest tasks that fit in available time"""
        if not self.data['tasks']:
            print("📭 No pending tasks!")
            return
        
        # Filter tasks that fit in available time
        fitting_tasks = [t for t in self.data['tasks'] 
                        if t['time_required'] <= available_hours]
        
        if not fitting_tasks:
            print(f"⏱️  No tasks fit in {available_hours}h. Shortest task: "
                  f"{min(t['time_required'] for t in self.data['tasks'])}h")
            return
        
        # Sort by priority
        fitting_tasks = sorted(fitting_tasks, 
                             key=lambda t: self._calculate_priority(t), 
                             reverse=True)
        
        print(f"\n{'='*70}")
        print(f"YOU HAVE {available_hours}h - HERE'S WHAT TO DO:")
        print(f"{'='*70}\n")
        
        for i, task in enumerate(fitting_tasks[:3], 1):
            priority = self._calculate_priority(task)
            print(f"{i}. #{task['id']} {task['task']}")
            print(f"   💰 ${task['revenue_potential']} in {task['time_required']}h "
                  f"(priority: {priority:.0f})\n")
        
        print("Pick one and ship it. ⚡\n")
    
    def complete_task(self, task_id, actual_revenue=None):
        """Mark a task as complete"""
        # Find task
        task = None
        for t in self.data['tasks']:
            if t['id'] == task_id:
                task = t
                break
        
        if not task:
            print(f"❌ Task #{task_id} not found")
            return
        
        # Move to completed
        task['status'] = 'completed'
        task['completed_date'] = str(date.today())
        if actual_revenue is not None:
            task['actual_revenue'] = actual_revenue
            self.data['stats']['total_actual_revenue'] += actual_revenue
        
        self.data['tasks'].remove(task)
        self.data['completed'].append(task)
        self.data['stats']['tasks_completed'] += 1
        
        self._save_data()
        
        print(f"✅ Completed: {task['task']}")
        if actual_revenue is not None:
            print(f"   Revenue: ${actual_revenue} (expected: ${task['revenue_potential']})")
            accuracy = (actual_revenue / task['revenue_potential'] * 100) if task['revenue_potential'] > 0 else 0
            print(f"   Estimate accuracy: {accuracy:.0f}%")
    
    def weekly_report(self):
        """Show weekly performance report"""
        from datetime import datetime, timedelta
        
        # Get tasks completed in last 7 days
        week_ago = (date.today() - timedelta(days=7)).isoformat()
        recent_completed = [t for t in self.data['completed'] 
                          if t.get('completed_date', '2000-01-01') >= week_ago]
        
        if not recent_completed:
            print("📊 No tasks completed in the last 7 days")
            return
        
        print(f"\n{'='*70}")
        print("WEEKLY PERFORMANCE REPORT")
        print(f"{'='*70}\n")
        
        total_revenue = sum(t.get('actual_revenue', 0) or 0 for t in recent_completed)
        total_time = sum(t['time_required'] for t in recent_completed)
        
        print(f"Tasks completed: {len(recent_completed)}")
        print(f"Revenue generated: ${total_revenue}")
        print(f"Time invested: {total_time}h")
        print(f"Effective rate: ${total_revenue/total_time:.0f}/hr" if total_time > 0 else "")
        
        # Find top performers
        if any(t.get('actual_revenue') for t in recent_completed):
            revenue_tasks = [t for t in recent_completed if t.get('actual_revenue')]
            top_task = max(revenue_tasks, key=lambda t: t['actual_revenue'])
            
            print(f"\n🏆 Top performer: {top_task['task']}")
            print(f"   Generated: ${top_task['actual_revenue']}")
        
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Revenue Task Queue - Prioritize money-making work'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add task
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('task', nargs='+', help='Task description')
    add_parser.add_argument('--revenue', type=float, required=True, help='Revenue potential ($)')
    add_parser.add_argument('--time', type=float, required=True, help='Time required (hours)')
    add_parser.add_argument('--ease', choices=['easy', 'medium', 'hard'], default='medium')
    
    # List tasks
    subparsers.add_parser('list', help='List all tasks sorted by priority')
    
    # Next task
    subparsers.add_parser('next', help='Show highest priority task')
    
    # Suggest
    suggest_parser = subparsers.add_parser('suggest', help='Suggest tasks for available time')
    suggest_parser.add_argument('hours', type=float, help='Available hours')
    
    # Complete
    complete_parser = subparsers.add_parser('complete', help='Mark task as complete')
    complete_parser.add_argument('task_id', type=int, help='Task ID')
    complete_parser.add_argument('--revenue', type=float, help='Actual revenue earned')
    
    # Weekly report
    subparsers.add_parser('weekly', help='Show weekly performance report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    queue = RevenueQueue()
    
    if args.command == 'add':
        task_text = ' '.join(args.task)
        queue.add_task(task_text, args.revenue, args.time, args.ease)
    
    elif args.command == 'list':
        queue.list_tasks()
    
    elif args.command == 'next':
        queue.next_task()
    
    elif args.command == 'suggest':
        queue.suggest(args.hours)
    
    elif args.command == 'complete':
        queue.complete_task(args.task_id, args.revenue)
    
    elif args.command == 'weekly':
        queue.weekly_report()


if __name__ == '__main__':
    main()
