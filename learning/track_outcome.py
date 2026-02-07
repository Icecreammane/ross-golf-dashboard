#!/usr/bin/env python3
"""Track outcomes for suggestions."""

import time
import sys
from typing import Optional
from db import get_connection

def track_outcome(
    suggestion_id: int,
    status: str,
    result: Optional[str] = None,
    notes: Optional[str] = None
) -> int:
    """
    Track the outcome of a suggestion.
    
    Args:
        suggestion_id: ID of the suggestion
        status: One of: implemented, ignored, deferred, rejected, in_progress
        result: One of: success, failure, partial, unknown (optional)
        notes: Additional notes about the outcome
    
    Returns:
        The outcome ID
    """
    valid_statuses = ['implemented', 'ignored', 'deferred', 'rejected', 'in_progress']
    valid_results = ['success', 'failure', 'partial', 'unknown']
    
    if status not in valid_statuses:
        raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
    
    if result and result not in valid_results:
        raise ValueError(f"Invalid result: {result}. Must be one of {valid_results}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verify suggestion exists
    cursor.execute("SELECT id FROM suggestions WHERE id = ?", (suggestion_id,))
    if not cursor.fetchone():
        conn.close()
        raise ValueError(f"Suggestion #{suggestion_id} not found")
    
    cursor.execute("""
        INSERT INTO outcomes (suggestion_id, status, result, notes, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (suggestion_id, status, result, notes, int(time.time())))
    
    outcome_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return outcome_id

def get_latest_suggestions(limit: int = 10):
    """Get the most recent suggestions without outcomes."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.id, s.text, s.category, s.confidence, 
               datetime(s.timestamp, 'unixepoch', 'localtime') as time
        FROM suggestions s
        LEFT JOIN outcomes o ON s.id = o.suggestion_id
        WHERE o.id IS NULL
        ORDER BY s.timestamp DESC
        LIMIT ?
    """, (limit,))
    
    results = cursor.fetchall()
    conn.close()
    return results

def main():
    """CLI interface for tracking outcomes."""
    if len(sys.argv) < 3:
        print("Usage: track_outcome.py <suggestion_id> <status> [result] [notes]")
        print("\nOr: track_outcome.py --list  (show recent suggestions)")
        print("\nStatus: implemented, ignored, deferred, rejected, in_progress")
        print("Result: success, failure, partial, unknown")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        suggestions = get_latest_suggestions(20)
        if not suggestions:
            print("No untracked suggestions found.")
            return
        
        print("\n📋 Recent suggestions without outcomes:\n")
        for s in suggestions:
            print(f"  #{s['id']:3d} | {s['time']} | [{s['category']:12s}] {s['text'][:60]}")
        print()
        return
    
    suggestion_id = int(sys.argv[1])
    status = sys.argv[2]
    result = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != '-' else None
    notes = sys.argv[4] if len(sys.argv) > 4 else None
    
    outcome_id = track_outcome(suggestion_id, status, result, notes)
    print(f"✅ Tracked outcome #{outcome_id} for suggestion #{suggestion_id}")
    print(f"   Status: {status}" + (f" | Result: {result}" if result else ""))

if __name__ == "__main__":
    main()
