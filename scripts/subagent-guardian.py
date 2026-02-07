#!/usr/bin/env python3
"""
Sub-Agent Guardian
Safety monitoring and enforcement for sub-agents.
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# Add script dir to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# Import tracker
try:
    from track_subagents import SubAgentTracker
except ImportError:
    # Fallback: load directly
    import importlib.util
    spec = importlib.util.spec_from_file_location("track_subagents", SCRIPT_DIR / "track-subagents.py")
    track_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(track_module)
    SubAgentTracker = track_module.SubAgentTracker


class SubAgentGuardian:
    """Monitor and enforce safety limits for sub-agents."""
    
    # Safety limits (configurable)
    MAX_CONCURRENT = 3
    MAX_COST_PER_TASK = 50.0
    MAX_RUNTIME_HOURS = 12.0
    HEALTH_CHECK_INTERVAL = 30  # minutes
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or os.path.expanduser("~/clawd")
        self.tracker = SubAgentTracker(workspace_dir)
        self.logs_dir = os.path.join(self.workspace_dir, "logs", "subagents")
        self.guardian_log = os.path.join(self.logs_dir, "guardian.log")
    
    def check_all(self) -> Dict:
        """Run all safety checks."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # Check concurrent limit
        concurrent_check = self._check_concurrent_limit()
        results["checks"]["concurrent_limit"] = concurrent_check
        
        # Check runtime limits
        runtime_check = self._check_runtime_limits()
        results["checks"]["runtime_limits"] = runtime_check
        
        # Check for stuck agents
        stuck_check = self._check_stuck_agents()
        results["checks"]["stuck_agents"] = stuck_check
        
        # Check cost limits
        cost_check = self._check_cost_limits()
        results["checks"]["cost_limits"] = cost_check
        
        # Determine overall status
        all_ok = all(
            check.get("ok", True)
            for check in results["checks"].values()
        )
        
        results["overall_status"] = "OK" if all_ok else "ALERT"
        
        # Log results
        self._log_check(results)
        
        return results
    
    def _check_concurrent_limit(self) -> Dict:
        """Check if concurrent agent limit is exceeded."""
        running = self.tracker.list_agents(status_filter="running")
        count = len(running)
        
        if count > self.MAX_CONCURRENT:
            return {
                "ok": False,
                "level": "warning",
                "message": f"{count} concurrent agents exceeds limit of {self.MAX_CONCURRENT}",
                "count": count,
                "limit": self.MAX_CONCURRENT,
                "agents": [a["session_id"] for a in running]
            }
        
        return {
            "ok": True,
            "count": count,
            "limit": self.MAX_CONCURRENT
        }
    
    def _check_runtime_limits(self) -> Dict:
        """Check for agents exceeding runtime limits."""
        running = self.tracker.list_agents(status_filter="running")
        violations = []
        
        for agent in running:
            runtime = agent.get("runtime", 0)
            if runtime > self.MAX_RUNTIME_HOURS:
                violations.append({
                    "session_id": agent["session_id"],
                    "runtime": runtime,
                    "limit": self.MAX_RUNTIME_HOURS,
                    "task": agent["task"][:60]
                })
        
        if violations:
            return {
                "ok": False,
                "level": "error",
                "message": f"{len(violations)} agents exceeded runtime limit",
                "violations": violations,
                "action": "Consider killing long-running agents"
            }
        
        return {"ok": True}
    
    def _check_stuck_agents(self) -> Dict:
        """Check for agents that appear stuck (no log activity)."""
        running = self.tracker.list_agents(status_filter="running")
        stuck = []
        
        for agent in running:
            session_id = agent["session_id"]
            log_file = os.path.join(self.logs_dir, f"{session_id}.log")
            
            if not os.path.exists(log_file):
                stuck.append({
                    "session_id": session_id,
                    "reason": "No log file",
                    "runtime": agent.get("runtime", 0)
                })
                continue
            
            # Check last modification time
            last_modified = datetime.fromtimestamp(os.path.getmtime(log_file))
            age_minutes = (datetime.now() - last_modified).total_seconds() / 60
            
            # If no activity for 60 minutes, consider stuck
            if age_minutes > 60:
                stuck.append({
                    "session_id": session_id,
                    "reason": f"No log activity for {age_minutes:.0f} minutes",
                    "last_activity": last_modified.isoformat(),
                    "runtime": agent.get("runtime", 0)
                })
        
        if stuck:
            return {
                "ok": False,
                "level": "warning",
                "message": f"{len(stuck)} agents appear stuck",
                "stuck_agents": stuck,
                "action": "Investigate or kill stuck agents"
            }
        
        return {"ok": True}
    
    def _check_cost_limits(self) -> Dict:
        """Check if any agents are approaching cost limits."""
        running = self.tracker.list_agents(status_filter="running")
        warnings = []
        
        for agent in running:
            estimated = agent.get("estimated_cost", 0)
            
            if estimated > self.MAX_COST_PER_TASK:
                warnings.append({
                    "session_id": agent["session_id"],
                    "estimated_cost": estimated,
                    "limit": self.MAX_COST_PER_TASK,
                    "task": agent["task"][:60]
                })
        
        if warnings:
            return {
                "ok": False,
                "level": "warning",
                "message": f"{len(warnings)} agents have high estimated costs",
                "warnings": warnings
            }
        
        return {"ok": True}
    
    def auto_recover(self, dry_run: bool = False) -> Dict:
        """Attempt automatic recovery for problematic agents."""
        actions_taken = []
        
        # Check for agents exceeding runtime limits
        running = self.tracker.list_agents(status_filter="running")
        
        for agent in running:
            runtime = agent.get("runtime", 0)
            
            # Auto-kill if >12 hours
            if runtime > self.MAX_RUNTIME_HOURS:
                action = {
                    "type": "kill",
                    "session_id": agent["session_id"],
                    "reason": f"Exceeded runtime limit ({runtime:.1f}h > {self.MAX_RUNTIME_HOURS}h)",
                    "dry_run": dry_run
                }
                
                if not dry_run:
                    result = self.tracker.kill_agent(agent["session_id"])
                    action["result"] = result
                
                actions_taken.append(action)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "actions_taken": actions_taken,
            "count": len(actions_taken)
        }
    
    def get_health_report(self) -> Dict:
        """Generate comprehensive health report."""
        summary = self.tracker.get_summary()
        checks = self.check_all()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "safety_checks": checks,
            "health_status": checks["overall_status"]
        }
    
    def _log_check(self, results: Dict):
        """Log check results."""
        os.makedirs(self.logs_dir, exist_ok=True)
        
        with open(self.guardian_log, 'a') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"Guardian Check: {results['timestamp']}\n")
            f.write(f"Status: {results['overall_status']}\n")
            f.write(f"{'='*80}\n")
            
            for check_name, check_result in results["checks"].items():
                f.write(f"\n{check_name}: ")
                f.write("OK\n" if check_result.get("ok") else f"{check_result.get('level', 'ERROR').upper()}\n")
                
                if not check_result.get("ok"):
                    f.write(f"  Message: {check_result.get('message')}\n")
                    if "action" in check_result:
                        f.write(f"  Action: {check_result['action']}\n")
            
            f.write("\n")
    
    def format_health_report(self, report: Dict) -> str:
        """Format health report for display."""
        output = f"\n{'='*80}\n"
        output += f"Sub-Agent Guardian - Health Report\n"
        output += f"{'='*80}\n\n"
        
        output += f"**Time:** {report['timestamp']}\n"
        output += f"**Overall Status:** {report['health_status']}\n\n"
        
        # Summary
        summary = report['summary']
        output += "**Summary:**\n"
        output += f"  Total Agents: {summary['total']}\n"
        output += f"  🟢 Running: {summary['running']}\n"
        output += f"  ✅ Completed: {summary['completed']}\n"
        output += f"  ❌ Failed: {summary['failed']}\n"
        output += f"  ⏹️  Killed: {summary['killed']}\n"
        output += f"  💰 Est. Cost: ${summary['total_estimated_cost']:.2f}\n\n"
        
        # Safety checks
        output += "**Safety Checks:**\n"
        checks = report['safety_checks']['checks']
        
        for check_name, check_result in checks.items():
            status_icon = "✅" if check_result.get("ok") else "⚠️"
            output += f"  {status_icon} {check_name}: "
            
            if check_result.get("ok"):
                output += "OK\n"
            else:
                output += f"{check_result.get('level', 'ERROR').upper()}\n"
                output += f"     {check_result.get('message')}\n"
                
                if "action" in check_result:
                    output += f"     💡 {check_result['action']}\n"
        
        return output


