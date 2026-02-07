#!/usr/bin/env python3
"""
Cron Manager CLI
Manage Jarvis's automated cron jobs
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import re

# Configuration
HOME = Path.home()
JOBS_DIR = HOME / "clawd" / "automation" / "jobs"
LOG_DIR = HOME / "clawd" / "logs" / "cron"
CRON_COMMENT = "# Jarvis Automation"

# Job definitions
JOBS = {
    "morning-brief": {
        "schedule": "30 7 * * *",
        "script": "morning-brief.sh",
        "description": "Morning brief generation with voice"
    },
    "deal-flow-update": {
        "schedule": "0 9 * * *",
        "script": "deal-flow-update.sh",
        "description": "Deal flow pipeline update"
    },
    "nba-update": {
        "schedule": "0 10 * * *",
        "script": "nba-update.sh",
        "description": "NBA rankings refresh"
    },
    "health-check": {
        "schedule": "0 12 * * *",
        "script": "health-check.sh",
        "description": "System health diagnostics"
    },
    "evening-checkin": {
        "schedule": "0 20 * * *",
        "script": "evening-checkin.sh",
        "description": "Evening check-in trigger"
    },
    "overnight-research": {
        "schedule": "0 23 * * *",
        "script": "overnight-research.sh",
        "description": "Overnight builds and research"
    }
}


def get_current_crontab():
    """Get current crontab contents"""
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        return ""
    except Exception:
        return ""


def list_jobs():
    """List all Jarvis cron jobs"""
    crontab = get_current_crontab()
    
    print("Jarvis Automated Jobs")
    print("=" * 70)
    print(f"{'Job':<20} {'Schedule':<15} {'Status':<10} {'Description'}")
    print("-" * 70)
    
    for job_name, config in JOBS.items():
        # Check if job is in crontab
        pattern = f"{JOBS_DIR}/{config['script']}"
        is_enabled = pattern in crontab and not f"#{pattern}" in crontab
        status = "✓ Enabled" if is_enabled else "✗ Disabled"
        
        print(f"{job_name:<20} {config['schedule']:<15} {status:<10} {config['description']}")


def enable_job(job_name):
    """Enable a specific job"""
    if job_name not in JOBS:
        print(f"Error: Unknown job '{job_name}'")
        print(f"Available jobs: {', '.join(JOBS.keys())}")
        return 1
    
    config = JOBS[job_name]
    crontab = get_current_crontab()
    
    # Check if already enabled
    script_path = f"{JOBS_DIR}/{config['script']}"
    if script_path in crontab and not f"#{script_path}" in crontab:
        print(f"Job '{job_name}' is already enabled")
        return 0
    
    # Remove any disabled version
    lines = crontab.split('\n')
    lines = [l for l in lines if script_path not in l]
    
    # Add enabled job
    job_line = f"{config['schedule']} {script_path}  {CRON_COMMENT} {job_name}"
    lines.append(job_line)
    
    # Update crontab
    new_crontab = '\n'.join(lines)
    try:
        subprocess.run(["crontab", "-"], input=new_crontab, text=True, check=True)
        print(f"✓ Enabled job '{job_name}'")
        print(f"  Schedule: {config['schedule']}")
        print(f"  Script: {config['script']}")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error updating crontab: {e}")
        return 1


def disable_job(job_name):
    """Disable a specific job"""
    if job_name not in JOBS:
        print(f"Error: Unknown job '{job_name}'")
        print(f"Available jobs: {', '.join(JOBS.keys())}")
        return 1
    
    config = JOBS[job_name]
    crontab = get_current_crontab()
    script_path = f"{JOBS_DIR}/{config['script']}"
    
    # Remove job from crontab
    lines = crontab.split('\n')
    lines = [l for l in lines if script_path not in l]
    
    # Update crontab
    new_crontab = '\n'.join(lines)
    try:
        subprocess.run(["crontab", "-"], input=new_crontab, text=True, check=True)
        print(f"✓ Disabled job '{job_name}'")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error updating crontab: {e}")
        return 1


def show_status():
    """Show detailed status of all jobs"""
    print("Jarvis Cron Jobs - Detailed Status")
    print("=" * 70)
    
    for job_name, config in JOBS.items():
        print(f"\n{job_name}")
        print(f"  Description: {config['description']}")
        print(f"  Schedule: {config['schedule']}")
        
        # Check if enabled
        crontab = get_current_crontab()
        script_path = f"{JOBS_DIR}/{config['script']}"
        is_enabled = script_path in crontab
        print(f"  Status: {'✓ Enabled' if is_enabled else '✗ Disabled'}")
        
        # Check for today's log
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = LOG_DIR / f"{job_name}-{today}.log"
        
        if log_file.exists():
            # Get last line from log
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        print(f"  Last run: {last_line}")
            except Exception:
                pass
        else:
            print(f"  Last run: No log for today")


def show_logs(job_name, lines=50):
    """Show recent logs for a job"""
    if job_name not in JOBS:
        print(f"Error: Unknown job '{job_name}'")
        return 1
    
    # Find most recent log file
    log_pattern = f"{job_name}-*.log"
    log_files = sorted(LOG_DIR.glob(log_pattern), reverse=True)
    
    if not log_files:
        print(f"No logs found for job '{job_name}'")
        return 1
    
    log_file = log_files[0]
    print(f"Showing last {lines} lines from: {log_file.name}")
    print("=" * 70)
    
    try:
        result = subprocess.run(["tail", f"-{lines}", str(log_file)], 
                              capture_output=True, text=True)
        print(result.stdout)
        return 0
    except Exception as e:
        print(f"Error reading log: {e}")
        return 1


def test_job(job_name):
    """Test run a job manually"""
    if job_name not in JOBS:
        print(f"Error: Unknown job '{job_name}'")
        return 1
    
    config = JOBS[job_name]
    script_path = JOBS_DIR / config['script']
    
    if not script_path.exists():
        print(f"Error: Script not found: {script_path}")
        return 1
    
    print(f"Testing job: {job_name}")
    print(f"Running: {script_path}")
    print("=" * 70)
    
    try:
        result = subprocess.run([str(script_path)], cwd=HOME)
        print("=" * 70)
        if result.returncode == 0:
            print(f"✓ Test successful")
        else:
            print(f"✗ Test failed with exit code {result.returncode}")
        return result.returncode
    except Exception as e:
        print(f"Error running test: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Manage Jarvis automated cron jobs",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # List command
    subparsers.add_parser('list', help='List all cron jobs')
    
    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Enable a job')
    enable_parser.add_argument('job', help='Job name')
    
    # Disable command
    disable_parser = subparsers.add_parser('disable', help='Disable a job')
    disable_parser.add_argument('job', help='Job name')
    
    # Status command
    subparsers.add_parser('status', help='Show detailed status of all jobs')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='Show logs for a job')
    logs_parser.add_argument('job', help='Job name')
    logs_parser.add_argument('-n', '--lines', type=int, default=50, 
                           help='Number of lines to show (default: 50)')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test run a job')
    test_parser.add_argument('job', help='Job name')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate function
    if args.command == 'list':
        list_jobs()
        return 0
    elif args.command == 'enable':
        return enable_job(args.job)
    elif args.command == 'disable':
        return disable_job(args.job)
    elif args.command == 'status':
        show_status()
        return 0
    elif args.command == 'logs':
        return show_logs(args.job, args.lines)
    elif args.command == 'test':
        return test_job(args.job)
    
    return 1


if __name__ == '__main__':
    sys.exit(main())
