#!/usr/bin/env python3
"""
Tiered Model Router - Intelligent model selection for cost optimization
Routes tasks to cheapest capable model
"""

import json
from enum import Enum

class TaskComplexity(Enum):
    TRIVIAL = 1      # Local models (free)
    SIMPLE = 2       # Haiku ($0.25/M)
    MEDIUM = 3       # Sonnet ($3/M) or GPT-4o-mini
    COMPLEX = 4      # Sonnet ($3/M) or GPT-4o
    CRITICAL = 5     # Opus ($15/M) or GPT-5

# Model tiers with fallbacks
MODEL_TIERS = {
    TaskComplexity.TRIVIAL: [
        'local-fast',       # Batman - Llama 8B (free)
        'local-brain',      # LD - Qwen 14B (free)  
        'claude-haiku-4-5'  # Fallback if local unavailable
    ],
    TaskComplexity.SIMPLE: [
        'local-smart',      # Arnold - Qwen 32B (free)
        'local-brain',      # LD - Qwen 14B (free)
        'claude-haiku-4-5', # $0.25/M
        'gpt-4o-mini'       # $0.15/M
    ],
    TaskComplexity.MEDIUM: [
        'claude-sonnet-4-5',  # $3/M (best quality/price)
        'gpt-4o'              # $2.50/M (alternative)
    ],
    TaskComplexity.COMPLEX: [
        'claude-sonnet-4-5',  # $3/M (primary)
        'gpt-4o',             # $2.50/M (alternative)
        'gpt-5.2'             # $5/M (if needed)
    ],
    TaskComplexity.CRITICAL: [
        'claude-opus-4-5',    # $15/M (highest quality)
        'gpt-5.2'             # $5/M (alternative)
    ]
}

def classify_task(task_description):
    """
    Classify task complexity based on description
    Returns TaskComplexity enum
    """
    desc_lower = task_description.lower()
    
    # Trivial tasks (local models)
    trivial_keywords = [
        'simple', 'quick', 'list', 'format', 'summarize short',
        'extract', 'parse', 'count', 'check', 'yes/no'
    ]
    if any(kw in desc_lower for kw in trivial_keywords):
        return TaskComplexity.TRIVIAL
    
    # Simple tasks (cheap API)
    simple_keywords = [
        'summarize', 'classify', 'basic', 'straightforward',
        'routine', 'standard', 'common'
    ]
    if any(kw in desc_lower for kw in simple_keywords):
        return TaskComplexity.SIMPLE
    
    # Critical tasks (expensive models)
    critical_keywords = [
        'critical', 'production', 'customer-facing', 'final',
        'important decision', 'launch', 'revenue'
    ]
    if any(kw in desc_lower for kw in critical_keywords):
        return TaskComplexity.CRITICAL
    
    # Complex tasks (smart models)
    complex_keywords = [
        'analyze deeply', 'complex', 'nuanced', 'strategic',
        'multi-step', 'detailed analysis', 'architecture'
    ]
    if any(kw in desc_lower for kw in complex_keywords):
        return TaskComplexity.COMPLEX
    
    # Default to medium
    return TaskComplexity.MEDIUM

def route_task(task_description, prefer_local=True):
    """
    Route task to appropriate model
    
    Args:
        task_description: Description of the task
        prefer_local: Whether to prefer local models when possible
        
    Returns:
        dict with model, tier, estimated_cost
    """
    complexity = classify_task(task_description)
    models = MODEL_TIERS[complexity]
    
    # Filter out local models if not preferred or not available
    if not prefer_local:
        models = [m for m in models if not m.startswith('local-')]
    
    selected_model = models[0]  # Pick first (cheapest/best)
    
    # Estimate cost (assuming 1000 input + 500 output tokens)
    cost_estimates = {
        'local-fast': 0,
        'local-brain': 0,
        'local-smart': 0,
        'claude-haiku-4-5': 0.00088,
        'gpt-4o-mini': 0.00045,
        'claude-sonnet-4-5': 0.0105,
        'gpt-4o': 0.00875,
        'gpt-5.2': 0.015,
        'claude-opus-4-5': 0.06
    }
    
    return {
        'model': selected_model,
        'tier': complexity.name,
        'estimated_cost': cost_estimates.get(selected_model, 0.01),
        'reasoning': f"Task classified as {complexity.name} → routed to {selected_model}"
    }

# Example task classifications
EXAMPLE_TASKS = {
    "List all files in the directory": TaskComplexity.TRIVIAL,
    "Summarize this short article": TaskComplexity.SIMPLE,
    "Write a product launch strategy": TaskComplexity.COMPLEX,
    "Review this production code for critical bugs": TaskComplexity.CRITICAL,
    "Generate a daily task list from goals": TaskComplexity.MEDIUM,
}

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: tiered_model_router.py <task_description>")
        print("\nExamples:")
        for task, expected in EXAMPLE_TASKS.items():
            result = route_task(task)
            print(f"\nTask: {task}")
            print(f"  → {result['model']} (${result['estimated_cost']:.4f})")
        sys.exit(0)
    
    task = ' '.join(sys.argv[1:])
    result = route_task(task)
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
