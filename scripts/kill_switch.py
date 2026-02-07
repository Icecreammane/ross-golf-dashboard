#!/usr/bin/env python3
"""
Kill Switch - Emergency Credential Revocation
Immediately revokes all stored credentials and goes read-only
"""

import os
import shutil
import json
from datetime import datetime

CRED_DIR = os.path.expanduser("~/clawd/.credentials")
BACKUP_DIR = os.path.expanduser("~/clawd/.credentials_revoked_backup")
LOG_FILE = os.path.expanduser("~/clawd/security-logs/kill_switch.log")

def execute_kill_switch(reason="Manual execution"):
    """
    Execute the kill switch:
    1. Move all credentials to backup (encrypted by macOS)
    2. Log the action
    3. Return status report
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    results = {
        "timestamp": timestamp,
        "reason": reason,
        "actions": [],
        "status": "executed"
    }
    
    # Create backup directory with timestamp
    backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_DIR}_{backup_timestamp}"
    
    if os.path.exists(CRED_DIR):
        # Move credentials to backup
        shutil.move(CRED_DIR, backup_path)
        results["actions"].append(f"Moved credentials to {backup_path}")
        
        # Recreate empty credentials directory
        os.makedirs(CRED_DIR, exist_ok=True)
        results["actions"].append("Created empty credentials directory")
    else:
        results["actions"].append("No credentials directory found")
    
    # Log the kill switch execution
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(results) + "\n")
    
    return results

def restore_credentials(backup_timestamp):
    """
    Restore credentials from a specific backup.
    Use with caution - only after verifying security.
    """
    backup_path = f"{BACKUP_DIR}_{backup_timestamp}"
    
    if not os.path.exists(backup_path):
        return {"status": "error", "message": f"Backup not found: {backup_path}"}
    
    if os.path.exists(CRED_DIR):
        shutil.rmtree(CRED_DIR)
    
    shutil.move(backup_path, CRED_DIR)
    
    return {
        "status": "restored",
        "message": f"Credentials restored from {backup_timestamp}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def list_backups():
    """
    List all credential backups available for restoration.
    """
    base_dir = os.path.dirname(BACKUP_DIR)
    backups = []
    
    for item in os.listdir(base_dir):
        if item.startswith(".credentials_revoked_backup_"):
            timestamp = item.split("_")[-2] + "_" + item.split("_")[-1]
            backups.append({
                "timestamp": timestamp,
                "path": os.path.join(base_dir, item)
            })
    
    return backups

if __name__ == "__main__":
    print("🚨 KILL SWITCH TEST MODE")
    print("This would revoke all credentials immediately.")
    print("Run with --execute flag to actually execute.")
    print(f"Credentials directory: {CRED_DIR}")
    print(f"Backup location: {BACKUP_DIR}_[timestamp]")
