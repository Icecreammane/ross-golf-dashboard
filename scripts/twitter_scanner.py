#!/usr/bin/env python3
"""
Twitter Opportunity Scanner

Monitors:
- Replies to Ross's tweets
- DMs
- Mentions
- Engagement patterns

Detects opportunities for business conversations.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path.home() / "clawd" / "scripts"))
from opportunity_scanner import Opportunity, OpportunityQueue, score_opportunity

WORKSPACE = Path.home() / "clawd"
STATE_FILE = WORKSPACE / "twitter_scanner_state.json"

def load_state():
    """Load scanner state (last checked tweet ID, etc.)"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_checked": None, "processed_tweets": []}

def save_state(state):
    """Save scanner state"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def scan_twitter_activity():
    """
    Scan Twitter for opportunities using bird CLI
    
    For now, returns mock data since Reddit API isn't set up yet.
    TODO: Integrate with actual bird CLI once API is configured.
    """
    
    opportunities = []
    
    # Mock opportunity for testing (remove when API ready)
    mock_opportunity = Opportunity(
        id=f"twitter_{int(datetime.now().timestamp())}",
        source="twitter",
        type="engagement",
        title="Reply to your tweet about AI automation",
        context="Someone replied: 'This is exactly what I need for my business. How can I implement something like this?' - Shows clear interest in your automation skills.",
        url="https://twitter.com/_icecreammane/status/mock",
        score=score_opportunity(
            keywords=["business", "implement"],
            urgency_signals=["need"],
            context="This is exactly what I need for my business. How can I implement something like this?"
        ),
        detected_at=datetime.now().isoformat()
    )
    
    opportunities.append(mock_opportunity)
    
    return opportunities

def main():
    """Run Twitter scanner"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Scanning Twitter...")
    
    queue = OpportunityQueue()
    state = load_state()
    
    # Scan for new opportunities
    new_opps = scan_twitter_activity()
    
    added = 0
    for opp in new_opps:
        if queue.add(opp):
            added += 1
            print(f"  ✅ New opportunity: {opp.title} (score: {opp.score})")
    
    if added == 0:
        print("  No new opportunities")
    
    # Update state
    state["last_checked"] = datetime.now().isoformat()
    save_state(state)
    
    stats = queue.get_stats()
    print(f"\n📊 Queue stats: {stats['pending']} pending, {stats['drafted']} drafted")

if __name__ == "__main__":
    main()
