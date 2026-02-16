#!/usr/bin/env python3
"""
Cost Dashboard - Show real-time savings from multi-tier intelligence routing
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from local_router import LocalRouter


def format_currency(amount: float) -> str:
    """Format currency with color"""
    if amount > 0:
        return f"${amount:.2f}"
    return f"${abs(amount):.2f}"


def show_dashboard(days: int = 7):
    """Display cost savings dashboard"""
    router = LocalRouter()
    
    print("\n" + "="*70)
    print("💰 MULTI-TIER INTELLIGENCE COST DASHBOARD")
    print("="*70 + "\n")
    
    # Get stats for different time periods
    today_stats = router.get_stats(days=1)
    week_stats = router.get_stats(days=7)
    month_stats = router.get_stats(days=30)
    
    # Today's summary
    print("📊 TODAY'S SUMMARY")
    print("-" * 70)
    print(f"  Total Tasks:        {today_stats['total_tasks']}")
    print(f"  Local (Ollama):     {today_stats['ollama_tasks']} ({today_stats['local_percentage']:.1f}%)")
    print(f"  Sonnet:             {today_stats['sonnet_tasks']}")
    print(f"  Cost Spent:         {format_currency(today_stats['total_cost'])}")
    print(f"  💚 Amount Saved:    {format_currency(today_stats['total_saved'])}")
    
    if today_stats['total_saved'] > 0:
        old_cost = today_stats['total_cost'] + today_stats['total_saved']
        reduction = (today_stats['total_saved'] / old_cost * 100) if old_cost > 0 else 0
        print(f"  📉 Cost Reduction:  {reduction:.1f}%")
    print()
    
    # This week
    print("📅 THIS WEEK (7 days)")
    print("-" * 70)
    print(f"  Total Tasks:        {week_stats['total_tasks']}")
    print(f"  Local (Ollama):     {week_stats['ollama_tasks']} ({week_stats['local_percentage']:.1f}%)")
    print(f"  Sonnet:             {week_stats['sonnet_tasks']}")
    print(f"  Cost Spent:         {format_currency(week_stats['total_cost'])}")
    print(f"  💚 Amount Saved:    {format_currency(week_stats['total_saved'])}")
    
    if week_stats['total_saved'] > 0:
        old_cost = week_stats['total_cost'] + week_stats['total_saved']
        reduction = (week_stats['total_saved'] / old_cost * 100) if old_cost > 0 else 0
        print(f"  📉 Cost Reduction:  {reduction:.1f}%")
    print()
    
    # This month
    print("📆 THIS MONTH (30 days)")
    print("-" * 70)
    print(f"  Total Tasks:        {month_stats['total_tasks']}")
    print(f"  Local (Ollama):     {month_stats['ollama_tasks']} ({month_stats['local_percentage']:.1f}%)")
    print(f"  Sonnet:             {month_stats['sonnet_tasks']}")
    print(f"  Cost Spent:         {format_currency(month_stats['total_cost'])}")
    print(f"  💚 Amount Saved:    {format_currency(month_stats['total_saved'])}")
    
    if month_stats['total_saved'] > 0:
        old_cost = month_stats['total_cost'] + month_stats['total_saved']
        reduction = (month_stats['total_saved'] / old_cost * 100) if old_cost > 0 else 0
        print(f"  📉 Cost Reduction:  {reduction:.1f}%")
    print()
    
    # Daily breakdown (last 7 days)
    print("📈 DAILY BREAKDOWN (Last 7 days)")
    print("-" * 70)
    
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    dates.reverse()  # Oldest first
    
    for date in dates:
        if date in week_stats['daily_breakdown']:
            day = week_stats['daily_breakdown'][date]
            local_pct = (day['ollama_tasks'] / day['total_tasks'] * 100) if day['total_tasks'] > 0 else 0
            print(f"  {date}:  {day['total_tasks']:2d} tasks | {day['ollama_tasks']:2d} local ({local_pct:4.1f}%) | Saved: {format_currency(day['total_saved'])}")
    
    print()
    
    # Projections
    print("🔮 PROJECTIONS")
    print("-" * 70)
    
    if today_stats['total_tasks'] > 0:
        # Project daily cost if we continued with all Sonnet
        old_daily_cost = today_stats['total_cost'] + today_stats['total_saved']
        new_daily_cost = today_stats['total_cost']
        
        print(f"  Without multi-tier:  ~${old_daily_cost * 30:.2f}/month (${old_daily_cost:.2f}/day)")
        print(f"  With multi-tier:     ~${new_daily_cost * 30:.2f}/month (${new_daily_cost:.2f}/day)")
        print(f"  💰 Monthly Savings:  ~${today_stats['total_saved'] * 30:.2f}")
    
    print("\n" + "="*70)
    print("✨ Multi-tier intelligence routing keeps Jarvis affordable!")
    print("="*70 + "\n")


def show_compact(period: str = "today"):
    """Show compact stats for a specific period"""
    router = LocalRouter()
    
    days_map = {"today": 1, "week": 7, "month": 30}
    days = days_map.get(period, 1)
    
    stats = router.get_stats(days=days)
    
    print(f"\n💰 {period.upper()} - Intelligence Routing Stats")
    print(f"   {stats['total_tasks']} tasks: {stats['ollama_tasks']} local ({stats['local_percentage']:.1f}%), {stats['sonnet_tasks']} Sonnet")
    print(f"   Spent: ${stats['total_cost']:.4f} | Saved: ${stats['total_saved']:.4f}")
    
    if stats['total_saved'] > 0:
        old_cost = stats['total_cost'] + stats['total_saved']
        reduction = (stats['total_saved'] / old_cost * 100) if old_cost > 0 else 0
        print(f"   📉 Cost reduced by {reduction:.1f}%")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Cost Dashboard")
    parser.add_argument("--period", choices=["today", "week", "month"], help="Show compact stats for period")
    parser.add_argument("--full", action="store_true", help="Show full dashboard")
    
    args = parser.parse_args()
    
    if args.period:
        show_compact(args.period)
    else:
        show_dashboard()


if __name__ == "__main__":
    main()
