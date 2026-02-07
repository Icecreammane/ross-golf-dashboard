#!/usr/bin/env python3
"""
cleanup_memory.py - Automatic memory optimization

Cleans:
- Old session transcripts (keep last 7 days)
- Temp files
- Large logs
- Old progress data
- Completed build records

Keeps the system fast and storage-efficient.

Usage:
    python3 cleanup_memory.py [--dry-run] [--keep-days N]
"""

import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import shutil

WORKSPACE = Path.home() / "clawd"
SESSIONS_DIR = Path.home() / ".clawdbot" / "sessions"

# Retention policies
DEFAULT_KEEP_DAYS = 7
LOG_KEEP_DAYS = 7
PROGRESS_KEEP_HOURS = 48


def human_size(bytes_size: int) -> str:
    """Convert bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def clean_old_sessions(keep_days: int, dry_run: bool = False) -> tuple:
    """Clean old session transcripts"""
    if not SESSIONS_DIR.exists():
        return 0, 0
    
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    removed_count = 0
    freed_space = 0
    
    print(f"\n🗂️  Cleaning sessions older than {keep_days} days...")
    
    for session_file in SESSIONS_DIR.glob("**/*.jsonl"):
        try:
            mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
            
            if mtime < cutoff_date:
                size = session_file.stat().st_size
                
                if dry_run:
                    print(f"   [DRY RUN] Would remove: {session_file.name} ({human_size(size)})")
                else:
                    session_file.unlink()
                    print(f"   ✅ Removed: {session_file.name} ({human_size(size)})")
                
                removed_count += 1
                freed_space += size
        except Exception as e:
            print(f"   ⚠️  Error processing {session_file.name}: {e}")
    
    return removed_count, freed_space


def clean_temp_files(dry_run: bool = False) -> tuple:
    """Clean temporary files in workspace"""
    temp_patterns = [
        "*.tmp",
        "*.temp",
        ".DS_Store",
        "*.pyc",
        "__pycache__",
    ]
    
    removed_count = 0
    freed_space = 0
    
    print(f"\n🧹 Cleaning temporary files...")
    
    for pattern in temp_patterns:
        for temp_file in WORKSPACE.rglob(pattern):
            try:
                size = temp_file.stat().st_size if temp_file.is_file() else sum(
                    f.stat().st_size for f in temp_file.rglob("*") if f.is_file()
                )
                
                if dry_run:
                    print(f"   [DRY RUN] Would remove: {temp_file.relative_to(WORKSPACE)} ({human_size(size)})")
                else:
                    if temp_file.is_file():
                        temp_file.unlink()
                    else:
                        shutil.rmtree(temp_file)
                    print(f"   ✅ Removed: {temp_file.relative_to(WORKSPACE)} ({human_size(size)})")
                
                removed_count += 1
                freed_space += size
            except Exception as e:
                print(f"   ⚠️  Error processing {temp_file.name}: {e}")
    
    return removed_count, freed_space


def clean_large_logs(max_size_mb: int = 10, dry_run: bool = False) -> tuple:
    """Truncate or remove large log files"""
    max_size = max_size_mb * 1024 * 1024
    removed_count = 0
    freed_space = 0
    
    print(f"\n📋 Checking for large log files (>{max_size_mb}MB)...")
    
    log_files = list(WORKSPACE.rglob("*.log")) + list(WORKSPACE.rglob("*.txt"))
    
    for log_file in log_files:
        try:
            if not log_file.is_file():
                continue
            
            size = log_file.stat().st_size
            
            if size > max_size:
                if dry_run:
                    print(f"   [DRY RUN] Would truncate: {log_file.relative_to(WORKSPACE)} ({human_size(size)})")
                else:
                    # Keep last 1000 lines
                    with open(log_file, "r") as f:
                        lines = f.readlines()
                    
                    if len(lines) > 1000:
                        with open(log_file, "w") as f:
                            f.writelines(lines[-1000:])
                        
                        new_size = log_file.stat().st_size
                        saved = size - new_size
                        
                        print(f"   ✅ Truncated: {log_file.relative_to(WORKSPACE)} (saved {human_size(saved)})")
                        
                        removed_count += 1
                        freed_space += saved
        except Exception as e:
            print(f"   ⚠️  Error processing {log_file.name}: {e}")
    
    return removed_count, freed_space


def clean_old_progress(dry_run: bool = False) -> int:
    """Clean old completed progress entries"""
    from sub_agent_progress import clean_completed
    
    print(f"\n📊 Cleaning old progress data (completed >{PROGRESS_KEEP_HOURS}h ago)...")
    
    if dry_run:
        print(f"   [DRY RUN] Would clean progress entries")
        return 0
    else:
        clean_completed(PROGRESS_KEEP_HOURS)
        return 1


def clean_old_memory_files(keep_days: int, dry_run: bool = False) -> tuple:
    """Clean old daily memory files"""
    memory_dir = WORKSPACE / "memory"
    
    if not memory_dir.exists():
        return 0, 0
    
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    removed_count = 0
    freed_space = 0
    
    print(f"\n📝 Cleaning daily memory files older than {keep_days} days...")
    
    # Look for YYYY-MM-DD.md files
    for memory_file in memory_dir.glob("????-??-??.md"):
        try:
            # Parse date from filename
            date_str = memory_file.stem
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            if file_date < cutoff_date:
                size = memory_file.stat().st_size
                
                if dry_run:
                    print(f"   [DRY RUN] Would remove: {memory_file.name} ({human_size(size)})")
                else:
                    memory_file.unlink()
                    print(f"   ✅ Removed: {memory_file.name} ({human_size(size)})")
                
                removed_count += 1
                freed_space += size
        except Exception as e:
            print(f"   ⚠️  Error processing {memory_file.name}: {e}")
    
    return removed_count, freed_space


def show_summary(results: dict):
    """Show cleanup summary"""
    total_files = sum(r[0] for r in results.values())
    total_space = sum(r[1] if len(r) > 1 else 0 for r in results.values())
    
    print(f"\n{'='*60}")
    print(f"🎯 CLEANUP SUMMARY")
    print(f"{'='*60}")
    print(f"Total files processed: {total_files}")
    print(f"Total space freed: {human_size(total_space)}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Clean up workspace and optimize memory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed without removing")
    parser.add_argument("--keep-days", type=int, default=DEFAULT_KEEP_DAYS,
                       help=f"Days to keep files (default: {DEFAULT_KEEP_DAYS})")
    
    args = parser.parse_args()
    
    print("🧹 Starting memory optimization...")
    
    if args.dry_run:
        print("⚠️  DRY RUN MODE - No files will be removed\n")
    
    results = {
        "sessions": clean_old_sessions(args.keep_days, args.dry_run),
        "temp_files": clean_temp_files(args.dry_run),
        "large_logs": clean_large_logs(dry_run=args.dry_run),
        "progress": (clean_old_progress(args.dry_run), 0),
        "memory_files": clean_old_memory_files(args.keep_days, args.dry_run),
    }
    
    show_summary(results)
    
    if args.dry_run:
        print("💡 Run without --dry-run to actually remove files\n")
    else:
        print("✅ Cleanup complete!\n")


if __name__ == "__main__":
    main()
