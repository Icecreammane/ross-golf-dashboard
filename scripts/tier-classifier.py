#!/usr/bin/env python3
"""
Sub-Agent Tier Classifier
Analyzes task descriptions and recommends the appropriate tier.
"""

import json
import re
import sys
from typing import Dict, Tuple


# Tier definitions
TIER_SPECS = {
    "quick": {
        "name": "Quick Builder",
        "emoji": "🟢",
        "hours": (1, 2),
        "cost_range": (2, 5),
        "use_cases": [
            "Bug fixes",
            "Small optimizations",
            "Documentation updates",
            "Simple feature additions",
            "Code cleanup"
        ],
        "recommended_model": "google/gemini-2.0-flash-exp:free"
    },
    "deep": {
        "name": "Deep Builder",
        "emoji": "🟡",
        "hours": (4, 6),
        "cost_range": (10, 20),
        "use_cases": [
            "Complex features",
            "System integrations",
            "Multi-file refactors",
            "API implementations"
        ],
        "recommended_model": "anthropic/claude-sonnet-4-5"
    },
    "enforcer": {
        "name": "The Enforcer",
        "emoji": "🔴",
        "hours": (8, 12),
        "cost_range": (30, 50),
        "use_cases": [
            "Full system builds",
            "Weekend monsters",
            "Major infrastructure",
            "Multi-system integration"
        ],
        "recommended_model": "anthropic/claude-sonnet-4-5"
    }
}


def classify_task(task_description: str) -> Dict:
    """
    Classify a task and recommend tier, model, and estimated time/cost.
    
    Args:
        task_description: Task description to analyze
    
    Returns:
        Dictionary with classification results
    """
    desc_lower = task_description.lower()
    
    # Calculate complexity score
    score, indicators = _calculate_complexity_score(desc_lower)
    
    # Determine tier based on score
    if score <= 2:
        tier = "quick"
    elif score <= 5:
        tier = "deep"
    else:
        tier = "enforcer"
    
    tier_spec = TIER_SPECS[tier]
    
    # Select model based on task type
    model = _select_model(desc_lower, tier)
    
    # Estimate hours (average of range)
    estimated_hours = sum(tier_spec["hours"]) / 2
    
    # Estimate cost (average of range, but we'll refine with calculator)
    estimated_cost = sum(tier_spec["cost_range"]) / 2
    
    return {
        "tier": tier,
        "tier_name": tier_spec["name"],
        "tier_emoji": tier_spec["emoji"],
        "recommended_model": model,
        "estimated_hours": estimated_hours,
        "estimated_cost_range": tier_spec["cost_range"],
        "estimated_cost": estimated_cost,
        "complexity_score": score,
        "indicators": indicators,
        "use_cases": tier_spec["use_cases"]
    }


def _calculate_complexity_score(desc_lower: str) -> Tuple[int, list]:
    """
    Calculate complexity score based on keywords and patterns.
    Returns: (score, list of indicators found)
    """
    score = 0
    indicators = []
    
    # Quick tier indicators (subtract from score if these dominate)
    quick_patterns = {
        "bug fix": -1,
        "fix": -1,
        "typo": -2,
        "update doc": -1,
        "cleanup": -1,
        "format": -1,
        "simple": -1
    }
    
    # Deep tier indicators
    deep_patterns = {
        "feature": 2,
        "implement": 2,
        "integration": 3,
        "api": 2,
        "refactor": 2,
        "optimize": 1,
        "database": 2,
        "authentication": 2,
        "complex": 2
    }
    
    # Enforcer tier indicators
    enforcer_patterns = {
        "system": 3,
        "infrastructure": 4,
        "architecture": 3,
        "multi-system": 5,
        "complete system": 5,
        "full": 2,
        "major": 2,
        "entire": 3,
        "rebuild": 3,
        "dashboard": 2
    }
    
    # Check all patterns
    for pattern, points in quick_patterns.items():
        if pattern in desc_lower:
            score += points
            indicators.append(f"Quick: {pattern}")
    
    for pattern, points in deep_patterns.items():
        if pattern in desc_lower:
            score += points
            indicators.append(f"Deep: {pattern}")
    
    for pattern, points in enforcer_patterns.items():
        if pattern in desc_lower:
            score += points
            indicators.append(f"Enforcer: {pattern}")
    
    # Adjust based on length (longer descriptions often mean complex tasks)
    word_count = len(desc_lower.split())
    if word_count > 50:
        score += 2
        indicators.append("Long description (+2)")
    elif word_count < 10:
        score -= 1
        indicators.append("Short description (-1)")
    
    # Minimum score of 0
    score = max(0, score)
    
    return score, indicators


def _select_model(desc_lower: str, tier: str) -> str:
    """
    Select the best model for the task.
    
    Decision tree:
    1. Complex reasoning → Sonnet 4.5
    2. Coding-heavy → Codex (if available)
    3. Simple/routine → Gemini Flash
    """
    
    # Complex reasoning indicators → Sonnet
    complex_keywords = ["architecture", "design", "system", "integration", "complex"]
    if any(kw in desc_lower for kw in complex_keywords):
        return "anthropic/claude-sonnet-4-5"
    
    # Coding-heavy indicators → Codex (but we'll use Sonnet for now since Codex may not be available)
    coding_keywords = ["implement", "code", "function", "api", "algorithm"]
    if any(kw in desc_lower for kw in coding_keywords) and tier == "deep":
        # For production, we'll use Sonnet since it's reliable
        return "anthropic/claude-sonnet-4-5"
    
    # Simple/routine → Gemini Flash
    if tier == "quick":
        return "google/gemini-2.0-flash-exp:free"
    
    # Default to tier recommendation
    return TIER_SPECS[tier]["recommended_model"]


def format_classification(classification: Dict) -> str:
    """Format classification results for display."""
    result = f"""
{classification['tier_emoji']} **{classification['tier_name']}**

**Recommended Model:** {classification['recommended_model']}
**Estimated Time:** {classification['estimated_hours']} hours
**Estimated Cost:** ${classification['estimated_cost']:.0f} (${classification['estimated_cost_range'][0]}-${classification['estimated_cost_range'][1]})

**Complexity Score:** {classification['complexity_score']}

**Indicators Found:**
""".strip()
    
    for indicator in classification['indicators'][:5]:  # Show top 5
        result += f"\n  • {indicator}"
    
    if len(classification['indicators']) > 5:
        result += f"\n  • ... and {len(classification['indicators']) - 5} more"
    
    result += f"\n\n**This tier is good for:**"
    for use_case in classification['use_cases'][:3]:  # Show top 3
        result += f"\n  • {use_case}"
    
    return result


def main():
    """CLI interface for tier classification."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Classify task and recommend tier")
    parser.add_argument("task", help="Task description")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    try:
        classification = classify_task(args.task)
        
        if args.json:
            print(json.dumps(classification, indent=2))
        else:
            print(format_classification(classification))
            print(f"\n💡 Next: ./spawn-agent.sh \"{args.task}\" --tier {classification['tier']}")
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
