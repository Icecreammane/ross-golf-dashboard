#!/usr/bin/env python3
"""
Email Opportunity Scanner

Monitors bigmeatyclawd@gmail.com for:
- Project inquiries
- Business opportunities
- Collaboration requests
- Anything with $$ potential

Uses keywords: hire, project, quote, budget, opportunity, collab
"""

import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path.home() / "clawd" / "scripts"))
from opportunity_scanner import Opportunity, OpportunityQueue, score_opportunity

WORKSPACE = Path.home() / "clawd"
STATE_FILE = WORKSPACE / "email_scanner_state.json"

def load_state():
    """Load scanner state"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_checked": None, "processed_emails": []}

def save_state(state):
    """Save scanner state"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def scan_email():
    """
    Scan email for opportunities
    
    TODO: Integrate with himalaya CLI once configured
    For now, returns mock data for testing
    """
    
    opportunities = []
    
    # Mock opportunity for testing
    mock_opportunity = Opportunity(
        id=f"email_{int(datetime.now().timestamp())}",
        source="email",
        type="inquiry",
        title="Project inquiry - Fitness tracking dashboard",
        context="Email from potential client: 'I saw your work and I'm interested in building a custom fitness tracking dashboard for my gym. We have a budget of $5-7k. Can you help?' - Clear project scope, budget mentioned, aligns with your skills.",
        url=None,
        score=score_opportunity(
            keywords=["project", "budget", "help"],
            urgency_signals=[],
            context="fitness tracking dashboard budget $5-7k custom gym"
        ),
        detected_at=datetime.now().isoformat()
    )
    
    opportunities.append(mock_opportunity)
    
    return opportunities

def main():
    """Run email scanner"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Scanning Email...")
    
    queue = OpportunityQueue()
    state = load_state()
    
    # Scan for new opportunities
    new_opps = scan_email()
    
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
