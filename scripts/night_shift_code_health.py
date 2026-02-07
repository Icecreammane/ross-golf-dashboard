#!/usr/bin/env python3
"""
Night Shift: Code Health Report
Scans scripts for issues, duplicates, and optimization opportunities
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/Users/clawdbot/clawd")
SCRIPTS_DIR = WORKSPACE / "scripts"
OUTPUT_DIR = WORKSPACE / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def scan_scripts():
    """Scan all Python scripts"""
    if not SCRIPTS_DIR.exists():
        return []
    
    scripts = list(SCRIPTS_DIR.glob("*.py"))
    return scripts

def check_script_size(scripts):
    """Find large scripts that might need refactoring"""
    large = []
    for script in scripts:
        size = script.stat().st_size
        lines = len(script.read_text().splitlines())
        if lines > 200:
            large.append((script.name, lines, size))
    
    return large

def find_duplicates(scripts):
    """Find scripts with similar names (potential duplicates)"""
    names = defaultdict(list)
    for script in scripts:
        base = script.stem.replace('-', '_').replace('_', '')
        names[base].append(script.name)
    
    duplicates = {k: v for k, v in names.items() if len(v) > 1}
    return duplicates

def check_last_modified(scripts):
    """Find scripts not modified in 30+ days"""
    old = []
    now = datetime.now().timestamp()
    thirty_days = 30 * 24 * 60 * 60
    
    for script in scripts:
        mtime = script.stat().st_mtime
        if now - mtime > thirty_days:
            days_old = int((now - mtime) / (24 * 60 * 60))
            old.append((script.name, days_old))
    
    return sorted(old, key=lambda x: x[1], reverse=True)

def generate_report():
    """Generate code health report"""
    
    scripts = scan_scripts()
    large_scripts = check_script_size(scripts)
    duplicates = find_duplicates(scripts)
    old_scripts = check_last_modified(scripts)
    
    report = f"""# Code Health Report - {datetime.now().strftime('%Y-%m-%d')}

Generated at: {datetime.now().strftime('%I:%M %p')}

## Summary

- **Total Scripts:** {len(scripts)}
- **Large Scripts:** {len(large_scripts)} (>200 lines)
- **Potential Duplicates:** {len(duplicates)} groups
- **Stale Scripts:** {len(old_scripts)} (30+ days)

---

## Large Scripts (Consider Refactoring)

"""
    
    if large_scripts:
        for name, lines, size in sorted(large_scripts, key=lambda x: x[1], reverse=True)[:10]:
            report += f"- `{name}`: {lines} lines ({size} bytes)\n"
    else:
        report += "*No scripts over 200 lines - nice!*\n"
    
    report += "\n---\n\n## Potential Duplicates\n\n"
    
    if duplicates:
        for base, files in list(duplicates.items())[:5]:
            report += f"**{base}:**\n"
            for f in files:
                report += f"  - `{f}`\n"
    else:
        report += "*No duplicate script names detected*\n"
    
    report += "\n---\n\n## Stale Scripts (30+ days)\n\n"
    
    if old_scripts:
        for name, days in old_scripts[:10]:
            report += f"- `{name}`: {days} days old\n"
        report += "\n*Consider: Archive if unused, or verify still needed*\n"
    else:
        report += "*All scripts recently active*\n"
    
    report += """

---

## Recommendations

**Immediate Actions:**
- Review large scripts for refactoring opportunities
- Consolidate duplicate scripts if functionality overlaps
- Archive or document stale scripts

**Quick Wins:**
- Add docstrings to undocumented scripts
- Create README for scripts/ directory
- Set up automated testing for critical scripts

**Future:**
- Implement code linting (ruff/black)
- Add type hints
- Create script dependency map

---

*This report runs automatically. To improve detection, add more analysis rules.*
"""
    
    output_file = OUTPUT_DIR / f"code-health-{datetime.now().strftime('%Y%m%d')}.md"
    with open(output_file, "w") as f:
        f.write(report)
    
    return output_file

def main():
    print("💻 Night Shift: Code Health Report")
    print("=" * 50)
    
    print("\nScanning scripts...")
    print("Checking for large files...")
    print("Finding duplicates...")
    print("Identifying stale scripts...")
    
    report_file = generate_report()
    print(f"\n✅ Report: {report_file}")
    
    print("\n✨ Code health scan complete!")
    
    return {"report": str(report_file)}

if __name__ == "__main__":
    main()
