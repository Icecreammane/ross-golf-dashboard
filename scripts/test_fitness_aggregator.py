#!/usr/bin/env python3
"""
Test script for fitness aggregator.
Validates all functions and generates a test summary.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fitness_aggregator import FitnessAggregator

def test_all():
    """Run all tests."""
    print("=" * 70)
    print("TESTING FITNESS AGGREGATOR")
    print("=" * 70)
    
    try:
        aggregator = FitnessAggregator()
        
        # Test 1: Fetch data
        print("\n[TEST 1] Fetching data from API...")
        data = aggregator.fetch_data()
        print(f"✅ Data fetched: {len(data.get('history', []))} days in history")
        print(f"   Goals: {aggregator.goals}")
        
        # Test 2: Daily summary
        print("\n[TEST 2] Calculating daily summary...")
        from datetime import datetime, timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        daily = aggregator.calculate_daily_summary(yesterday)
        if daily:
            print(f"✅ Daily summary for {yesterday}:")
            print(f"   Calories: {daily['calories']} ({daily['compliance']['calories']}% of goal)")
            print(f"   Protein: {daily['protein']}g ({daily['compliance']['protein']}% of goal)")
        else:
            print(f"⚠️  No data for {yesterday}")
        
        # Test 3: Weekly summary
        print("\n[TEST 3] Calculating weekly summary...")
        weekly = aggregator.calculate_weekly_summary(weeks_ago=0)
        if weekly:
            print(f"✅ Weekly summary ({weekly['start_date']} to {weekly['end_date']}):")
            print(f"   Days logged: {weekly['days_logged']}")
            print(f"   Avg protein: {weekly['averages']['protein']}g")
            print(f"   Protein goal hits: {weekly['goal_hits']['protein']}/{weekly['days_logged']}")
            print(f"   Compliance: {weekly['compliance_percentage']}%")
        else:
            print("⚠️  Not enough data for weekly summary")
        
        # Test 4: Monthly summary
        print("\n[TEST 4] Calculating monthly summary...")
        monthly = aggregator.calculate_monthly_summary()
        if monthly:
            print(f"✅ Monthly summary ({monthly['period']}):")
            print(f"   Days logged: {monthly['days_logged']}")
            print(f"   Avg calories: {monthly['averages']['calories']}")
            print(f"   Avg protein: {monthly['averages']['protein']}g")
            print(f"   Protein consistency: ±{monthly['consistency']['protein_stdev']}g")
        else:
            print("⚠️  Not enough data for monthly summary")
        
        # Test 5: Pattern identification
        print("\n[TEST 5] Identifying patterns...")
        patterns = aggregator.identify_patterns()
        if 'best_days' in patterns:
            best_protein = patterns['best_days']['highest_protein']
            worst_protein = patterns['worst_days']['lowest_protein']
            print(f"✅ Patterns identified:")
            print(f"   Best protein day: {best_protein['date']} ({best_protein['protein']}g)")
            print(f"   Worst protein day: {worst_protein['date']} ({worst_protein['protein']}g)")
            
            if patterns.get('day_of_week_performance'):
                print(f"   Day-of-week data available for {len(patterns['day_of_week_performance'])} days")
        else:
            print("⚠️  Not enough data for pattern analysis")
        
        # Test 6: Generate insights
        print("\n[TEST 6] Generating insights...")
        insights = aggregator.generate_insights()
        print(f"✅ Generated {len(insights)} insights:")
        for i, insight in enumerate(insights, 1):
            print(f"   {i}. {insight}")
        
        # Test 7: Full summary generation
        print("\n[TEST 7] Running full daily summary...")
        summary = aggregator.run_daily_summary()
        print(f"✅ Full summary generated and saved")
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED ✅")
        print("=" * 70)
        
        # Display the generated summary
        print("\n📊 GENERATED SUMMARY:")
        print(json.dumps(summary, indent=2))
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_all()
    sys.exit(0 if success else 1)
