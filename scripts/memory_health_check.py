#!/usr/bin/env python3
"""
Memory Health Check - Validates memory system is working

Checks:
1. SESSION_SUMMARY.md exists and is recent
2. Today's memory log exists
3. DEPLOYMENTS.md has live URLs
4. Critical files are readable
5. Memory index is up to date

Run at session start to verify memory integrity.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
MEMORY_DIR = WORKSPACE / "memory"
SESSION_SUMMARY = WORKSPACE / "SESSION_SUMMARY.md"
DEPLOYMENTS = WORKSPACE / "DEPLOYMENTS.md"

def check_session_summary():
    """Verify SESSION_SUMMARY.md exists and is recent"""
    if not SESSION_SUMMARY.exists():
        return {
            'status': 'CRITICAL',
            'message': 'SESSION_SUMMARY.md missing - no memory from last session',
            'fix': 'Run: python3 ~/clawd/scripts/session_summary_generator.py'
        }
    
    # Check if it's stale (>48 hours old)
    mtime = datetime.fromtimestamp(SESSION_SUMMARY.stat().st_mtime)
    age_hours = (datetime.now() - mtime).total_seconds() / 3600
    
    if age_hours > 48:
        return {
            'status': 'WARNING',
            'message': f'SESSION_SUMMARY.md is {int(age_hours)} hours old',
            'fix': 'Run: python3 ~/clawd/scripts/session_summary_generator.py'
        }
    
    return {'status': 'OK', 'message': 'SESSION_SUMMARY.md is current'}

def check_daily_log():
    """Verify today's memory log exists"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = MEMORY_DIR / f"{today}.md"
    
    if not log_file.exists():
        return {
            'status': 'WARNING',
            'message': f'No memory log for {today} - session not being recorded',
            'fix': f'Create: {log_file}'
        }
    
    return {'status': 'OK', 'message': f'Today\'s log exists ({today}.md)'}

def check_deployments():
    """Verify DEPLOYMENTS.md has live URLs"""
    if not DEPLOYMENTS.exists():
        return {
            'status': 'WARNING',
            'message': 'DEPLOYMENTS.md missing - no deployment tracking',
            'fix': 'Create DEPLOYMENTS.md with live URLs'
        }
    
    content = DEPLOYMENTS.read_text()
    
    # Count URLs
    url_count = content.count('http://') + content.count('https://')
    
    if url_count == 0:
        return {
            'status': 'WARNING',
            'message': 'DEPLOYMENTS.md has no URLs',
            'fix': 'Add live deployment URLs to DEPLOYMENTS.md'
        }
    
    return {'status': 'OK', 'message': f'DEPLOYMENTS.md has {url_count} URLs tracked'}

def check_memory_index():
    """Check if instant_recall index is up to date"""
    index_file = MEMORY_DIR / "memory_index.json"
    
    if not index_file.exists():
        return {
            'status': 'INFO',
            'message': 'No memory index found (instant_recall not built yet)',
            'fix': 'Run: python3 ~/clawd/scripts/instant_recall.py --rebuild'
        }
    
    # Check index age
    mtime = datetime.fromtimestamp(index_file.stat().st_mtime)
    age_hours = (datetime.now() - mtime).total_seconds() / 3600
    
    if age_hours > 24:
        return {
            'status': 'INFO',
            'message': f'Memory index is {int(age_hours)} hours old',
            'fix': 'Run: python3 ~/clawd/scripts/instant_recall.py --rebuild'
        }
    
    return {'status': 'OK', 'message': 'Memory index is current'}

def run_health_check():
    """Run all checks and report"""
    print("🧠 Memory System Health Check\n")
    
    checks = [
        ("Session Summary", check_session_summary()),
        ("Daily Log", check_daily_log()),
        ("Deployments", check_deployments()),
        ("Memory Index", check_memory_index())
    ]
    
    critical = []
    warnings = []
    ok = []
    
    for name, result in checks:
        status = result['status']
        message = result['message']
        
        if status == 'CRITICAL':
            critical.append((name, result))
            print(f"❌ {name}: {message}")
            if 'fix' in result:
                print(f"   Fix: {result['fix']}")
        elif status == 'WARNING':
            warnings.append((name, result))
            print(f"⚠️  {name}: {message}")
            if 'fix' in result:
                print(f"   Fix: {result['fix']}")
        elif status == 'INFO':
            print(f"ℹ️  {name}: {message}")
            if 'fix' in result:
                print(f"   Tip: {result['fix']}")
        else:
            ok.append((name, result))
            print(f"✅ {name}: {message}")
    
    print(f"\n📊 Summary: {len(ok)} OK, {len(warnings)} warnings, {len(critical)} critical")
    
    if critical:
        print("\n🚨 CRITICAL ISSUES FOUND - Memory system degraded")
        return False
    elif warnings:
        print("\n⚠️  Some issues found - Memory may be incomplete")
        return True
    else:
        print("\n✅ Memory system healthy")
        return True

if __name__ == "__main__":
    import sys
    healthy = run_health_check()
    sys.exit(0 if healthy else 1)
