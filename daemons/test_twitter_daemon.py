#!/usr/bin/env python3
"""
Test Suite for Twitter Daemon

Comprehensive testing before production deployment.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Setup paths
WORKSPACE = Path("/Users/clawdbot/clawd")
sys.path.insert(0, str(WORKSPACE / "daemons"))

# Import daemon modules
from twitter_daemon import OpportunityScorer, TwitterDaemon

# Load environment
load_dotenv(WORKSPACE / ".env")

def test_environment():
    """Test 1: Environment and credentials"""
    print("\n" + "="*60)
    print("TEST 1: Environment and Credentials")
    print("="*60)
    
    required_vars = [
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_SECRET',
    ]
    
    optional_vars = ['TWITTER_BEARER_TOKEN']
    
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:15]}...")
        else:
            print(f"❌ {var}: NOT SET")
            all_good = False
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:15]}... (optional)")
        else:
            print(f"⚠️  {var}: NOT SET (optional but recommended)")
    
    if all_good:
        print("\n✅ Environment configured correctly")
        return True
    else:
        print("\n❌ Missing required environment variables")
        print("   Add them to /Users/clawdbot/clawd/.env")
        return False


def test_scorer():
    """Test 2: Opportunity scoring logic"""
    print("\n" + "="*60)
    print("TEST 2: Opportunity Scoring")
    print("="*60)
    
    test_cases = [
        {
            'text': "Hey Ross! Love your fitness content. Would you be interested in a coaching partnership?",
            'expected_min_score': 20,
            'expected_types': ['fitness', 'coaching', 'partnership']
        },
        {
            'text': "Your golf swing tips are amazing! Can you coach me? I need help ASAP.",
            'expected_min_score': 20,
            'expected_types': ['golf', 'coaching']
        },
        {
            'text': "Really impressed with your macro tracking approach. Would love feedback on my fitness app!",
            'expected_min_score': 15,
            'expected_types': ['fitness', 'product_feedback']
        },
        {
            'text': "Nice tweet!",
            'expected_min_score': 0,
            'expected_types': []
        },
        {
            'text': "Looking for a fitness coach who understands nutrition and strength training. Anyone?",
            'expected_min_score': 15,
            'expected_types': ['fitness', 'coaching']
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        result = OpportunityScorer.score(test['text'])
        
        passed = result['score'] >= test['expected_min_score']
        
        if passed:
            print(f"\n✅ Test {i} PASSED")
        else:
            print(f"\n❌ Test {i} FAILED")
            all_passed = False
        
        print(f"   Text: {test['text'][:60]}...")
        print(f"   Score: {result['score']} (expected min: {test['expected_min_score']})")
        print(f"   Type: {result['opportunity_type']}")
        print(f"   All types: {result['all_types']}")
        print(f"   Reasons: {', '.join(result['reasons'])}")
    
    if all_passed:
        print("\n✅ All scoring tests passed")
        return True
    else:
        print("\n❌ Some scoring tests failed")
        return False


def test_authentication():
    """Test 3: Twitter API authentication"""
    print("\n" + "="*60)
    print("TEST 3: Twitter API Authentication")
    print("="*60)
    
    try:
        daemon = TwitterDaemon()
        daemon.authenticate()
        
        print(f"\n✅ Successfully authenticated as @{daemon.my_username}")
        print(f"   User ID: {daemon.my_user_id}")
        return True
        
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        print("   Check your credentials in .env")
        return False


def test_file_operations():
    """Test 4: File operations (state, opportunities)"""
    print("\n" + "="*60)
    print("TEST 4: File Operations")
    print("="*60)
    
    daemon = TwitterDaemon()
    
    # Test state file
    print("\n📝 Testing state file operations...")
    test_state = {
        'last_mention_id': '12345',
        'last_dm_id': '67890',
        'test': True
    }
    
    daemon.save_state(test_state)
    loaded_state = daemon.load_state()
    
    if loaded_state.get('last_mention_id') == '12345':
        print("✅ State save/load working")
    else:
        print("❌ State save/load failed")
        return False
    
    # Test opportunities file
    print("\n📝 Testing opportunities file operations...")
    test_opportunities = [
        {
            'id': 'test_123',
            'type': 'mention',
            'sender': 'testuser',
            'content': 'Test opportunity',
            'timestamp': datetime.now().isoformat(),
            'score': 85,
            'opportunity_type': 'coaching',
            'all_types': ['coaching'],
            'reasons': ['test'],
            'url': 'https://twitter.com/test/status/123'
        }
    ]
    
    daemon.save_opportunities(test_opportunities)
    loaded_opps = daemon.load_opportunities()
    
    if len(loaded_opps) > 0 and loaded_opps[0]['id'] == 'test_123':
        print("✅ Opportunities save/load working")
    else:
        print("❌ Opportunities save/load failed")
        return False
    
    print("\n✅ All file operations working")
    return True


def test_full_run():
    """Test 5: Full daemon run"""
    print("\n" + "="*60)
    print("TEST 5: Full Daemon Run")
    print("="*60)
    
    print("\n🏃 Running full daemon cycle...")
    print("   This will check Twitter API for real mentions and DMs")
    print("   (May take 10-30 seconds)\n")
    
    try:
        daemon = TwitterDaemon()
        daemon.run()
        
        print("\n✅ Full daemon run completed successfully")
        
        # Check if output file exists and has content
        opportunities = daemon.load_opportunities()
        print(f"\n📊 Results:")
        print(f"   Total opportunities in database: {len(opportunities)}")
        
        if opportunities:
            print(f"\n   Top 5 opportunities:")
            for opp in sorted(opportunities, key=lambda x: x['score'], reverse=True)[:5]:
                print(f"   • Score {opp['score']}: {opp['opportunity_type']} from @{opp['sender']}")
                print(f"     {opp['content'][:80]}...")
        else:
            print("   (No opportunities found yet - this is normal if account has no recent mentions)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Full run failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" "*20 + "TWITTER DAEMON TEST SUITE")
    print("="*70)
    
    results = []
    
    # Test 1: Environment
    results.append(("Environment", test_environment()))
    
    if not results[0][1]:
        print("\n⚠️  Skipping remaining tests - fix environment first")
        return
    
    # Test 2: Scoring logic
    results.append(("Scoring Logic", test_scorer()))
    
    # Test 3: Authentication (requires credentials)
    try:
        results.append(("Authentication", test_authentication()))
    except Exception as e:
        print(f"❌ Authentication test crashed: {e}")
        results.append(("Authentication", False))
    
    # Test 4: File operations
    results.append(("File Operations", test_file_operations()))
    
    # Test 5: Full run (only if previous tests passed)
    if all(r[1] for r in results):
        results.append(("Full Daemon Run", test_full_run()))
    else:
        print("\n⚠️  Skipping full run test - fix failures first")
        results.append(("Full Daemon Run", None))
    
    # Summary
    print("\n" + "="*70)
    print(" "*25 + "TEST SUMMARY")
    print("="*70)
    
    for test_name, result in results:
        if result is True:
            print(f"✅ {test_name:<30} PASSED")
        elif result is False:
            print(f"❌ {test_name:<30} FAILED")
        else:
            print(f"⚠️  {test_name:<30} SKIPPED")
    
    passed = sum(1 for _, r in results if r is True)
    total = len([r for _, r in results if r is not None])
    
    print("\n" + "="*70)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Daemon is ready for production.")
        print("\n📋 Next steps:")
        print("   1. Review the setup guide: cat daemons/SETUP.md")
        print("   2. Install launchd service: See SETUP.md section 4")
        print("   3. Monitor logs: tail -f logs/twitter-daemon.log")
    else:
        print("\n⚠️  Some tests failed. Review errors above and fix before deploying.")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
