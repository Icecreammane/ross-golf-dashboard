#!/usr/bin/env python3
"""
Sub-Agent Model Selector
Smart model selection based on task characteristics.
"""

import json
import sys
from typing import Dict, List


MODELS = {
    "anthropic/claude-sonnet-4-5": {
        "name": "Claude Sonnet 4.5",
        "strengths": ["Complex reasoning", "Architecture", "System design", "Multi-step planning"],
        "cost_per_m": {"input": 3.00, "output": 15.00},
        "speed": "medium",
        "reliability": "excellent"
    },
    "google/gemini-2.0-flash-exp:free": {
        "name": "Gemini 2.0 Flash",
        "strengths": ["Fast iteration", "Simple tasks", "Bug fixes", "Code cleanup"],
        "cost_per_m": {"input": 0.075, "output": 0.30},
        "speed": "fast",
        "reliability": "good"
    },
    "openai/gpt-5.2-codex": {
        "name": "GPT-5.2 Codex",
        "strengths": ["Code generation", "API implementation", "Algorithms", "Testing"],
        "cost_per_m": {"input": 2.50, "output": 10.00},
        "speed": "medium",
        "reliability": "very-good"
    }
}


def select_model(task_description: str, tier: str = None, user_preference: str = None) -> Dict:
    """
    Select the best model for a task.
    
    Args:
        task_description: Description of the task
        tier: Optional tier (quick/deep/enforcer)
        user_preference: Optional user override
    
    Returns:
        Dictionary with model selection and justification
    """
    
    # If user specified a preference, validate and use it
    if user_preference:
        if user_preference not in MODELS:
            # Try fuzzy matching
            user_lower = user_preference.lower()
            for model_id in MODELS:
                if user_lower in model_id.lower() or user_lower in MODELS[model_id]["name"].lower():
                    return {
                        "model": model_id,
                        "model_name": MODELS[model_id]["name"],
                        "reason": f"User override: {user_preference}",
                        "confidence": "user-specified",
                        "alternatives": []
                    }
            raise ValueError(f"Unknown model: {user_preference}. Available: {list(MODELS.keys())}")
        else:
            return {
                "model": user_preference,
                "model_name": MODELS[user_preference]["name"],
                "reason": "User-specified model",
                "confidence": "user-specified",
                "alternatives": []
            }
    
    desc_lower = task_description.lower()
    
    # Analyze task characteristics
    characteristics = _analyze_task_characteristics(desc_lower)
    
    # Score each model
    scores = {}
    for model_id, model_info in MODELS.items():
        score = _score_model(characteristics, model_id, model_info, tier)
        scores[model_id] = score
    
    # Sort by score
    sorted_models = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_model = sorted_models[0][0]
    best_score = sorted_models[0][1]
    
    # Generate justification
    reason = _generate_justification(characteristics, best_model, MODELS[best_model])
    
    # Confidence based on score gap
    score_gap = best_score - sorted_models[1][1] if len(sorted_models) > 1 else best_score
    if score_gap > 3:
        confidence = "high"
    elif score_gap > 1:
        confidence = "medium"
    else:
        confidence = "low"
    
    # Alternative recommendations
    alternatives = [
        {
            "model": model_id,
            "model_name": MODELS[model_id]["name"],
            "score": score,
            "reason": f"Good for: {', '.join(MODELS[model_id]['strengths'][:2])}"
        }
        for model_id, score in sorted_models[1:3]
    ]
    
    return {
        "model": best_model,
        "model_name": MODELS[best_model]["name"],
        "reason": reason,
        "confidence": confidence,
        "characteristics": characteristics,
        "scores": {m: s for m, s in sorted_models},
        "alternatives": alternatives
    }


def _analyze_task_characteristics(desc_lower: str) -> Dict:
    """Analyze task to determine characteristics."""
    characteristics = {
        "complexity": "simple",
        "reasoning_heavy": False,
        "coding_heavy": False,
        "architecture": False,
        "bug_fix": False,
        "integration": False,
        "optimization": False
    }
    
    # Complexity
    complex_keywords = ["complex", "multi-", "system", "architecture", "infrastructure"]
    if any(kw in desc_lower for kw in complex_keywords):
        characteristics["complexity"] = "complex"
    elif any(kw in desc_lower for kw in ["feature", "implement", "refactor"]):
        characteristics["complexity"] = "medium"
    
    # Reasoning-heavy
    reasoning_keywords = ["design", "architecture", "plan", "strategy", "approach"]
    characteristics["reasoning_heavy"] = any(kw in desc_lower for kw in reasoning_keywords)
    
    # Coding-heavy
    coding_keywords = ["implement", "code", "function", "api", "algorithm", "write"]
    characteristics["coding_heavy"] = any(kw in desc_lower for kw in coding_keywords)
    
    # Architecture
    characteristics["architecture"] = any(kw in desc_lower for kw in ["architecture", "system design", "infrastructure"])
    
    # Bug fix
    characteristics["bug_fix"] = any(kw in desc_lower for kw in ["bug", "fix", "error", "issue"])
    
    # Integration
    characteristics["integration"] = any(kw in desc_lower for kw in ["integrat", "connect", "link"])
    
    # Optimization
    characteristics["optimization"] = any(kw in desc_lower for kw in ["optimi", "performance", "speed", "improve"])
    
    return characteristics


