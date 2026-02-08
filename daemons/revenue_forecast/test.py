#!/usr/bin/env python3
"""
Test suite for revenue forecasting with mock data
"""
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from daemons.revenue_forecast.database import RevenueDatabase
from daemons.revenue_forecast.forecaster import RevenueForecast
from daemons.revenue_forecast.stripe_integration import StripeIntegration

def test_database():
    """Test database operations"""
    print("Testing database operations...")
    
    db = RevenueDatabase("data/test_revenue.db")
    
    # Add test snapshots with specific timestamps
    for i in range(30):
        date = datetime.now() - timedelta(days=29-i)
        mrr = 15000 + (i * 50)  # Growing from $150 to $164.50
        db.add_mrr_snapshot(
            mrr, 
            customer_count=5 + (i // 7), 
            source="test",
            timestamp=date.isoformat()
        )
    
    # Check current MRR
    current = db.get_current_mrr()
    assert current is not None, "Should have current MRR"
    print(f"✅ Current MRR: ${current['mrr_cents']/100:.2f}")
    
    # Check history
    history = db.get_historical_mrr(30)
    assert len(history) > 0, "Should have history"
    print(f"✅ History: {len(history)} days")
    
    # Check trend (need at least 2 days)
    trend = db.get_trend_summary(7)
    if len(history) >= 2:
        assert trend['status'] == 'ok', "Should calculate trend"
        print(f"✅ Trend: {trend['trend']} ({trend['pct_change']:+.1f}%)")
    else:
        print(f"⚠️  Trend: Insufficient data ({len(history)} days)")
    
    print("✅ Database tests passed\n")
    return db

def test_forecasting(db):
    """Test forecasting calculations"""
    print("Testing forecasting...")
    
    # Use the test database
    config_path = Path(__file__).parent / "config.json"
    forecast = RevenueForecast(config_path)
    forecast.db = db  # Use the test database
    
    # Calculate growth rates
    growth = forecast.calculate_growth_rates()
    assert growth is not None, "Should calculate growth rates"
    print(f"✅ Daily growth: {growth['daily_rate']:+.2f}%")
    print(f"✅ Weekly growth: {growth['weekly_rate']:+.2f}%")
    
    # Update metrics
    metrics = forecast.update_metrics()
    assert 'error' not in metrics, "Should update metrics"
    print(f"✅ Days to target: {metrics['days_to_target']}")
    print(f"✅ Customers needed: {metrics['customers_needed']}")
    
    # Generate scenarios
    scenarios = forecast.generate_all_scenarios()
    assert len(scenarios) > 0, "Should generate scenarios"
    print(f"✅ Generated {len(scenarios)} scenarios")
    
    for s in scenarios:
        print(f"   - {s['scenario_name']}: {s['days_to_target']} days")
    
    # Generate daily update
    update = forecast.generate_daily_update()
    assert len(update) > 0, "Should generate update"
    print(f"✅ Daily update: {update}")
    
    # Get dashboard data
    dashboard = forecast.get_dashboard_data()
    assert dashboard['status'] == 'ok', "Should get dashboard data"
    print(f"✅ Dashboard data ready: {dashboard['pct_complete']:.1f}% complete")
    
    print("✅ Forecasting tests passed\n")
    return forecast

def test_stripe_integration():
    """Test Stripe integration (mock mode)"""
    print("Testing Stripe integration...")
    
    stripe = StripeIntegration()
    assert stripe.mock_mode, "Should be in mock mode"
    
    # Get mock data
    data = stripe.get_current_mrr()
    assert 'mrr_cents' in data, "Should return MRR data"
    assert data['source'] == 'mock', "Should be mock source"
    print(f"✅ Mock MRR: ${data['mrr_cents']/100:.2f}")
    print(f"✅ Mock customers: {data['customer_count']}")
    
    # Update baseline
    stripe.update_mock_baseline(20000, 8)
    data = stripe.get_current_mrr()
    assert data['mrr_cents'] >= 19000, "Should update baseline"
    print(f"✅ Updated baseline: ${data['mrr_cents']/100:.2f}")
    
    print("✅ Stripe integration tests passed\n")

def test_end_to_end():
    """Test complete workflow"""
    print("Testing end-to-end workflow...")
    
    # Initialize with mock data
    stripe = StripeIntegration()
    stripe.update_mock_baseline(15000, 5)
    
    # Create database
    db = RevenueDatabase("data/test_revenue_e2e.db")
    
    # Simulate 30 days of data
    for i in range(30):
        data = stripe.get_current_mrr()
        # Add some variance each day
        mrr = data['mrr_cents'] + (i * 60)  # Growing trend
        date = datetime.now() - timedelta(days=29-i)
        db.add_mrr_snapshot(
            mrr, 
            customer_count=5 + (i // 7), 
            source="test",
            timestamp=date.isoformat()
        )
    
    # Run forecast
    forecast = RevenueForecast()
    forecast.db = db
    
    # Update metrics
    metrics = forecast.update_metrics()
    print(f"✅ Current: ${metrics['current_mrr']:.2f}")
    print(f"✅ Target: ${metrics['target_mrr']:.2f}")
    print(f"✅ Days to target: {metrics['days_to_target']}")
    
    # Generate scenarios
    scenarios = forecast.generate_all_scenarios()
    print(f"✅ Scenarios: {len(scenarios)}")
    
    # Generate brief
    update = forecast.generate_daily_update()
    db.save_daily_update(update)
    retrieved = db.get_daily_update()
    assert retrieved == update, "Should save and retrieve update"
    print(f"✅ Daily update saved")
    
    # Generate dashboard
    dashboard = forecast.get_dashboard_data()
    output_file = Path("data/test_revenue_widget.json")
    with open(output_file, 'w') as f:
        json.dump(dashboard, f, indent=2)
    print(f"✅ Dashboard written to {output_file}")
    
    print("✅ End-to-end test passed\n")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("  Revenue Forecast Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_database()
        test_stripe_integration()
        test_forecasting(RevenueDatabase("data/test_revenue.db"))
        test_end_to_end()
        
        print("=" * 60)
        print("  ✅ ALL TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    run_all_tests()