def main():
    """CLI interface for guardian."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sub-agent safety guardian")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # check command
    check_parser = subparsers.add_parser("check", help="Run safety checks")
    check_parser.add_argument("--json", action="store_true", help="Output JSON")
    
    # report command
    report_parser = subparsers.add_parser("report", help="Generate health report")
    report_parser.add_argument("--json", action="store_true", help="Output JSON")
    
    # recover command
    recover_parser = subparsers.add_parser("recover", help="Auto-recover problematic agents")
    recover_parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    recover_parser.add_argument("--json", action="store_true", help="Output JSON")
    
    # monitor command (continuous monitoring)
    monitor_parser = subparsers.add_parser("monitor", help="Continuous monitoring mode")
    monitor_parser.add_argument("--interval", type=int, default=30, help="Check interval in minutes")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    guardian = SubAgentGuardian()
    
    try:
        if args.command == "check":
            results = guardian.check_all()
            
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                if results["overall_status"] == "OK":
                    print("✅ All safety checks passed")
                else:
                    print("⚠️  Safety issues detected:")
                    
                    for check_name, check_result in results["checks"].items():
                        if not check_result.get("ok"):
                            print(f"\n  {check_name}:")
                            print(f"    {check_result.get('message')}")
                            if "action" in check_result:
                                print(f"    💡 {check_result['action']}")
        
        elif args.command == "report":
            report = guardian.get_health_report()
            
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                print(guardian.format_health_report(report))
        
        elif args.command == "recover":
            result = guardian.auto_recover(dry_run=args.dry_run)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if args.dry_run:
                    print("🔍 Dry run - no actions taken")
                
                if result["count"] == 0:
                    print("✅ No recovery actions needed")
                else:
                    print(f"⚡ Took {result['count']} recovery actions:")
                    for action in result["actions_taken"]:
                        print(f"\n  {action['type'].upper()}: {action['session_id']}")
                        print(f"    Reason: {action['reason']}")
        
        elif args.command == "monitor":
            print(f"🛡️  Guardian monitoring started (interval: {args.interval}m)")
            print("   Press Ctrl+C to stop\n")
            
            try:
                while True:
                    results = guardian.check_all()
                    
                    if results["overall_status"] != "OK":
                        print(f"\n⚠️  [{datetime.now().strftime('%H:%M:%S')}] Issues detected!")
                        for check_name, check_result in results["checks"].items():
                            if not check_result.get("ok"):
                                print(f"  {check_name}: {check_result.get('message')}")
                    else:
                        print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] All checks passed")
                    
                    time.sleep(args.interval * 60)
            
            except KeyboardInterrupt:
                print("\n\n🛑 Monitoring stopped")
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
