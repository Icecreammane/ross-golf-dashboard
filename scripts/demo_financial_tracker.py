#!/usr/bin/env python3
"""
Demo script showing financial tracker in action
Creates sample data and generates report
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from financial_tracker import FinancialTracker

def demo():
    print("\n" + "="*70)
    print(" 🎬 FINANCIAL TRACKER DEMO")
    print("="*70)
    print("\nThis demo shows how the financial tracker works with sample data.")
    print()
    
    # Initialize tracker
    tracker = FinancialTracker()
    
    # Clear existing test data
    tracker.data = {
        "florida_fund_balance": 18500,
        "total_savings": 62000,
        "monthly_revenue": 6800,
        "snapshots": [],
        "goals": {
            "florida_fund": 50000,
            "fi_monthly_target": 3000
        }
    }
    
    print("📝 Adding sample entry...")
    print()
    
    # Sample entry for today
    sample_entry = {
        'balance': 12500,
        'expenses': {
            'food': 45.32,      # Groceries
            'gym': 0,            # No gym today
            'living': 55.00,     # Utilities portion
            'business': 15.99,   # ChatGPT subscription
            'other': 8.50        # Coffee
        },
        'revenue': 250.00,      # Client payment
        'notes': 'Good day - client paid invoice'
    }
    
    print("Today's Data:")
    print(f"  Balance: ${sample_entry['balance']:,.2f}")
    print(f"  Expenses:")
    for category, amount in sample_entry['expenses'].items():
        print(f"    {category.capitalize():12} ${amount:>7.2f}")
    print(f"  Revenue: ${sample_entry['revenue']:.2f}")
    print(f"  Notes: {sample_entry['notes']}")
    print()
    
    # Add the entry
    tracker.add_snapshot(manual_entry=sample_entry)
    
    total_expenses = sum(sample_entry['expenses'].values())
    net = sample_entry['revenue'] - total_expenses
    
    print(f"✅ Entry saved!")
    print()
    print(f"Quick Summary:")
    print(f"  Total Expenses: ${total_expenses:.2f}")
    print(f"  Revenue:        ${sample_entry['revenue']:.2f}")
    print(f"  Net Today:      ${net:.2f}")
    print()
    
    # Update goals
    tracker.data['florida_fund_balance'] = 18500
    tracker.data['total_savings'] = 62000
    tracker.save_data()
    
    print("=" * 70)
    print()
    print("Now generating full report (would use 30-day history)...")
    print()
    
    # For demo purposes, show what the report would look like
    print("📊 Note: Report needs 30 days of data for accurate calculations.")
    print("    After daily use, you'll see:")
    print("    - 30-day expense averages")
    print("    - Savings rate trends")
    print("    - Runway calculations")
    print("    - Goal projections based on your pace")
    print()
    
    # Show goal status
    print("🎯 CURRENT GOAL STATUS:")
    print()
    print(f"  Florida Fund:")
    print(f"    Current: ${tracker.data['florida_fund_balance']:,.2f}")
    print(f"    Target:  ${tracker.data['goals']['florida_fund']:,.2f}")
    remaining = tracker.data['goals']['florida_fund'] - tracker.data['florida_fund_balance']
    print(f"    Remaining: ${remaining:,.2f}")
    print()
    print(f"  Financial Independence:")
    print(f"    Current Savings: ${tracker.data['total_savings']:,.2f}")
    fi_target = tracker.data['goals']['fi_monthly_target'] * 12 / 0.04
    print(f"    Target Savings: ${fi_target:,.2f} (4% rule)")
    fi_remaining = fi_target - tracker.data['total_savings']
    print(f"    Remaining: ${fi_remaining:,.2f}")
    print()
    
    print("=" * 70)
    print()
    print("✨ Demo complete!")
    print()
    print("To use with real data:")
    print("  bash ~/clawd/scripts/finance_entry.sh")
    print()
    print("To view reports:")
    print("  bash ~/clawd/scripts/finance_report.sh")
    print()


if __name__ == "__main__":
    demo()
