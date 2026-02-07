#!/usr/bin/env python3
"""
Sub-Agent Spawner (Python API)
Programmatic interface for spawning sub-agents with cost estimation.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Import our cost/tier/model modules
sys.path.insert(0, str(Path(__file__).parent))
try:
    from tier_classifier import classify_task
    from select_model import select_model
except ImportError:
    # If run as script, use subprocess fallback
    classify_task = None
    select_model = None


class SubAgentSpawner:
    """Manages sub-agent spawning with cost estimation and safety checks."""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or os.path.expanduser("~/clawd")
        self.subagents_dir = os.path.join(self.workspace_dir, "subagents")
        self.logs_dir = os.path.join(self.workspace_dir, "logs", "subagents")
        self.state_file = os.path.join(self.subagents_dir, "active_agents.json")
        
        # Ensure directories exist
        os.makedirs(self.subagents_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def analyze_task(self, task_description: str, tier: str = None, model: str = None) -> Dict:
        """
        Analyze a task and provide recommendations.
        
        Returns:
            Dictionary with classification, model selection, and cost estimate
        """
        # Classify tier if not provided
        if tier is None:
            if classify_task:
                classification = classify_task(task_description)
                tier = classification["tier"]
                estimated_hours = classification["estimated_hours"]
            else:
                # Fallback: call script
                result = subprocess.run(
                    [sys.executable, os.path.join(os.path.dirname(__file__), "tier-classifier.py"),
                     task_description, "--json"],
                    capture_output=True, text=True, check=True
                )
                classification = json.loads(result.stdout)
                tier = classification["tier"]
                estimated_hours = classification["estimated_hours"]
        else:
            # Use tier defaults
            tier_hours = {"quick": 1.5, "deep": 5, "enforcer": 10}
            estimated_hours = tier_hours.get(tier, 5)
            classification = {"tier": tier, "estimated_hours": estimated_hours}
        
        # Select model if not provided
        if model is None:
            if select_model:
                model_selection = select_model(task_description, tier)
                model = model_selection["model"]
            else:
                # Fallback: call script
                result = subprocess.run(
                    [sys.executable, os.path.join(os.path.dirname(__file__), "select-model.py"),
                     task_description, "--tier", tier, "--json"],
                    capture_output=True, text=True, check=True
                )
                model_selection = json.loads(result.stdout)
                model = model_selection["model"]
        else:
            model_selection = {"model": model, "reason": "User-specified"}
        
        # Calculate cost
        result = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(__file__), "subagent-cost-calculator.py"),
             task_description, "--hours", str(estimated_hours), "--model", model, "--json"],
            capture_output=True, text=True, check=True
        )
        cost_estimate = json.loads(result.stdout)
        
        return {
            "task": task_description,
            "classification": classification,
            "model_selection": model_selection,
            "cost_estimate": cost_estimate,
            "ready_to_launch": True
        }
    
    def spawn(self, task_description: str, tier: str = None, model: str = None,
              label: str = None, dry_run: bool = False, auto_approve: bool = False) -> Dict:
        """
        Spawn a sub-agent.
        
        Args:
            task_description: Task for the sub-agent
            tier: Optional tier override (quick/deep/enforcer)
            model: Optional model override
            label: Optional human-readable label
            dry_run: If True, only analyze without spawning
            auto_approve: If True, skip confirmation
        
        Returns:
            Dictionary with spawn result
        """
        # Analyze task
        analysis = self.analyze_task(task_description, tier, model)
        
        # Safety checks
        safety_check = self._check_safety(analysis)
        if not safety_check["safe"]:
            return {
                "success": False,
                "error": safety_check["reason"],
                "analysis": analysis
            }
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "analysis": analysis,
                "message": "Dry run complete. No agent spawned."
            }
        
        # Confirmation (unless auto-approved)
        if not auto_approve:
            print(self._format_analysis(analysis))
            response = input("\n🚀 Ready to launch? [Y/n]: ").strip().lower()
            if response and response not in ['y', 'yes']:
                return {
                    "success": False,
                    "error": "User cancelled",
                    "analysis": analysis
                }
        
        # Generate unique session ID
        session_id = self._generate_session_id(label or task_description)
        
        # Prepare sub-agent context
        context = self._prepare_context(task_description, analysis, session_id)
        
        # Spawn using Clawdbot API
        spawn_result = self._spawn_clawdbot_subagent(context, analysis)
        
        # Track active agent
        self._track_agent(session_id, task_description, analysis, spawn_result)
        
        # Log spawn
        self._log_spawn(session_id, task_description, analysis)
        
        return {
            "success": True,
            "session_id": session_id,
            "task": task_description,
            "analysis": analysis,
            "spawn_result": spawn_result,
            "message": f"✅ Sub-agent spawned: {session_id}"
        }
    
    def _check_safety(self, analysis: Dict) -> Dict:
        """Check if task is safe to spawn."""
        cost = analysis["cost_estimate"]["estimated_cost"]
        
        # Cost limit check
        if cost > 50:
            return {
                "safe": False,
                "reason": f"Cost ${cost:.2f} exceeds safety limit of $50. Use --force to override."
            }
        
        # Check concurrent agents
        active_count = self._count_active_agents()
        if active_count >= 3:
            return {
                "safe": False,
                "reason": f"Already {active_count} active agents (max 3). Wait for completion or kill one."
            }
        
        return {"safe": True}
    
    def _count_active_agents(self) -> int:
        """Count currently active sub-agents."""
        if not os.path.exists(self.state_file):
            return 0
        
        with open(self.state_file, 'r') as f:
            state = json.load(f)
        
        return len([a for a in state.get("agents", []) if a.get("status") == "running"])
    
    def _generate_session_id(self, label: str) -> str:
        """Generate unique session ID."""
        import re
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = re.sub(r'[^a-z0-9]+', '-', label.lower())[:30].strip('-')
        return f"subagent_{slug}_{timestamp}"
    
    def _prepare_context(self, task: str, analysis: Dict, session_id: str) -> str:
        """Prepare context file for sub-agent."""
        context_file = os.path.join(self.subagents_dir, f"{session_id}_context.md")
        
        context = f"""# Sub-Agent Task Context

