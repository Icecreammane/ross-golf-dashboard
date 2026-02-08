#!/usr/bin/env python3
"""
Local Model Analyzer - Smart Tier 2 using Ollama

Uses local LLM (qwen2.5:14b or llama3.1:8b) to analyze daemon signals,
make intelligent decisions, and handle tasks autonomously.

Only escalates to Sonnet when:
- Needs external API access (Twitter, email, etc.)
- Uncertain about decision
- Requires Ross's explicit approval
- Beyond local model capabilities
"""

import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / "clawd"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Model preference: qwen2.5:14b (smarter) > llama3.1:8b (faster)
LOCAL_MODELS = ["qwen2.5:14b", "llama3.1:8b"]

def call_ollama(prompt, model="qwen2.5:14b", temperature=0.3):
    """Call local ollama model using standard library"""
    try:
        data = json.dumps({
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(
            OLLAMA_URL,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response")
            
    except Exception as e:
        print(f"Ollama error: {e}", file=__import__('sys').stderr)
        return None

def analyze_goals_change(goals_content):
    """Analyze GOALS.md changes and decide action"""
    prompt = f"""You are an autonomous assistant analyzing goal changes.

CURRENT GOALS.MD:
{goals_content}

TASK:
1. Identify any NEW high-priority goals or urgent items
2. Determine if action is needed immediately
3. Decide: HANDLE (you can act), ESCALATE (needs Sonnet), or IGNORE (routine update)

Respond in JSON:
{{
  "decision": "HANDLE|ESCALATE|IGNORE",
  "priority": "low|medium|high|urgent",
  "reasoning": "brief explanation",
  "action": "what to do (if HANDLE)",
  "escalation_reason": "why escalate (if ESCALATE)"
}}

Be autonomous - only escalate if you truly need Sonnet's help or Ross's approval."""

    response = call_ollama(prompt)
    if not response:
        return None
    
    try:
        # Extract JSON from response (model might add extra text)
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            return json.loads(response[json_start:json_end])
    except:
        pass
    
    return None

def analyze_task_queue(queue_content, pending_count):
    """Analyze task queue state and recommend action"""
    prompt = f"""You are managing a task queue. Current state:

PENDING TASKS: {pending_count}

TASK_QUEUE.MD:
{queue_content[:2000]}  # First 2000 chars

TASK:
Analyze the queue and decide what to do.

If tasks are getting backed up (>10), determine:
- Can tasks be delegated to sub-agents?
- Are tasks blocked by dependencies?
- Should some be deprioritized?

If queue is low (<3), determine:
- Should new tasks be generated from GOALS.md?
- What type of tasks are needed?

Respond in JSON:
{{
  "decision": "HANDLE|ESCALATE|IGNORE",
  "priority": "low|medium|high",
  "reasoning": "brief explanation",
  "action": "specific action to take"
}}"""

    response = call_ollama(prompt)
    if not response:
        return None
    
    try:
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            return json.loads(response[json_start:json_end])
    except:
        pass
    
    return None

def generate_new_tasks():
    """Use local model to generate tasks from GOALS.md"""
    goals_file = WORKSPACE / "GOALS.md"
    if not goals_file.exists():
        return None
    
    with open(goals_file) as f:
        goals = f.read()
    
    prompt = f"""You are generating actionable tasks from goals.

CURRENT GOALS:
{goals}

TASK:
Generate 5-7 specific, actionable tasks that move toward these goals.

Format each task as:
- [ ] Task description (estimated time: Xh)

Focus on:
- Small, concrete actions
- Things that can be done today/this week
- Mix of easy wins and important progress
- Variety across different goal areas

Return ONLY the task list, no extra commentary."""

    response = call_ollama(prompt, temperature=0.7)  # Higher temp for creativity
    if response:
        return response.strip()
    
    return None

def handle_signal_locally(signal_type, data):
    """Try to handle signal with local model before escalating"""
    
    if signal_type == "goals_updated":
        # Analyze goals change
        goals_file = WORKSPACE / "GOALS.md"
        if goals_file.exists():
            with open(goals_file) as f:
                goals = f.read()
            
            analysis = analyze_goals_change(goals)
            if analysis and analysis["decision"] == "HANDLE":
                return {
                    "handled": True,
                    "action_taken": analysis.get("action", "Analyzed goals"),
                    "log": f"Local model handled goals update: {analysis['reasoning']}"
                }
            elif analysis and analysis["decision"] == "ESCALATE":
                return {
                    "handled": False,
                    "escalate": True,
                    "reason": analysis.get("escalation_reason"),
                    "priority": analysis.get("priority", "medium")
                }
    
    elif signal_type == "generate_tasks":
        # Generate tasks from goals
        new_tasks = generate_new_tasks()
        if new_tasks:
            # Append to TASK_QUEUE.md
            queue_file = WORKSPACE / "TASK_QUEUE.md"
            with open(queue_file, 'a') as f:
                f.write(f"\n\n## Generated {datetime.now().strftime('%Y-%m-%d %I:%M%p')}\n")
                f.write(new_tasks + "\n")
            
            return {
                "handled": True,
                "action_taken": f"Generated {new_tasks.count('- [ ]')} new tasks",
                "log": "Local model generated tasks from GOALS.md"
            }
    
    elif signal_type == "task_queue_growing":
        # Analyze queue state
        queue_file = WORKSPACE / "TASK_QUEUE.md"
        if queue_file.exists():
            with open(queue_file) as f:
                queue = f.read()
            
            pending = data.get("pending_tasks", 0)
            analysis = analyze_task_queue(queue, pending)
            
            if analysis and analysis["decision"] == "HANDLE":
                return {
                    "handled": True,
                    "action_taken": analysis.get("action"),
                    "log": f"Local model analyzed queue: {analysis['reasoning']}"
                }
    
    # Default: escalate if we can't handle
    return {
        "handled": False,
        "escalate": True,
        "reason": f"Signal type '{signal_type}' requires Sonnet",
        "priority": data.get("priority", "medium")
    }

def main():
    """Handle signal from stdin (called by daemon)"""
    import sys
    
    # Read signal from stdin
    signal_json = sys.stdin.read()
    if not signal_json:
        print(json.dumps({"handled": False, "error": "No input"}))
        sys.exit(1)
    
    try:
        signal = json.loads(signal_json)
        result = handle_signal_locally(signal["type"], signal.get("data", {}))
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"handled": False, "error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
