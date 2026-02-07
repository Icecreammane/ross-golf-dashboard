#!/usr/bin/env python3
"""
Feedback Tracker - Learn what works and what doesn't
Tracks outcomes, usage patterns, and effectiveness
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

CLAWD_DIR = Path.home() / "clawd"
FEEDBACK_FILE = CLAWD_DIR / "data" / "feedback.json"

def load_feedback():
    """Load feedback data"""
    if FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, 'r') as f:
            return json.load(f)
    return {
        "suggestions": [],
        "feature_usage": {},
        "brief_reactions": [],
        "tool_opens": {},
        "outcomes": [],
        "meta_reviews": []
    }

def save_feedback(data):
    """Save feedback data"""
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def log_suggestion(suggestion_type, content, context=None):
    """Log a suggestion I made"""
    data = load_feedback()
    
    entry = {
        "id": f"sug_{datetime.now().timestamp()}",
        "timestamp": datetime.now().isoformat(),
        "type": suggestion_type,
        "content": content,
        "context": context,
        "outcome": None,  # To be filled later
        "helpful": None   # To be filled by Ross's feedback
    }
    
    data['suggestions'].append(entry)
    save_feedback(data)
    
    print(f"✓ Logged suggestion: {suggestion_type}")
    return entry['id']

def log_outcome(suggestion_id, outcome, helpful=None):
    """Log the outcome of a suggestion"""
    data = load_feedback()
    
    for suggestion in data['suggestions']:
        if suggestion['id'] == suggestion_id:
            suggestion['outcome'] = outcome
            suggestion['outcome_time'] = datetime.now().isoformat()
            if helpful is not None:
                suggestion['helpful'] = helpful
            break
    
    save_feedback(data)
    print(f"✓ Logged outcome for {suggestion_id}")

def log_brief_reaction(brief_date, reaction):
    """Log reaction to morning brief (thumbs up/down)"""
    data = load_feedback()
    
    entry = {
        "date": brief_date,
        "timestamp": datetime.now().isoformat(),
        "reaction": reaction  # "up" or "down"
    }
    
    data['brief_reactions'].append(entry)
    save_feedback(data)
    
    print(f"✓ Logged brief reaction: {reaction}")

def log_tool_usage(tool_name):
    """Log that a tool was opened/used"""
    data = load_feedback()
    
    if tool_name not in data['tool_opens']:
        data['tool_opens'][tool_name] = []
    
    data['tool_opens'][tool_name].append(datetime.now().isoformat())
    save_feedback(data)

def log_feature_usage(feature_name, context=None):
    """Log feature usage"""
    data = load_feedback()
    
    if feature_name not in data['feature_usage']:
        data['feature_usage'][feature_name] = []
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "context": context
    }
    
    data['feature_usage'][feature_name].append(entry)
    save_feedback(data)

def analyze_suggestions(days=7):
    """Analyze suggestion effectiveness over last N days"""
    data = load_feedback()
    cutoff = datetime.now() - timedelta(days=days)
    
    recent = [
        s for s in data['suggestions']
        if datetime.fromisoformat(s['timestamp']) > cutoff
    ]
    
    total = len(recent)
    if total == 0:
        return {"total": 0, "helpful": 0, "not_helpful": 0, "no_feedback": 0}
    
    helpful = sum(1 for s in recent if s.get('helpful') == True)
    not_helpful = sum(1 for s in recent if s.get('helpful') == False)
    no_feedback = sum(1 for s in recent if s.get('helpful') is None)
    
    return {
        "total": total,
        "helpful": helpful,
        "not_helpful": not_helpful,
        "no_feedback": no_feedback,
        "helpful_rate": helpful / total if total > 0 else 0
    }

def analyze_tool_usage(days=7):
    """Analyze which tools are being used"""
    data = load_feedback()
    cutoff = datetime.now() - timedelta(days=days)
    
    usage_counts = {}
    for tool, timestamps in data['tool_opens'].items():
        recent = [
            t for t in timestamps
            if datetime.fromisoformat(t) > cutoff
        ]
        usage_counts[tool] = len(recent)
    
    # Sort by usage
    sorted_usage = sorted(usage_counts.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_usage)

def analyze_brief_reactions(days=30):
    """Analyze morning brief reactions"""
    data = load_feedback()
    cutoff = datetime.now() - timedelta(days=days)
    
    recent = [
        r for r in data['brief_reactions']
        if datetime.fromisoformat(r['timestamp']) > cutoff
    ]
    
    if not recent:
        return {"total": 0, "positive": 0, "negative": 0, "positive_rate": 0}
    
    positive = sum(1 for r in recent if r['reaction'] == 'up')
    negative = sum(1 for r in recent if r['reaction'] == 'down')
    
    return {
        "total": len(recent),
        "positive": positive,
        "negative": negative,
        "positive_rate": positive / len(recent) if recent else 0
    }

def generate_report(days=7):
    """Generate feedback report"""
    suggestions = analyze_suggestions(days)
    tool_usage = analyze_tool_usage(days)
    brief_reactions = analyze_brief_reactions(30)
    
    report = {
        "period": f"Last {days} days",
        "generated": datetime.now().isoformat(),
        "suggestions": suggestions,
        "tool_usage": tool_usage,
        "brief_reactions": brief_reactions
    }
    
    return report

def print_report(days=7):
    """Print human-readable feedback report"""
    report = generate_report(days)
    
    print(f"\n{'='*60}")
    print(f"FEEDBACK REPORT - {report['period']}")
    print(f"{'='*60}\n")
    
    # Suggestions
    sug = report['suggestions']
    print("📊 SUGGESTIONS:")
    print(f"  Total: {sug['total']}")
    if sug['total'] > 0:
        print(f"  Helpful: {sug['helpful']} ({sug.get('helpful_rate', 0):.1%})")
        print(f"  Not Helpful: {sug['not_helpful']}")
        print(f"  No Feedback: {sug['no_feedback']}")
    else:
        print(f"  No suggestions tracked yet")
    
    # Tool Usage
    print("\n🛠️ TOOL USAGE:")
    if report['tool_usage']:
        for tool, count in report['tool_usage'].items():
            print(f"  {tool}: {count} opens")
    else:
        print("  No tool usage tracked yet")
    
    # Brief Reactions
    brief = report['brief_reactions']
    print("\n☀️ MORNING BRIEF REACTIONS:")
    print(f"  Total: {brief['total']}")
    print(f"  Positive: {brief['positive']} ({brief['positive_rate']:.1%})")
    print(f"  Negative: {brief['negative']}")
    
    print(f"\n{'='*60}\n")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 feedback_tracker.py suggest <type> <content>")
        print("  python3 feedback_tracker.py outcome <id> <outcome> [helpful=yes/no]")
        print("  python3 feedback_tracker.py brief <date> <up/down>")
        print("  python3 feedback_tracker.py tool <name>")
        print("  python3 feedback_tracker.py report [days]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "suggest":
        suggestion_type = sys.argv[2]
        content = sys.argv[3]
        context = sys.argv[4] if len(sys.argv) > 4 else None
        suggestion_id = log_suggestion(suggestion_type, content, context)
        print(f"Suggestion ID: {suggestion_id}")
    
    elif command == "outcome":
        suggestion_id = sys.argv[2]
        outcome = sys.argv[3]
        helpful = None
        if len(sys.argv) > 4:
            helpful = sys.argv[4].lower() in ['yes', 'true', 'helpful']
        log_outcome(suggestion_id, outcome, helpful)
    
    elif command == "brief":
        brief_date = sys.argv[2]
        reaction = sys.argv[3]
        log_brief_reaction(brief_date, reaction)
    
    elif command == "tool":
        tool_name = sys.argv[2]
        log_tool_usage(tool_name)
    
    elif command == "report":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        print_report(days)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
