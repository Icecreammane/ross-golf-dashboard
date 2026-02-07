#!/usr/bin/env python3
"""Demo script to populate the database with realistic test data."""

import time
import random
from log_suggestion import log_suggestion
from track_outcome import track_outcome
from agent_integration import OutcomeLearner

def create_demo_data():
    """Create realistic demo data showing various patterns."""
    print("🧠 Creating demo data for the outcome learning system...\n")
    
    # Productivity suggestions (high implementation rate)
    productivity_suggestions = [
        ("Set up automated backups", "high", "implemented", "success", "Running daily"),
        ("Build a task prioritization system", "high", "implemented", "success", "Really helpful"),
        ("Create morning briefing script", "medium", "implemented", "success", "Love starting the day with this"),
        ("Add keyboard shortcuts to common tasks", "medium", "implemented", "partial", "Some work, some don't"),
        ("Set up focus time blocks", "low", "rejected", None, "Too rigid for my schedule"),
        ("Implement pomodoro timer", "medium", "ignored", None, "Never got around to it"),
        ("Create weekly review template", "high", "implemented", "success", "Game changer"),
        ("Build habit tracking system", "medium", "deferred", None, "Maybe later"),
    ]
    
    # Fun suggestions (medium implementation rate)
    fun_suggestions = [
        ("Add random dad jokes to notifications", "low", "rejected", None, "Too silly"),
        ("Create a music mood detector", "medium", "implemented", "success", "Actually pretty cool"),
        ("Build a meme generator", "low", "ignored", None, "Not interested"),
        ("Add easter eggs to the system", "low", "implemented", "partial", "Fun but not essential"),
        ("Create a daily weird fact feature", "medium", "deferred", None, "Cute but low priority"),
    ]
    
    # Revenue suggestions (very high implementation rate)
    revenue_suggestions = [
        ("Set up payment reminder automation", "high", "implemented", "success", "Paying for itself"),
        ("Build client onboarding workflow", "high", "implemented", "success", "Saves hours"),
        ("Create proposal template system", "high", "implemented", "success", "Closes deals faster"),
        ("Add invoice tracking dashboard", "medium", "implemented", "success", "Know exactly where money is"),
        ("Build referral tracking system", "medium", "deferred", None, "Good idea, need time"),
    ]
    
    # Infrastructure suggestions (medium-low implementation rate)
    infrastructure_suggestions = [
        ("Upgrade to latest framework version", "low", "rejected", None, "If it ain't broke..."),
        ("Implement comprehensive logging", "medium", "implemented", "success", "Saved me when debugging"),
        ("Set up load balancing", "low", "ignored", None, "Overkill for current scale"),
        ("Add monitoring dashboard", "high", "implemented", "success", "Essential"),
        ("Refactor database schema", "low", "rejected", None, "Too risky right now"),
        ("Set up CI/CD pipeline", "medium", "deferred", None, "Want this but big project"),
    ]
    
    # Learning suggestions (high implementation rate) 
    learning_suggestions = [
        ("Read about async patterns", "medium", "implemented", "success", "Learned a lot"),
        ("Take course on system design", "high", "implemented", "success", "Worth every minute"),
        ("Learn new language feature", "low", "ignored", None, "Not urgent"),
        ("Study competitor approaches", "medium", "implemented", "partial", "Some good ideas"),
    ]
    
    all_suggestions = [
        ("productivity", productivity_suggestions),
        ("fun", fun_suggestions),
        ("revenue", revenue_suggestions),
        ("infrastructure", infrastructure_suggestions),
        ("learning", learning_suggestions),
    ]
    
    total_created = 0
    
    for category, suggestions in all_suggestions:
        print(f"📝 Creating {category} suggestions...")
        
        for text, confidence, status, result, notes in suggestions:
            # Create suggestion with timestamp spread over last 30 days
            days_ago = random.randint(1, 30)
            timestamp = int(time.time()) - (days_ago * 86400)
            
            # Log suggestion (manually set timestamp for demo)
            import sqlite3
            from db import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO suggestions (timestamp, text, category, confidence, context, session_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, text, category, confidence, f"Demo suggestion for {category}", "demo"))
            suggestion_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Track outcome with slight delay
            outcome_timestamp = timestamp + random.randint(3600, 86400)  # 1-24 hours later
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO outcomes (suggestion_id, status, result, notes, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (suggestion_id, status, result, notes, outcome_timestamp))
            conn.commit()
            conn.close()
            
            total_created += 1
    
    print(f"\n✅ Created {total_created} demo suggestions with outcomes\n")
    
    # Show summary
    learner = OutcomeLearner()
    print(learner.weekly_summary(days=30))
    print("\n" + "="*60 + "\n")
    
    insights = learner.get_insights()
    print("💡 Generated Insights:\n")
    for insight in insights['insights']:
        print(f"   {insight}")
    
    print("\n" + "="*60)
    print("\n🎯 Try these commands:")
    print("   python3 analyze_patterns.py                    # Full report")
    print("   python3 track_outcome.py --list                # List suggestions")
    print("   python3 analyze_patterns.py --json             # JSON output")
    print("   ./generate_dashboard.sh --serve                # View dashboard")
    print()

if __name__ == "__main__":
    create_demo_data()
