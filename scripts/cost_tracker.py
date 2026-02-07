#!/usr/bin/env python3
"""
cost_tracker.py - Track API costs for sub-agent builds

Tracks:
- Tokens per sub-agent (input + output)
- Cost per build
- Daily/weekly totals
- Budget alerts

Usage:
    python3 cost_tracker.py --log <session_id> <input_tokens> <output_tokens>
    python3 cost_tracker.py --today
    python3 cost_tracker.py --week
    python3 cost_tracker.py --report
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

WORKSPACE = Path.home() / "clawd"
COST_DATA_FILE = WORKSPACE / "cost-data.json"
COST_REPORT_FILE = WORKSPACE / "cost-report.json"

# Pricing (as of 2024 - update as needed)
# Claude Sonnet 4.5 pricing
COST_PER_INPUT_TOKEN = 0.000003  # $3 per 1M input tokens
COST_PER_OUTPUT_TOKEN = 0.000015  # $15 per 1M output tokens

# Budget thresholds
DAILY_BUDGET = 20.00  # $20/day
WEEKLY_BUDGET = 100.00  # $100/week
MONTHLY_BUDGET = 400.00  # $400/month


def load_cost_data() -> dict:
    """Load cost data from file"""
    if not COST_DATA_FILE.exists():
        return {
            "builds": {},
            "daily_totals": {},
            "weekly_totals": {},
            "monthly_totals": {}
        }
    
    try:
        with open(COST_DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {
            "builds": {},
            "daily_totals": {},
            "weekly_totals": {},
            "monthly_totals": {}
        }


def save_cost_data(data: dict):
    """Save cost data to file"""
    with open(COST_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def log_build_cost(
    session_id: str,
    input_tokens: int,
    output_tokens: int,
    task_name: str = "Unknown Task",
    model: str = "claude-sonnet-4.5"
):
    """
    Log costs for a build.
    
    Args:
        session_id: Sub-agent session ID
        input_tokens: Number of input tokens used
        output_tokens: Number of output tokens used
        task_name: Name of the task being built
        model: Model name used
    """
    data = load_cost_data()
    
    # Calculate cost
    input_cost = input_tokens * COST_PER_INPUT_TOKEN
    output_cost = output_tokens * COST_PER_OUTPUT_TOKEN
    total_cost = input_cost + output_cost
    
    timestamp = datetime.now()
    date_key = timestamp.strftime("%Y-%m-%d")
    week_key = timestamp.strftime("%Y-W%W")
    month_key = timestamp.strftime("%Y-%m")
    
    # Log build
    data["builds"][session_id] = {
        "session_id": session_id,
        "task_name": task_name,
        "model": model,
        "timestamp": timestamp.isoformat(),
        "date": date_key,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost": round(input_cost, 4),
        "output_cost": round(output_cost, 4),
        "total_cost": round(total_cost, 4)
    }
    
    # Update daily total
    if date_key not in data["daily_totals"]:
        data["daily_totals"][date_key] = {
            "date": date_key,
            "builds": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }
    
    data["daily_totals"][date_key]["builds"] += 1
    data["daily_totals"][date_key]["total_tokens"] += input_tokens + output_tokens
    data["daily_totals"][date_key]["total_cost"] = round(
        data["daily_totals"][date_key]["total_cost"] + total_cost, 4
    )
    
    # Update weekly total
    if week_key not in data["weekly_totals"]:
        data["weekly_totals"][week_key] = {
            "week": week_key,
            "builds": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }
    
    data["weekly_totals"][week_key]["builds"] += 1
    data["weekly_totals"][week_key]["total_tokens"] += input_tokens + output_tokens
    data["weekly_totals"][week_key]["total_cost"] = round(
        data["weekly_totals"][week_key]["total_cost"] + total_cost, 4
    )
    
    # Update monthly total
    if month_key not in data["monthly_totals"]:
        data["monthly_totals"][month_key] = {
            "month": month_key,
            "builds": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }
    
    data["monthly_totals"][month_key]["builds"] += 1
    data["monthly_totals"][month_key]["total_tokens"] += input_tokens + output_tokens
    data["monthly_totals"][month_key]["total_cost"] = round(
        data["monthly_totals"][month_key]["total_cost"] + total_cost, 4
    )
    
    save_cost_data(data)
    
    # Check budget alerts
    check_budget_alerts(data, date_key, week_key, month_key)
    
    print(f"💰 Cost logged: {session_id}")
    print(f"   Tokens: {input_tokens:,} in + {output_tokens:,} out = {input_tokens + output_tokens:,} total")
    print(f"   Cost: ${total_cost:.4f}")
    
    return total_cost


def check_budget_alerts(data: dict, date_key: str, week_key: str, month_key: str):
    """Check if we're over budget and alert"""
    alerts = []
    
    # Daily check
    if date_key in data["daily_totals"]:
        daily_cost = data["daily_totals"][date_key]["total_cost"]
        daily_percent = (daily_cost / DAILY_BUDGET) * 100
        
        if daily_cost > DAILY_BUDGET:
            alerts.append(f"🚨 OVER DAILY BUDGET: ${daily_cost:.2f} / ${DAILY_BUDGET:.2f} ({daily_percent:.0f}%)")
        elif daily_percent > 80:
            alerts.append(f"⚠️  Daily budget warning: ${daily_cost:.2f} / ${DAILY_BUDGET:.2f} ({daily_percent:.0f}%)")
    
    # Weekly check
    if week_key in data["weekly_totals"]:
        weekly_cost = data["weekly_totals"][week_key]["total_cost"]
        weekly_percent = (weekly_cost / WEEKLY_BUDGET) * 100
        
        if weekly_cost > WEEKLY_BUDGET:
            alerts.append(f"🚨 OVER WEEKLY BUDGET: ${weekly_cost:.2f} / ${WEEKLY_BUDGET:.2f} ({weekly_percent:.0f}%)")
        elif weekly_percent > 80:
            alerts.append(f"⚠️  Weekly budget warning: ${weekly_cost:.2f} / ${WEEKLY_BUDGET:.2f} ({weekly_percent:.0f}%)")
    
    # Monthly check
    if month_key in data["monthly_totals"]:
        monthly_cost = data["monthly_totals"][month_key]["total_cost"]
        monthly_percent = (monthly_cost / MONTHLY_BUDGET) * 100
        
        if monthly_cost > MONTHLY_BUDGET:
            alerts.append(f"🚨 OVER MONTHLY BUDGET: ${monthly_cost:.2f} / ${MONTHLY_BUDGET:.2f} ({monthly_percent:.0f}%)")
        elif monthly_percent > 80:
            alerts.append(f"⚠️  Monthly budget warning: ${monthly_cost:.2f} / ${MONTHLY_BUDGET:.2f} ({monthly_percent:.0f}%)")
    
    if alerts:
        print("\n" + "\n".join(alerts) + "\n")


