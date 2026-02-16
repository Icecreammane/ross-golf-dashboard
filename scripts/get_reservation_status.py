#!/usr/bin/env python3
"""Get reservation status for Mission Control"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / 'data'
SAVED_SEARCHES_PATH = DATA_DIR / 'saved_searches.json'

def get_reservation_status():
    """Get reservation status"""
    if not SAVED_SEARCHES_PATH.exists():
        return {
            'active_searches': 0,
            'new_availability': [],
            'last_check': None
        }
    
    with open(SAVED_SEARCHES_PATH, 'r') as f:
        data = json.load(f)
    
    searches = [s for s in data.get('searches', []) if s.get('active', True)]
    
    # Note: new_availability would be populated by reservation_check_daemon.py
    # For now, just return active search count
    
    return {
        'active_searches': len(searches),
        'new_availability': [],  # Populated by daemon
        'searches': [
            {
                'id': s['id'],
                'party_size': s.get('party_size', 2),
                'time': s.get('time', 'TBD'),
                'cuisine': s.get('cuisine', 'Any'),
                'location': s.get('location', 'Unknown'),
                'restaurant_name': s.get('restaurant_name'),
            }
            for s in searches
        ],
        'last_check': datetime.now().isoformat()
    }

if __name__ == '__main__':
    status = get_reservation_status()
    print(json.dumps(status, indent=2))
