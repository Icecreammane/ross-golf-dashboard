#!/usr/bin/env python3
"""
Nightly Build Report Generator
Reads build logs and generates summary report
"""

import os
from datetime import datetime
import json

def parse_build_log(log_path):
    """Parse the daily build log markdown file"""
    if not os.path.exists(log_path):
        return {"error": "Log file not found"}
    
    with open(log_path, 'r') as f:
        content = f.read()
    
    # Extract key metrics
    tasks_done = content.count('✅')
    tasks_building = content.count('🔨')
    tasks_pending = content.count('⏳')
    blockers = content.count('🚫')
    
    return {
        "completed": tasks_done,
        "in_progress": tasks_building,
        "pending": tasks_pending,
        "blockers": blockers,
        "content": content
    }

def generate_report(date_str):
    """Generate build report for a given date"""
    log_path = f"/Users/clawdbot/clawd/memory/{date_str}.md"
    output_path = f"/Users/clawdbot/clawd/build-report-{date_str}.md"
    
    stats = parse_build_log(log_path)
    
    if "error" in stats:
        return f"Error: {stats['error']}"
    
    # Calculate progress percentage
    total = stats["completed"] + stats["in_progress"] + stats["pending"]
    progress = (stats["completed"] / total * 100) if total > 0 else 0
    
    report = f"""# Build Report - {date_str}

## Summary
- **Overall Progress:** {progress:.1f}%
- **Tasks Completed:** {stats["completed"]}
- **Tasks In Progress:** {stats["in_progress"]}
- **Tasks Pending:** {stats["pending"]}
- **Blockers:** {stats["blockers"]}

## Status Breakdown

### ✅ Completed Tasks
"""
    
    # Extract completed items from log
    lines = stats["content"].split('\n')
    for line in lines:
        if '✅' in line:
            report += f"- {line.strip()}\n"
    
    report += "\n### 🔨 In Progress\n"
    for line in lines:
        if '🔨' in line:
            report += f"- {line.strip()}\n"
    
    report += "\n### ⏳ Pending\n"
    for line in lines:
        if '⏳' in line:
            report += f"- {line.strip()}\n"
    
    if stats["blockers"] > 0:
        report += "\n### 🚫 Blockers\n"
        for line in lines:
            if '🚫' in line or 'BLOCKER' in line.upper():
                report += f"- {line.strip()}\n"
    
    report += f"""

## Key Achievements
*(Review the log above and highlight wins)*

## Lessons Learned
*(Document what worked, what didn't)*

## Next Steps
*(What needs to happen next)*

---
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Source: {log_path}*
"""
    
    with open(output_path, 'w') as f:
        f.write(report)
    
    return f"Report generated: {output_path}"

if __name__ == "__main__":
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')
    result = generate_report(date)
    print(result)
