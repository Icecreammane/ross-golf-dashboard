#!/usr/bin/env python3
"""
Opportunity Viewer

Displays aggregated opportunities from opportunity_aggregator.py
Shows top opportunities ranked by revenue potential.

Usage:
    python3 view_opportunities.py           # Show top 10
    python3 view_opportunities.py --all     # Show all
    python3 view_opportunities.py --top 5   # Show top 5
    python3 view_opportunities.py --type golf_coaching  # Filter by type
    python3 view_opportunities.py --source twitter      # Filter by source
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import argparse
from typing import List, Dict, Optional

# Paths
WORKSPACE = Path("/Users/clawdbot/clawd")
OPPORTUNITIES_FILE = WORKSPACE / "data" / "opportunities.json"

# Color codes for terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def load_opportunities() -> Optional[Dict]:
    """Load opportunities from JSON file"""
    if not OPPORTUNITIES_FILE.exists():
        print(f"{Colors.FAIL}❌ Opportunities file not found: {OPPORTUNITIES_FILE}{Colors.ENDC}")
        print(f"{Colors.WARNING}💡 Run opportunity_aggregator.py first to generate opportunities.{Colors.ENDC}")
        return None
    
    try:
        with open(OPPORTUNITIES_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"{Colors.FAIL}❌ Failed to parse opportunities file: {e}{Colors.ENDC}")
        return None
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error loading opportunities: {e}{Colors.ENDC}")
        return None


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}\n")


def print_summary(data: Dict):
    """Print opportunity summary"""
    summary = data.get('summary', {})
    total = data.get('total_opportunities', 0)
    last_updated = data.get('last_updated', 'unknown')
    
    # Parse timestamp
    try:
        dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
        updated_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        updated_str = last_updated
    
    print(f"{Colors.BOLD}📊 Summary{Colors.ENDC}")
    print(f"   Last updated: {updated_str}")
    print(f"   Total opportunities: {total}")
    print()
    
    # Priority breakdown
    high = summary.get('high_priority', 0)
    medium = summary.get('medium_priority', 0)
    low = summary.get('low_priority', 0)
    
    print(f"   {Colors.FAIL}🔥 High priority (80-100):{Colors.ENDC} {high}")
    print(f"   {Colors.WARNING}⚡ Medium priority (50-79):{Colors.ENDC} {medium}")
    print(f"   {Colors.OKBLUE}💡 Low priority (<50):{Colors.ENDC} {low}")
    print()
    
    # By type
    by_type = summary.get('by_type', {})
    if by_type:
        print(f"   {Colors.BOLD}By type:{Colors.ENDC}")
        for opp_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            print(f"      {opp_type}: {count}")
        print()
    
    # By source
    by_source = summary.get('by_source', {})
    if by_source:
        print(f"   {Colors.BOLD}By source:{Colors.ENDC}")
        for source, count in sorted(by_source.items()):
            print(f"      {source}: {count}")
        print()


def get_priority_color(score: int) -> str:
    """Get color based on priority score"""
    if score >= 80:
        return Colors.FAIL  # Red for high priority
    elif score >= 50:
        return Colors.WARNING  # Yellow for medium
    else:
        return Colors.OKBLUE  # Blue for low


def get_priority_label(score: int) -> str:
    """Get priority label"""
    if score >= 80:
        return "🔥 HIGH"
    elif score >= 50:
        return "⚡ MED"
    else:
        return "💡 LOW"


def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        # If today, show time; otherwise show date
        now = datetime.now(dt.tzinfo)
        if dt.date() == now.date():
            return dt.strftime('%H:%M')
        else:
            return dt.strftime('%b %d')
    except:
        return timestamp[:10]


def print_opportunity(opp: Dict, index: int):
    """Print single opportunity with formatting"""
    score = opp.get('score', 0)
    opp_type = opp.get('type', 'unknown')
    source = opp.get('source', 'unknown')
    sender = opp.get('sender', 'unknown')
    content = opp.get('content', '')
    revenue = opp.get('revenue_potential', 'unknown')
    action = opp.get('action_required', 'No action specified')
    timestamp = opp.get('timestamp', '')
    
    color = get_priority_color(score)
    priority = get_priority_label(score)
    
    # Header
    print(f"{color}{Colors.BOLD}#{index} | Score: {score} | {priority}{Colors.ENDC}")
    print(f"   📌 Type: {opp_type.replace('_', ' ').title()}")
    print(f"   📍 Source: {source}")
    print(f"   👤 Sender: {sender}")
    print(f"   💰 Revenue: {revenue}")
    print(f"   ⏰ Time: {format_timestamp(timestamp)}")
    
    # Content (truncate if too long)
    if len(content) > 200:
        content_display = content[:200] + "..."
    else:
        content_display = content
    print(f"   💬 Content: {content_display}")
    
    # Action
    print(f"   {Colors.OKGREEN}✅ Action: {action}{Colors.ENDC}")
    
    # Additional fields
    if 'url' in opp and opp['url']:
        print(f"   🔗 URL: {opp['url']}")
    
    if 'subject' in opp:
        print(f"   📧 Subject: {opp['subject']}")
    
    print()


def filter_opportunities(
    opportunities: List[Dict],
    opp_type: Optional[str] = None,
    source: Optional[str] = None,
    min_score: Optional[int] = None
) -> List[Dict]:
    """Filter opportunities based on criteria"""
    filtered = opportunities
    
    if opp_type:
        filtered = [o for o in filtered if o.get('type', '').lower() == opp_type.lower()]
    
    if source:
        filtered = [o for o in filtered if o.get('source', '').lower() == source.lower()]
    
    if min_score is not None:
        filtered = [o for o in filtered if o.get('score', 0) >= min_score]
    
    return filtered


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='View aggregated opportunities',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Show all opportunities (default: top 10)'
    )
    parser.add_argument(
        '--top',
        type=int,
        metavar='N',
        help='Show top N opportunities'
    )
    parser.add_argument(
        '--type',
        type=str,
        metavar='TYPE',
        help='Filter by opportunity type (e.g., golf_coaching, partnership)'
    )
    parser.add_argument(
        '--source',
        type=str,
        metavar='SOURCE',
        help='Filter by source (twitter, email, revenue_dashboard)'
    )
    parser.add_argument(
        '--min-score',
        type=int,
        metavar='SCORE',
        help='Show only opportunities with score >= SCORE'
    )
    parser.add_argument(
        '--summary-only',
        action='store_true',
        help='Show only summary, not individual opportunities'
    )
    
    args = parser.parse_args()
    
    # Load opportunities
    data = load_opportunities()
    if not data:
        sys.exit(1)
    
    # Print header
    print_header("🎯 OPPORTUNITY DASHBOARD")
    
    # Print summary
    print_summary(data)
    
    if args.summary_only:
        sys.exit(0)
    
    # Get opportunities
    opportunities = data.get('opportunities', [])
    
    if not opportunities:
        print(f"{Colors.WARNING}No opportunities found.{Colors.ENDC}")
        sys.exit(0)
    
    # Filter opportunities
    filtered = filter_opportunities(
        opportunities,
        opp_type=args.type,
        source=args.source,
        min_score=args.min_score
    )
    
    if not filtered:
        print(f"{Colors.WARNING}No opportunities match the filters.{Colors.ENDC}")
        sys.exit(0)
    
    # Determine how many to show
    if args.all:
        count = len(filtered)
    elif args.top:
        count = min(args.top, len(filtered))
    else:
        count = min(10, len(filtered))
    
    # Print opportunities
    print(f"{Colors.BOLD}{'─'*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}Top {count} Opportunities{Colors.ENDC}")
    if len(filtered) > count:
        print(f"{Colors.OKBLUE}(Showing {count} of {len(filtered)} total){Colors.ENDC}")
    print(f"{Colors.BOLD}{'─'*80}{Colors.ENDC}\n")
    
    for i, opp in enumerate(filtered[:count], 1):
        print_opportunity(opp, i)
    
    # Footer
    if len(filtered) > count:
        print(f"{Colors.OKBLUE}💡 Use --all to see all opportunities or --top N to see top N{Colors.ENDC}")


if __name__ == "__main__":
    main()
