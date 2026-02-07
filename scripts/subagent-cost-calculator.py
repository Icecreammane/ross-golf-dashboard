#!/usr/bin/env python3
"""
Sub-Agent Cost Calculator
Estimates token usage and API costs for sub-agent tasks.
"""

import json
import sys
from typing import Dict, Optional

# Pricing as of Feb 2026 (per million tokens)
MODEL_PRICING = {
    "anthropic/claude-sonnet-4-5": {
        "input": 3.00,
        "output": 15.00,
        "name": "Claude Sonnet 4.5"
    },
    "google/gemini-2.0-flash-exp:free": {
        "input": 0.075,
        "output": 0.30,
        "name": "Gemini 2.0 Flash"
    },
    "openai/gpt-5.2-codex": {
        "input": 2.50,
        "output": 10.00,
        "name": "GPT-5.2 Codex"
    }
}

# Token usage patterns (tokens per hour)
TOKENS_PER_HOUR = {
    "base": 25000,  # Average baseline
    "quick": 25000,  # 1-2 hours
    "deep": 25000,   # 4-6 hours (sustained)
    "enforcer": 25000  # 8-12 hours (sustained)
}

# Input/output ratio (typically 20% input, 80% output for coding tasks)
IO_RATIO = {
    "input": 0.20,
    "output": 0.80
}


def estimate_cost(
    task_description: str,
    estimated_hours: float,
    model: str,
    tier: Optional[str] = None
) -> Dict:
    """
    Estimate the cost of running a sub-agent task.
    
    Args:
        task_description: Description of the task
        estimated_hours: Expected runtime in hours
        model: Model identifier (e.g., "anthropic/claude-sonnet-4-5")
        tier: Optional tier override (quick/deep/enforcer)
    
    Returns:
        Dictionary with cost breakdown and estimates
    """
    
    # Validate model
    if model not in MODEL_PRICING:
        raise ValueError(f"Unknown model: {model}. Available: {list(MODEL_PRICING.keys())}")
    
    pricing = MODEL_PRICING[model]
    
    # Determine tier if not specified
    if tier is None:
        if estimated_hours <= 2:
            tier = "quick"
        elif estimated_hours <= 6:
            tier = "deep"
        else:
            tier = "enforcer"
    
    # Calculate total tokens
    base_tokens_per_hour = TOKENS_PER_HOUR.get(tier, TOKENS_PER_HOUR["base"])
    total_tokens = int(base_tokens_per_hour * estimated_hours)
    
    # Apply complexity multiplier based on task description keywords
    complexity_multiplier = _analyze_complexity(task_description)
    total_tokens = int(total_tokens * complexity_multiplier)
    
    # Split into input/output
    input_tokens = int(total_tokens * IO_RATIO["input"])
    output_tokens = int(total_tokens * IO_RATIO["output"])
    
    # Calculate costs
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost
    
    return {
        "estimated_tokens": total_tokens,
        "estimated_cost": round(total_cost, 2),
        "model": model,
        "model_name": pricing["name"],
        "tier": tier,
        "estimated_hours": estimated_hours,
        "complexity_multiplier": complexity_multiplier,
        "breakdown": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": round(input_cost, 2),
            "output_cost": round(output_cost, 2)
        }
    }


def _analyze_complexity(task_description: str) -> float:
    """
    Analyze task complexity based on keywords.
    Returns multiplier: 0.7 (simple) to 1.5 (very complex)
    """
    desc_lower = task_description.lower()
    
    # Simple task indicators (0.7x)
    simple_keywords = ["fix", "bug", "typo", "update", "cleanup", "format", "refactor simple"]
    if any(kw in desc_lower for kw in simple_keywords):
        return 0.7
    
    # Complex task indicators (1.3x)
    complex_keywords = ["integration", "architecture", "system", "multi-", "complex", "full"]
    if any(kw in desc_lower for kw in complex_keywords):
        return 1.3
    
    # Very complex indicators (1.5x)
    very_complex = ["multi-system", "infrastructure", "complete system", "major"]
    if any(kw in desc_lower for kw in very_complex):
        return 1.5
    
    # Default (1.0x)
    return 1.0


def format_estimate(estimate: Dict) -> str:
    """Format cost estimate for display."""
    tier_emoji = {
        "quick": "🟢",
        "deep": "🟡",
        "enforcer": "🔴"
    }
    
    emoji = tier_emoji.get(estimate["tier"], "⚪")
    
    output = f"""
📊 **Cost Estimate**

{emoji} **Tier:** {estimate['tier'].title()} Builder
🤖 **Model:** {estimate['model_name']}
⏱️  **Time:** ~{estimate['estimated_hours']} hours
💰 **Cost:** ${estimate['estimated_cost']:.2f}

**Breakdown:**
  • Input: {estimate['breakdown']['input_tokens']:,} tokens (${estimate['breakdown']['input_cost']:.2f})
  • Output: {estimate['breakdown']['output_tokens']:,} tokens (${estimate['breakdown']['output_cost']:.2f})
  • Total: {estimate['estimated_tokens']:,} tokens

**Complexity:** {estimate['complexity_multiplier']}x multiplier
""".strip()
    
    return output


def main():
    """CLI interface for cost estimation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Estimate sub-agent task costs")
    parser.add_argument("task", help="Task description")
    parser.add_argument("--hours", type=float, required=True, help="Estimated hours")
    parser.add_argument("--model", default="anthropic/claude-sonnet-4-5", help="Model to use")
    parser.add_argument("--tier", choices=["quick", "deep", "enforcer"], help="Override tier")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of formatted text")
    
    args = parser.parse_args()
    
    try:
        estimate = estimate_cost(args.task, args.hours, args.model, args.tier)
        
        if args.json:
            print(json.dumps(estimate, indent=2))
        else:
            print(format_estimate(estimate))
            print(f"\n💡 Ready to launch? Run: ./spawn-agent.sh \"{args.task}\" --tier {estimate['tier']}")
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
