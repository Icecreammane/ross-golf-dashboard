#!/usr/bin/env python3
"""
Sub-Agent Progress Tracker
Monitor and manage active sub-agents.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


class SubAgentTracker:
    """Track and manage sub-agent progress."""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or os.path.expanduser("~/clawd")
        self.subagents_dir = os.path.join(self.workspace_dir, "subagents")
        self.logs_dir = os.path.join(self.workspace_dir, "logs", "subagents")
        self.state_file = os.path.join(self.subagents_dir, "active_agents.json")
    
    def list_agents(self, status_filter: str = None) -> List[Dict]:
        """
        List all agents, optionally filtered by status.
        
        Args:
            status_filter: Optional filter (running/completed/failed)
        
        Returns:
            List of agent info dictionaries
        """
        if not os.path.exists(self.state_file):
            return []
        
        with open(self.state_file, 'r') as f:
            state = json.load(f)
        
        agents = state.get("agents", [])
        
        if status_filter:
            agents = [a for a in agents if a.get("status") == status_filter]
        
        # Enrich with runtime info
        for agent in agents:
            agent["runtime"] = self._calculate_runtime(agent)
            agent["estimated_completion"] = self._estimate_completion(agent)
        
        return agents
    
    def get_status(self, session_id: str) -> Optional[Dict]:
        """Get detailed status for a specific agent."""
        agents = self.list_agents()
        
        for agent in agents:
            if agent["session_id"] == session_id:
                # Add log tail
                log_file = os.path.join(self.logs_dir, f"{session_id}.log")
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        agent["recent_logs"] = lines[-20:]  # Last 20 lines
                else:
                    agent["recent_logs"] = []
                
                return agent
        
        return None
    
    def get_logs(self, session_id: str, lines: int = 50) -> List[str]:
        """Get recent log lines for an agent."""
        log_file = os.path.join(self.logs_dir, f"{session_id}.log")
        
        if not os.path.exists(log_file):
            return []
        
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            return all_lines[-lines:]
    
    def kill_agent(self, session_id: str) -> Dict:
        """Kill a running agent."""
        agent = self.get_status(session_id)
        
        if not agent:
            return {"success": False, "error": "Agent not found"}
        
        if agent["status"] != "running":
            return {"success": False, "error": f"Agent not running (status: {agent['status']})"}
        
        # Update status
        self._update_agent_status(session_id, "killed", {
            "killed_at": datetime.now().isoformat(),
            "reason": "Manual kill"
        })
        
        # Log kill
        log_file = os.path.join(self.logs_dir, f"{session_id}.log")
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Agent killed at {datetime.now().isoformat()}\n")
            f.write(f"{'='*50}\n")
        
        return {"success": True, "message": f"Killed agent: {session_id}"}
    
    def mark_completed(self, session_id: str, actual_cost: float = None, summary: str = None) -> Dict:
        """Mark an agent as completed."""
        agent = self.get_status(session_id)
        
        if not agent:
            return {"success": False, "error": "Agent not found"}
        
        completion_data = {
            "completed_at": datetime.now().isoformat(),
            "actual_cost": actual_cost,
            "summary": summary
        }
        
        self._update_agent_status(session_id, "completed", completion_data)
        
        return {"success": True, "message": f"Marked completed: {session_id}"}
    
    def mark_failed(self, session_id: str, error: str = None) -> Dict:
        """Mark an agent as failed."""
        agent = self.get_status(session_id)
        
        if not agent:
            return {"success": False, "error": "Agent not found"}
        
        failure_data = {
            "failed_at": datetime.now().isoformat(),
            "error": error
        }
        
        self._update_agent_status(session_id, "failed", failure_data)
        
        return {"success": True, "message": f"Marked failed: {session_id}"}
    
    def get_summary(self) -> Dict:
        """Get summary of all agents."""
        agents = self.list_agents()
        
        summary = {
            "total": len(agents),
            "running": len([a for a in agents if a["status"] == "running"]),
            "completed": len([a for a in agents if a["status"] == "completed"]),
            "failed": len([a for a in agents if a["status"] == "failed"]),
            "killed": len([a for a in agents if a["status"] == "killed"]),
            "total_estimated_cost": sum(a.get("estimated_cost", 0) for a in agents),
            "total_actual_cost": sum(a.get("actual_cost", 0) for a in agents if "actual_cost" in a)
        }
        
        return summary
    
    def _calculate_runtime(self, agent: Dict) -> float:
        """Calculate runtime in hours."""
        spawned = datetime.fromisoformat(agent["spawned_at"])
        
        if agent["status"] == "completed" and "completed_at" in agent:
            ended = datetime.fromisoformat(agent["completed_at"])
        elif agent["status"] in ["failed", "killed"]:
            ended = datetime.fromisoformat(agent.get("failed_at") or agent.get("killed_at") or datetime.now().isoformat())
        else:
            ended = datetime.now()
        
        delta = ended - spawned
        return delta.total_seconds() / 3600
    
    def _estimate_completion(self, agent: Dict) -> Optional[str]:
        """Estimate completion time for running agents."""
        if agent["status"] != "running":
            return None
        
        spawned = datetime.fromisoformat(agent["spawned_at"])
        estimated_hours = agent.get("estimated_hours", agent.get("estimated_cost", 5) / 3)  # Rough estimate
        
        estimated_end = spawned + timedelta(hours=estimated_hours)
        
        if estimated_end < datetime.now():
            return "Overdue"
        else:
            remaining = estimated_end - datetime.now()
            hours = remaining.total_seconds() / 3600
            return f"~{hours:.1f}h remaining"
    
    def _update_agent_status(self, session_id: str, status: str, extra_data: Dict = None):
        """Update agent status in state file."""
        if not os.path.exists(self.state_file):
            return
        
        with open(self.state_file, 'r') as f:
            state = json.load(f)
        
        for agent in state["agents"]:
            if agent["session_id"] == session_id:
                agent["status"] = status
                if extra_data:
                    agent.update(extra_data)
                break
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def format_agent_list(self, agents: List[Dict]) -> str:
        """Format agent list for display."""
        if not agents:
            return "No agents found."
        
        output = f"\n{'='*80}\n"
        output += f"{'Sub-Agents':^80}\n"
        output += f"{'='*80}\n\n"
        
        status_emoji = {
            "running": "🟢",
            "completed": "✅",
            "failed": "❌",
            "killed": "⏹️"
        }
        
        for agent in agents:
            emoji = status_emoji.get(agent["status"], "⚪")
            output += f"{emoji} **{agent['session_id']}**\n"
            output += f"   Status: {agent['status']}\n"
            output += f"   Task: {agent['task'][:60]}...\n" if len(agent['task']) > 60 else f"   Task: {agent['task']}\n"
            output += f"   Tier: {agent['tier']} | Model: {agent['model']}\n"
            output += f"   Runtime: {agent['runtime']:.1f}h"
            
            if agent["status"] == "running" and agent["estimated_completion"]:
                output += f" | {agent['estimated_completion']}"
            
            output += f"\n   Est. Cost: ${agent['estimated_cost']:.2f}"
            
            if "actual_cost" in agent:
                output += f" | Actual: ${agent['actual_cost']:.2f}"
            
            output += "\n\n"
        
        return output
    
    def format_status(self, agent: Dict) -> str:
        """Format detailed status for display."""
        status_emoji = {
            "running": "🟢 RUNNING",
            "completed": "✅ COMPLETED",
            "failed": "❌ FAILED",
            "killed": "⏹️ KILLED"
        }
        
        output = f"\n{'='*80}\n"
        output += f"Sub-Agent Status: {agent['session_id']}\n"
        output += f"{'='*80}\n\n"
        
        output += f"**Status:** {status_emoji.get(agent['status'], agent['status'])}\n"
        output += f"**Task:** {agent['task']}\n"
        output += f"**Tier:** {agent['tier']}\n"
        output += f"**Model:** {agent['model']}\n"
        output += f"**Spawned:** {agent['spawned_at']}\n"
        output += f"**Runtime:** {agent['runtime']:.2f} hours\n"
        
        if agent["status"] == "running" and agent["estimated_completion"]:
            output += f"**Est. Completion:** {agent['estimated_completion']}\n"
        
        output += f"**Est. Cost:** ${agent['estimated_cost']:.2f}\n"
        
        if "actual_cost" in agent:
            output += f"**Actual Cost:** ${agent['actual_cost']:.2f}\n"
        
        if "completed_at" in agent:
            output += f"**Completed:** {agent['completed_at']}\n"
        
        if "summary" in agent:
            output += f"\n**Summary:**\n{agent['summary']}\n"
        
        if "error" in agent:
            output += f"\n**Error:**\n{agent['error']}\n"
        
        if "recent_logs" in agent and agent["recent_logs"]:
            output += f"\n**Recent Logs (last 20 lines):**\n"
            output += "".join(agent["recent_logs"][-20:])
        
        return output


def main():
    """CLI interface for tracking."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Track sub-agent progress")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List all agents")
    list_parser.add_argument("--status", choices=["running", "completed", "failed", "killed"],
                           help="Filter by status")
    list_parser.add_argument("--json", action="store_true", help="Output JSON")
    
    # status command
    status_parser = subparsers.add_parser("status", help="Get agent status")
    status_parser.add_argument("session_id", help="Session ID")
    status_parser.add_argument("--json", action="store_true", help="Output JSON")
    
    # logs command
    logs_parser = subparsers.add_parser("logs", help="Get agent logs")
    logs_parser.add_argument("session_id", help="Session ID")
    logs_parser.add_argument("--lines", type=int, default=50, help="Number of lines")
    
    # kill command
    kill_parser = subparsers.add_parser("kill", help="Kill running agent")
    kill_parser.add_argument("session_id", help="Session ID")
    
    # summary command
    summary_parser = subparsers.add_parser("summary", help="Get summary of all agents")
    summary_parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    tracker = SubAgentTracker()
    
    try:
        if args.command == "list":
            agents = tracker.list_agents(args.status)
            if args.json:
                print(json.dumps(agents, indent=2))
            else:
                print(tracker.format_agent_list(agents))
        
        elif args.command == "status":
            agent = tracker.get_status(args.session_id)
            if not agent:
                print(f"❌ Agent not found: {args.session_id}", file=sys.stderr)
                sys.exit(1)
            
            if args.json:
                print(json.dumps(agent, indent=2))
            else:
                print(tracker.format_status(agent))
        
        elif args.command == "logs":
            logs = tracker.get_logs(args.session_id, args.lines)
            if not logs:
                print(f"No logs found for: {args.session_id}", file=sys.stderr)
                sys.exit(1)
            
            print("".join(logs))
        
        elif args.command == "kill":
            result = tracker.kill_agent(args.session_id)
            if result["success"]:
                print(f"✅ {result['message']}")
            else:
                print(f"❌ {result['error']}", file=sys.stderr)
                sys.exit(1)
        
        elif args.command == "summary":
            summary = tracker.get_summary()
            if args.json:
                print(json.dumps(summary, indent=2))
            else:
                print("\n📊 Sub-Agent Summary")
                print(f"   Total: {summary['total']}")
                print(f"   🟢 Running: {summary['running']}")
                print(f"   ✅ Completed: {summary['completed']}")
                print(f"   ❌ Failed: {summary['failed']}")
                print(f"   ⏹️  Killed: {summary['killed']}")
                print(f"\n   💰 Total Est. Cost: ${summary['total_estimated_cost']:.2f}")
                if summary['total_actual_cost'] > 0:
                    print(f"   💰 Total Actual Cost: ${summary['total_actual_cost']:.2f}")
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
