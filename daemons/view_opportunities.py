#!/usr/bin/env python3
"""
View Twitter Opportunities

User-friendly viewer for opportunities detected by the Twitter daemon.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("/Users/clawdbot/clawd/data/twitter-opportunities.json")


def load_opportunities():
    """Load opportunities from JSON"""
    if not DATA_FILE.exists():
        print("❌ No opportunities file found.")
        print(f"   Expected: {DATA_FILE}")
        print("   Run the daemon first: python3 daemons/twitter_daemon.py")
        return []
    
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def format_timestamp(iso_timestamp):
    """Format ISO timestamp to human-readable"""
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return iso_timestamp


def view_all(limit=None):
    """View all opportunities (sorted by score)"""
    opps = load_opportunities()
    
    if not opps:
        print("📭 No opportunities found yet.")
        return
    
    opps_sorted = sorted(opps, key=lambda x: (x['score'], x['timestamp']), reverse=True)
    
    if limit:
        opps_sorted = opps_sorted[:limit]
    
    print(f"\n{'='*80}")
    print(f" Twitter Opportunities ({len(opps_sorted)} shown, {len(opps)} total)")
    print(f"{'='*80}\n")
    
    for i, opp in enumerate(opps_sorted, 1):
        score_emoji = "🔥" if opp['score'] >= 50 else "⭐" if opp['score'] >= 30 else "📌"
        
        print(f"{score_emoji} #{i} | Score: {opp['score']:3d} | Type: {opp['opportunity_type'].upper()}")
        print(f"   From: @{opp['sender']} ({opp.get('author_followers', 0):,} followers)")
        print(f"   When: {format_timestamp(opp['timestamp'])}")
        print(f"   Type: {opp['type'].upper()}")
        
        # Content (wrapped)
        content = opp['content']
        if len(content) > 150:
            content = content[:147] + "..."
        print(f"   Message: {content}")
        
        # Reasons
        if opp.get('reasons'):
            print(f"   Why: {', '.join(opp['reasons'][:3])}")
        
        print(f"   Link: {opp['url']}")
        print()


def view_by_type(opp_type):
    """View opportunities filtered by type"""
    opps = load_opportunities()
    
    if not opps:
        print("📭 No opportunities found yet.")
        return
    
    filtered = [o for o in opps if opp_type in o.get('all_types', []) or o['opportunity_type'] == opp_type]
    
    if not filtered:
        print(f"📭 No {opp_type} opportunities found.")
        return
    
    print(f"\n{'='*80}")
    print(f" {opp_type.upper()} Opportunities ({len(filtered)} found)")
    print(f"{'='*80}\n")
    
    for opp in sorted(filtered, key=lambda x: x['score'], reverse=True):
        print(f"🎯 Score {opp['score']}: @{opp['sender']}")
        print(f"   {opp['content'][:100]}...")
        print(f"   {opp['url']}\n")


def view_stats():
    """View statistics"""
    opps = load_opportunities()
    
    if not opps:
        print("📭 No opportunities found yet.")
        return
    
    # Calculate stats
    total = len(opps)
    by_type = {}
    by_source = {'mention': 0, 'dm': 0}
    high_score = sum(1 for o in opps if o['score'] >= 50)
    medium_score = sum(1 for o in opps if 30 <= o['score'] < 50)
    low_score = sum(1 for o in opps if o['score'] < 30)
    
    for opp in opps:
        opp_type = opp['opportunity_type']
        by_type[opp_type] = by_type.get(opp_type, 0) + 1
        by_source[opp['type']] = by_source.get(opp['type'], 0) + 1
    
    avg_score = sum(o['score'] for o in opps) / total
    
    print(f"\n{'='*80}")
    print(" Twitter Opportunities Statistics")
    print(f"{'='*80}\n")
    
    print(f"📊 Total Opportunities: {total}")
    print(f"   Average Score: {avg_score:.1f}")
    print()
    
    print("🎯 By Score:")
    print(f"   🔥 High (≥50): {high_score}")
    print(f"   ⭐ Medium (30-49): {medium_score}")
    print(f"   📌 Low (<30): {low_score}")
    print()
    
    print("📂 By Type:")
    for typ, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        print(f"   {typ.capitalize()}: {count}")
    print()
    
    print("📥 By Source:")
    for source, count in by_source.items():
        print(f"   {source.upper()}: {count}")
    print()
    
    # Top sender
    senders = {}
    for opp in opps:
        sender = opp['sender']
        senders[sender] = senders.get(sender, 0) + 1
    
    if senders:
        top_sender = max(senders.items(), key=lambda x: x[1])
        print(f"👤 Most Active Sender: @{top_sender[0]} ({top_sender[1]} opportunities)")
    
    print()


def main():
    """Main entry point"""
    if len(sys.argv) == 1:
        # Default: show top 10
        view_all(limit=10)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'all':
        view_all()
    elif command == 'top':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        view_all(limit=limit)
    elif command == 'stats':
        view_stats()
    elif command in ['golf', 'fitness', 'coaching', 'partnership', 'product_feedback', 'general']:
        view_by_type(command)
    elif command == 'help':
        print("""
Twitter Opportunities Viewer

Usage:
    python3 view_opportunities.py [command]

Commands:
    (none)      Show top 10 opportunities
    all         Show all opportunities
    top N       Show top N opportunities
    stats       Show statistics
    golf        Show golf opportunities
    fitness     Show fitness opportunities
    coaching    Show coaching opportunities
    partnership Show partnership opportunities
    product_feedback Show product feedback opportunities
    help        Show this help

Examples:
    python3 view_opportunities.py
    python3 view_opportunities.py top 20
    python3 view_opportunities.py fitness
    python3 view_opportunities.py stats
        """)
    else:
        print(f"❌ Unknown command: {command}")
        print("   Run with 'help' for usage")


if __name__ == "__main__":
    main()
