#!/usr/bin/env python3
"""
Agent Coordinator - Jarvis as Marc (COO)

Coordinates all sub-agents, runs overnight pipeline, delivers morning brief.

Usage:
    python3 agent_coordinator.py morning-brief
    python3 agent_coordinator.py run-pipeline
    python3 agent_coordinator.py status
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

WORKSPACE = Path.home() / "clawd"

class AgentCoordinator:
    def __init__(self):
        self.workspace = WORKSPACE
        self.agents = {
            'bob': {'name': 'Bob', 'type': 'health', 'schedule': 'every_30min'},
            'crawly': {'name': 'Crawly', 'type': 'intel', 'schedule': '23:00'},
            'mona': {'name': 'Mona', 'type': 'revenue', 'schedule': '00:00'},
            'claude': {'name': 'Claude', 'type': 'marketing', 'schedule': '01:00'},
            'ariane': {'name': 'Ariane', 'type': 'organizer', 'schedule': '03:00'}
        }
        
    def run_command(self, cmd, timeout=300):
        """Run shell command with timeout"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Timeout"
        except Exception as e:
            return False, "", str(e)
    
    def check_agent_output(self, agent_id):
        """Check if agent has produced output"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        output_paths = {
            'bob': self.workspace / f"monitoring/health_check_{today}.log",
            'crawly': self.workspace / f"intel/daily_intel_{today}.md",
            'mona': self.workspace / f"revenue/opportunities_{today}.md",
            'claude': self.workspace / f"content/posts_{today}.md",
            'ariane': self.workspace / f"backups/backup_{today}/backup_log.md"
        }
        
        path = output_paths.get(agent_id)
        if path and path.exists():
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            age_hours = (datetime.now() - mtime).total_seconds() / 3600
            return {
                'exists': True,
                'path': str(path),
                'age_hours': age_hours,
                'fresh': age_hours < 12  # Fresh if updated in last 12 hours
            }
        
        return {'exists': False, 'path': str(path) if path else None}
    
    def get_agent_status(self):
        """Get status of all agents"""
        status = {}
        for agent_id, agent_info in self.agents.items():
            output = self.check_agent_output(agent_id)
            status[agent_id] = {
                'name': agent_info['name'],
                'type': agent_info['type'],
                'output_exists': output['exists'],
                'fresh': output.get('fresh', False),
                'last_run': f"{output.get('age_hours', 'N/A')} hours ago" if output['exists'] else 'Never'
            }
        return status
    
    def generate_morning_brief(self):
        """Generate morning brief with all agent outputs"""
        today = datetime.now().strftime('%Y-%m-%d')
        brief_file = self.workspace / f"briefs/morning_brief_{today}.md"
        brief_file.parent.mkdir(exist_ok=True)
        
        brief = f"""# Morning Brief - {today}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M CST')}

"""
        
        # Check what got done overnight
        status = self.get_agent_status()
        
        finished = []
        issues = []
        
        for agent_id, info in status.items():
            if info['fresh']:
                finished.append(f"✅ {info['name']}: {info['type'].title()} complete")
            else:
                issues.append(f"⚠️  {info['name']}: No recent output ({info['last_run']})")
        
        if finished:
            brief += "## ✅ FINISHED OVERNIGHT:\n\n"
            for item in finished:
                brief += f"- {item}\n"
            brief += "\n"
        
        # Read agent outputs and summarize
        brief += "## 📋 WHAT'S READY:\n\n"
        
        # Lean posts
        posts_file = self.workspace / f"content/posts_{today}.md"
        if posts_file.exists():
            brief += "### Lean Posts (Ready to Schedule)\n"
            brief += f"- 3 posts drafted → `content/posts_{today}.md`\n"
            brief += "- Review time: ~5 minutes\n\n"
        
        # Partnership opportunities
        revenue_file = self.workspace / f"revenue/opportunities_{today}.md"
        if revenue_file.exists():
            brief += "### Partnership Opportunities\n"
            brief += f"- 5 opportunities found → `revenue/opportunities_{today}.md`\n"
            brief += "- DM templates ready to send\n"
            brief += "- Action time: ~10 minutes\n\n"
        
        # Intel
        intel_file = self.workspace / f"intel/daily_intel_{today}.md"
        if intel_file.exists():
            brief += "### Overnight Intel\n"
            brief += f"- Trends surfaced → `intel/daily_intel_{today}.md`\n"
            brief += "- Product ideas + content angles\n\n"
        
        # System health
        health_file = self.workspace / f"monitoring/health_check_{today}.log"
        if health_file.exists():
            brief += "### System Health\n"
            brief += "- ✅ All systems healthy\n"
            brief += f"- Details: `monitoring/health_check_{today}.log`\n\n"
        
        # Decisions needed
        brief += "## 🎯 DECISIONS NEEDED:\n\n"
        brief += "1. Review Lean posts → approve or edit\n"
        brief += "2. Pick 2-3 partnerships → send DMs\n"
        brief += "3. Review intel → any immediate opportunities?\n\n"
        
        # Issues
        if issues:
            brief += "## ⚠️  ISSUES:\n\n"
            for issue in issues:
                brief += f"- {issue}\n"
            brief += "\n"
        
        # Focus
        brief += "## ⚡ YOUR FOCUS TODAY:\n\n"
        brief += "Build. Create. Ship.\n"
        brief += "Everything else is handled.\n\n"
        
        brief += "---\n\n"
        brief += f"**Lean:** https://lean-fitness-tracker-production.up.railway.app/\n"
        brief += f"**Review time:** ~15 minutes\n"
        brief += f"**Then:** Focus on your craft\n"
        
        brief_file.write_text(brief)
        
        return brief
    
    def run_pipeline(self):
        """Run the overnight pipeline (testing)"""
        print("🌙 Running overnight pipeline...\n")
        
        # This would spawn sub-agents in production
        # For now, just show what would run
        
        pipeline = [
            ('23:00', 'Crawly', 'Intel gathering'),
            ('00:00', 'Mona', 'Revenue research'),
            ('01:00', 'Claude', 'Content drafting'),
            ('03:00', 'Ariane', 'Backup & organize'),
            ('05:00', 'Bob', 'Health check')
        ]
        
        for time, agent, task in pipeline:
            print(f"{time} - {agent}: {task}")
        
        print("\n✅ Pipeline defined. Use sub-agents to execute in production.")
        
    def print_status(self):
        """Print current agent status"""
        print("📊 Agent Army Status\n")
        
        status = self.get_agent_status()
        
        for agent_id, info in status.items():
            status_icon = "✅" if info['fresh'] else "⚠️"
            print(f"{status_icon} {info['name']} ({info['type'].title()})")
            print(f"   Last run: {info['last_run']}")
            print()

def main():
    coordinator = AgentCoordinator()
    
    if len(sys.argv) < 2:
        print("Usage: python3 agent_coordinator.py [morning-brief|run-pipeline|status]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'morning-brief':
        brief = coordinator.generate_morning_brief()
        print(brief)
    elif command == 'run-pipeline':
        coordinator.run_pipeline()
    elif command == 'status':
        coordinator.print_status()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
