#!/usr/bin/env python3
"""
Test script for Fitness Dashboard API
Run this after starting the server to verify everything works
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:3001"

def test_summary():
    """Test summary endpoint"""
    print("Testing /api/summary...")
    try:
        response = requests.get(f"{BASE_URL}/api/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Summary endpoint working!")
            print(f"   Today's calories: {data['today_calories']}/{data['calorie_goal']}")
            print(f"   Today's protein: {data['today_protein']}g/{data['protein_goal']}g")
            print(f"   Latest weight: {data['latest_weight']} lbs")
            print(f"   Week workouts: {data['week_workouts']}")
            return True
        else:
            print(f"❌ Summary endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Summary endpoint error: {e}")
        return False

def test_calories():
    """Test calorie logging"""
    print("\nTesting /api/calories...")
    try:
        # GET
        response = requests.get(f"{BASE_URL}/api/calories")
        if response.status_code == 200:
            calories = response.json()
            print(f"✅ GET calories working! ({len(calories)} entries)")
        
        # POST
        test_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "calories": 500,
            "meal": "Test meal"
        }
        response = requests.post(f"{BASE_URL}/api/calories", json=test_data)
        if response.status_code == 200:
            print(f"✅ POST calories working!")
            return True
        else:
            print(f"❌ POST calories failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Calories endpoint error: {e}")
        return False

def test_workouts():
    """Test workout logging"""
    print("\nTesting /api/workouts...")
    try:
        # GET
        response = requests.get(f"{BASE_URL}/api/workouts")
        if response.status_code == 200:
            workouts = response.json()
            print(f"✅ GET workouts working! ({len(workouts)} entries)")
        
        # POST
        test_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Test",
            "notes": "API test"
        }
        response = requests.post(f"{BASE_URL}/api/workouts", json=test_data)
        if response.status_code == 200:
            print(f"✅ POST workouts working!")
            return True
        else:
            print(f"❌ POST workouts failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Workouts endpoint error: {e}")
        return False

def test_weight():
    """Test weight logging"""
    print("\nTesting /api/weight...")
    try:
        # GET
        response = requests.get(f"{BASE_URL}/api/weight")
        if response.status_code == 200:
            weights = response.json()
            print(f"✅ GET weight working! ({len(weights)} entries)")
        
        # POST
        test_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "weight": 225.5
        }
        response = requests.post(f"{BASE_URL}/api/weight", json=test_data)
        if response.status_code == 200:
            print(f"✅ POST weight working!")
            return True
        else:
            print(f"❌ POST weight failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Weight endpoint error: {e}")
        return False

def test_macros():
    """Test macro logging"""
    print("\nTesting /api/macros...")
    try:
        # GET
        response = requests.get(f"{BASE_URL}/api/macros")
        if response.status_code == 200:
            macros = response.json()
            print(f"✅ GET macros working! ({len(macros)} entries)")
        
        # POST
        test_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "protein": 40,
            "meal": "Test meal"
        }
        response = requests.post(f"{BASE_URL}/api/macros", json=test_data)
        if response.status_code == 200:
            print(f"✅ POST macros working!")
            return True
        else:
            print(f"❌ POST macros failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Macros endpoint error: {e}")
        return False

def main():
    print("=" * 50)
    print("🏋️  Fitness Dashboard API Test Suite")
    print("=" * 50)
    
    # Test if server is running
    try:
        response = requests.get(BASE_URL, timeout=2)
        print(f"✅ Server is running on {BASE_URL}\n")
    except Exception as e:
        print(f"❌ Server is not running on {BASE_URL}")
        print(f"   Error: {e}")
        print("\n   Start the server with: python3 app.py")
        return
    
    # Run tests
    results = []
    results.append(("Summary", test_summary()))
    results.append(("Calories", test_calories()))
    results.append(("Workouts", test_workouts()))
    results.append(("Weight", test_weight()))
    results.append(("Macros", test_macros()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Dashboard is ready to use.")
        print(f"\n📊 Open dashboard at: {BASE_URL}")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
