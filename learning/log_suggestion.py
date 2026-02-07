#!/usr/bin/env python3
"""Log suggestions for tracking and learning."""

import time
import sys
from typing import Optional
from db import get_connection

def log_suggestion(
    suggestion: str,
    category: str = "other",
    confidence: str = "medium",
    context: Optional[str] = None,
    session_id: Optional[str] = None
) -> int:
    """
    Log a suggestion to the database.
    
    Args:
        suggestion: The suggestion text
        category: One of: productivity, fun, revenue, infrastructure, learning, health, social, other
        confidence: One of: high, medium, low
        context: Why this suggestion was made
        session_id: Optional session identifier
    
    Returns:
        The suggestion ID
    """
    valid_categories = ['productivity', 'fun', 'revenue', 'infrastructure', 'learning', 'health', 'social', 'other']
    valid_confidence = ['high', 'medium', 'low']
    
    if category not in valid_categories:
        raise ValueError(f"Invalid category: {category}. Must be one of {valid_categories}")
    
    if confidence not in valid_confidence:
        raise ValueError(f"Invalid confidence: {confidence}. Must be one of {valid_confidence}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO suggestions (timestamp, text, category, confidence, context, session_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (int(time.time()), suggestion, category, confidence, context, session_id))
    
    suggestion_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return suggestion_id

def main():
    """CLI interface for logging suggestions."""
    if len(sys.argv) < 2:
        print("Usage: log_suggestion.py <suggestion> [category] [confidence] [context]")
        print("Categories: productivity, fun, revenue, infrastructure, learning, health, social, other")
        print("Confidence: high, medium, low")
        sys.exit(1)
    
    suggestion = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else "other"
    confidence = sys.argv[3] if len(sys.argv) > 3 else "medium"
    context = sys.argv[4] if len(sys.argv) > 4 else None
    
    suggestion_id = log_suggestion(suggestion, category, confidence, context)
    print(f"✅ Logged suggestion #{suggestion_id}: {suggestion}")
    print(f"   Category: {category} | Confidence: {confidence}")

if __name__ == "__main__":
    main()
