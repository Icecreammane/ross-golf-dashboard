#!/usr/bin/env python3
"""
Opportunity Scanner - Base framework for detecting business opportunities

Monitors multiple sources (Reddit, Twitter, Email) and queues high-value
opportunities for the auto-drafting engine.
"""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

WORKSPACE = Path.home() / "clawd"
OPPORTUNITIES_DIR = WORKSPACE / "opportunities"
OPPORTUNITIES_FILE = OPPORTUNITIES_DIR / "queue.json"

# Ensure directory exists
OPPORTUNITIES_DIR.mkdir(exist_ok=True)

@dataclass
class Opportunity:
    """Represents a business opportunity"""
    id: str
    source: str  # reddit, twitter, email
    type: str    # lead, engagement, inquiry
    title: str
    context: str
    url: Optional[str]
    score: float  # 0-100, higher = better opportunity
    detected_at: str
    status: str = "pending"  # pending, drafted, approved, rejected
    draft: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)

class OpportunityQueue:
    """Manages the queue of detected opportunities"""
    
    def __init__(self):
        self.opportunities = self._load()
    
    def _load(self) -> List[Opportunity]:
        """Load opportunities from JSON"""
        if not OPPORTUNITIES_FILE.exists():
            return []
        
        with open(OPPORTUNITIES_FILE) as f:
            data = json.load(f)
            return [Opportunity(**opp) for opp in data]
    
    def _save(self):
        """Save opportunities to JSON"""
        data = [opp.to_dict() for opp in self.opportunities]
        with open(OPPORTUNITIES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add(self, opportunity: Opportunity):
        """Add new opportunity to queue"""
        # Check for duplicates
        if any(opp.id == opportunity.id for opp in self.opportunities):
            return False
        
        self.opportunities.append(opportunity)
        self.opportunities.sort(key=lambda x: x.score, reverse=True)
        self._save()
        return True
    
    def get_pending(self, limit: int = 10) -> List[Opportunity]:
        """Get pending opportunities, highest score first"""
        pending = [opp for opp in self.opportunities if opp.status == "pending"]
        return pending[:limit]
    
    def update_status(self, opp_id: str, status: str, draft: Optional[str] = None):
        """Update opportunity status"""
        for opp in self.opportunities:
            if opp.id == opp_id:
                opp.status = status
                if draft:
                    opp.draft = draft
                self._save()
                return True
        return False
    
    def get_stats(self) -> Dict:
        """Get queue statistics"""
        return {
            "total": len(self.opportunities),
            "pending": len([o for o in self.opportunities if o.status == "pending"]),
            "drafted": len([o for o in self.opportunities if o.status == "drafted"]),
            "approved": len([o for o in self.opportunities if o.status == "approved"]),
            "rejected": len([o for o in self.opportunities if o.status == "rejected"])
        }

def score_opportunity(keywords: List[str], urgency_signals: List[str], 
                     context: str) -> float:
    """
    Score an opportunity based on keywords and urgency signals
    
    Returns score 0-100:
    - 80-100: Hot lead (budget mentioned, urgent, perfect fit)
    - 60-80: Good opportunity (clear need, some urgency)
    - 40-60: Worth exploring (potential fit)
    - 0-40: Low priority (vague, no urgency)
    """
    score = 0
    context_lower = context.lower()
    
    # Budget/money mentions (+30)
    budget_keywords = ["budget", "$", "pay", "hire", "quote", "cost", "price", "invest"]
    if any(kw in context_lower for kw in budget_keywords):
        score += 30
    
    # Urgency signals (+25)
    urgency_words = ["asap", "urgent", "quickly", "soon", "deadline", "immediate"]
    if any(kw in context_lower for kw in urgency_words):
        score += 25
    
    # Skill match (+20)
    skill_keywords = ["website", "app", "automation", "data", "analysis", "development", 
                     "dashboard", "api", "ai", "ml", "python", "javascript"]
    matches = sum(1 for kw in skill_keywords if kw in context_lower)
    score += min(matches * 5, 20)
    
    # Specificity (+15)
    if len(context) > 200:  # Detailed description
        score += 15
    elif len(context) > 100:
        score += 10
    
    # Question/ask detected (+10)
    if "?" in context or any(w in context_lower for w in ["looking for", "need help", "recommend"]):
        score += 10
    
    return min(score, 100)

def main():
    """Test the opportunity queue"""
    queue = OpportunityQueue()
    
    # Test opportunity
    test_opp = Opportunity(
        id="test_001",
        source="reddit",
        type="lead",
        title="Need help building fitness tracker",
        context="Looking for someone to build a fitness tracking app. Budget around $2-3k. Need it done ASAP.",
        url="https://reddit.com/r/test",
        score=score_opportunity([], [], "Budget $2-3k ASAP fitness tracking app"),
        detected_at=datetime.now().isoformat()
    )
    
    if queue.add(test_opp):
        print(f"Added opportunity: {test_opp.title} (score: {test_opp.score})")
    
    print(f"\nQueue stats: {queue.get_stats()}")
    
    pending = queue.get_pending()
    print(f"\nPending opportunities: {len(pending)}")
    for opp in pending:
        print(f"  - {opp.title} (score: {opp.score})")

if __name__ == "__main__":
    main()
