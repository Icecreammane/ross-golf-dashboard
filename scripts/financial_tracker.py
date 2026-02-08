#!/usr/bin/env python3
"""
Financial Tracker Daemon
Tracks daily expenses, calculates run rates, projects financial goals
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Paths
WORKSPACE = Path("/Users/clawdbot/clawd")
DATA_FILE = WORKSPACE / "data" / "financial-tracking.json"
LOG_FILE = WORKSPACE / "logs" / "financial-daemon.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Financial goals
FLORIDA_FUND_GOAL = 50000  # $50K target
FINANCIAL_INDEPENDENCE_MONTHLY = 3000  # $3K/month = $36K/year = ~$900K @ 4% rule

class FinancialTracker:
    def __init__(self):
        self.data = self.load_data()
    
    def load_data(self):
        """Load existing financial data or create new structure"""
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            return {
                "florida_fund_balance": 0,
                "total_savings": 0,
                "monthly_revenue": 0,
                "snapshots": [],
                "goals": {
                    "florida_fund": FLORIDA_FUND_GOAL,
                    "fi_monthly_target": FINANCIAL_INDEPENDENCE_MONTHLY
                }
            }
    
    def save_data(self):
        """Save data to JSON file"""
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
        logger.info(f"Data saved to {DATA_FILE}")
    
    def add_snapshot(self, manual_entry=None):
        """
        Add daily snapshot of financial state
        manual_entry: dict with keys: balance, expenses (dict), revenue (optional)
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check if snapshot already exists for today
        existing = [s for s in self.data['snapshots'] if s['date'] == today]
        if existing and not manual_entry:
            logger.info(f"Snapshot already exists for {today}")
            return existing[0]
        
        if manual_entry:
            snapshot = {
                "date": today,
                "timestamp": datetime.now().isoformat(),
                "balance": manual_entry.get('balance', 0),
                "expenses": manual_entry.get('expenses', {
                    "food": 0,
                    "gym": 0,
                    "living": 0,
                    "business": 0,
                    "other": 0
                }),
                "revenue": manual_entry.get('revenue', 0),
                "notes": manual_entry.get('notes', '')
            }
        else:
            # Use last known values if no manual entry
            last_snapshot = self.data['snapshots'][-1] if self.data['snapshots'] else None
            snapshot = {
                "date": today,
                "timestamp": datetime.now().isoformat(),
                "balance": last_snapshot['balance'] if last_snapshot else 0,
                "expenses": {"food": 0, "gym": 0, "living": 0, "business": 0, "other": 0},
                "revenue": 0,
                "notes": "Auto-generated snapshot"
            }
        
        # Remove existing snapshot for today if replacing
        self.data['snapshots'] = [s for s in self.data['snapshots'] if s['date'] != today]
        self.data['snapshots'].append(snapshot)
        
        # Sort by date
        self.data['snapshots'].sort(key=lambda x: x['date'])
        
        self.save_data()
        logger.info(f"Added snapshot for {today}")
        return snapshot
    
    def calculate_metrics(self, days=30):
        """Calculate financial metrics over specified period"""
        if not self.data['snapshots']:
            return None
        
        # Get snapshots for period
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        period_snapshots = [s for s in self.data['snapshots'] if s['date'] >= cutoff_date]
        
        if not period_snapshots:
            return None
        
        # Calculate totals
        total_expenses = sum(
            sum(s['expenses'].values()) for s in period_snapshots
        )
        total_revenue = sum(s.get('revenue', 0) for s in period_snapshots)
        
        # Daily average
        days_actual = len(period_snapshots)
        daily_expenses = total_expenses / days_actual if days_actual > 0 else 0
        daily_revenue = total_revenue / days_actual if days_actual > 0 else 0
        
        # Weekly & monthly projections
        weekly_expenses = daily_expenses * 7
        monthly_expenses = daily_expenses * 30
        monthly_revenue = daily_revenue * 30
        
        # Net monthly
        monthly_net = monthly_revenue - monthly_expenses
        
        # Savings rate
        savings_rate = (monthly_net / monthly_revenue * 100) if monthly_revenue > 0 else 0
        
        # Expense breakdown
        expense_breakdown = {"food": 0, "gym": 0, "living": 0, "business": 0, "other": 0}
        for snapshot in period_snapshots:
            for category, amount in snapshot['expenses'].items():
                expense_breakdown[category] = expense_breakdown.get(category, 0) + amount
        
        # Current balance
        current_balance = period_snapshots[-1]['balance'] if period_snapshots else 0
        
        # Runway months
        runway_months = (current_balance / monthly_expenses) if monthly_expenses > 0 else 999
        
        return {
            "period_days": days_actual,
            "total_expenses": total_expenses,
            "total_revenue": total_revenue,
            "daily_expenses": daily_expenses,
            "daily_revenue": daily_revenue,
            "weekly_expenses": weekly_expenses,
            "monthly_expenses": monthly_expenses,
            "monthly_revenue": monthly_revenue,
            "monthly_net": monthly_net,
            "savings_rate": savings_rate,
            "expense_breakdown": expense_breakdown,
            "current_balance": current_balance,
            "runway_months": runway_months
        }
    
    def project_goals(self):
        """Project when financial goals will be hit"""
        metrics = self.calculate_metrics(days=90)  # Use 90-day average for projections
        
        if not metrics or metrics['monthly_net'] <= 0:
            return {
                "florida_fund": {
                    "current": self.data.get('florida_fund_balance', 0),
                    "target": FLORIDA_FUND_GOAL,
                    "months_to_goal": None,
                    "projected_date": None,
                    "message": "Negative or zero savings rate - goal not achievable at current pace"
                },
                "financial_independence": {
                    "current_monthly": metrics['monthly_net'] if metrics else 0,
                    "target_monthly": FINANCIAL_INDEPENDENCE_MONTHLY,
                    "months_to_goal": None,
                    "projected_date": None,
                    "message": "Negative or zero savings rate - goal not achievable at current pace"
                }
            }
        
        # Florida Fund projection
        florida_current = self.data.get('florida_fund_balance', 0)
        florida_remaining = FLORIDA_FUND_GOAL - florida_current
        florida_months = florida_remaining / metrics['monthly_net'] if metrics['monthly_net'] > 0 else None
        florida_date = (datetime.now() + timedelta(days=florida_months * 30)).strftime('%Y-%m-%d') if florida_months else None
        
        # Financial Independence projection (need ~$900K @ 4% rule for $3K/month)
        fi_target = FINANCIAL_INDEPENDENCE_MONTHLY * 12 / 0.04  # $900K
        fi_current = self.data.get('total_savings', 0)
        fi_remaining = fi_target - fi_current
        fi_months = fi_remaining / metrics['monthly_net'] if metrics['monthly_net'] > 0 else None
        fi_date = (datetime.now() + timedelta(days=fi_months * 30)).strftime('%Y-%m-%d') if fi_months else None
        
        return {
            "florida_fund": {
                "current": florida_current,
                "target": FLORIDA_FUND_GOAL,
                "remaining": florida_remaining,
                "months_to_goal": round(florida_months, 1) if florida_months else None,
                "projected_date": florida_date,
                "message": f"At current pace: {florida_months:.1f} months ({florida_date})" if florida_months else "Goal already met!"
            },
            "financial_independence": {
                "current": fi_current,
                "target": fi_target,
                "remaining": fi_remaining,
                "target_monthly": FINANCIAL_INDEPENDENCE_MONTHLY,
                "current_monthly_net": metrics['monthly_net'],
                "months_to_goal": round(fi_months, 1) if fi_months else None,
                "projected_date": fi_date,
                "message": f"At current pace: {fi_months:.1f} months ({fi_date})" if fi_months else "Financially independent!"
            }
        }
    
    def generate_report(self):
        """Generate comprehensive financial report"""
        metrics_30 = self.calculate_metrics(days=30)
        metrics_7 = self.calculate_metrics(days=7)
        projections = self.project_goals()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "metrics": {
                "last_7_days": metrics_7,
                "last_30_days": metrics_30
            },
            "projections": projections,
            "total_snapshots": len(self.data['snapshots'])
        }
        
        return report
    
    def print_report(self):
        """Print human-readable report"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("FINANCIAL TRACKER REPORT")
        print("="*60)
        print(f"Generated: {report['generated_at']}")
        print()
        
        if report['metrics']['last_30_days']:
            m30 = report['metrics']['last_30_days']
            print("📊 LAST 30 DAYS:")
            print(f"  Daily Expenses:   ${m30['daily_expenses']:.2f}")
            print(f"  Weekly Expenses:  ${m30['weekly_expenses']:.2f}")
            print(f"  Monthly Expenses: ${m30['monthly_expenses']:.2f}")
            print(f"  Monthly Revenue:  ${m30['monthly_revenue']:.2f}")
            print(f"  Monthly Net:      ${m30['monthly_net']:.2f}")
            print(f"  Savings Rate:     {m30['savings_rate']:.1f}%")
            print(f"  Current Balance:  ${m30['current_balance']:.2f}")
            print(f"  Runway:           {m30['runway_months']:.1f} months")
            print()
            print("  Expense Breakdown:")
            for category, amount in m30['expense_breakdown'].items():
                pct = (amount / m30['total_expenses'] * 100) if m30['total_expenses'] > 0 else 0
                print(f"    {category.capitalize():12} ${amount:>8.2f} ({pct:>5.1f}%)")
        
        print()
        print("🎯 GOAL PROJECTIONS:")
        
        florida = report['projections']['florida_fund']
        print(f"\n  Florida Fund (${FLORIDA_FUND_GOAL:,} goal):")
        print(f"    Current: ${florida['current']:,.2f}")
        if florida['months_to_goal']:
            print(f"    Time to Goal: {florida['months_to_goal']} months")
            print(f"    Target Date: {florida['projected_date']}")
        else:
            print(f"    {florida['message']}")
        
        fi = report['projections']['financial_independence']
        print(f"\n  Financial Independence (${FINANCIAL_INDEPENDENCE_MONTHLY:,}/mo target):")
        print(f"    Current Savings: ${fi['current']:,.2f}")
        print(f"    Target Savings: ${fi['target']:,.2f} (4% rule)")
        if fi['months_to_goal']:
            print(f"    Time to Goal: {fi['months_to_goal']} months ({fi['months_to_goal']/12:.1f} years)")
            print(f"    Target Date: {fi['projected_date']}")
        else:
            print(f"    {fi['message']}")
        
        print("\n" + "="*60 + "\n")


def manual_entry():
    """Interactive manual entry for daily financial data"""
    print("\n💰 FINANCIAL TRACKER - Manual Entry")
    print("="*50)
    
    tracker = FinancialTracker()
    
    # Get current balance
    balance = float(input("Current account balance: $"))
    
    # Get expenses by category
    print("\nDaily Expenses:")
    expenses = {}
    expenses['food'] = float(input("  Food: $"))
    expenses['gym'] = float(input("  Gym: $"))
    expenses['living'] = float(input("  Living (rent, utilities, etc.): $"))
    expenses['business'] = float(input("  Business: $"))
    expenses['other'] = float(input("  Other: $"))
    
    # Get revenue
    revenue = float(input("\nRevenue today: $"))
    
    # Optional notes
    notes = input("Notes (optional): ")
    
    # Update Florida fund and total savings
    florida_fund = float(input("\nFlorida Fund balance: $"))
    total_savings = float(input("Total Savings (all accounts): $"))
    
    tracker.data['florida_fund_balance'] = florida_fund
    tracker.data['total_savings'] = total_savings
    
    # Add snapshot
    entry = {
        'balance': balance,
        'expenses': expenses,
        'revenue': revenue,
        'notes': notes
    }
    
    tracker.add_snapshot(manual_entry=entry)
    
    print("\n✅ Entry saved!")
    
    # Show quick summary
    total_expenses = sum(expenses.values())
    net = revenue - total_expenses
    print(f"\nToday's Summary:")
    print(f"  Expenses: ${total_expenses:.2f}")
    print(f"  Revenue:  ${revenue:.2f}")
    print(f"  Net:      ${net:.2f}")
    
    return tracker


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "entry":
            tracker = manual_entry()
            tracker.print_report()
        
        elif command == "report":
            tracker = FinancialTracker()
            tracker.print_report()
        
        elif command == "snapshot":
            tracker = FinancialTracker()
            tracker.add_snapshot()
            print("✅ Snapshot added")
        
        elif command == "test":
            print("Running test calculations...")
            from test_financial_tracker import run_tests
            run_tests()
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: financial_tracker.py [entry|report|snapshot|test]")
            sys.exit(1)
    else:
        # Default: add snapshot and log
        logger.info("Running daily financial tracker daemon")
        tracker = FinancialTracker()
        tracker.add_snapshot()
        report = tracker.generate_report()
        logger.info(f"Report generated: {json.dumps(report, indent=2)}")


if __name__ == "__main__":
    main()
