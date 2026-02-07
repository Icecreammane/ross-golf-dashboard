#!/usr/bin/env python3
"""
Launch Accountability Bot
Tracks built vs launched projects and applies increasing pressure.
Because shipping > perfecting.
"""

import json
import sys
import argparse
from datetime import datetime, date
from pathlib import Path

DATA_FILE = Path.home() / "clawd" / "data" / "launch-accountability.json"

class LaunchAccountability:
    def __init__(self):
        self.data_file = DATA_FILE
        self.data = self._load_data()
        self._update_days_sitting()
        
    def _load_data(self):
        """Load accountability data"""
        if not self.data_file.exists():
            return {
                "projects": {},
                "goal": {
                    "target_mrr": 3000,
                    "current_mrr": 0,
                    "deadline": "2026-03-31",
                    "days_remaining": 0
                },
                "pressure_history": []
            }
        
        with open(self.data_file, 'r') as f:
            return json.load(f)
    
    def _save_data(self):
        """Save accountability data"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def _update_days_sitting(self):
        """Update days_sitting for all unlaunched projects"""
        today = date.today()
        
        for project_id, project in self.data['projects'].items():
            if not project['launched']:
                built_date = datetime.strptime(project['built_date'], '%Y-%m-%d').date()
                days = (today - built_date).days
                project['days_sitting'] = days
        
        # Update days remaining to deadline
        if self.data['goal']['deadline']:
            deadline = datetime.strptime(self.data['goal']['deadline'], '%Y-%m-%d').date()
            days_remaining = (deadline - today).days
            self.data['goal']['days_remaining'] = days_remaining
        
        self._save_data()
    
    def status(self):
        """Show current accountability status"""
        print(f"\n{'='*70}")
        print("LAUNCH ACCOUNTABILITY STATUS")
        print(f"{'='*70}\n")
        
        # Projects section
        built_count = len(self.data['projects'])
        launched_count = sum(1 for p in self.data['projects'].values() if p['launched'])
        unlaunched_count = built_count - launched_count
        
        print(f"Projects built: {built_count}")
        print(f"Projects launched: {launched_count}")
        print(f"Projects sitting: {unlaunched_count}")
        
        if unlaunched_count > 0:
            print(f"\n{'─'*70}")
            print("UNLAUNCHED PROJECTS:")
            print(f"{'─'*70}\n")
            
            for project_id, project in self.data['projects'].items():
                if not project['launched']:
                    emoji = self._get_pressure_emoji(project['days_sitting'])
                    print(f"{emoji} {project['name']}")
                    print(f"   Built: {project['built_date']}")
                    print(f"   Days sitting: {project['days_sitting']}")
                    print(f"   Revenue: ${project['revenue']}")
                    print()
        
        # Goal tracking
        print(f"{'─'*70}")
        print("GOAL TRACKING:")
        print(f"{'─'*70}\n")
        
        goal = self.data['goal']
        print(f"Current MRR: ${goal['current_mrr']}")
        print(f"Target MRR: ${goal['target_mrr']}")
        print(f"Gap: ${goal['target_mrr'] - goal['current_mrr']}")
        print(f"Deadline: {goal['deadline']}")
        print(f"Days remaining: {goal['days_remaining']}")
        
        if goal['days_remaining'] > 0:
            daily_required = (goal['target_mrr'] - goal['current_mrr']) / goal['days_remaining']
            print(f"Required daily growth: ${daily_required:.2f}/day")
        
        print()
    
    def _get_pressure_emoji(self, days):
        """Get emoji based on pressure level"""
        if days <= 2:
            return "🟢"
        elif days <= 5:
            return "🟡"
        elif days <= 10:
            return "🟠"
        else:
            return "🔴"
    
    def pressure(self):
        """Show uncomfortable truth - escalating pressure based on days sitting"""
        self._update_days_sitting()
        
        unlaunched = {pid: p for pid, p in self.data['projects'].items() 
                     if not p['launched']}
        
        if not unlaunched:
            print("✅ All projects are launched. Good job shipping!\n")
            return
        
        max_days = max(p['days_sitting'] for p in unlaunched.values())
        total_projects = len(unlaunched)
        
        print(f"\n{'='*70}")
        print("⚠️  UNCOMFORTABLE TRUTH")
        print(f"{'='*70}\n")
        
        # Escalating message based on days
        if max_days == 0:
            message = f"Everything is ready to launch. Perfect is the enemy of shipped."
        elif max_days <= 2:
            projects = ', '.join(p['name'] for p in unlaunched.values())
            message = f"{projects} {'is' if total_projects == 1 else 'are'} ready. Launch when you're comfortable."
        elif max_days <= 5:
            message = f"{max_days} days, $0 revenue. {total_projects} project{'s' if total_projects > 1 else ''} sitting."
        elif max_days <= 7:
            message = f"You've built for {max_days} days straight. LAUNCH SOMETHING."
        elif max_days <= 14:
            goal = self.data['goal']
            message = f"{max_days} days of building. Still ${goal['current_mrr']} MRR. {goal['days_remaining']} days to deadline."
        else:
            message = f"{max_days} DAYS. Building ≠ Shipping. Ship ≠ Perfect. LAUNCH NOW."
        
        print(message)
        print()
        
        # Show each project
        for project_id, project in sorted(unlaunched.items(), 
                                         key=lambda x: x[1]['days_sitting'], 
                                         reverse=True):
            emoji = self._get_pressure_emoji(project['days_sitting'])
            print(f"{emoji} {project['name']}: {project['days_sitting']} days, ${project['revenue']} revenue")
        
        # Math tracker
        goal = self.data['goal']
        print(f"\n{'─'*70}")
        print("THE MATH:")
        print(f"{'─'*70}")
        print(f"Current MRR: ${goal['current_mrr']}")
        print(f"Target MRR: ${goal['target_mrr']}")
        print(f"Days remaining: {goal['days_remaining']}")
        
        if goal['days_remaining'] > 0:
            required = (goal['target_mrr'] - goal['current_mrr']) / goal['days_remaining']
            print(f"Required daily growth: ${required:.2f}/day")
            
            # Projection
            if goal['current_mrr'] == 0:
                print(f"At current rate: You'll hit ${goal['current_mrr']} by {goal['deadline']}")
            else:
                print(f"At current rate: On track? {'Yes ✅' if goal['current_mrr'] > 0 else 'No ❌'}")
        
        print(f"{'='*70}\n")
        
        # Log this pressure check
        self.data['pressure_history'].append({
            'date': str(date.today()),
            'max_days_sitting': max_days,
            'unlaunched_count': total_projects,
            'current_mrr': goal['current_mrr']
        })
        self._save_data()
    
    def add_project(self, project_id, name, built_date=None):
        """Add a new project to track"""
        if built_date is None:
            built_date = str(date.today())
        
        self.data['projects'][project_id] = {
            'name': name,
            'built_date': built_date,
            'launched': False,
            'days_sitting': 0,
            'revenue': 0,
            'launch_date': None
        }
        
        self._save_data()
        print(f"✅ Added project: {name}")
        print(f"   Built date: {built_date}")
        print(f"   Now tracking for launch accountability\n")
    
    def launched(self, project_id, revenue=None):
        """Mark a project as launched"""
        if project_id not in self.data['projects']:
            print(f"❌ Project '{project_id}' not found")
            return
        
        project = self.data['projects'][project_id]
        project['launched'] = True
        project['launch_date'] = str(date.today())
        
        if revenue is not None:
            project['revenue'] = revenue
            self.data['goal']['current_mrr'] += revenue
        
        self._save_data()
        
        print(f"🚀 LAUNCHED: {project['name']}")
        print(f"   Days from build to launch: {project['days_sitting']}")
        if revenue:
            print(f"   Revenue: ${revenue}")
        print(f"   Launch date: {project['launch_date']}")
        print(f"\n✅ That's how it's done. Keep shipping.\n")
    
    def update_revenue(self, project_id, revenue):
        """Update revenue for a project"""
        if project_id not in self.data['projects']:
            print(f"❌ Project '{project_id}' not found")
            return
        
        project = self.data['projects'][project_id]
        old_revenue = project['revenue']
        delta = revenue - old_revenue
        
        project['revenue'] = revenue
        self.data['goal']['current_mrr'] += delta
        
        self._save_data()
        
        print(f"💰 Updated {project['name']}: ${old_revenue} → ${revenue}")
        print(f"   Current total MRR: ${self.data['goal']['current_mrr']}\n")
    
    def set_goal(self, target_mrr, deadline):
        """Set or update MRR goal"""
        self.data['goal']['target_mrr'] = target_mrr
        self.data['goal']['deadline'] = deadline
        
        # Calculate days remaining
        deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
        days = (deadline_date - date.today()).days
        self.data['goal']['days_remaining'] = days
        
        self._save_data()
        
        print(f"🎯 Goal updated:")
        print(f"   Target: ${target_mrr} MRR")
        print(f"   Deadline: {deadline}")
        print(f"   Days remaining: {days}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Launch Accountability Bot - Ship more, build less'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Status
    subparsers.add_parser('status', help='Show current status')
    
    # Pressure
    subparsers.add_parser('pressure', help='Show uncomfortable truth')
    
    # Add project
    add_parser = subparsers.add_parser('add', help='Add a project to track')
    add_parser.add_argument('project_id', help='Project ID (e.g., fittrack-pro)')
    add_parser.add_argument('name', nargs='+', help='Project name')
    add_parser.add_argument('--date', help='Built date (YYYY-MM-DD)', default=None)
    
    # Launched
    launch_parser = subparsers.add_parser('launched', help='Mark project as launched')
    launch_parser.add_argument('project_id', help='Project ID')
    launch_parser.add_argument('--revenue', type=float, help='Initial MRR')
    
    # Update revenue
    revenue_parser = subparsers.add_parser('revenue', help='Update project revenue')
    revenue_parser.add_argument('project_id', help='Project ID')
    revenue_parser.add_argument('amount', type=float, help='New MRR amount')
    
    # Set goal
    goal_parser = subparsers.add_parser('goal', help='Set MRR goal')
    goal_parser.add_argument('target', type=float, help='Target MRR')
    goal_parser.add_argument('deadline', help='Deadline (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    bot = LaunchAccountability()
    
    if args.command == 'status':
        bot.status()
    
    elif args.command == 'pressure':
        bot.pressure()
    
    elif args.command == 'add':
        name = ' '.join(args.name)
        bot.add_project(args.project_id, name, args.date)
    
    elif args.command == 'launched':
        bot.launched(args.project_id, args.revenue)
    
    elif args.command == 'revenue':
        bot.update_revenue(args.project_id, args.amount)
    
    elif args.command == 'goal':
        bot.set_goal(args.target, args.deadline)


if __name__ == '__main__':
    main()
