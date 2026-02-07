#!/usr/bin/env python3
"""
Reddit Scanner - Auto-scans target subreddits for opportunities
Finds: "need help", "looking for", "want to build" posts matching Ross's solutions
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
OUTPUT_DIR = WORKSPACE / "revenue"
OPPORTUNITIES_FILE = OUTPUT_DIR / "reddit-opportunities.json"

# Target subreddits and keywords
TARGET_SUBS = [
    "Fitness",
    "SideProject", 
    "Entrepreneur",
    "webdev",
    "productivity",
    "learnprogramming"
]

OPPORTUNITY_KEYWORDS = [
    # Fitness tracker related
    "fitness app", "track workouts", "meal tracking", "fitness dashboard",
    "workout logger", "macro tracking", "fitness automation",
    
    # Automation related
    "automate workflow", "productivity tool", "dashboard", "automation",
    
    # Building/help related
    "need help", "looking for", "anyone know", "how to build",
    "want to create", "building a tool"
]

def scan_reddit_placeholder():
    """
    Placeholder scanner until Reddit API is set up
    Returns example opportunities for testing
    """
    
    # Example opportunities (would come from API)
    opportunities = [
        {
            "subreddit": "r/Fitness",
            "title": "Looking for a simple workout tracking app",
            "url": "https://reddit.com/r/Fitness/example1",
            "score": 45,
            "comments": 12,
            "created": (datetime.now() - timedelta(hours=2)).isoformat(),
            "relevance": 0.9,
            "reason": "Direct ask for fitness tracking solution"
        },
        {
            "subreddit": "r/SideProject",
            "title": "Anyone building meal planning automation?",
            "url": "https://reddit.com/r/SideProject/example2",
            "score": 23,
            "comments": 8,
            "created": (datetime.now() - timedelta(hours=5)).isoformat(),
            "relevance": 0.85,
            "reason": "Matches meal planning feature roadmap"
        }
    ]
    
    return opportunities

def score_opportunity(post):
    """Score opportunity based on relevance and urgency"""
    score = 0.0
    
    # Recency (newer = better)
    created = datetime.fromisoformat(post["created"])
    hours_old = (datetime.now() - created).total_seconds() / 3600
    if hours_old < 6:
        score += 0.3
    elif hours_old < 24:
        score += 0.2
    
    # Engagement (more upvotes/comments = validation)
    if post["score"] > 20:
        score += 0.2
    if post["comments"] > 5:
        score += 0.1
    
    # Inherent relevance
    score += post.get("relevance", 0.5)
    
    return min(score, 1.0)

def generate_response_template(opportunity):
    """Generate response template for opportunity"""
    
    templates = {
        "fitness_tracking": """Hey! I'm actually building something similar - a fitness tracker that learns your patterns and automates meal planning.

Still early stages but happy to chat about what you're looking for. What features are most important to you?""",
        
        "automation": """Interesting problem! I've been working on automation tools - curious what specific workflow you're trying to optimize?

Might have some insights to share from what I'm building.""",
        
        "general_help": """I've been working on similar problems lately. What have you tried so far?

Might be able to point you in the right direction or collaborate if there's overlap."""
    }
    
    # Smart template selection based on keywords
    title_lower = opportunity["title"].lower()
    
    if any(word in title_lower for word in ["fitness", "workout", "meal"]):
        return templates["fitness_tracking"]
    elif any(word in title_lower for word in ["automate", "productivity", "workflow"]):
        return templates["automation"]
    else:
        return templates["general_help"]

def scan_and_report():
    """Main scanner function"""
    
    print("🔍 Scanning Reddit for opportunities...")
    
    # Get opportunities (placeholder until API set up)
    opportunities = scan_reddit_placeholder()
    
    # Score and filter
    scored = []
    for opp in opportunities:
        opp["score_calculated"] = score_opportunity(opp)
        opp["response_template"] = generate_response_template(opp)
        if opp["score_calculated"] > 0.5:  # Only high-quality leads
            scored.append(opp)
    
    # Sort by score
    scored.sort(key=lambda x: x["score_calculated"], reverse=True)
    
    # Save to file
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    report = {
        "scan_time": datetime.now().isoformat(),
        "opportunities_found": len(scored),
        "high_priority": [o for o in scored if o["score_calculated"] > 0.8],
        "all_opportunities": scored
    }
    
    with open(OPPORTUNITIES_FILE, "w") as f:
        json.dump(report, f, indent=2)
    
    # Generate markdown report
    md_report = f"""# Reddit Opportunities - {datetime.now().strftime('%Y-%m-%d')}

**Scan time:** {datetime.now().strftime('%I:%M %p CST')}  
**Opportunities found:** {len(scored)}  
**High priority:** {len(report['high_priority'])}

---

## 🔥 High Priority (Act Fast)

"""
    
    for opp in report["high_priority"]:
        md_report += f"""### {opp['title']}
- **Subreddit:** {opp['subreddit']}
- **Score:** {opp['score']} upvotes, {opp['comments']} comments
- **Posted:** {opp['created']}
- **Relevance:** {int(opp['score_calculated']*100)}%
- **Link:** {opp['url']}

**Why this matters:** {opp['reason']}

**Suggested response:**
```
{opp['response_template']}
```

---

"""
    
    md_report += """
## 📊 All Opportunities

"""
    
    for opp in scored:
        if opp not in report["high_priority"]:
            md_report += f"- [{opp['title']}]({opp['url']}) - {opp['subreddit']} - Relevance: {int(opp['score_calculated']*100)}%\n"
    
    md_report += """

---

## 🎯 Next Steps

1. Review high priority opportunities
2. Reply with provided templates (customize to your voice)
3. Follow the thread
4. Build relationships before selling

**Remember:** Provide value first, sell second. Build trust through helping.

---

*This is placeholder data until Reddit API is configured. See REDDIT_SETUP.md for instructions.*
"""
    
    md_file = OUTPUT_DIR / f"reddit-scan-{datetime.now().strftime('%Y%m%d')}.md"
    with open(md_file, "w") as f:
        f.write(md_report)
    
    print(f"✅ Found {len(scored)} opportunities")
    print(f"📁 Report: {md_file}")
    
    return report

if __name__ == "__main__":
    scan_and_report()
