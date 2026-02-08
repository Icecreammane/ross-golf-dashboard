#!/usr/bin/env python3
"""
Quick Analytics Summary
Display current analytics at a glance
"""

import json
from pathlib import Path
from datetime import datetime

# Colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

WORKSPACE = Path.home() / "clawd"
DATA_DIR = WORKSPACE / "data"


def load_json(filename):
    """Load JSON file"""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return {}
    try:
        with open(filepath) as f:
            return json.load(f)
    except:
        return {}


def print_header(title):
    """Print section header"""
    print(f"\n{BOLD}{BLUE}{title}{RESET}")
    print("━" * 60)


def main():
    # Load data
    analytics = load_json("analytics.json")
    insights = load_json("analytics-insights.json")
    
    # Header
    print(f"\n{'='*60}")
    print(f"{BOLD}{CYAN}📊 ANALYTICS SUMMARY{RESET}")
    print(f"{'='*60}")
    
    # Overview
    print_header("📈 Overview")
    
    opportunities = analytics.get('opportunities', [])
    conversions = analytics.get('conversions', [])
    social_posts = analytics.get('social_posts', [])
    
    total_opps = len(opportunities)
    converted = sum(1 for o in opportunities if o.get('converted'))
    conversion_rate = (converted / total_opps * 100) if total_opps > 0 else 0
    total_revenue = sum(c['revenue'] for c in conversions)
    
    print(f"  Opportunities Tracked: {GREEN}{total_opps}{RESET}")
    print(f"  Conversions: {GREEN}{converted}{RESET} ({conversion_rate:.1f}%)")
    print(f"  Total Revenue: {GREEN}${total_revenue:.0f}{RESET}")
    print(f"  Social Posts Tracked: {GREEN}{len(social_posts)}{RESET}")
    
    # Source Performance
    print_header("🎯 Performance by Source")
    
    source_perf = analytics.get('source_performance', {})
    for source, data in sorted(source_perf.items()):
        if data['total'] > 0:
            rate = (data['converted'] / data['total']) * 100
            print(f"  {source.capitalize():12} {rate:5.1f}%  " + 
                  f"({data['converted']}/{data['total']})  " +
                  f"${data['revenue']:.0f}")
    
    # Best Posting Time
    print_header("⏰ Best Posting Times")
    
    engagement_by_hour = analytics.get('engagement_by_hour', {})
    hourly = []
    for hour, data in engagement_by_hour.items():
        if data['posts'] > 0:
            avg = data['engagement'] / data['posts']
            hourly.append((int(hour), avg, data['posts']))
    
    if hourly:
        hourly.sort(key=lambda x: x[1], reverse=True)
        for hour, avg, posts in hourly[:5]:
            time_str = f"{hour % 12 or 12}{'am' if hour < 12 else 'pm'}"
            print(f"  {time_str:6} {avg:6.1f} avg engagement  ({posts} posts)")
    else:
        print(f"  {YELLOW}Not enough data yet{RESET}")
    
    # Top Insights
    print_header("💡 Key Insights")
    
    insights_list = insights.get('insights', [])
    if insights_list:
        # Show top 3 high priority
        high_priority = [i for i in insights_list if i['priority'] == 'high']
        for insight in high_priority[:3]:
            category = insight.get('category', '').upper()
            text = insight.get('insight', '')
            print(f"  🔴 [{category}] {text}")
        
        # Show top 2 medium priority
        medium_priority = [i for i in insights_list if i['priority'] == 'medium']
        for insight in medium_priority[:2]:
            category = insight.get('category', '').upper()
            text = insight.get('insight', '')
            print(f"  🟡 [{category}] {text}")
    else:
        print(f"  {YELLOW}No insights generated yet{RESET}")
    
    # Last Updated
    print_header("📅 Status")
    
    last_updated = analytics.get('last_updated', '')
    if last_updated:
        dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
        time_str = dt.strftime('%Y-%m-%d %H:%M UTC')
        print(f"  Last Updated: {time_str}")
    
    state = load_json("analytics-state.json")
    if state.get('last_sync'):
        dt = datetime.fromisoformat(state['last_sync'])
        time_str = dt.strftime('%Y-%m-%d %H:%M UTC')
        print(f"  Last Sync: {time_str}")
        print(f"  Sync Count: {state.get('sync_count', 0)}")
    
    # Footer
    print(f"\n{'='*60}")
    print(f"{YELLOW}💾 View full report:{RESET} ~/clawd/reports/analytics_report_latest.html")
    print(f"{YELLOW}📊 Dashboard:{RESET} http://10.0.0.18:8080/revenue/dashboard.html")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
