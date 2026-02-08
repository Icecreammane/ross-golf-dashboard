#!/usr/bin/env python3
"""
Test Suite for Unified Dashboard
Validates all endpoints and functionality
"""

import sys
import requests
import time
from datetime import datetime

# Configuration
BASE_URL = 'http://localhost:3000'
TIMEOUT = 5

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def test_endpoint(name, url, expected_keys=None):
    """Test a single endpoint"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=TIMEOUT)
        elapsed = (time.time() - start_time) * 1000  # ms
        
        if response.status_code == 200:
            data = response.json()
            
            # Check expected keys
            if expected_keys:
                missing = [k for k in expected_keys if k not in data]
                if missing:
                    print(f"❌ {name}: Missing keys: {missing}")
                    return False
            
            print(f"✅ {name}: {response.status_code} ({elapsed:.0f}ms)")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False

def test_dashboard_page():
    """Test main dashboard loads"""
    try:
        response = requests.get(BASE_URL, timeout=TIMEOUT)
        if response.status_code == 200 and 'Command Center' in response.text:
            print(f"✅ Dashboard page: Loaded successfully")
            return True
        else:
            print(f"❌ Dashboard page: Failed to load")
            return False
    except Exception as e:
        print(f"❌ Dashboard page: {str(e)}")
        return False

def test_static_assets():
    """Test static files load"""
    assets = [
        ('/static/css/styles.css', 'CSS'),
        ('/static/js/dashboard.js', 'JavaScript')
    ]
    
    results = []
    for path, name in assets:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
            if response.status_code == 200:
                print(f"✅ {name}: Loaded")
                results.append(True)
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
            results.append(False)
    
    return all(results)

def run_all_tests():
    """Run complete test suite"""
    print_header("Unified Dashboard Test Suite")
    print(f"Testing: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tests = []
    
    # Test main page
    print_header("Page Load Test")
    tests.append(test_dashboard_page())
    
    # Test static assets
    print_header("Static Assets Test")
    tests.append(test_static_assets())
    
    # Test API endpoints
    print_header("API Endpoints Test")
    
    tests.append(test_endpoint(
        "Health Check",
        f"{BASE_URL}/api/health",
        ['status', 'timestamp']
    ))
    
    tests.append(test_endpoint(
        "Revenue API",
        f"{BASE_URL}/api/revenue",
        ['mrr', 'goal', 'progress']
    ))
    
    tests.append(test_endpoint(
        "Opportunities API",
        f"{BASE_URL}/api/opportunities",
        ['opportunities', 'total_count']
    ))
    
    tests.append(test_endpoint(
        "Morning Brief API",
        f"{BASE_URL}/api/morning-brief",
        ['generated', 'date']
    ))
    
    tests.append(test_endpoint(
        "Fitness API",
        f"{BASE_URL}/api/fitness",
        ['current_weight', 'target_weight']
    ))
    
    tests.append(test_endpoint(
        "Golf API",
        f"{BASE_URL}/api/golf",
        ['total_rounds', 'average_score']
    ))
    
    tests.append(test_endpoint(
        "NBA API",
        f"{BASE_URL}/api/nba",
        ['has_slate', 'date']
    ))
    
    tests.append(test_endpoint(
        "All Data API (Fast Load)",
        f"{BASE_URL}/api/all",
        ['revenue', 'opportunities', 'fitness']
    ))
    
    # Performance test
    print_header("Performance Test")
    print("Testing /api/all endpoint (should be <1s)...")
    start = time.time()
    response = requests.get(f"{BASE_URL}/api/all", timeout=TIMEOUT)
    elapsed = time.time() - start
    
    if elapsed < 1.0:
        print(f"✅ Fast load time: {elapsed*1000:.0f}ms")
        tests.append(True)
    else:
        print(f"⚠️  Slow load time: {elapsed*1000:.0f}ms (target: <1000ms)")
        tests.append(False)
    
    # Results summary
    print_header("Test Results")
    passed = sum(tests)
    total = len(tests)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Passed: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
