#!/usr/bin/env python3
"""
Email Monitor - Check inbox for urgent messages via Himalaya CLI
Outputs JSON with urgent count and top subjects
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Urgent keywords that flag importance
URGENT_KEYWORDS = [
    'urgent', 'asap', 'emergency', 'critical', 'immediate',
    'action required', 'deadline', 'important', 'security alert',
    'password reset', 'suspicious activity', 'verify', 'confirm'
]

# VIP senders (add emails of important people)
VIP_SENDERS = [
    'bigmeatyclawd@gmail.com',
    # Add more VIP emails as needed
]

# Spam/newsletter indicators to ignore
IGNORE_KEYWORDS = [
    'unsubscribe', 'newsletter', 'update', 'digest',
    'notification', 'noreply', 'no-reply', 'automated'
]

STATE_FILE = Path(__file__).parent / 'state' / 'email-state.json'


def run_himalaya(args):
    """Run Himalaya CLI command"""
    try:
        result = subprocess.run(
            ['himalaya'] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        return None, -1
    except FileNotFoundError:
        return None, -2


def load_state():
    """Load previous check state"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {'last_check': None, 'seen_ids': []}


def save_state(state):
    """Save current check state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def is_urgent(subject, sender, body_preview=''):
    """Determine if email is urgent"""
    text = f"{subject} {sender} {body_preview}".lower()
    
    # Check for spam/newsletter indicators first
    for ignore in IGNORE_KEYWORDS:
        if ignore in text:
            return False
    
    # VIP sender = always important
    for vip in VIP_SENDERS:
        if vip.lower() in sender.lower():
            return True
    
    # Check urgent keywords
    for keyword in URGENT_KEYWORDS:
        if keyword in text:
            return True
    
    return False


def check_inbox():
    """Check inbox for urgent messages"""
    state = load_state()
    
    # Get unread messages (adjust for your Himalaya setup)
    output, code = run_himalaya(['list', '--max-size', '50'])
    
    if code == -2:
        return {
            'status': 'error',
            'error': 'Himalaya CLI not found',
            'timestamp': datetime.now().isoformat()
        }
    
    if code != 0 or output is None:
        return {
            'status': 'error',
            'error': 'Failed to fetch emails',
            'timestamp': datetime.now().isoformat()
        }
    
    # Parse email list (format depends on Himalaya output)
    # This is a simplified parser - adjust based on actual output format
    urgent_emails = []
    lines = output.strip().split('\n')
    
    for line in lines[2:]:  # Skip header rows
        if not line.strip():
            continue
        
        # Parse line - adjust based on actual Himalaya format
        # Expected format: ID | FLAGS | SUBJECT | SENDER | DATE
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 4:
            continue
        
        email_id = parts[0]
        flags = parts[1] if len(parts) > 1 else ''
        subject = parts[2] if len(parts) > 2 else 'No subject'
        sender = parts[3] if len(parts) > 3 else 'Unknown'
        
        # Skip if already seen
        if email_id in state['seen_ids']:
            continue
        
        # Check if urgent
        if 'seen' not in flags.lower() and is_urgent(subject, sender):
            urgent_emails.append({
                'id': email_id,
                'subject': subject,
                'sender': sender
            })
            state['seen_ids'].append(email_id)
    
    # Keep only last 500 seen IDs to prevent bloat
    state['seen_ids'] = state['seen_ids'][-500:]
    state['last_check'] = datetime.now().isoformat()
    save_state(state)
    
    # Return top 3 urgent
    result = {
        'status': 'ok',
        'urgent_count': len(urgent_emails),
        'top_urgent': urgent_emails[:3],
        'timestamp': datetime.now().isoformat()
    }
    
    return result


if __name__ == '__main__':
    result = check_inbox()
    print(json.dumps(result, indent=2))
    
    # Exit code indicates urgency
    sys.exit(1 if result.get('urgent_count', 0) > 0 else 0)