def show_today():
    """Show today's costs"""
    data = load_cost_data()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if today not in data["daily_totals"]:
        print(f"📊 Today ({today}): No builds yet")
        return
    
    daily = data["daily_totals"][today]
    percent = (daily["total_cost"] / DAILY_BUDGET) * 100
    
    print(f"\n📊 Today's Costs ({today})")
    print(f"   Builds: {daily['builds']}")
    print(f"   Tokens: {daily['total_tokens']:,}")
    print(f"   Cost: ${daily['total_cost']:.2f} / ${DAILY_BUDGET:.2f} budget ({percent:.1f}%)")
    
    # Show progress bar
    bar_width = 30
    filled = int(bar_width * min(percent / 100, 1.0))
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"   [{bar}]")
    
    if percent > 100:
        print(f"   🚨 OVER BUDGET by ${daily['total_cost'] - DAILY_BUDGET:.2f}")
    elif percent > 80:
        remaining = DAILY_BUDGET - daily["total_cost"]
        print(f"   ⚠️  ${remaining:.2f} remaining today")


def show_week():
    """Show this week's costs"""
    data = load_cost_data()
    week = datetime.now().strftime("%Y-W%W")
    
    if week not in data["weekly_totals"]:
        print(f"📊 This week ({week}): No builds yet")
        return
    
    weekly = data["weekly_totals"][week]
    percent = (weekly["total_cost"] / WEEKLY_BUDGET) * 100
    
    print(f"\n📊 This Week's Costs ({week})")
    print(f"   Builds: {weekly['builds']}")
    print(f"   Tokens: {weekly['total_tokens']:,}")
    print(f"   Cost: ${weekly['total_cost']:.2f} / ${WEEKLY_BUDGET:.2f} budget ({percent:.1f}%)")
    
    # Show progress bar
    bar_width = 30
    filled = int(bar_width * min(percent / 100, 1.0))
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"   [{bar}]")


def generate_report():
    """Generate cost report JSON for dashboard"""
    data = load_cost_data()
    today = datetime.now().strftime("%Y-%m-%d")
    week = datetime.now().strftime("%Y-W%W")
    month = datetime.now().strftime("%Y-%m")
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "today": data["daily_totals"].get(today, {
            "date": today,
            "builds": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }),
        "this_week": data["weekly_totals"].get(week, {
            "week": week,
            "builds": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }),
        "this_month": data["monthly_totals"].get(month, {
            "month": month,
            "builds": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }),
        "budgets": {
            "daily": DAILY_BUDGET,
            "weekly": WEEKLY_BUDGET,
            "monthly": MONTHLY_BUDGET
        },
        "recent_builds": []
    }
    
    # Add last 10 builds
    builds = list(data["builds"].values())
    builds.sort(key=lambda x: x["timestamp"], reverse=True)
    report["recent_builds"] = builds[:10]
    
    # Save report
    with open(COST_REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Cost report generated: {COST_REPORT_FILE}")
    
    return report


def main():
    parser = argparse.ArgumentParser(description="Track API costs for sub-agent builds")
    parser.add_argument("--log", nargs=4, metavar=("SESSION_ID", "INPUT_TOKENS", "OUTPUT_TOKENS", "TASK_NAME"),
                       help="Log a build's cost")
    parser.add_argument("--today", action="store_true", help="Show today's costs")
    parser.add_argument("--week", action="store_true", help="Show this week's costs")
    parser.add_argument("--report", action="store_true", help="Generate cost report JSON")
    
    args = parser.parse_args()
    
    if args.log:
        session_id, input_tokens, output_tokens, task_name = args.log
        log_build_cost(session_id, int(input_tokens), int(output_tokens), task_name)
    elif args.today:
        show_today()
    elif args.week:
        show_week()
    elif args.report:
        generate_report()
    else:
        # Default: show today and generate report
        show_today()
        generate_report()


if __name__ == "__main__":
    main()
