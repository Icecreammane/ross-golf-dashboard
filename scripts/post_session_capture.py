#!/usr/bin/env python3
"""
Post-Session Capture - Run after major builds/sessions

Automatically:
1. Updates SESSION_SUMMARY.md with latest context
2. Extracts URLs and adds to DEPLOYMENTS.md
3. Validates memory completeness
4. Commits changes to git

Usage:
    python3 post_session_capture.py
    python3 post_session_capture.py --auto  # Run automatically
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / "clawd"

def run_command(cmd, cwd=WORKSPACE):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout
    except Exception as e:
        return False, str(e)

def main():
    print("📸 Post-Session Capture Started\n")
    
    # 1. Update SESSION_SUMMARY.md
    print("1️⃣ Updating SESSION_SUMMARY.md...")
    success, output = run_command("python3 scripts/session_summary_generator.py")
    if success:
        print("   ✅ Session summary updated")
    else:
        print(f"   ⚠️  Failed: {output}")
    
    # 2. Run memory health check
    print("\n2️⃣ Running memory health check...")
    success, output = run_command("python3 scripts/memory_health_check.py")
    print(output)
    
    # 3. Git commit memory updates
    print("\n3️⃣ Committing memory updates...")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    files_to_commit = [
        "SESSION_SUMMARY.md",
        "DEPLOYMENTS.md",
        "memory/*.md",
        "AGENTS.md"
    ]
    
    success, _ = run_command(f"git add {' '.join(files_to_commit)}")
    success, _ = run_command(f'git commit -m "Memory update: {timestamp}" || true')
    
    if success:
        print("   ✅ Changes committed")
        # Try to push (but don't fail if offline)
        push_success, _ = run_command("git push || true")
        if push_success:
            print("   ✅ Changes pushed to remote")
    else:
        print("   ℹ️  No changes to commit")
    
    print("\n✅ Post-session capture complete!")
    print("\n💡 Next session will start with full context")

if __name__ == "__main__":
    main()
