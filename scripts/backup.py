#!/usr/bin/env python3
"""
Automated backup system for Jarvis workspace
Runs daily via cron or on-demand
"""

import os
import shutil
from datetime import datetime
import json

WORKSPACE = os.path.expanduser("~/clawd")
BACKUP_DIR = os.path.expanduser("~/clawd/backups")
MAX_BACKUPS = 7  # Keep last 7 days

def create_backup():
    """Create timestamped backup of critical files"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
    
    # Ensure backup directory exists
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Critical files/dirs to backup
    to_backup = [
        "TODO.md",
        "CHANGELOG.md",
        "DECISIONS.md",
        "IDEAS.md",
        "AUTONOMOUS_WORK.md",
        "HEARTBEAT.md",
        "memory/",
        "projects/",
        "scripts/",
        "monitoring/",
        "ross/"
    ]
    
    os.makedirs(backup_path, exist_ok=True)
    
    backed_up = []
    for item in to_backup:
        source = os.path.join(WORKSPACE, item)
        if os.path.exists(source):
            dest = os.path.join(backup_path, item)
            try:
                if os.path.isdir(source):
                    shutil.copytree(source, dest)
                else:
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    shutil.copy2(source, dest)
                backed_up.append(item)
            except Exception as e:
                print(f"⚠️  Failed to backup {item}: {e}")
    
    # Create manifest
    manifest = {
        "timestamp": timestamp,
        "files": backed_up,
        "backup_path": backup_path
    }
    
    with open(os.path.join(backup_path, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Backup created: {backup_path}")
    print(f"📦 Backed up {len(backed_up)} items")
    
    # Cleanup old backups
    cleanup_old_backups()
    
    return backup_path

def cleanup_old_backups():
    """Remove backups older than MAX_BACKUPS"""
    if not os.path.exists(BACKUP_DIR):
        return
    
    backups = sorted([
        d for d in os.listdir(BACKUP_DIR) 
        if d.startswith("backup_") and os.path.isdir(os.path.join(BACKUP_DIR, d))
    ])
    
    while len(backups) > MAX_BACKUPS:
        old_backup = backups.pop(0)
        old_path = os.path.join(BACKUP_DIR, old_backup)
        try:
            shutil.rmtree(old_path)
            print(f"🗑️  Removed old backup: {old_backup}")
        except Exception as e:
            print(f"⚠️  Failed to remove {old_backup}: {e}")

def list_backups():
    """List available backups"""
    if not os.path.exists(BACKUP_DIR):
        print("No backups found")
        return
    
    backups = sorted([
        d for d in os.listdir(BACKUP_DIR) 
        if d.startswith("backup_") and os.path.isdir(os.path.join(BACKUP_DIR, d))
    ], reverse=True)
    
    print(f"\n📦 Available Backups ({len(backups)}):")
    print("━" * 50)
    for backup in backups:
        manifest_path = os.path.join(BACKUP_DIR, backup, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path) as f:
                manifest = json.load(f)
                print(f"  {manifest['timestamp']} - {len(manifest['files'])} items")
        else:
            print(f"  {backup}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_backups()
    else:
        create_backup()
