#!/usr/bin/env python3
"""
Cost Tracker - Log API usage and costs
Appends to daily memory files and generates reports
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Cost per 1M tokens (approximate)
MODEL_COSTS = {
    "anthropic/claude-sonnet-4-5": {"input": 3.0, "output": 15.0},
    "anthropic/claude-haiku-4-5": {"input": 0.25, "output": 1.25},
    "anthropic/claude-opus-4-5": {"input": 15.0, "output": 75.0},
    "openai/gpt-5.2-codex": {"input": 2.5, "output": 10.0},
    "openai/gpt-4o": {"input": 2.5, "output": 10.0},
    "ollama/qwen2.5:14b": {"input": 0.0, "output": 0.0},
    "ollama/llama3.1:8b": {"input": 0.0, "output": 0.0},
}

def log_api_call(model, input_tokens, output_tokens, context="", session="main"):
    """Log an API call with cost calculation"""
    
    # Calculate cost
    costs = MODEL_COSTS.get(model, {"input": 0, "output": 0})
    input_cost = (input_tokens / 1_000_000) * costs["input"]
    output_cost = (output_tokens / 1_000_000) * costs["output"]
    total_cost = input_cost + output_cost
    
    # Prepare log entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "model": model,
        "session": session,
        "context": context,
        "tokens": {
            "input": input_tokens,
            "output": output_tokens,
            "total": input_tokens + output_tokens
        },
        "cost": {
            "input": round(input_cost, 4),
            "output": round(output_cost, 4),
            "total": round(total_cost, 4)
        }
    }
    
    # Log to daily file
    today = datetime.now().strftime("%Y-%m-%d")
    memory_dir = Path.home() / "clawd" / "memory"
    cost_log = memory_dir / f"cost-log-{today}.json"
    
    # Append to log
    logs = []
    if cost_log.exists():
        with open(cost_log, 'r') as f:
            logs = json.load(f)
    
    logs.append(entry)
    
    with open(cost_log, 'w') as f:
        json.dump(logs, f, indent=2)
    
    return entry

def daily_summary(date=None):
    """Generate daily cost summary"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    memory_dir = Path.home() / "clawd" / "memory"
    cost_log = memory_dir / f"cost-log-{date}.json"
    
    if not cost_log.exists():
        return {
            "date": date,
            "total_cost": 0,
            "total_tokens": 0,
            "calls": 0
        }
    
    with open(cost_log, 'r') as f:
        logs = json.load(f)
    
    total_cost = sum(entry["cost"]["total"] for entry in logs)
    total_tokens = sum(entry["tokens"]["total"] for entry in logs)
    
    # Group by model
    by_model = {}
    for entry in logs:
        model = entry["model"]
        if model not in by_model:
            by_model[model] = {
                "calls": 0,
                "tokens": 0,
                "cost": 0
            }
        by_model[model]["calls"] += 1
        by_model[model]["tokens"] += entry["tokens"]["total"]
        by_model[model]["cost"] += entry["cost"]["total"]
    
    return {
        "date": date,
        "total_cost": round(total_cost, 2),
        "total_tokens": total_tokens,
        "calls": len(logs),
        "by_model": by_model
    }

def monthly_summary(year=None, month=None):
    """Generate monthly cost summary"""
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month
    
    memory_dir = Path.home() / "clawd" / "memory"
    
    # Find all cost logs for the month
    pattern = f"cost-log-{year}-{month:02d}-*.json"
    cost_logs = sorted(memory_dir.glob(pattern))
    
    total_cost = 0
    total_tokens = 0
    total_calls = 0
    by_model = {}
    daily_costs = []
    
    for log_file in cost_logs:
        with open(log_file, 'r') as f:
            logs = json.load(f)
        
        day_cost = sum(entry["cost"]["total"] for entry in logs)
        day_tokens = sum(entry["tokens"]["total"] for entry in logs)
        
        daily_costs.append({
            "date": log_file.stem.replace("cost-log-", ""),
            "cost": round(day_cost, 2),
            "tokens": day_tokens,
            "calls": len(logs)
        })
        
        total_cost += day_cost
        total_tokens += day_tokens
        total_calls += len(logs)
        
        # Aggregate by model
        for entry in logs:
            model = entry["model"]
            if model not in by_model:
                by_model[model] = {
                    "calls": 0,
                    "tokens": 0,
                    "cost": 0
                }
            by_model[model]["calls"] += 1
            by_model[model]["tokens"] += entry["tokens"]["total"]
            by_model[model]["cost"] += entry["cost"]["total"]
    
    return {
        "year": year,
        "month": month,
        "total_cost": round(total_cost, 2),
        "total_tokens": total_tokens,
        "total_calls": total_calls,
        "by_model": by_model,
        "daily": daily_costs,
        "average_daily": round(total_cost / max(len(daily_costs), 1), 2)
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 cost_tracker.py daily [YYYY-MM-DD]")
        print("  python3 cost_tracker.py monthly [YYYY] [MM]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "daily":
        date = sys.argv[2] if len(sys.argv) > 2 else None
        summary = daily_summary(date)
        print(json.dumps(summary, indent=2))
    
    elif command == "monthly":
        year = int(sys.argv[2]) if len(sys.argv) > 2 else None
        month = int(sys.argv[3]) if len(sys.argv) > 3 else None
        summary = monthly_summary(year, month)
        print(json.dumps(summary, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
