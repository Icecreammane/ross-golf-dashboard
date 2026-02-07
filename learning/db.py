#!/usr/bin/env python3
"""Database utilities for the outcome learning system."""

import sqlite3
import os
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "suggestions.db"

def get_connection() -> sqlite3.Connection:
    """Get database connection, initializing if needed."""
    needs_init = not DB_PATH.exists()
    conn = sqlite3.Connection(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    
    if needs_init:
        init_db(conn)
    
    return conn

def init_db(conn: Optional[sqlite3.Connection] = None):
    """Initialize database with schema."""
    should_close = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        should_close = True
    
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path) as f:
        conn.executescript(f.read())
    conn.commit()
    
    if should_close:
        conn.close()

if __name__ == "__main__":
    init_db()
    print(f"✅ Database initialized at {DB_PATH}")
