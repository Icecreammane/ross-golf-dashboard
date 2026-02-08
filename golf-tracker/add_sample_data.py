#!/usr/bin/env python3
"""
Add sample data to Golf Tracker for testing and demonstration
Run this to populate your tracker with sample rounds
"""

from app import GolfDataManager, DATA_FILE
from datetime import datetime, timedelta
import random

def add_sample_data():
    """Add realistic sample golf rounds."""
    manager = GolfDataManager(DATA_FILE)
    
    courses = [
        ("Pebble Beach", 72),
        ("Augusta National", 72),
        ("St. Andrews", 72),
        ("Pinehurst No. 2", 71),
        ("Torrey Pines", 72),
        ("Bethpage Black", 71),
    ]
    
    notes_options = [
        "Great weather, played well",
        "Windy conditions, tough day",
        "Best putting round in months",
        "Struggled with driver today",
        "New personal best on this course!",
        "Played with friends, had a blast",
        "Early morning round, beautiful sunrise",
        "Back nine was much better",
        "Need to work on short game",
        ""
    ]
    
    # Add rounds over the past 3 months
    start_date = datetime.now() - timedelta(days=90)
    
    print("Adding sample golf rounds...")
    print("=" * 50)
    
    rounds_added = 0
    for i in range(25):
        # Random date in the past 90 days
        days_ago = random.randint(0, 90)
        round_date = (start_date + timedelta(days=days_ago)).date().isoformat()
        
        # Random course
        course_name, course_par = random.choice(courses)
        
        # Score trending downward (getting better over time)
        base_score = 95 - (i * 0.5)  # Improvement trend
        score = int(base_score + random.randint(-3, 5))
        score = max(70, min(105, score))  # Keep realistic
        
        # Handicap estimate
        handicap = round((score - course_par) * 0.96, 1)
        
        # Random notes
        notes = random.choice(notes_options)
        
        try:
            round_data = manager.add_round(
                date=round_date,
                course=course_name,
                score=score,
                par=course_par,
                handicap_estimate=handicap,
                notes=notes
            )
            rounds_added += 1
            print(f"✓ {round_date} - {course_name}: {score} ({score - course_par:+d})")
        except Exception as e:
            print(f"✗ Error adding round: {e}")
    
    # Add a couple of goals
    print("\nAdding sample goals...")
    manager.add_goal("break_score", 80, "Break 80 before end of year")
    manager.add_goal("break_score", 75, "Ultimate goal: break 75")
    print("✓ Added 2 goals")
    
    print("\n" + "=" * 50)
    print(f"Sample data complete! Added {rounds_added} rounds.")
    print(f"\nData stored in: {DATA_FILE}")
    print("\nStart the web app to see your data:")
    print("  bash start.sh")
    print("\nOr view insights via CLI:")
    print("  python golf_cli.py insights")

if __name__ == '__main__':
    print("⛳ Golf Tracker - Sample Data Generator")
    print()
    response = input("This will add 25 sample rounds to your tracker. Continue? (y/N): ")
    
    if response.lower() == 'y':
        add_sample_data()
    else:
        print("Cancelled.")
