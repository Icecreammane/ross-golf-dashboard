#!/usr/bin/env python3
"""
Reservation Check Daemon - Check saved searches for availability
Runs hourly via cron
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from find_reservation import load_saved_searches, find_reservations

def check_saved_searches():
    """Check all active saved searches"""
    print(f"[{datetime.now()}] Checking saved reservation searches...")
    
    data = load_saved_searches()
    searches = [s for s in data.get('searches', []) if s.get('active', True)]
    
    if not searches:
        print("No active searches to check")
        return
    
    alerts = []
    
    for search in searches:
        print(f"\n📋 Checking search #{search['id']}...")
        
        results = find_reservations(
            search.get('party_size', 2),
            search.get('time', '7:00 PM'),
            search.get('cuisine'),
            search.get('location', 'Nashville')
        )
        
        # Filter for specific restaurant if specified
        if search.get('restaurant_name'):
            results = [r for r in results if search['restaurant_name'].lower() in r['restaurant'].lower()]
        
        if results:
            alert = {
                'search_id': search['id'],
                'restaurant_name': search.get('restaurant_name'),
                'results': results,
            }
            alerts.append(alert)
            print(f"✅ Found {len(results)} matches!")
    
    # Generate alerts
    if alerts:
        print(f"\n🎉 RESERVATION ALERTS ({len(alerts)} searches have availability)\n")
        
        for alert in alerts:
            if alert['restaurant_name']:
                print(f"🔔 '{alert['restaurant_name']}' has availability!")
            else:
                print(f"🔔 Search #{alert['search_id']} has {len(alert['results'])} options")
            
            for result in alert['results'][:3]:  # Top 3
                print(f"   • {result['restaurant']}: {', '.join(result['available_times'])}")
                print(f"     {result['booking_url']}")
            print()
        
        # TODO: Send Telegram notification to Ross
        # This would integrate with the message tool
    else:
        print("No new availability found")

if __name__ == '__main__':
    check_saved_searches()
