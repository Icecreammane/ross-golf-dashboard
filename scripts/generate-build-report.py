#!/usr/bin/env python3
"""
Nightly Build Reporter
Auto-generates summary of what shipped today.
Saves to ~/clawd/build-reports/YYYY-MM-DD.md in email/Telegram-ready format.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import re

# Configuration
WORKSPACE = Path.home() / "clawd"
BUILD_REPORTS_DIR = WORKSPACE / "build-reports"
SUBAGENTS_DIR = WORKSPACE / "subagents"
MEMORY_DIR = WORKSPACE / "memory"
BUILD_QUEUE_FILE = WORKSPACE / "build-queue.md"
ACTIVE_FILE = SUBAGENTS_DIR / "active.json"

# Ensure directories exist
BUILD_REPORTS_DIR.mkdir(exist_ok=True)


def load_active_builds():
    """Load active and completed builds from active.json"""
    if not ACTIVE_FILE.exists():
        return {"active": [], "completed": []}
    
    try:
        with open(ACTIVE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"active": [], "completed": []}


def parse_build_queue():
    """Extract completed items from build-queue.md"""
    if not BUILD_QUEUE_FILE.exists():
        return []
    
    with open(BUILD_QUEUE_FILE, 'r') as f:
        content = f.read()
    
    # Find the COMPLETED section
    completed_section = re.search(r'## ✅ COMPLETED\n\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if not completed_section:
        return []
    
    # Extract items
    items = []
    lines = completed_section.group(1).strip().split('\n')
    for line in lines:
        if line.strip().startswith('- **'):
            # Extract project name
            match = re.search(r'\*\*(.+?)\*\*', line)
            if match:
                items.append(match.group(1))
    
    return items


def get_todays_progress_logs():
    """Find all progress logs updated today"""
    today = datetime.now().date()
    progress_logs = []
    
    if not SUBAGENTS_DIR.exists():
        return progress_logs
    
    for log_file in SUBAGENTS_DIR.glob('*-progress.md'):
        stat = log_file.stat()
        modified_date = datetime.fromtimestamp(stat.st_mtime).date()
        
        if modified_date == today:
            with open(log_file, 'r') as f:
                content = f.read()
            
            progress_logs.append({
                'agent': log_file.stem.replace('-progress', ''),
                'content': content
            })
    
    return progress_logs


def get_todays_memory():
    """Load today's memory log for context"""
    today = datetime.now().strftime('%Y-%m-%d')
    memory_file = MEMORY_DIR / f"{today}.md"
    
    if not memory_file.exists():
        return None
    
    with open(memory_file, 'r') as f:
        return f.read()


def count_deliverables(build_data):
    """Count total deliverables from completed builds"""
    count = 0
    for build in build_data.get('completed', []):
        if 'deliverables' in build:
            count += len(build['deliverables'])
    return count


def generate_report():
    """Generate the nightly build report"""
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    
    # Load data
    build_data = load_active_builds()
    completed_queue = parse_build_queue()
    progress_logs = get_todays_progress_logs()
    memory = get_todays_memory()
    
    # Count stats
    active_count = len(build_data.get('active', []))
    completed_count = len(build_data.get('completed', []))
    deliverables_count = count_deliverables(build_data)
    
    # Build report
    report = f"""# 📊 Nightly Build Report
**Date:** {today.strftime('%B %d, %Y')}
**Generated:** {today.strftime('%I:%M %p %Z')}

---

## 🎯 Summary

"""
    
    if completed_count == 0 and active_count == 0:
        report += "**Status:** 🌙 Quiet night - no builds in progress\n\n"
    elif completed_count > 0:
        report += f"**Status:** ✅ {completed_count} build{'s' if completed_count != 1 else ''} completed\n"
        report += f"**Deliverables:** {deliverables_count} items shipped\n"
        if active_count > 0:
            report += f"**In Progress:** {active_count} build{'s' if active_count != 1 else ''} still running\n"
        report += "\n"
    else:
        report += f"**Status:** 🔨 {active_count} build{'s' if active_count != 1 else ''} in progress\n\n"
    
    # Completed Builds
    if build_data.get('completed'):
        report += "## ✅ Completed Builds\n\n"
        for build in build_data['completed']:
            report += f"### {build.get('label', 'Unnamed Build')}\n"
            report += f"**Completed:** {build.get('completed', 'Unknown time')}\n"
            if 'duration' in build:
                report += f"**Duration:** {build['duration']}\n"
            report += "\n"
            
            if 'deliverables' in build:
                report += "**Deliverables:**\n"
                for item in build['deliverables']:
                    report += f"- ✓ {item}\n"
                report += "\n"
            
            if 'links' in build:
                report += "**Links:**\n"
                for link in build['links']:
                    report += f"- [{link['label']}]({link['url']})\n"
                report += "\n"
    
    # Active Builds
    if build_data.get('active'):
        report += "## 🔨 Active Builds\n\n"
        for build in build_data['active']:
            report += f"### {build.get('label', 'Unnamed Build')}\n"
            report += f"**Started:** {build.get('started', 'Unknown time')}\n"
            report += f"**Status:** {build.get('status', 'unknown')}\n"
            
            if 'tasks' in build:
                completed_tasks = [t for t in build['tasks'] if isinstance(t, dict) and t.get('status') == 'done']
                total_tasks = len(build['tasks'])
                progress = (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0
                report += f"**Progress:** {progress:.0f}% ({len(completed_tasks)}/{total_tasks} tasks)\n"
            
            report += "\n"
    
    # Completed Queue Items
    if completed_queue:
        report += "## 📋 Completed Queue Items\n\n"
        for item in completed_queue:
            report += f"- {item}\n"
        report += "\n"
    
    # Progress Logs
    if progress_logs:
        report += "## 📝 Progress Logs Updated Today\n\n"
        for log in progress_logs:
            report += f"### {log['agent']}\n"
            report += "```\n"
            # Include last 20 lines of progress log
            lines = log['content'].split('\n')
            report += '\n'.join(lines[-20:])
            report += "\n```\n\n"
    
    # Footer
    report += "---\n\n"
    report += "## 📬 Delivery\n\n"
    report += "**Ready for:**\n"
    report += "- ✉️ Email (copy/paste into Gmail)\n"
    report += "- 💬 Telegram (formatted and ready)\n"
    report += "- 📄 Archive (saved in build-reports/)\n\n"
    
    report += f"**Dashboard:** [View Progress](file://{WORKSPACE}/progress.html)\n"
    report += f"**Build Queue:** [View Queue](file://{BUILD_QUEUE_FILE})\n\n"
    
    report += "*Generated by nightly build reporter - Clawdbot autonomous build system*\n"
    
    return report


def save_report(report):
    """Save report to file"""
    today = datetime.now().strftime('%Y-%m-%d')
    report_file = BUILD_REPORTS_DIR / f"{today}.md"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    return report_file


def main():
    """Generate and save the nightly build report"""
    print("🔨 Generating nightly build report...")
    
    try:
        report = generate_report()
        report_file = save_report(report)
        
        print(f"✅ Report generated: {report_file}")
        print()
        print("Preview:")
        print("=" * 60)
        print(report[:500] + "..." if len(report) > 500 else report)
        print("=" * 60)
        print()
        print(f"📄 Full report saved to: {report_file}")
        
        return 0
    
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
