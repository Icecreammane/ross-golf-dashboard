"""
Email Template Generator - Database Management
Handles storage of templates, feedback, and learning data
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'templates.db')

def init_db():
    """Initialize database with required tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Templates table - stores generated emails
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_type TEXT NOT NULL,
            email_type TEXT NOT NULL,
            variation TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            context TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used INTEGER DEFAULT 0,
            converted INTEGER DEFAULT 0,
            feedback_score INTEGER,
            feedback_notes TEXT
        )
    ''')
    
    # Past successful emails - user's real emails that worked
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS successful_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_type TEXT NOT NULL,
            email_type TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            context TEXT,
            outcome TEXT,
            conversion_rate REAL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Learning patterns - extracted patterns from successful emails
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT NOT NULL,
            pattern_data TEXT NOT NULL,
            effectiveness_score REAL,
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Performance tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER,
            action TEXT NOT NULL,
            result TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (template_id) REFERENCES templates(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_template(recipient_type: str, email_type: str, variation: str, 
                subject: str, body: str, context: str = None) -> int:
    """Add a new generated template"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO templates (recipient_type, email_type, variation, subject, body, context)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (recipient_type, email_type, variation, subject, body, context))
    
    template_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return template_id

def add_successful_email(recipient_type: str, email_type: str, subject: str,
                        body: str, context: str = None, outcome: str = None,
                        conversion_rate: float = None):
    """Add a past successful email for pattern learning"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO successful_emails 
        (recipient_type, email_type, subject, body, context, outcome, conversion_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (recipient_type, email_type, subject, body, context, outcome, conversion_rate))
    
    conn.commit()
    conn.close()

def get_templates(recipient_type: str = None, email_type: str = None, 
                 variation: str = None, limit: int = 50) -> List[Dict]:
    """Retrieve templates with optional filters"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM templates WHERE 1=1"
    params = []
    
    if recipient_type:
        query += " AND recipient_type = ?"
        params.append(recipient_type)
    if email_type:
        query += " AND email_type = ?"
        params.append(email_type)
    if variation:
        query += " AND variation = ?"
        params.append(variation)
    
    query += " ORDER BY generated_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_successful_emails(recipient_type: str = None, email_type: str = None) -> List[Dict]:
    """Get past successful emails for pattern matching"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM successful_emails WHERE 1=1"
    params = []
    
    if recipient_type:
        query += " AND recipient_type = ?"
        params.append(recipient_type)
    if email_type:
        query += " AND email_type = ?"
        params.append(email_type)
    
    query += " ORDER BY conversion_rate DESC, added_at DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def update_template_feedback(template_id: int, used: bool = None, 
                            converted: bool = None, feedback_score: int = None,
                            feedback_notes: str = None):
    """Update feedback for a template"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if used is not None:
        updates.append("used = used + 1")
    if converted is not None:
        updates.append("converted = converted + 1")
    if feedback_score is not None:
        updates.append("feedback_score = ?")
        params.append(feedback_score)
    if feedback_notes is not None:
        updates.append("feedback_notes = ?")
        params.append(feedback_notes)
    
    if updates:
        params.append(template_id)
        query = f"UPDATE templates SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        
        # Log the feedback
        cursor.execute('''
            INSERT INTO performance_log (template_id, action, result)
            VALUES (?, ?, ?)
        ''', (template_id, 'feedback', json.dumps({
            'used': used, 'converted': converted, 
            'score': feedback_score, 'notes': feedback_notes
        })))
    
    conn.commit()
    conn.close()

def get_best_templates(recipient_type: str = None, email_type: str = None, 
                      limit: int = 10) -> List[Dict]:
    """Get highest performing templates"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT *, 
               CAST(converted AS FLOAT) / NULLIF(used, 0) as conversion_rate
        FROM templates 
        WHERE used > 0
    """
    params = []
    
    if recipient_type:
        query += " AND recipient_type = ?"
        params.append(recipient_type)
    if email_type:
        query += " AND email_type = ?"
        params.append(email_type)
    
    query += " ORDER BY conversion_rate DESC, used DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def add_pattern(pattern_type: str, pattern_data: dict, effectiveness_score: float = 0.5):
    """Store a learned pattern"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO patterns (pattern_type, pattern_data, effectiveness_score)
        VALUES (?, ?, ?)
    ''', (pattern_type, json.dumps(pattern_data), effectiveness_score))
    
    conn.commit()
    conn.close()

def get_patterns(pattern_type: str = None, min_effectiveness: float = 0.0) -> List[Dict]:
    """Retrieve learned patterns"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM patterns WHERE effectiveness_score >= ?"
    params = [min_effectiveness]
    
    if pattern_type:
        query += " AND pattern_type = ?"
        params.append(pattern_type)
    
    query += " ORDER BY effectiveness_score DESC, usage_count DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        result = dict(row)
        result['pattern_data'] = json.loads(result['pattern_data'])
        results.append(result)
    
    return results

def update_pattern_effectiveness(pattern_id: int, effectiveness_delta: float):
    """Update pattern effectiveness based on usage results"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE patterns 
        SET effectiveness_score = effectiveness_score + ?,
            usage_count = usage_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (effectiveness_delta, pattern_id))
    
    conn.commit()
    conn.close()

# Initialize database on import
init_db()
