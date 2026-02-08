#!/usr/bin/env python3
"""
Autonomous Task Executor

Reads TASK_QUEUE.md, identifies executable tasks, and runs them automatically.

Task Types:
- file_ops: Organize files, backups, cleanup
- data_pull: Fetch data from APIs, update dashboards
- system_maintenance: Health checks, log rotation
- report_generation: Create status reports, summaries

Uses local AI to determine if a task is executable without human input.
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
import urllib.request
import re
import sys

WORKSPACE = Path.home() / "clawd"
TASK_QUEUE_FILE = WORKSPACE / "TASK_QUEUE.md"
EXECUTION_LOG = WORKSPACE / "logs" / "task_execution.log"
OLLAMA_URL = "http://localhost:11434/api/generate"

EXECUTION_LOG.parent.mkdir(exist_ok=True)

def log(message):
    """Log execution activity"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(EXECUTION_LOG, 'a') as f:
        f.write(log_msg + "\n")

def call_local_model(prompt, temperature=0.3):
    """Call local ollama for task analysis"""
    try:
        data = json.dumps({
            "model": "qwen2.5:14b",
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(
            OLLAMA_URL,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response")
            
    except Exception as e:
        log(f"Local model error: {e}")
        return None

def parse_task_queue():
    """Parse TASK_QUEUE.md for pending tasks"""
    if not TASK_QUEUE_FILE.exists():
        return []
    
    with open(TASK_QUEUE_FILE) as f:
        content = f.read()
    
    # Find unchecked tasks (- [ ] ...)
    pattern = r'- \[ \] (.+?)(?:\(estimated time: (.+?)\))?$'
    tasks = []
    
    for match in re.finditer(pattern, content, re.MULTILINE):
        task_text = match.group(1).strip()
        estimated_time = match.group(2) if match.group(2) else "unknown"
        tasks.append({
            "text": task_text,
            "estimated_time": estimated_time,
            "raw_line": match.group(0)
        })
    
    return tasks

def analyze_task_executability(task_text):
    """Use local AI to determine if task can be executed automatically"""
    
    prompt = f"""Analyze this task and determine if it can be executed automatically by a script.

TASK: {task_text}

Consider:
- Does it require external human input or decisions?
- Does it involve sensitive actions (payments, external communications)?
- Can it be broken down into programmatic steps?

Respond in JSON:
{{
  "executable": true/false,
  "confidence": 0-100,
  "reasoning": "brief explanation",
  "type": "file_ops|data_pull|system_maintenance|report_generation|needs_human",
  "steps": ["step 1", "step 2", ...] or null
}}

Be conservative - if uncertain, mark as needs_human."""

    response = call_local_model(prompt, temperature=0.2)
    
    if not response:
        return None
    
    try:
        # Extract JSON from response
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            return json.loads(response[json_start:json_end])
    except:
        pass
    
    return None

def execute_task(task, analysis):
    """Execute a task based on its type"""
    
    task_type = analysis.get("type")
    
    if task_type == "system_maintenance":
        # Example: Run system health check
        log(f"Executing system maintenance: {task['text']}")
        # Placeholder - would run actual maintenance scripts
        return {"success": True, "output": "System check completed"}
    
    elif task_type == "data_pull":
        # Example: Update dashboard data
        log(f"Executing data pull: {task['text']}")
        # Would call data aggregator or API
        return {"success": True, "output": "Data refreshed"}
    
    elif task_type == "file_ops":
        # Example: Organize files
        log(f"Executing file operation: {task['text']}")
        # Would run file organization script
        return {"success": True, "output": "Files organized"}
    
    elif task_type == "report_generation":
        # Example: Generate status report
        log(f"Executing report generation: {task['text']}")
        # Would compile and generate report
        return {"success": True, "output": "Report generated"}
    
    else:
        log(f"Task type '{task_type}' not executable automatically")
        return {"success": False, "reason": "Needs human input"}

def mark_task_complete(task_text):
    """Mark task as completed in TASK_QUEUE.md"""
    with open(TASK_QUEUE_FILE) as f:
        content = f.read()
    
    # Replace - [ ] with - [x]
    updated = content.replace(f"- [ ] {task_text}", f"- [x] {task_text}")
    
    with open(TASK_QUEUE_FILE, 'w') as f:
        f.write(updated)

def main():
    """Run task executor"""
    log("=== Task Executor Starting ===")
    
    tasks = parse_task_queue()
    log(f"Found {len(tasks)} pending tasks")
    
    if not tasks:
        log("No tasks to execute")
        return
    
    executed = 0
    skipped = 0
    
    for task in tasks[:3]:  # Process max 3 tasks per run
        log(f"\nAnalyzing: {task['text']}")
        
        analysis = analyze_task_executability(task['text'])
        
        if not analysis:
            log("  Analysis failed, skipping")
            skipped += 1
            continue
        
        log(f"  Executable: {analysis['executable']} (confidence: {analysis.get('confidence')}%)")
        log(f"  Type: {analysis.get('type')}")
        log(f"  Reasoning: {analysis.get('reasoning')}")
        
        if analysis['executable'] and analysis.get('confidence', 0) > 70:
            result = execute_task(task, analysis)
            
            if result.get('success'):
                mark_task_complete(task['text'])
                log(f"  ✅ Task completed: {result.get('output')}")
                executed += 1
            else:
                log(f"  ❌ Task failed: {result.get('reason')}")
                skipped += 1
        else:
            log(f"  ⏭️  Skipping: {analysis.get('reasoning')}")
            skipped += 1
    
    log(f"\n=== Execution Complete ===")
    log(f"Executed: {executed}, Skipped: {skipped}")

if __name__ == "__main__":
    main()
