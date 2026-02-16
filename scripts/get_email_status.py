#!/usr/bin/env python3
"""Get email status for Mission Control"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / 'data'
EMAIL_DATA_PATH = DATA_DIR / 'email_classifications.json'

def get_email_status():
    """Get email status"""
    if not EMAIL_DATA_PATH.exists():
        return {
            'urgent': 0,
            'action_required': 0,
            'fyi': 0,
            'today_processed': 0,
            'auto_archived': 0,
            'last_check': None
        }
    
    with open(EMAIL_DATA_PATH, 'r') as f:
        data = json.load(f)
    
    emails = data.get('emails', [])
    
    # Count unread by category (approximate - would need Gmail API to check read status)
    urgent = sum(1 for e in emails if e['category'] == 'urgent')
    action_required = sum(1 for e in emails if e['category'] == 'action_required')
    fyi = sum(1 for e in emails if e['category'] == 'fyi')
    
    # Count today's emails
    today = datetime.now().date()
    today_emails = [
        e for e in emails
        if datetime.fromisoformat(e['classified_at']).date() == today
    ]
    
    auto_archived = sum(1 for e in today_emails if e['category'] == 'spam')
    
    # Get urgent emails for display
    urgent_emails = [
        {
            'subject': e['subject'],
            'sender': e['sender'],
            'gmail_url': e['gmail_url']
        }
        for e in emails
        if e['category'] == 'urgent'
    ][:5]  # Top 5
    
    return {
        'urgent': urgent,
        'action_required': action_required,
        'fyi': fyi,
        'today_processed': len(today_emails),
        'auto_archived': auto_archived,
        'urgent_emails': urgent_emails,
        'last_check': data.get('last_check')
    }

if __name__ == '__main__':
    status = get_email_status()
    print(json.dumps(status, indent=2))