def _score_model(characteristics: Dict, model_id: str, model_info: Dict, tier: str) -> float:
    """Score a model based on task characteristics."""
    score = 5.0  # Base score
    
    # Complexity matching
    if characteristics["complexity"] == "complex":
        if model_id == "anthropic/claude-sonnet-4-5":
            score += 3
        elif model_id == "openai/gpt-5.2-codex":
            score += 2
        else:
            score -= 1
    elif characteristics["complexity"] == "simple":
        if model_id == "google/gemini-2.0-flash-exp:free":
            score += 3
        else:
            score -= 0.5
    
    # Reasoning-heavy
    if characteristics["reasoning_heavy"]:
        if model_id == "anthropic/claude-sonnet-4-5":
            score += 3
    
    # Coding-heavy
    if characteristics["coding_heavy"]:
        if model_id == "openai/gpt-5.2-codex":
            score += 2
        elif model_id == "anthropic/claude-sonnet-4-5":
            score += 1
    
    # Architecture
    if characteristics["architecture"]:
        if model_id == "anthropic/claude-sonnet-4-5":
            score += 3
    
    # Bug fix
    if characteristics["bug_fix"]:
        if model_id == "google/gemini-2.0-flash-exp:free":
            score += 2
        else:
            score += 0.5
    
    # Integration
    if characteristics["integration"]:
        if model_id == "anthropic/claude-sonnet-4-5":
            score += 2
        elif model_id == "openai/gpt-5.2-codex":
            score += 1
    
    # Tier-based preferences
    if tier == "quick":
        if model_id == "google/gemini-2.0-flash-exp:free":
            score += 2
    elif tier == "enforcer":
        if model_id == "anthropic/claude-sonnet-4-5":
            score += 2
    
    return score


def _generate_justification(characteristics: Dict, model_id: str, model_info: Dict) -> str:
    """Generate human-readable justification for model selection."""
    reasons = []
    
    if characteristics["complexity"] == "complex":
        reasons.append("complex task requiring strong reasoning")
    elif characteristics["complexity"] == "simple":
        reasons.append("straightforward task, cost efficiency preferred")
    
    if characteristics["reasoning_heavy"]:
        reasons.append("requires architectural thinking")
    
    if characteristics["coding_heavy"]:
        reasons.append("heavy code generation")
    
    if characteristics["bug_fix"]:
        reasons.append("bug fix (quick iteration valuable)")
    
    if characteristics["integration"]:
        reasons.append("system integration task")
    
    if not reasons:
        reasons.append("balanced general-purpose task")
    
    justification = f"{model_info['name']} selected: {', '.join(reasons)}. "
    justification += f"Strengths: {', '.join(model_info['strengths'][:2])}."
    
    return justification


def format_selection(selection: Dict) -> str:
    """Format model selection for display."""
    result = f"""
🤖 **Model Selection: {selection['model_name']}**

**Confidence:** {selection['confidence'].upper()}

**Reason:** {selection['reason']}

**Task Characteristics:**
""".strip()
    
    for key, value in selection['characteristics'].items():
        if isinstance(value, bool) and value:
            result += f"\n  • {key.replace('_', ' ').title()}"
        elif not isinstance(value, bool):
            result += f"\n  • {key.replace('_', ' ').title()}: {value}"
    
    if selection['alternatives']:
        result += "\n\n**Alternatives:**"
        for alt in selection['alternatives']:
            result += f"\n  • {alt['model_name']}: {alt['reason']}"
    
    return result


def main():
    """CLI interface for model selection."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Select best model for task")
    parser.add_argument("task", help="Task description")
    parser.add_argument("--tier", choices=["quick", "deep", "enforcer"], help="Task tier")
    parser.add_argument("--prefer", help="Preferred model (override)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    try:
        selection = select_model(args.task, args.tier, args.prefer)
        
        if args.json:
            print(json.dumps(selection, indent=2))
        else:
            print(format_selection(selection))
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