**Session ID:** {session_id}
**Spawned:** {datetime.now().isoformat()}
**Tier:** {analysis['cost_estimate']['tier']}
**Model:** {analysis['cost_estimate']['model']}
**Estimated Time:** {analysis['cost_estimate']['estimated_hours']} hours
**Estimated Cost:** ${analysis['cost_estimate']['estimated_cost']:.2f}

---

## Task

{task}

---

## Instructions

You are a sub-agent spawned to complete this specific task. Follow these rules:

1. **Focus:** Complete the task described above. Nothing else.
2. **Conservative:** Don't modify existing core systems unless necessary.
3. **Test:** Test your work before reporting completion.
4. **Document:** Leave clear documentation of what you built.
5. **Report:** When done, provide a clear summary of what you accomplished.

## Deliverables

- Working implementation
- Tests (if applicable)
- Documentation
- Summary of changes

## Workspace

Your workspace: `{self.workspace_dir}`

Log your progress to: `{os.path.join(self.logs_dir, session_id + '.log')}`

---

**Good luck! Complete this task thoroughly and report back when done.**
"""
        
        with open(context_file, 'w') as f:
            f.write(context)
        
        return context_file
    
    def _spawn_clawdbot_subagent(self, context_file: str, analysis: Dict) -> Dict:
        """Spawn sub-agent using Clawdbot."""
        # For now, return mock result
        # In production, this would call the actual Clawdbot spawn API
        return {
            "method": "clawdbot_api",
            "context_file": context_file,
            "model": analysis["cost_estimate"]["model"],
            "status": "spawned"
        }
    
    def _track_agent(self, session_id: str, task: str, analysis: Dict, spawn_result: Dict):
        """Track active agent in state file."""
        state = {"agents": []}
        
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
        
        state["agents"].append({
            "session_id": session_id,
            "task": task,
            "tier": analysis["cost_estimate"]["tier"],
            "model": analysis["cost_estimate"]["model"],
            "estimated_cost": analysis["cost_estimate"]["estimated_cost"],
            "spawned_at": datetime.now().isoformat(),
            "status": "running",
            "spawn_result": spawn_result
        })
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _log_spawn(self, session_id: str, task: str, analysis: Dict):
        """Log spawn event."""
        log_file = os.path.join(self.logs_dir, f"{session_id}.log")
        
        log_entry = f"""
========================================
Sub-Agent Spawn Log
========================================
Session ID: {session_id}
Time: {datetime.now().isoformat()}
Task: {task}
Tier: {analysis['cost_estimate']['tier']}
Model: {analysis['cost_estimate']['model']}
Estimated Cost: ${analysis['cost_estimate']['estimated_cost']:.2f}
Estimated Time: {analysis['cost_estimate']['estimated_hours']} hours
========================================
""".strip()
        
        with open(log_file, 'w') as f:
            f.write(log_entry + "\n\n")
    
    def _format_analysis(self, analysis: Dict) -> str:
        """Format analysis for display."""
        cost = analysis["cost_estimate"]
        tier_emoji = {"quick": "🟢", "deep": "🟡", "enforcer": "🔴"}
        emoji = tier_emoji.get(cost["tier"], "⚪")
        
        return f"""
📊 **Cost Estimate**

{emoji} **Tier:** {cost['tier'].title()} Builder
🤖 **Model:** {cost['model_name']}
⏱️  **Time:** ~{cost['estimated_hours']} hours
💰 **Cost:** ${cost['estimated_cost']:.2f}

**Breakdown:**
  • Input: {cost['breakdown']['input_tokens']:,} tokens (${cost['breakdown']['input_cost']:.2f})
  • Output: {cost['breakdown']['output_tokens']:,} tokens (${cost['breakdown']['output_cost']:.2f})
""".strip()


def main():
    """CLI wrapper for Python API."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Spawn sub-agents")
    parser.add_argument("task", nargs="?", help="Task description")
    parser.add_argument("--tier", choices=["quick", "deep", "enforcer"], help="Force tier")
    parser.add_argument("--model", help="Force model")
    parser.add_argument("--label", help="Human-readable label")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze, don't spawn")
    parser.add_argument("--yes", "-y", action="store_true", help="Auto-approve (skip confirmation)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    if not args.task:
        parser.error("Task description required")
    
    spawner = SubAgentSpawner()
    
    try:
        if args.analyze_only:
            analysis = spawner.analyze_task(args.task, args.tier, args.model)
            if args.json:
                print(json.dumps(analysis, indent=2))
            else:
                print(spawner._format_analysis(analysis))
        else:
            result = spawner.spawn(
                args.task,
                tier=args.tier,
                model=args.model,
                label=args.label,
                auto_approve=args.yes
            )
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result["success"]:
                    print(f"\n✅ {result['message']}")
                    print(f"📝 Session ID: {result['session_id']}")
                    print(f"\n💡 Track progress: ./track-subagents.py status {result['session_id']}")
                else:
                    print(f"\n❌ Error: {result['error']}")
                    sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
