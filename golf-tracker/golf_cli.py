#!/usr/bin/env python3
"""
Golf Tracker CLI - Command-line interface for logging rounds
Usage: python3 golf_cli.py [command] [options]
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
import json

# Import the data manager from the web app
sys.path.insert(0, str(Path(__file__).parent))
from app import GolfDataManager, DATA_FILE


def add_round_interactive():
    """Interactively add a new round."""
    print("\n⛳ Golf Round Entry")
    print("=" * 50)
    
    # Get date
    date_input = input("Date (YYYY-MM-DD, or press Enter for today): ").strip()
    if not date_input:
        date_input = datetime.now().date().isoformat()
    
    # Get course
    course = input("Course name: ").strip()
    if not course:
        print("Error: Course name is required")
        return
    
    # Get score
    try:
        score = int(input("Your score: "))
    except ValueError:
        print("Error: Score must be a number")
        return
    
    # Get par
    par_input = input("Course par (default 72): ").strip()
    par = int(par_input) if par_input else 72
    
    # Get handicap (optional)
    handicap_input = input("Handicap estimate (optional, press Enter to skip): ").strip()
    handicap = float(handicap_input) if handicap_input else None
    
    # Get notes
    notes = input("Notes (optional): ").strip()
    
    # Save round
    try:
        manager = GolfDataManager(DATA_FILE)
        round_data = manager.add_round(date_input, course, score, par, handicap, notes)
        
        print("\n✅ Round saved successfully!")
        print(f"   Date: {round_data['date']}")
        print(f"   Course: {round_data['course']}")
        print(f"   Score: {round_data['score']} ({round_data['differential']:+d} vs par)")
        print(f"   ID: {round_data['id']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def list_rounds(count=10):
    """List recent rounds."""
    manager = GolfDataManager(DATA_FILE)
    rounds = manager.get_recent_rounds(count)
    
    if not rounds:
        print("\nNo rounds found. Add your first round!")
        return
    
    print(f"\n⛳ Recent Rounds (last {len(rounds)})")
    print("=" * 80)
    print(f"{'Date':<12} {'Course':<25} {'Score':<8} {'Par':<6} {'Diff':<8}")
    print("-" * 80)
    
    for r in rounds:
        diff_str = f"{r['differential']:+d}"
        print(f"{r['date']:<12} {r['course']:<25} {r['score']:<8} {r['par']:<6} {diff_str:<8}")


def show_insights():
    """Display performance insights."""
    manager = GolfDataManager(DATA_FILE)
    insights = manager.get_insights()
    
    if "message" in insights:
        print(f"\n{insights['message']}")
        return
    
    print("\n📊 Performance Insights")
    print("=" * 50)
    
    if "recent_average" in insights:
        print(f"\n5-Round Average: {insights['recent_average']}")
    
    if "this_month_avg" in insights:
        print(f"This Month Average: {insights['this_month_avg']} ({insights['this_month_count']} rounds)")
    
    if "last_month_avg" in insights:
        print(f"Last Month Average: {insights['last_month_avg']}")
    
    if "improvement" in insights:
        if insights["trend"] == "improving":
            print(f"\n🎉 Great progress! You've improved by {insights['improvement']} strokes!")
        elif insights["trend"] == "declining":
            print(f"\n📉 Scores increased by {abs(insights['improvement'])} strokes. Keep practicing!")
        else:
            print(f"\n📊 Performance is stable.")
    
    if "best_score" in insights:
        print(f"\nBest Score: {insights['best_score']}")
        print(f"Worst Score: {insights['worst_score']}")
        print(f"Total Rounds: {insights['total_rounds']}")
    
    if "best_course" in insights:
        print(f"\nBest Course: {insights['best_course']['name']} (avg: {insights['best_course']['avg_score']})")
    
    if "worst_course" in insights:
        print(f"Most Challenging: {insights['worst_course']['name']} (avg: {insights['worst_course']['avg_score']})")


def show_courses():
    """Display course statistics."""
    manager = GolfDataManager(DATA_FILE)
    courses = manager.get_course_stats()
    
    if not courses:
        print("\nNo course data available yet.")
        return
    
    print("\n🏌️ Course Statistics")
    print("=" * 80)
    print(f"{'Course':<30} {'Rounds':<10} {'Average':<10} {'Best':<10} {'Worst':<10}")
    print("-" * 80)
    
    for course_name, stats in sorted(courses.items(), key=lambda x: x[1]['average_score']):
        print(f"{course_name:<30} {stats['rounds_played']:<10} "
              f"{stats['average_score']:<10.1f} {stats['best_score']:<10} {stats['worst_score']:<10}")


def export_data(output_file):
    """Export all data to JSON file."""
    manager = GolfDataManager(DATA_FILE)
    
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Data exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Golf Tracker CLI - Track your golf rounds and performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  golf_cli.py add                    # Add a round interactively
  golf_cli.py list                   # List recent rounds
  golf_cli.py list --count 20        # List last 20 rounds
  golf_cli.py insights               # Show performance insights
  golf_cli.py courses                # Show course statistics
  golf_cli.py export data.json       # Export all data
  
  # Quick add (non-interactive):
  golf_cli.py add --date 2024-01-15 --course "Pebble Beach" --score 87 --par 72
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new round')
    add_parser.add_argument('--date', help='Date (YYYY-MM-DD)')
    add_parser.add_argument('--course', help='Course name')
    add_parser.add_argument('--score', type=int, help='Your score')
    add_parser.add_argument('--par', type=int, default=72, help='Course par (default: 72)')
    add_parser.add_argument('--handicap', type=float, help='Handicap estimate')
    add_parser.add_argument('--notes', default='', help='Round notes')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List recent rounds')
    list_parser.add_argument('--count', type=int, default=10, help='Number of rounds to show')
    
    # Insights command
    subparsers.add_parser('insights', help='Show performance insights')
    
    # Courses command
    subparsers.add_parser('courses', help='Show course statistics')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data to JSON file')
    export_parser.add_argument('output', help='Output file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'add':
            if args.date and args.course and args.score:
                # Non-interactive add
                manager = GolfDataManager(DATA_FILE)
                round_data = manager.add_round(
                    args.date, args.course, args.score, args.par, args.handicap, args.notes
                )
                print(f"✅ Round added: {args.course} on {args.date}, score: {args.score}")
            else:
                # Interactive add
                add_round_interactive()
        
        elif args.command == 'list':
            list_rounds(args.count)
        
        elif args.command == 'insights':
            show_insights()
        
        elif args.command == 'courses':
            show_courses()
        
        elif args.command == 'export':
            export_data(args.output)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
