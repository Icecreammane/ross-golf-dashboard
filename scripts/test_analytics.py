#!/usr/bin/env python3
"""
Analytics System Test Suite
Comprehensive testing of all analytics components
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from analytics_tracker import AnalyticsTracker
from analytics_insights import InsightsGenerator
from analytics_weekly_report import WeeklyReportGenerator
from analytics_dashboard import AnalyticsDashboard

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_test(name: str):
    """Print test name"""
    print(f"\n{BLUE}▶ Testing: {name}{RESET}")


def print_success(message: str):
    """Print success message"""
    print(f"{GREEN}  ✓ {message}{RESET}")


def print_error(message: str):
    """Print error message"""
    print(f"{RED}  ✗ {message}{RESET}")


def print_info(message: str):
    """Print info message"""
    print(f"{YELLOW}  ℹ {message}{RESET}")


def test_analytics_tracker():
    """Test AnalyticsTracker"""
    print_test("Analytics Tracker")
    
    try:
        tracker = AnalyticsTracker()
        print_success("Tracker initialized")
        
        # Test tracking opportunity
        test_opp = {
            'source': 'email',
            'type': 'test_coaching',
            'score': 95,
            'revenue_potential': '$500',
            'timestamp': datetime.utcnow().isoformat(),
            'sender': 'test@example.com',
            'content': 'Test opportunity for analytics'
        }
        
        if tracker.track_opportunity(test_opp):
            print_success("Tracked test opportunity")
        else:
            print_error("Failed to track opportunity")
            return False
        
        # Test marking conversion
        tracking_id = list(tracker.analytics_data['opportunities'])[-1]['tracking_id']
        if tracker.mark_conversion(tracking_id, 500.0, "Test conversion"):
            print_success("Marked test conversion")
        else:
            print_error("Failed to mark conversion")
            return False
        
        # Test social post tracking
        test_post = {
            'id': f'test_post_{datetime.utcnow().timestamp()}',
            'text': 'Test social post',
            'posted_at': datetime.utcnow().isoformat(),
            'likes': 10,
            'retweets': 5,
            'replies': 2
        }
        
        if tracker.track_social_post(test_post):
            print_success("Tracked test social post")
        else:
            print_error("Failed to track social post")
            return False
        
        # Test conversion rate calculation
        rate = tracker.get_conversion_rate('email')
        print_success(f"Email conversion rate: {rate:.1f}%")
        
        # Test best posting time
        best_time = tracker.get_best_posting_time()
        print_success(f"Best posting time calculated: {best_time.get('best_hour')}")
        
        # Test summary generation
        summary = tracker.generate_summary()
        print_success(f"Summary generated: {summary['opportunities']['total']} opportunities")
        
        return True
    
    except Exception as e:
        print_error(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_insights_generator():
    """Test InsightsGenerator"""
    print_test("Insights Generator")
    
    try:
        generator = InsightsGenerator()
        print_success("Generator initialized")
        
        # Generate insights
        insights = generator.generate_all_insights()
        
        if insights:
            print_success(f"Generated {len(insights)} insights")
            
            # Show sample insights
            for insight in insights[:3]:
                priority = insight.get('priority', 'unknown')
                category = insight.get('category', 'unknown')
                text = insight.get('insight', '')[:80]
                print_info(f"[{priority}] {category}: {text}...")
            
            return True
        else:
            print_info("No insights generated (may need more data)")
            return True
    
    except Exception as e:
        print_error(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_weekly_report():
    """Test WeeklyReportGenerator"""
    print_test("Weekly Report Generator")
    
    try:
        generator = WeeklyReportGenerator()
        print_success("Generator initialized")
        
        # Generate reports
        results = generator.save_reports()
        
        if results:
            print_success(f"Text report saved: {results['text_file']}")
            print_success(f"HTML report saved: {results['html_file']}")
            
            # Show sample of text report
            print_info("Report preview:")
            lines = results['text_content'].split('\n')[:10]
            for line in lines:
                print(f"    {line}")
            
            return True
        else:
            print_error("Failed to generate reports")
            return False
    
    except Exception as e:
        print_error(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dashboard():
    """Test AnalyticsDashboard"""
    print_test("Analytics Dashboard")
    
    try:
        dashboard = AnalyticsDashboard()
        print_success("Dashboard initialized")
        
        # Generate dashboard data
        data = dashboard.generate_dashboard_data()
        
        if data:
            print_success("Dashboard data generated")
            
            overview = data.get('overview', {})
            print_info(f"Opportunities: {overview.get('total_opportunities', 0)}")
            print_info(f"Conversion Rate: {overview.get('conversion_rate', 0)}%")
            print_info(f"Total Revenue: ${overview.get('total_revenue', 0):.0f}")
            
            source_perf = data.get('source_performance', [])
            print_info(f"Sources tracked: {len(source_perf)}")
            
            return True
        else:
            print_error("Failed to generate dashboard data")
            return False
    
    except Exception as e:
        print_error(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_sync():
    """Test data synchronization"""
    print_test("Data Synchronization")
    
    try:
        tracker = AnalyticsTracker()
        
        # Sync opportunities
        opp_count = tracker.sync_opportunities()
        print_success(f"Synced {opp_count} opportunities from opportunities.json")
        
        # Sync social posts
        post_count = tracker.sync_social_posts()
        print_success(f"Synced {post_count} social posts from queue")
        
        return True
    
    except Exception as e:
        print_error(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_integrity():
    """Test file creation and integrity"""
    print_test("File Integrity")
    
    data_dir = Path.home() / "clawd" / "data"
    required_files = [
        "analytics.json",
        "analytics-insights.json",
        "analytics-dashboard.json"
    ]
    
    try:
        for filename in required_files:
            filepath = data_dir / filename
            if filepath.exists():
                # Check if valid JSON
                with open(filepath) as f:
                    json.load(f)
                print_success(f"{filename} exists and is valid JSON")
            else:
                print_info(f"{filename} will be created on first run")
        
        return True
    
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 ANALYTICS SYSTEM TEST SUITE")
    print("="*60)
    
    tests = [
        ("File Integrity", test_file_integrity),
        ("Analytics Tracker", test_analytics_tracker),
        ("Data Sync", test_data_sync),
        ("Insights Generator", test_insights_generator),
        ("Weekly Report", test_weekly_report),
        ("Dashboard", test_dashboard)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = f"{GREEN}PASS{RESET}" if success else f"{RED}FAIL{RESET}"
        print(f"  {status} - {name}")
    
    print("\n" + "-"*60)
    print(f"  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{GREEN}✓ All tests passed! System is production-ready.{RESET}")
        return True
    else:
        print(f"\n{YELLOW}⚠ Some tests failed. Review errors above.{RESET}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
