#!/usr/bin/env python3
"""
Add Build Task - Quick CLI for adding tasks to BUILD_QUEUE.md

Usage:
    python3 add_build_task.py --name "Task Name" --desc "Description" --priority high
    python3 add_build_task.py --name "Task Name" --desc "Description" --priority medium --time "4 hours"
"""

import argparse
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
BUILD_QUEUE = WORKSPACE / "BUILD_QUEUE.md"


def add_task(name, description, priority="Medium", estimated_time="Unknown", tech_stack="", notes=""):
    """Add task to BUILD_QUEUE.md"""
    
    # Ensure BUILD_QUEUE.md exists
    if not BUILD_QUEUE.exists():
        initialize_queue()
    
    content = BUILD_QUEUE.read_text()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Add to queue section based on priority
    if priority.lower() == "high":
        section = "## 🔴 Priority (Building Now)"
        # Actually add to "Active Queue" below building
        section = "## 🟡 Active Queue (Next Up)"
    elif priority.lower() == "medium":
        section = "## 📊 MEDIUM PRIORITY (Do Soon)"
    else:
        section = "## 💡 LOW PRIORITY (Nice to Have)"
    
    # Create queue entry
    queue_entry = f"- [ ] {name} - Added: {now} - Priority: {priority.capitalize()}\n"
    
    # Add to queue section
    if section in content:
        content = content.replace(section, f"{section}\n{queue_entry}")
    else:
        # Section doesn't exist, add it
        content += f"\n{section}\n{queue_entry}\n"
    
    # Add to Task Details section
    details_section = "## 📋 Task Details"
    
    task_details = f"""
### {name}
- **Description:** {description}
- **Completion Criteria:** {notes if notes else "To be defined"}
- **Tech Stack:** {tech_stack if tech_stack else "To be determined"}
- **Estimated Time:** {estimated_time}
- **Priority:** {priority.capitalize()}
- **Added:** {now}
"""
    
    if details_section in content:
        # Find the end of the details section (next ## or end of file)
        details_match = re.search(r'(## 📋 Task Details.*?)(?=\n##|\Z)', content, re.DOTALL)
        if details_match:
            existing_details = details_match.group(1)
            new_details = existing_details + task_details
            content = content.replace(existing_details, new_details)
    else:
        # Add details section
        content += f"\n{details_section}\n{task_details}\n"
    
    # Update timestamp
    content = re.sub(
        r'\*Last updated:.*?\*',
        f'*Last updated: {now}*',
        content
    )
    
    BUILD_QUEUE.write_text(content)
    
    print(f"✅ Task added to BUILD_QUEUE.md")
    print(f"   Name: {name}")
    print(f"   Priority: {priority.capitalize()}")
    print(f"   Estimated Time: {estimated_time}")
    print(f"\nNext: Review BUILD_QUEUE.md and run auto_build_manager.py to start building")


def initialize_queue():
    """Initialize BUILD_QUEUE.md if it doesn't exist"""
    template = """# Build Queue - Jarvis Autonomous Builds

*Last updated: {timestamp}*

## 🔴 Priority (Building Now)
*Currently being built*

*(No active builds)*

## 🟡 Active Queue (Next Up)
*Ready to start*

*(Add high priority items here)*

## 📊 MEDIUM PRIORITY (Do Soon)

*(Add medium priority items here)*

## 💡 LOW PRIORITY (Nice to Have)

*(Future ideas and experiments)*

## 🟢 Completed (Last 7 Days)

*(Finished builds move here)*

## 📋 Task Details

*(Task specifications appear here)*

---

## Template: Add New Build Item

Copy this template when adding new items manually:

```markdown
- **[Project Name]** (label: [agent-label])
  - **Goal:** [What we're building and why]
  - **Deliverables:**
    - [ ] [Specific output 1]
    - [ ] [Specific output 2]
  - **Success Criteria:** [How we know it's done]
  - **Estimated Time:** [hours or days]
  - **Priority:** [high/medium/low]
```

---

*This queue is the single source of truth for what's being built.*
""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    BUILD_QUEUE.write_text(template)
    print(f"📝 Initialized BUILD_QUEUE.md")


def main():
    parser = argparse.ArgumentParser(description="Add task to BUILD_QUEUE.md")
    parser.add_argument("--name", required=True, help="Task name")
    parser.add_argument("--desc", "--description", required=True, help="Task description")
    parser.add_argument("--priority", default="Medium", choices=["high", "medium", "low", "High", "Medium", "Low"], help="Task priority")
    parser.add_argument("--time", "--estimated-time", default="Unknown", help="Estimated time (e.g., '2 hours', '1 day')")
    parser.add_argument("--tech", "--tech-stack", default="", help="Technologies to use")
    parser.add_argument("--notes", default="", help="Additional notes or completion criteria")
    
    args = parser.parse_args()
    
    add_task(
        name=args.name,
        description=args.desc,
        priority=args.priority,
        estimated_time=args.time,
        tech_stack=args.tech,
        notes=args.notes
    )


if __name__ == '__main__':
    main()
