#!/usr/bin/env python3
"""
Helper functions for Jarvis to use tiered routing and cost tracking
"""

import sys
import os
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path.home() / "clawd" / "scripts"))

from tiered_model_router import route_task
from cost_tracker_advanced import log_api_call

def smart_route(task_description):
    """
    Route task to best model and return model name
    Jarvis can use this before spawning agents or making AI calls
    """
    result = route_task(task_description)
    print(f"🎯 Routed '{task_description[:50]}...' → {result['model']} (${result['estimated_cost']:.4f})")
    return result['model']

def log_cost(model, workflow, input_tokens, output_tokens):
    """
    Log API cost for tracking
    Jarvis can call this after AI operations
    """
    cost = log_api_call(model, workflow, input_tokens, output_tokens)
    return cost

# Quick test
if __name__ == '__main__':
    print("Testing Jarvis helpers...")
    
    test_tasks = [
        "Generate daily tasks from GOALS.md",
        "Summarize a short article",
        "Critical production launch decision"
    ]
    
    for task in test_tasks:
        model = smart_route(task)
        print(f"  Would use: {model}\n")
