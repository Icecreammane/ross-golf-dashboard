#!/usr/bin/env python3
"""
Autonomous System Orchestrator

Coordinates all autonomous systems:
- Daemon monitors files/logs
- Scanners detect opportunities
- Drafter generates responses
- Executor runs tasks
- Everything flows automatically

Called by daemon or cron to run periodic workflows.
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / "clawd"
LOG_FILE = WORKSPACE / "logs" / "orchestrator.log"

LOG_FILE.parent.mkdir(exist_ok=True)

def log(message):
    """Log orchestrator activity"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_FILE, 'a') as f:
        f.write(log_msg + "\n")

def run_script(script_name, timeout=300):
    """Run a script and return success status"""
    script_path = WORKSPACE / "scripts" / script_name
    
    try:
        result = subprocess.run(
            ['python3', str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            log(f"  ✅ {script_name} completed")
            return {"success": True, "output": result.stdout}
        else:
            log(f"  ❌ {script_name} failed: {result.stderr[:200]}")
            return {"success": False, "error": result.stderr}
            
    except subprocess.TimeoutExpired:
        log(f"  ⏱️ {script_name} timed out")
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        log(f"  ❌ {script_name} error: {e}")
        return {"success": False, "error": str(e)}

def opportunity_workflow():
    """Run the opportunity detection → drafting workflow"""
    log("=== Opportunity Workflow Starting ===")
    
    # 1. Scan Twitter
    log("Scanning Twitter...")
    run_script("twitter_scanner.py", timeout=60)
    
    # 2. Scan Email
    log("Scanning Email...")
    run_script("email_scanner.py", timeout=60)
    
    # 3. Draft responses
    log("Drafting responses...")
    result = run_script("opportunity_drafter.py", timeout=300)
    
    if result.get("success"):
        # Check if there are drafted opportunities
        queue_file = WORKSPACE / "opportunities" / "queue.json"
        if queue_file.exists():
            with open(queue_file) as f:
                queue = json.load(f)
                drafted = [o for o in queue if o.get("status") == "drafted"]
                
                if drafted:
                    log(f"  📬 {len(drafted)} opportunities ready for review")
                    # TODO: Send notification to Ross
                    return {"opportunities": len(drafted)}
    
    log("=== Opportunity Workflow Complete ===")
    return {"opportunities": 0}

def task_workflow():
    """Run the task generation → execution workflow"""
    log("=== Task Workflow Starting ===")
    
    # 1. Check if task queue needs tasks
    task_queue = WORKSPACE / "TASK_QUEUE.md"
    if task_queue.exists():
        with open(task_queue) as f:
            content = f.read()
            pending = content.count("- [ ]")
            
            log(f"Task queue: {pending} pending tasks")
            
            # If low, generate more
            if pending < 5:
                log("Generating new tasks...")
                # Daemon will handle this via local_analyzer
    
    # 2. Execute tasks
    log("Running task executor...")
    result = run_script("task_executor.py", timeout=300)
    
    log("=== Task Workflow Complete ===")
    return result

def system_health_check():
    """Check system health"""
    log("=== System Health Check ===")
    
    checks = {
        "daemon_running": False,
        "ollama_running": False,
        "dashboard_running": False
    }
    
    # Check daemon
    try:
        pid_file = WORKSPACE / "daemon.pid"
        if pid_file.exists():
            with open(pid_file) as f:
                pid = f.read().strip()
            
            result = subprocess.run(['ps', '-p', pid], capture_output=True)
            checks["daemon_running"] = result.returncode == 0
    except:
        pass
    
    # Check ollama
    try:
        result = subprocess.run(['pgrep', '-f', 'ollama'], capture_output=True)
        checks["ollama_running"] = result.returncode == 0
    except:
        pass
    
    # Check dashboard
    try:
        result = subprocess.run(
            ['python3', '-c', 'import urllib.request; urllib.request.urlopen("http://localhost:8081", timeout=2)'],
            capture_output=True,
            timeout=5
        )
        checks["dashboard_running"] = result.returncode == 0
    except:
        pass
    
    log(f"Health: Daemon={checks['daemon_running']}, Ollama={checks['ollama_running']}, Dashboard={checks['dashboard_running']}")
    
    return checks

def main(mode="full"):
    """
    Run orchestrator
    
    Modes:
    - full: Run all workflows
    - opportunities: Just opportunity workflow
    - tasks: Just task workflow
    - health: Just health check
    """
    log(f"=== Orchestrator Starting (mode: {mode}) ===")
    
    results = {}
    
    if mode in ["full", "opportunities"]:
        results["opportunities"] = opportunity_workflow()
    
    if mode in ["full", "tasks"]:
        results["tasks"] = task_workflow()
    
    if mode in ["full", "health"]:
        results["health"] = system_health_check()
    
    log(f"=== Orchestrator Complete ===")
    print(json.dumps(results, indent=2))
    
    return results

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    main(mode)
