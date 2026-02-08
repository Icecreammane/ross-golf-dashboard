#!/usr/bin/env python3
"""
Quick test script to verify dashboard setup
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    try:
        import flask
        print("  ✅ Flask")
        import stripe
        print("  ✅ Stripe")
        import flask_cors
        print("  ✅ Flask-CORS")
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_directories():
    """Test that required directories exist"""
    print("\n📁 Testing directories...")
    dirs = ['logs', 'data', 'static/css', 'static/js', 'templates']
    all_exist = True
    for d in dirs:
        if os.path.exists(d):
            print(f"  ✅ {d}")
        else:
            print(f"  ❌ {d} missing")
            all_exist = False
    return all_exist

def test_files():
    """Test that required files exist"""
    print("\n📄 Testing files...")
    files = [
        'app.py',
        'templates/dashboard.html',
        'static/css/dashboard.css',
        'static/js/dashboard.js',
        'requirements.txt',
        'README.md'
    ]
    all_exist = True
    for f in files:
        if os.path.exists(f):
            print(f"  ✅ {f}")
        else:
            print(f"  ❌ {f} missing")
            all_exist = False
    return all_exist

def test_env():
    """Test environment configuration"""
    print("\n🔑 Testing environment...")
    if os.path.exists('.env'):
        print("  ✅ .env file exists")
        
        # Check for required keys
        with open('.env', 'r') as f:
            content = f.read()
            
        if 'STRIPE_API_KEY' in content:
            if 'your_stripe_secret_key_here' in content:
                print("  ⚠️  STRIPE_API_KEY needs to be configured")
            else:
                print("  ✅ STRIPE_API_KEY configured")
        else:
            print("  ❌ STRIPE_API_KEY missing")
        
        return True
    else:
        print("  ⚠️  .env file not found (will use .env.example)")
        return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("Revenue Dashboard - Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports(),
        test_directories(),
        test_files(),
        test_env()
    ]
    
    print("\n" + "=" * 50)
    if all(tests):
        print("✅ All tests passed! Dashboard is ready to run.")
        print("\nStart with: python app.py")
    else:
        print("❌ Some tests failed. Check output above.")
        sys.exit(1)
    print("=" * 50)

if __name__ == '__main__':
    main()
