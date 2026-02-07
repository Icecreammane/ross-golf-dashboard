#!/usr/bin/env python3
"""
Learning Loop - Tracks Ross's preferences and automatically adapts
Logs: approvals, rejections, decisions, patterns, optimal times
"""

import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
MEMORY_DIR = WORKSPACE / "memory"
LEARNING_DATA = MEMORY_DIR / "learning_data.json"

def load_learning_data():
    """Load existing learning data"""
    if LEARNING_DATA.exists():
        with open(LEARNING_DATA) as f:
            return json.load(f)
    
    return {
        "content_preferences": {
            "tweet_approvals": [],
            "tweet_rejections": [],
            "tweet_styles": {}
        },
        "decision_patterns": {
            "decisions": [],
            "outcomes": []
        },
        "activity_patterns": {
            "active_hours": [],
            "productive_hours": []
        },
        "task_priorities": {
            "completed": [],
            "skipped": []
        },
        "learning_insights": []
    }

def log_content_approval(content_type, content_text, approved=True):
    """Log when Ross approves or rejects content"""
    data = load_learning_data()
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "type": content_type,
        "content": content_text[:200],  # First 200 chars
        "approved": approved
    }
    
    if approved:
        data["content_preferences"][f"{content_type}_approvals"].append(entry)
    else:
        data["content_preferences"][f"{content_type}_rejections"].append(entry)
    
    # Save
    with open(LEARNING_DATA, "w") as f:
        json.dump(data, f, indent=2)

def log_decision(decision_text, context="", outcome=None):
    """Log a decision Ross makes"""
    data = load_learning_data()
    
    decision = {
        "timestamp": datetime.now().isoformat(),
        "decision": decision_text,
        "context": context,
        "outcome": outcome,
        "hour": datetime.now().hour
    }
    
    data["decision_patterns"]["decisions"].append(decision)
    
    # Save
    with open(LEARNING_DATA, "w") as f:
        json.dump(data, f, indent=2)
    
    return decision

def log_activity(activity_type="active"):
    """Log when Ross is active (helps find productive hours)"""
    data = load_learning_data()
    
    timestamp = datetime.now().isoformat()
    hour = datetime.now().hour
    
    data["activity_patterns"]["active_hours"].append({
        "timestamp": timestamp,
        "hour": hour,
        "type": activity_type
    })
    
    # Save
    with open(LEARNING_DATA, "w") as f:
        json.dump(data, f, indent=2)

def analyze_patterns():
    """Analyze patterns and generate insights"""
    data = load_learning_data()
    insights = []
    
    # Analyze tweet preferences
    tweet_approvals = data["content_preferences"].get("tweet_approvals", [])
    tweet_rejections = data["content_preferences"].get("tweet_rejections", [])
    
    if len(tweet_approvals) > 5:
        # Find common themes in approved tweets
        approved_words = {}
        for tweet in tweet_approvals:
            words = tweet["content"].lower().split()
            for word in words:
                if len(word) > 4:  # Skip short words
                    approved_words[word] = approved_words.get(word, 0) + 1
        
        top_words = sorted(approved_words.items(), key=lambda x: x[1], reverse=True)[:5]
        insights.append({
            "type": "tweet_preference",
            "insight": f"Frequently approved words: {', '.join([w for w, c in top_words])}",
            "confidence": min(len(tweet_approvals) / 20, 1.0)
        })
    
    # Analyze active hours
    active_hours = data["activity_patterns"].get("active_hours", [])
    if len(active_hours) > 20:
        hour_counts = {}
        for entry in active_hours:
            hour = entry["hour"]
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        top_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        insights.append({
            "type": "activity_pattern",
            "insight": f"Most active hours: {', '.join([f'{h}:00' for h, c in top_hours])}",
            "confidence": min(len(active_hours) / 100, 1.0)
        })
    
    # Store insights
    data["learning_insights"] = insights
    
    with open(LEARNING_DATA, "w") as f:
        json.dump(data, f, indent=2)
    
    return insights

def get_recommendations():
    """Get personalized recommendations based on learning data"""
    data = load_learning_data()
    insights = data.get("learning_insights", [])
    
    recommendations = []
    
    for insight in insights:
        if insight["type"] == "tweet_preference" and insight["confidence"] > 0.5:
            recommendations.append(f"Content: {insight['insight']}")
        elif insight["type"] == "activity_pattern" and insight["confidence"] > 0.6:
            recommendations.append(f"Schedule: {insight['insight']}")
    
    return recommendations

def main():
    """CLI interface for learning loop"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 learning_loop.py analyze       - Analyze patterns")
        print("  python3 learning_loop.py recommend     - Get recommendations")
        print("  python3 learning_loop.py log-activity  - Log current activity")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze":
        insights = analyze_patterns()
        print("📊 Learning Insights:\n")
        for insight in insights:
            confidence_pct = int(insight["confidence"] * 100)
            print(f"• {insight['insight']} (confidence: {confidence_pct}%)")
    
    elif command == "recommend":
        recs = get_recommendations()
        print("💡 Personalized Recommendations:\n")
        for rec in recs:
            print(f"• {rec}")
        if not recs:
            print("Not enough data yet. Keep using the system!")
    
    elif command == "log-activity":
        log_activity()
        print("✅ Activity logged")

if __name__ == "__main__":
    main()
