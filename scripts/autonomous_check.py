#!/usr/bin/env python3
"""
autonomous_check.py - Jarvis's Autonomous Task Generator & Build Spawner (UPGRADED)

EFFICIENCY UPGRADES:
- Smart sequential/parallel spawning based on Ross's availability
- Failure recovery with auto-retry
- Task batching intelligence
- Quiet hours respect
- Build time estimates
- Cost tracking integration
- Progress tracking

This script runs on:
- Every session startup
- Every heartbeat (every 30 minutes)

What it does:
1. Reads GOALS.md (what we're working toward)
2. Reads recent memory (what's been built, what Ross mentioned)
3. Checks BUILD_QUEUE.md (current task list)
4. If queue is empty → generates 1-3 tasks aligned with goals
5. If nothing is building → spawns next task (with intelligent timing)
6. Logs all decisions to memory
"""

import os
import json
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# Paths
WORKSPACE = Path.home() / "clawd"
GOALS_FILE = WORKSPACE / "GOALS.md"
BUILD_QUEUE_FILE = WORKSPACE / "BUILD_QUEUE.md"
BUILD_STATUS_FILE = WORKSPACE / "BUILD_STATUS.md"
MEMORY_DIR = WORKSPACE / "memory"
JARVIS_JOURNAL = MEMORY_DIR / "jarvis-journal.md"
HEARTBEAT_STATE = MEMORY_DIR / "heartbeat-state.json"
PAUSE_FILE = WORKSPACE / ".pause_autonomy"
RETRY_STATE_FILE = MEMORY_DIR / "retry-state.json"

# Ensure directories exist
MEMORY_DIR.mkdir(exist_ok=True)
(WORKSPACE / "scripts").mkdir(exist_ok=True)


