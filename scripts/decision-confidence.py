#!/usr/bin/env python3
"""
Decision Confidence Scorer - helps Jarvis decide when to act vs. ask.
"""

import json

DECISION_RULES = {
    # High confidence (90-100%) - Just do it
    "high": {
        "patterns": [
            "bug fix",
            "optimization",
            "log cleanup",
            "documentation",
            "code cleanup",
            "refactor (non-breaking)",
            "performance improvement",
            "error handling"
        ],
        "action": "execute",
        "report": "after_completion"
    },
    
    # Medium confidence (70-89%) - Quick check
    "medium": {
        "patterns": [
            "new feature (obvious pattern)",
            "api integration (standard)",
            "config change (minor)",
            "ui tweak",
            "database optimization",
            "cache implementation"
        ],
        "action": "notify_and_execute",
        "report": "before_start"
    },
    
    # Low confidence (<70%) - Ask first
    "low": {
        "patterns": [
            "breaking change",
            "user-facing change",
            "cost implication",
            "security related",
            "data migration",
            "external integration (new service)",
            "major architecture"
        ],
        "action": "request_approval",
        "report": "detailed_proposal"
    }
}

def score_decision(task_description):
    """
    Scores confidence level for a decision.
    
    Returns:
        {
            "confidence": "high" | "medium" | "low",
            "score": 0-100,
            "action": "execute" | "notify_and_execute" | "request_approval",
            "reasoning": str
        }
    """
    
    task_lower = task_description.lower()
    
    # Check high confidence patterns
    for pattern in DECISION_RULES["high"]["patterns"]:
        if pattern in task_lower:
            return {
                "confidence": "high",
                "score": 95,
                "action": "execute",
                "reasoning": f"Matches high-confidence pattern: {pattern}",
                "approval_needed": False
            }
    
    # Check low confidence patterns (blockers)
    for pattern in DECISION_RULES["low"]["patterns"]:
        if pattern in task_lower:
            return {
                "confidence": "low",
                "score": 50,
                "action": "request_approval",
                "reasoning": f"Matches low-confidence pattern: {pattern}",
                "approval_needed": True
            }
    
    # Check medium confidence patterns
    for pattern in DECISION_RULES["medium"]["patterns"]:
        if pattern in task_lower:
            return {
                "confidence": "medium",
                "score": 80,
                "action": "notify_and_execute",
                "reasoning": f"Matches medium-confidence pattern: {pattern}",
                "approval_needed": False,
                "notify": True
            }
    
    # Default: medium-low (ask for clarification)
    return {
        "confidence": "medium-low",
        "score": 65,
        "action": "clarify_then_execute",
        "reasoning": "No clear pattern match. Quick clarification recommended.",
        "approval_needed": False,
        "clarify": True
    }

# Export for main agent
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: decision-confidence.py '<task description>'")
        sys.exit(1)
    
    result = score_decision(sys.argv[1])
    print(json.dumps(result, indent=2))
