#!/usr/bin/env python3
"""
Master Orchestrator - Coordinates all autonomous systems
Runs unified intelligence, operator loop, task executor, etc.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / "clawd"

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_script(script_name, timeout=30):
    """Run a script and return success/failure"""
    script_path = WORKSPACE / "scripts" / script_name
    
    if not script_path.exists():
        log(f"⚠️  Script not found: {script_name}")
        return False
    
    try:
        log(f"▶️  Running {script_name}...")
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            log(f"✅ {script_name} completed successfully")
            return True
        else:
            log(f"❌ {script_name} failed with code {result.returncode}")
            if result.stderr:
                log(f"   Error: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        log(f"⏱️  {script_name} timed out after {timeout}s")
        return False
    except Exception as e:
        log(f"❌ {script_name} crashed: {e}")
        return False

def check_system_health():
    """Check health of all systems"""
    log("🏥 Checking system health...")
    
    health = {
        "dashboards": {
            "main": (WORKSPACE / "dashboard" / "index.html").exists(),
            "god_mode": (WORKSPACE / "god_mode" / "dashboard.html").exists(),
            "revenue": (WORKSPACE / "revenue-dashboard.html").exists(),
            "multiverse": (WORKSPACE / "multiverse" / "dashboard.html").exists(),
            "unified": (WORKSPACE / "unified-intelligence.html").exists()
        },
        "data": {
            "behavioral": (WORKSPACE / "god_mode" / "behavioral_data.json").exists(),
            "opportunities": (WORKSPACE / "revenue" / "opportunities.json").exists(),
            "timelines": (WORKSPACE / "multiverse" / "timelines.json").exists(),
            "queue": (WORKSPACE / "opportunities" / "queue.json").exists()
        },
        "scripts": {
            "unified_intelligence": (WORKSPACE / "scripts" / "unified_intelligence.py").exists(),
            "orchestrator": (WORKSPACE / "scripts" / "orchestrator.py").exists(),
            "autonomous_daemon": (WORKSPACE / "scripts" / "autonomous_daemon.py").exists()
        }
    }
    
    all_healthy = True
    for category, checks in health.items():
        for name, status in checks.items():
            emoji = "✅" if status else "❌"
            log(f"  {emoji} {category}.{name}: {'OK' if status else 'MISSING'}")
            if not status:
                all_healthy = False
    
    return all_healthy

def run_unified_sync():
    """Run unified intelligence sync"""
    return run_script("unified_intelligence.py", timeout=20)

def run_operator_loop():
    """Run operator loop (opportunity scanner + drafter)"""
    return run_script("orchestrator.py", timeout=60)

def run_god_mode_update():
    """Update God Mode behavioral analysis"""
    return run_script("behavioral_analyzer.py", timeout=30)

def main(mode="full"):
    """
    Master orchestrator - coordinates all systems
    
    Modes:
    - full: Run everything (unified sync + operator + god mode)
    - quick: Just unified sync
    - operator: Just operator loop
    - health: Just health check
    """
    log("=" * 70)
    log("🤖 MASTER ORCHESTRATOR")
    log("=" * 70)
    log(f"Mode: {mode}")
    log("")
    
    # Always check health first
    healthy = check_system_health()
    log("")
    
    if not healthy:
        log("⚠️  System not fully healthy - some components missing")
        log("")
    
    results = {}
    
    if mode in ["full", "quick"]:
        # Unified intelligence sync
        results["unified_sync"] = run_unified_sync()
        log("")
    
    if mode in ["full", "operator"]:
        # Operator loop (opportunities)
        results["operator_loop"] = run_operator_loop()
        log("")
    
    if mode == "full":
        # God Mode update (behavioral analysis)
        results["god_mode"] = run_god_mode_update()
        log("")
    
    # Summary
    log("=" * 70)
    log("📊 ORCHESTRATION SUMMARY")
    log("=" * 70)
    
    if results:
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        
        for task, success in results.items():
            emoji = "✅" if success else "❌"
            log(f"{emoji} {task}: {'SUCCESS' if success else 'FAILED'}")
        
        log("")
        log(f"Overall: {success_count}/{total_count} tasks successful")
    else:
        log("No tasks run (health check only)")
    
    log("=" * 70)
    
    # Return success if all tasks succeeded
    return all(results.values()) if results else healthy


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    
    if mode not in ["full", "quick", "operator", "health"]:
        print("Usage: master_orchestrator.py [full|quick|operator|health]")
        print("")
        print("Modes:")
        print("  full     - Run everything (default)")
        print("  quick    - Just unified sync")
        print("  operator - Just operator loop")
        print("  health   - Just health check")
        sys.exit(1)
    
    success = main(mode)
    sys.exit(0 if success else 1)