def log_to_journal(message):
    """Append message to jarvis-journal.md with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(JARVIS_JOURNAL, "a") as f:
        f.write(f"\n[{timestamp}] {message}\n")


def read_goals():
    """Read and parse GOALS.md"""
    if not GOALS_FILE.exists():
        log_to_journal("⚠️ GOALS.md not found. Cannot generate tasks.")
        return None
    
    with open(GOALS_FILE, "r") as f:
        return f.read()


def read_recent_memory():
    """Read recent memory files (last 7 days)"""
    memory_content = []
    
    # Read daily memory files
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        date_file = MEMORY_DIR / f"{date.strftime('%Y-%m-%d')}.md"
        if date_file.exists():
            with open(date_file, "r") as f:
                memory_content.append(f.read())
    
    # Read jarvis-journal
    if JARVIS_JOURNAL.exists():
        with open(JARVIS_JOURNAL, "r") as f:
            memory_content.append(f.read())
    
    return "\n\n".join(memory_content)


def read_build_queue():
    """Read BUILD_QUEUE.md and parse tasks"""
    if not BUILD_QUEUE_FILE.exists():
        return []
    
    with open(BUILD_QUEUE_FILE, "r") as f:
        content = f.read()
    
    # Parse tasks (lines starting with - [ ] or - [x])
    tasks = []
    for line in content.split("\n"):
        if line.strip().startswith("- [ ]"):
            task = line.replace("- [ ]", "").strip()
            
            # Parse priority, ETA, cost if present
            priority = "medium"
            eta_minutes = None
            cost = None
            
            if "Priority:" in task or "priority:" in task:
                if "High" in task or "high" in task:
                    priority = "high"
                elif "Low" in task or "low" in task:
                    priority = "low"
            
            if "ETA:" in task:
                eta_match = re.search(r'ETA:\s*(\d+)\s*min', task)
                if eta_match:
                    eta_minutes = int(eta_match.group(1))
            
            if "Cost:" in task:
                cost_match = re.search(r'Cost:\s*~?\$?(\d+\.?\d*)', task)
                if cost_match:
                    cost = float(cost_match.group(1))
            
            tasks.append({
                "status": "pending",
                "task": task,
                "priority": priority,
                "eta_minutes": eta_minutes,
                "cost": cost
            })
        elif line.strip().startswith("- [x]"):
            task = line.replace("- [x]", "").strip()
            tasks.append({"status": "done", "task": task})
    
    return tasks


def read_build_status():
    """Check if anything is currently building"""
    if not BUILD_STATUS_FILE.exists():
        return None
    
    with open(BUILD_STATUS_FILE, "r") as f:
        content = f.read()
    
    # Check if there's an active build (contains "Status: Building" or similar)
    if "building" in content.lower() or "in progress" in content.lower():
        return content
    
    return None


def should_spawn_parallel():
    """
    Determine if we should spawn multiple agents or go sequential
    Based on Ross's availability and responsiveness
    """
    current_hour = datetime.now().hour
    current_day = datetime.now().weekday()  # 0=Monday, 6=Sunday
    is_weekday = current_day < 5
    
    # PARALLEL MODE (Ross is responsive, speed matters):
    # - Weekday evenings (6pm-11pm): He's home, at computer
    # - Weekend days (10am-10pm): He's actively building
    if (is_weekday and 18 <= current_hour <= 23) or \
       (not is_weekday and 10 <= current_hour <= 22):
        return True  # Spawn 2-3 agents if multiple high-priority tasks
    
    # SEQUENTIAL MODE (Ross is away, optimize cost):
    # - Late night (11pm-7am): He's sleeping
    # - Weekday work hours (9am-5pm): He's at work
    else:
        return False  # Spawn 1 at a time, queue others


def get_max_parallel_spawns():
    """How many agents can spawn at once"""
    if should_spawn_parallel():
        return 3  # Fast mode
    else:
        return 1  # Sequential mode


def is_quiet_hours():
    """Check if it's quiet hours (don't spawn unless urgent)"""
    current_hour = datetime.now().hour
    
    # QUIET HOURS: 2am-6am (deep sleep, even for overnight builds)
    if 2 <= current_hour < 6:
        return True
    
    return False


def estimate_build_time(task_description: str) -> int:
    """
    Estimate build time in minutes based on task description.
    Uses heuristics and pattern matching.
    
    Returns: estimated minutes
    """
    task_lower = task_description.lower()
    
    # Check for explicit ETA in task
    eta_match = re.search(r'eta:\s*(\d+)\s*min', task_lower)
    if eta_match:
        return int(eta_match.group(1))
    
    # Pattern-based estimates
    if any(word in task_lower for word in ["landing page", "simple page", "basic"]):
        return 30  # Landing pages: 30min
    
    if any(word in task_lower for word in ["integration", "api", "stripe", "payment"]):
        return 45  # Integrations: 45min
    
    if any(word in task_lower for word in ["dashboard", "admin", "complex"]):
        return 60  # Complex builds: 60min
    
    if any(word in task_lower for word in ["content", "generate", "write"]):
        return 20  # Content generation: 20min
    
    if "template" in task_lower:
        return 40  # Templates: 40min
    
    # Default estimate
    return 35  # Default: 35min


def estimate_build_cost(eta_minutes: int, task_description: str) -> float:
    """
    Estimate API cost based on build time and complexity.
    
    Returns: estimated cost in USD
    """
    # Base rate: ~$0.02 per minute of agent time (rough estimate)
    # This is based on Claude Sonnet 4.5 usage patterns
    base_cost_per_minute = 0.02
    
    # Adjust for complexity
    task_lower = task_description.lower()
    complexity_multiplier = 1.0
    
    if any(word in task_lower for word in ["complex", "advanced", "full"]):
        complexity_multiplier = 1.5
    elif any(word in task_lower for word in ["simple", "basic", "quick"]):
        complexity_multiplier = 0.7
    
    estimated_cost = eta_minutes * base_cost_per_minute * complexity_multiplier
    
    return round(estimated_cost, 2)


def batch_similar_tasks(tasks: List[Dict]) -> List[Dict]:
    """
    Identify tasks that can be batched together for efficiency.
    
    Smart batching:
    - Multiple landing pages → batch into one build
    - Similar content generation → batch
    - Similar integrations → batch
    
    Returns: list of batched tasks (some may be combined)
    """
    if len(tasks) <= 1:
        return tasks
    
    batched = []
    used_indices = set()
    
    # Look for landing page batching opportunities
    landing_pages = []
    for i, task in enumerate(tasks):
        if "landing page" in task["task"].lower() and i not in used_indices:
            landing_pages.append((i, task))
    
    if len(landing_pages) >= 2:
        # Batch them
        combined_task = {
            "status": "pending",
            "task": f"Build {len(landing_pages)} landing pages: " + 
                   ", ".join([t[1]["task"].split("landing page")[0].strip() for t in landing_pages]),
            "priority": "high",
            "eta_minutes": max(30, len(landing_pages) * 20),  # 20min per page after first
            "cost": None,
            "batched": True,
            "original_tasks": [t[1]["task"] for t in landing_pages]
        }
        batched.append(combined_task)
        used_indices.update([i for i, _ in landing_pages])
    
    # Look for content generation batching
    content_tasks = []
    for i, task in enumerate(tasks):
        if i not in used_indices and any(word in task["task"].lower() 
                                         for word in ["content", "generate", "write", "twitter", "post"]):
            content_tasks.append((i, task))
    
    if len(content_tasks) >= 2:
        combined_task = {
            "status": "pending",
            "task": f"Generate content batch: " + 
                   ", ".join([t[1]["task"][:50] for t in content_tasks]),
            "priority": "medium",
            "eta_minutes": len(content_tasks) * 15,
            "cost": None,
            "batched": True,
            "original_tasks": [t[1]["task"] for t in content_tasks]
        }
        batched.append(combined_task)
        used_indices.update([i for i, _ in content_tasks])
    
    # Add remaining unbatched tasks
    for i, task in enumerate(tasks):
        if i not in used_indices:
            batched.append(task)
    
    return batched


def load_retry_state() -> Dict:
    """Load retry state from file"""
    if not RETRY_STATE_FILE.exists():
        return {}
    
    try:
        with open(RETRY_STATE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_retry_state(state: Dict):
    """Save retry state to file"""
    with open(RETRY_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def handle_build_failure(task: str, attempt: int) -> Optional[str]:
    """
    Handle build failure with auto-retry logic.
    
    Retry strategy:
    - 1st failure → wait 5min → retry with refined prompt
    - 2nd failure → wait 10min → retry with simpler scope
    - 3rd failure → escalate to Ross
    
    Returns: action to take ("retry", "simplify", "escalate", or None if waiting)
    """
    retry_state = load_retry_state()
    
    task_key = task[:100]  # Use first 100 chars as key
    
    if task_key not in retry_state:
        retry_state[task_key] = {
            "task": task,
            "attempts": 1,
            "last_attempt": datetime.now().isoformat(),
            "next_retry": (datetime.now() + timedelta(minutes=5)).isoformat()
        }
        save_retry_state(retry_state)
        log_to_journal(f"⚠️ Build failed (attempt 1): {task}. Will retry in 5 minutes.")
        return None
    
    # Check if enough time has passed
    next_retry = datetime.fromisoformat(retry_state[task_key]["next_retry"])
    if datetime.now() < next_retry:
        return None  # Still waiting
    
    # Increment attempts
    retry_state[task_key]["attempts"] += 1
    retry_state[task_key]["last_attempt"] = datetime.now().isoformat()
    
    attempts = retry_state[task_key]["attempts"]
    
    if attempts == 2:
        # Second attempt: retry with refined prompt
        retry_state[task_key]["next_retry"] = (datetime.now() + timedelta(minutes=10)).isoformat()
        save_retry_state(retry_state)
        log_to_journal(f"🔄 Retry attempt 2: {task} (refined approach)")
        return "retry"
    
    elif attempts == 3:
        # Third attempt: simplify scope
        retry_state[task_key]["next_retry"] = (datetime.now() + timedelta(minutes=10)).isoformat()
        save_retry_state(retry_state)
        log_to_journal(f"🔄 Retry attempt 3: {task} (simplified scope)")
        return "simplify"
    
    else:
        # 3+ failures: escalate to Ross
        log_to_journal(f"🚨 Build failed 3 times: {task}. Escalating to Ross.")
        
        # Remove from retry state
        del retry_state[task_key]
        save_retry_state(retry_state)
        
        return "escalate"


def generate_tasks_from_goals():
    """
    Reads GOALS.md and recent memory, generates 1-3 tasks aligned with goals.
    Now includes time and cost estimates.
    """
    goals = read_goals()
    memory = read_recent_memory()
    
    if not goals:
        return []
    
    # Task generation logic
    tasks = []
    
    # Check memory for context clues
    fitness_mentioned = "fitness" in memory.lower() or "macro" in memory.lower()
    golf_mentioned = "golf" in memory.lower()
    notion_mentioned = "notion" in memory.lower()
    stripe_mentioned = "stripe" in memory.lower() or "payment" in memory.lower()
    
    # Revenue-focused tasks (highest priority)
    if not stripe_mentioned:
        task_desc = "Add Stripe integration to fitness tracker for $10/mo subscriptions"
        eta = estimate_build_time(task_desc)
        cost = estimate_build_cost(eta, task_desc)
        
        tasks.append({
            "priority": 1,
            "task": task_desc,
            "rationale": "Primary mission: $500 MRR. Fitness tracker mentioned in memory. Adding payment = first revenue.",
            "category": "revenue",
            "eta_minutes": eta,
            "cost": cost
        })
    
    if golf_mentioned and "golf coaching" not in memory.lower():
        task_desc = "Build golf coaching landing page with Stripe checkout ($29/mo)"
        eta = estimate_build_time(task_desc)
        cost = estimate_build_cost(eta, task_desc)
        
        tasks.append({
            "priority": 1,
            "task": task_desc,
            "rationale": "Quick win: Ross plays golf. Landing page can ship in <4 hours. Revenue potential: $29/mo.",
            "category": "revenue",
            "eta_minutes": eta,
            "cost": cost
        })
    
    if notion_mentioned:
        task_desc = "Create 'Side Hustler to $500 MRR' Notion template for Gumroad ($19-29)"
        eta = estimate_build_time(task_desc)
        cost = estimate_build_cost(eta, task_desc)
        
        tasks.append({
            "priority": 2,
            "task": task_desc,
            "rationale": "Ross is living this journey. Authentic template. Can ship in 2-3 hours.",
            "category": "revenue",
            "eta_minutes": eta,
            "cost": cost
        })
    
    # Automation tasks (time savings)
    if fitness_mentioned and "photo logger" not in memory.lower():
        task_desc = "Build photo food logger (snap pic → auto-log macros)"
        eta = estimate_build_time(task_desc)
        cost = estimate_build_cost(eta, task_desc)
        
        tasks.append({
            "priority": 2,
            "task": task_desc,
            "rationale": "Ross logs food 5x/day. Automation saves 10min/day = 1+ hr/week.",
            "category": "automation",
            "eta_minutes": eta,
            "cost": cost
        })
    
    # Content generation (audience building → future revenue)
    if "social" in memory.lower() or "twitter" in memory.lower():
        task_desc = "Generate 7 days of Twitter content about side hustle journey"
        eta = estimate_build_time(task_desc)
        cost = estimate_build_cost(eta, task_desc)
        
        tasks.append({
            "priority": 3,
            "task": task_desc,
            "rationale": "Audience building. Ross wants to build in public. Low effort, high leverage.",
            "category": "content",
            "eta_minutes": eta,
            "cost": cost
        })
    
    # Sort by priority, return top 3
    tasks.sort(key=lambda x: x["priority"])
    
    # Apply task batching intelligence
    batched_tasks = batch_similar_tasks(tasks[:3])
    
    return batched_tasks


def write_tasks_to_queue(tasks):
    """Write generated tasks to BUILD_QUEUE.md with estimates"""
    if not tasks:
        return
    
    # Read existing queue
    existing_content = ""
    if BUILD_QUEUE_FILE.exists():
        with open(BUILD_QUEUE_FILE, "r") as f:
            existing_content = f.read()
    
    # Append new tasks
    new_tasks_section = "\n\n## Auto-Generated Tasks (by autonomous_check.py)\n"
    new_tasks_section += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    
    for task in tasks:
        eta_str = f"{task.get('eta_minutes', 35)}min"
        cost_str = f"~${task.get('cost', 0.70):.2f}"
        priority_map = {1: "High", 2: "Medium", 3: "Low"}
        priority_str = priority_map.get(task.get('priority', 2), "Medium")
        
        new_tasks_section += f"- [ ] {task['task']}\n"
        new_tasks_section += f"  - **Priority:** {priority_str}\n"
        new_tasks_section += f"  - **ETA:** {eta_str}\n"
        new_tasks_section += f"  - **Cost:** {cost_str}\n"
        new_tasks_section += f"  - **Category:** {task.get('category', 'general')}\n"
        new_tasks_section += f"  - **Rationale:** {task.get('rationale', 'N/A')}\n"
        
        if task.get('batched'):
            new_tasks_section += f"  - **Batched:** Yes ({len(task.get('original_tasks', []))} tasks combined)\n"
        
        new_tasks_section += "\n"
    
    with open(BUILD_QUEUE_FILE, "w") as f:
        f.write(existing_content + new_tasks_section)
    
    log_to_journal(f"✅ Generated {len(tasks)} tasks and added to BUILD_QUEUE.md")


def should_spawn_build():
    """
    Determine if we should auto-spawn a build.
    
    Checks:
    - Is autonomy paused?
    - Is there a pending task in queue?
    - Is nothing currently building?
    - Is it appropriate time? (quiet hours, parallel limits)
    """
    # Check if paused
    if PAUSE_FILE.exists():
        log_to_journal("⏸️ Autonomy is paused. Not spawning.")
        return False
    
    # Check if anything is building
    if read_build_status():
        log_to_journal("⏸️ Build already in progress. Not spawning new one.")
        return False
    
    # Check queue for pending tasks
    queue = read_build_queue()
    pending = [t for t in queue if t["status"] == "pending"]
    
    if not pending:
        log_to_journal("📭 No pending tasks in queue.")
        return False
    
    # Check quiet hours (unless task is marked URGENT)
    if is_quiet_hours():
        urgent = any("urgent" in t["task"].lower() for t in pending)
        if not urgent:
            log_to_journal(f"🌙 Quiet hours (2am-6am). Waiting for better time to spawn build.")
            return False
    
    # Check time (don't spawn builds late night 23:00-02:00 unless urgent)
    hour = datetime.now().hour
    if hour >= 23 or hour < 2:
        urgent = any("urgent" in t["task"].lower() for t in pending)
        if not urgent:
            log_to_journal(f"🌙 Late night ({hour}:00). Waiting for better time to spawn build.")
            return False
    
    return True


def spawn_next_build():
    """
    Prepare the next pending build from BUILD_QUEUE.md
    
    Writes spawn instructions to a signal file that the calling agent will read.
    The agent has sessions_spawn tool access; this script doesn't.
    
    Returns the task info for the calling agent to spawn.
    """
    queue = read_build_queue()
    pending = [t for t in queue if t["status"] == "pending"]
    
    if not pending:
        return None
    
    # Sort by priority (high first)
    priority_order = {"high": 1, "medium": 2, "low": 3}
    pending.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 2))
    
    next_task = pending[0]
    
    # Calculate ETA if not present
    if not next_task.get("eta_minutes"):
        next_task["eta_minutes"] = estimate_build_time(next_task["task"])
    
    if not next_task.get("cost"):
        next_task["cost"] = estimate_build_cost(next_task["eta_minutes"], next_task["task"])
    
    log_to_journal(f"🚀 Ready to spawn build: {next_task['task']} (ETA: {next_task['eta_minutes']}min, Cost: ${next_task['cost']:.2f})")
    
    # Create label from task (first 30 chars, sanitized)
    label = "build-" + next_task["task"][:30].lower().replace(" ", "-").replace("/", "-")
    label = ''.join(c for c in label if c.isalnum() or c == '-')
    
    # Determine model based on task category
    task_lower = next_task["task"].lower()
    use_opus = any([
        "stripe" in task_lower,
        "payment" in task_lower,
        "landing page" in task_lower,
        "revenue" in task_lower,
        "checkout" in task_lower,
        "subscription" in task_lower,
        "conversion" in task_lower,
        next_task.get("category") == "revenue"
    ])
    
    model = "opus" if use_opus else "sonnet5"
    
    # Write spawn signal for agent to pick up
    spawn_signal = {
        "ready": True,
        "task": next_task["task"],
        "label": label,
        "priority": next_task.get("priority", "medium"),
        "eta_minutes": next_task.get("eta_minutes", 35),
        "cost": next_task.get("cost", 0.70),
        "model": model,
        "timestamp": datetime.now().isoformat()
    }
    
    spawn_signal_file = MEMORY_DIR / "spawn-signal.json"
    with open(spawn_signal_file, "w") as f:
        json.dump(spawn_signal, f, indent=2)
    
    log_to_journal(f"📝 Spawn signal written: {label}")
    
    return spawn_signal


def main():
    """Main autonomous check logic"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Force spawn even if conditions not met")
    args = parser.parse_args()
    
    print("🤖 Running autonomous check (UPGRADED)...")
    log_to_journal("🤖 Autonomous check started (efficiency mode)")
    
    # Show mode
    if should_spawn_parallel():
        print(f"⚡ PARALLEL MODE (max {get_max_parallel_spawns()} concurrent builds)")
    else:
        print("🔄 SEQUENTIAL MODE (1 build at a time)")
    
    # Step 1: Read goals
    goals = read_goals()
    if not goals:
        print("❌ Cannot proceed without GOALS.md")
        return
    
    print("✅ GOALS.md loaded")
    
    # Step 2: Check BUILD_QUEUE.md
    queue = read_build_queue()
    pending = [t for t in queue if t["status"] == "pending"]
    
    print(f"📋 Current queue: {len(pending)} pending tasks")
    
    # Step 3: Generate tasks if queue is empty
    if len(pending) == 0:
        print("🧠 Queue empty. Generating tasks from goals...")
        tasks = generate_tasks_from_goals()
        
        if tasks:
            print(f"✨ Generated {len(tasks)} tasks:")
            for task in tasks:
                eta = task.get('eta_minutes', 35)
                cost = task.get('cost', 0.70)
                print(f"  - [{task.get('priority', 2)}] {task['task']}")
                print(f"    └─ ETA: {eta}min, Cost: ~${cost:.2f}")
            
            write_tasks_to_queue(tasks)
        else:
            print("💭 No new tasks generated (nothing actionable in current context)")
            log_to_journal("💭 No new tasks generated from goals")
    else:
        print(f"✅ Queue has {len(pending)} pending tasks. No generation needed.")
    
    # Step 4: Check if we should spawn a build
    if should_spawn_build() or args.force:
        spawn_signal = spawn_next_build()
        if spawn_signal:
            print(f"\n🚀 READY TO SPAWN BUILD!")
            print(f"   Signal file: memory/spawn-signal.json")
            print(f"   Label: {spawn_signal['label']}")
            print(f"   Task: {spawn_signal['task']}")
            print(f"   Priority: {spawn_signal.get('priority', 'medium')}")
            print(f"   ETA: {spawn_signal.get('eta_minutes', 35)} minutes")
            print(f"   Est. Cost: ${spawn_signal.get('cost', 0.70):.2f}")
            
            # Calculate expected completion time
            completion_time = datetime.now() + timedelta(minutes=spawn_signal.get('eta_minutes', 35))
            print(f"   Expected completion: {completion_time.strftime('%I:%M %p')}")
            print(f"\n👉 Agent will spawn this via sessions_spawn tool")
        else:
            print("⚠️ No pending tasks to spawn")
    else:
        print("⏸️ Not spawning build (conditions not met or paused)")
        
        # Show reason
        if PAUSE_FILE.exists():
            print("   Reason: Autonomy is paused")
        elif is_quiet_hours():
            print("   Reason: Quiet hours (2am-6am)")
        elif read_build_status():
            print("   Reason: Build already in progress")
    
    print("\n✅ Autonomous check complete")
    log_to_journal("✅ Autonomous check complete")


if __name__ == "__main__":
    main()
