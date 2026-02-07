"""
Stripe Integration Test Suite
Run this to verify everything works
"""

import os
import sys
from stripe_integration import StripeIntegration
from stripe_alerts import StripeAlerts

def test_configuration():
    """Test if Stripe is configured"""
    print("🔍 Testing configuration...")
    
    integration = StripeIntegration()
    
    if not integration.is_configured():
        print("❌ Stripe not configured")
        print("   Add STRIPE_SECRET_KEY to .env file")
        return False
    
    print("✅ Stripe configured")
    return True

def test_mrr_calculation():
    """Test MRR calculation"""
    print("\n🔍 Testing MRR calculation...")
    
    integration = StripeIntegration()
    mrr_data = integration.get_mrr()
    
    if "error" in mrr_data:
        print(f"❌ Error: {mrr_data['error']}")
        return False
    
    mrr = mrr_data.get('mrr', 0)
    arr = mrr_data.get('arr', 0)
    subs = mrr_data.get('active_subscriptions', 0)
    
    print(f"✅ MRR: ${mrr:.2f}")
    print(f"✅ ARR: ${arr:.2f}")
    print(f"✅ Active Subscriptions: {subs}")
    
    return True

def test_customer_count():
    """Test customer counting"""
    print("\n🔍 Testing customer count...")
    
    integration = StripeIntegration()
    customer_data = integration.get_customer_count()
    
    if "error" in customer_data:
        print(f"❌ Error: {customer_data['error']}")
        return False
    
    total = customer_data.get('total_customers', 0)
    active = customer_data.get('active_customers', 0)
    
    print(f"✅ Total Customers: {total}")
    print(f"✅ Active Customers: {active}")
    
    return True

def test_growth_calculation():
    """Test growth data"""
    print("\n🔍 Testing growth calculation...")
    
    integration = StripeIntegration()
    growth_data = integration.get_growth_data(days=30)
    
    if "error" in growth_data:
        print(f"❌ Error: {growth_data['error']}")
        return False
    
    growth_pct = growth_data.get('growth_percentage', 0)
    daily_data = growth_data.get('daily_revenue', {})
    
    print(f"✅ 7-Day Growth: {growth_pct:+.2f}%")
    print(f"✅ Days with revenue: {len(daily_data)}")
    
    return True

def test_alerts():
    """Test alert system"""
    print("\n🔍 Testing alert system...")
    
    alerts = StripeAlerts()
    
    if not alerts.is_configured():
        print("⚠️  Telegram alerts not configured (optional)")
        print("   Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env")
        return True  # Not a failure, just optional
    
    print("✅ Telegram configured")
    print("📤 Sending test alert...")
    
    success = alerts.send_telegram("🧪 Test alert from Stripe integration!")
    
    if success:
        print("✅ Alert sent successfully!")
        return True
    else:
        print("❌ Alert failed to send")
        return False

def test_data_export():
    """Test data export"""
    print("\n🔍 Testing data export...")
    
    integration = StripeIntegration()
    
    try:
        filepath = integration.export_data("test_export.json")
        print(f"✅ Data exported to: {filepath}")
        
        # Clean up
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return True
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("🧪 STRIPE INTEGRATION TEST SUITE")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_mrr_calculation,
        test_customer_count,
        test_growth_calculation,
        test_alerts,
        test_data_export
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Integration ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
