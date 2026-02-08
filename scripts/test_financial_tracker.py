#!/usr/bin/env python3
"""
Test suite for Financial Tracker
Validates calculations and projections
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from financial_tracker import FinancialTracker, FLORIDA_FUND_GOAL, FINANCIAL_INDEPENDENCE_MONTHLY

def create_test_data():
    """Create test financial data"""
    test_data = {
        "florida_fund_balance": 15000,
        "total_savings": 50000,
        "monthly_revenue": 5000,
        "snapshots": [],
        "goals": {
            "florida_fund": FLORIDA_FUND_GOAL,
            "fi_monthly_target": FINANCIAL_INDEPENDENCE_MONTHLY
        }
    }
    
    # Generate 30 days of test data
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        snapshot = {
            "date": date.strftime('%Y-%m-%d'),
            "timestamp": date.isoformat(),
            "balance": 10000 + (i * 50),  # Growing balance
            "expenses": {
                "food": 25 + (i % 5),  # $25-30/day
                "gym": 5 if i % 7 == 0 else 0,  # ~$5/week
                "living": 40 if i % 7 == 0 else 0,  # ~$40/week = ~$160/month rent portion
                "business": 10 + (i % 3),  # $10-12/day
                "other": 5 + (i % 7)  # $5-12/day
            },
            "revenue": 150 + (i % 30) * 5,  # $150-300/day variable
            "notes": f"Test data day {i+1}"
        }
        test_data['snapshots'].append(snapshot)
    
    return test_data


def test_metric_calculations():
    """Test expense and revenue calculations"""
    print("\n" + "="*60)
    print("TEST 1: Metric Calculations")
    print("="*60)
    
    # Create tracker with test data
    tracker = FinancialTracker()
    tracker.data = create_test_data()
    
    # Calculate 30-day metrics
    metrics = tracker.calculate_metrics(days=30)
    
    print(f"\n✓ Calculated metrics for {metrics['period_days']} days")
    print(f"  Total Expenses: ${metrics['total_expenses']:.2f}")
    print(f"  Total Revenue: ${metrics['total_revenue']:.2f}")
    print(f"  Daily Expenses: ${metrics['daily_expenses']:.2f}")
    print(f"  Daily Revenue: ${metrics['daily_revenue']:.2f}")
    print(f"  Monthly Expenses: ${metrics['monthly_expenses']:.2f}")
    print(f"  Monthly Revenue: ${metrics['monthly_revenue']:.2f}")
    print(f"  Monthly Net: ${metrics['monthly_net']:.2f}")
    print(f"  Savings Rate: {metrics['savings_rate']:.1f}%")
    
    # Validate calculations
    assert metrics['period_days'] == 30, "Should have 30 days of data"
    assert metrics['total_expenses'] > 0, "Should have expenses"
    assert metrics['total_revenue'] > 0, "Should have revenue"
    assert metrics['monthly_net'] == metrics['monthly_revenue'] - metrics['monthly_expenses'], "Net calculation incorrect"
    assert abs(metrics['savings_rate'] - (metrics['monthly_net'] / metrics['monthly_revenue'] * 100)) < 0.01, "Savings rate incorrect"
    
    print("\n✅ All metric calculations passed!")
    return True


def test_expense_breakdown():
    """Test expense categorization"""
    print("\n" + "="*60)
    print("TEST 2: Expense Breakdown")
    print("="*60)
    
    tracker = FinancialTracker()
    tracker.data = create_test_data()
    
    metrics = tracker.calculate_metrics(days=30)
    breakdown = metrics['expense_breakdown']
    
    print("\nExpense Categories:")
    total = sum(breakdown.values())
    for category, amount in breakdown.items():
        pct = (amount / total * 100) if total > 0 else 0
        print(f"  {category.capitalize():12} ${amount:>8.2f} ({pct:>5.1f}%)")
    
    # Validate breakdown
    assert sum(breakdown.values()) == metrics['total_expenses'], "Breakdown doesn't match total expenses"
    assert all(amount >= 0 for amount in breakdown.values()), "Negative expenses found"
    
    print("\n✅ Expense breakdown validation passed!")
    return True


def test_runway_calculation():
    """Test runway months calculation"""
    print("\n" + "="*60)
    print("TEST 3: Runway Calculation")
    print("="*60)
    
    tracker = FinancialTracker()
    tracker.data = create_test_data()
    
    metrics = tracker.calculate_metrics(days=30)
    
    expected_runway = metrics['current_balance'] / metrics['monthly_expenses']
    
    print(f"\n  Current Balance: ${metrics['current_balance']:.2f}")
    print(f"  Monthly Expenses: ${metrics['monthly_expenses']:.2f}")
    print(f"  Runway: {metrics['runway_months']:.1f} months")
    
    assert abs(metrics['runway_months'] - expected_runway) < 0.01, "Runway calculation incorrect"
    
    print("\n✅ Runway calculation passed!")
    return True


def test_florida_fund_projection():
    """Test Florida fund goal projection"""
    print("\n" + "="*60)
    print("TEST 4: Florida Fund Projection")
    print("="*60)
    
    tracker = FinancialTracker()
    tracker.data = create_test_data()
    
    projections = tracker.project_goals()
    florida = projections['florida_fund']
    
    print(f"\n  Current: ${florida['current']:,.2f}")
    print(f"  Target: ${florida['target']:,.2f}")
    print(f"  Remaining: ${florida['remaining']:,.2f}")
    
    if florida['months_to_goal']:
        print(f"  Months to Goal: {florida['months_to_goal']}")
        print(f"  Projected Date: {florida['projected_date']}")
        
        # Validate calculation
        metrics = tracker.calculate_metrics(days=90)
        expected_months = florida['remaining'] / metrics['monthly_net']
        assert abs(florida['months_to_goal'] - expected_months) < 0.1, "Florida fund projection incorrect"
    else:
        print(f"  {florida['message']}")
    
    print("\n✅ Florida fund projection passed!")
    return True


def test_fi_projection():
    """Test financial independence projection"""
    print("\n" + "="*60)
    print("TEST 5: Financial Independence Projection")
    print("="*60)
    
    tracker = FinancialTracker()
    tracker.data = create_test_data()
    
    projections = tracker.project_goals()
    fi = projections['financial_independence']
    
    print(f"\n  Current Savings: ${fi['current']:,.2f}")
    print(f"  Target Savings: ${fi['target']:,.2f}")
    print(f"  Target Monthly: ${fi['target_monthly']:,.2f}")
    
    if fi['months_to_goal']:
        print(f"  Months to Goal: {fi['months_to_goal']} ({fi['months_to_goal']/12:.1f} years)")
        print(f"  Projected Date: {fi['projected_date']}")
        
        # Validate calculation
        metrics = tracker.calculate_metrics(days=90)
        expected_months = fi['remaining'] / metrics['monthly_net']
        assert abs(fi['months_to_goal'] - expected_months) < 0.1, "FI projection incorrect"
    else:
        print(f"  {fi['message']}")
    
    print("\n✅ Financial independence projection passed!")
    return True


def test_snapshot_creation():
    """Test daily snapshot creation and storage"""
    print("\n" + "="*60)
    print("TEST 6: Snapshot Creation")
    print("="*60)
    
    tracker = FinancialTracker()
    tracker.data = create_test_data()
    
    initial_count = len(tracker.data['snapshots'])
    
    # Add manual snapshot
    manual_data = {
        'balance': 12000,
        'expenses': {
            'food': 30,
            'gym': 0,
            'living': 50,
            'business': 20,
            'other': 10
        },
        'revenue': 200,
        'notes': 'Test snapshot'
    }
    
    snapshot = tracker.add_snapshot(manual_entry=manual_data)
    
    print(f"\n  Initial snapshots: {initial_count}")
    print(f"  After add: {len(tracker.data['snapshots'])}")
    print(f"  Snapshot date: {snapshot['date']}")
    print(f"  Total expenses: ${sum(snapshot['expenses'].values()):.2f}")
    
    assert snapshot['balance'] == manual_data['balance'], "Balance not stored correctly"
    assert snapshot['revenue'] == manual_data['revenue'], "Revenue not stored correctly"
    assert sum(snapshot['expenses'].values()) == sum(manual_data['expenses'].values()), "Expenses not stored correctly"
    
    print("\n✅ Snapshot creation passed!")
    return True


def test_full_report():
    """Test full report generation"""
    print("\n" + "="*60)
    print("TEST 7: Full Report Generation")
    print("="*60)
    
    tracker = FinancialTracker()
    tracker.data = create_test_data()
    
    report = tracker.generate_report()
    
    print(f"\n  Generated at: {report['generated_at']}")
    print(f"  Total snapshots: {report['total_snapshots']}")
    print(f"  Has 7-day metrics: {report['metrics']['last_7_days'] is not None}")
    print(f"  Has 30-day metrics: {report['metrics']['last_30_days'] is not None}")
    print(f"  Has projections: {report['projections'] is not None}")
    
    assert 'generated_at' in report, "Missing timestamp"
    assert 'metrics' in report, "Missing metrics"
    assert 'projections' in report, "Missing projections"
    assert report['total_snapshots'] > 0, "No snapshots in report"
    
    print("\n✅ Full report generation passed!")
    return True


def run_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print(" 🧪 FINANCIAL TRACKER TEST SUITE")
    print("="*70)
    
    tests = [
        test_metric_calculations,
        test_expense_breakdown,
        test_runway_calculation,
        test_florida_fund_projection,
        test_fi_projection,
        test_snapshot_creation,
        test_full_report
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"\n❌ Test failed: {e}")
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
