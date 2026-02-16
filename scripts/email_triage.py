#!/usr/bin/env python3
"""
Smart Email Triage - AI-powered email classification and alerts
Uses Gmail API + Ollama for local classification
"""

import os
import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import subprocess
import base64
import re

DATA_DIR = Path(__file__).parent.parent / 'data'
EMAIL_DATA_PATH = DATA_DIR / 'email_classifications.json'
CREDENTIALS_PATH = Path(__file__).parent.parent / 'credentials' / 'gmail_credentials.json'
TOKEN_PATH = Path(__file__).parent.parent / 'credentials' / 'gmail_token.pickle'

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.modify']

# Classification categories
CATEGORIES = {
    'urgent': '🔴 Urgent',
    'action_required': '🟡 Action Required',
    'fyi': '🔵 FYI',
    'spam': '⚫ Spam/Promo',
}

# Urgency keywords
URGENT_KEYWORDS = [
    'urgent', 'asap', 'immediate', 'deadline', 'today', 'emergency',
    'critical', 'important', 'time-sensitive', 'need your input'
]

SPAM_KEYWORDS = [
    'unsubscribe', 'promotional', 'sale', 'discount', 'offer',
    'newsletter', 'marketing', 'advertisement'
]

def load_email_data():
    """Load email classifications from JSON"""
    if EMAIL_DATA_PATH.exists():
        with open(EMAIL_DATA_PATH, 'r') as f:
            return json.load(f)
    return {
        'emails': [],
        'last_check': None,
        'stats': {
            'urgent': 0,
            'action_required': 0,
            'fyi': 0,
            'spam': 0,
        }
    }

def save_email_data(data):
    """Save email data to JSON"""
    DATA_DIR.mkdir(exist_ok=True)
    with open(EMAIL_DATA_PATH, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def get_gmail_service():
    """Authenticate and return Gmail service"""
    creds = None
    
    # Load credentials from token
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    # Refresh or create new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                print("❌ Gmail credentials not found!")
                print(f"   Place your credentials.json at: {CREDENTIALS_PATH}")
                print("   Get it from: https://console.cloud.google.com/")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials
        TOKEN_PATH.parent.mkdir(exist_ok=True)
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def classify_email_with_ollama(subject, sender, body_preview):
    """Use Ollama to classify email"""
    try:
        # Build classification prompt
        prompt = f"""Classify this email into ONE category:
- URGENT: From boss/client, deadline-related, time-sensitive
- ACTION_REQUIRED: Needs response within 24h
- FYI: Informational, no action needed
- SPAM: Promotional, newsletters, marketing

Email:
From: {sender}
Subject: {subject}
Preview: {body_preview}

Category (respond with just one word: URGENT, ACTION_REQUIRED, FYI, or SPAM):"""

        # Call Ollama
        result = subprocess.run(
            ['ollama', 'run', 'qwen2.5', prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        classification = result.stdout.strip().upper()
        
        # Map to our categories
        if 'URGENT' in classification:
            return 'urgent'
        elif 'ACTION' in classification or 'ACTION_REQUIRED' in classification:
            return 'action_required'
        elif 'SPAM' in classification:
            return 'spam'
        else:
            return 'fyi'
    
    except Exception as e:
        print(f"⚠️  Ollama classification failed: {e}")
        # Fallback to rule-based
        return classify_email_rules(subject, sender, body_preview)

def classify_email_rules(subject, sender, body_preview):
    """Rule-based email classification (fallback)"""
    subject_lower = subject.lower()
    body_lower = body_preview.lower()
    combined = f"{subject_lower} {body_lower}"
    
    # Check for spam first
    if any(keyword in combined for keyword in SPAM_KEYWORDS):
        return 'spam'
    
    # Check for urgent
    if any(keyword in combined for keyword in URGENT_KEYWORDS):
        return 'urgent'
    
    # Check for action required (questions, requests)
    if any(word in combined for word in ['?', 'please', 'could you', 'can you', 'need']):
        return 'action_required'
    
    # Default to FYI
    return 'fyi'

def get_email_body_preview(message):
    """Extract email body preview"""
    try:
        if 'payload' in message:
            payload = message['payload']
            
            # Try to get body from parts
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = part.get('body', {}).get('data', '')
                        if body:
                            decoded = base64.urlsafe_b64decode(body).decode('utf-8')
                            return decoded[:500]  # First 500 chars
            
            # Try direct body
            if 'body' in payload and 'data' in payload['body']:
                body = payload['body']['data']
                decoded = base64.urlsafe_b64decode(body).decode('utf-8')
                return decoded[:500]
        
        return ''
    except Exception:
        return ''

def check_inbox():
    """Check inbox and classify new emails"""
    print(f"[{datetime.now()}] Checking inbox...")
    
    service = get_gmail_service()
    if not service:
        return
    
    data = load_email_data()
    
    # Get emails from last hour (or all if first run)
    query = 'is:unread'
    if data.get('last_check'):
        last_check = datetime.fromisoformat(data['last_check'])
        # Gmail search format: after:2024/02/15
        after_date = last_check.strftime('%Y/%m/%d')
        query = f'is:unread after:{after_date}'
    
    try:
        # Fetch emails
        results = service.users().messages().list(userId='me', q=query, maxResults=50).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("✅ No new emails")
            data['last_check'] = datetime.now().isoformat()
            save_email_data(data)
            return
        
        print(f"📧 Found {len(messages)} new emails")
        
        classified_emails = []
        
        for msg in messages:
            # Get full message
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Get body preview
            body_preview = get_email_body_preview(message)
            
            # Classify email
            print(f"   Classifying: {subject[:50]}...")
            category = classify_email_with_ollama(subject, sender, body_preview)
            
            email_data = {
                'id': msg['id'],
                'subject': subject,
                'sender': sender,
                'date': date,
                'category': category,
                'body_preview': body_preview[:200],
                'classified_at': datetime.now().isoformat(),
                'gmail_url': f"https://mail.google.com/mail/u/0/#inbox/{msg['id']}",
            }
            
            classified_emails.append(email_data)
            data['stats'][category] += 1
        
        # Save classifications
        data['emails'].extend(classified_emails)
        data['last_check'] = datetime.now().isoformat()
        
        # Keep only last 1000 emails
        if len(data['emails']) > 1000:
            data['emails'] = data['emails'][-1000:]
        
        save_email_data(data)
        
        # Print summary
        print(f"\n📊 Classification Summary:")
        print(f"   🔴 Urgent: {sum(1 for e in classified_emails if e['category'] == 'urgent')}")
        print(f"   🟡 Action Required: {sum(1 for e in classified_emails if e['category'] == 'action_required')}")
        print(f"   🔵 FYI: {sum(1 for e in classified_emails if e['category'] == 'fyi')}")
        print(f"   ⚫ Spam: {sum(1 for e in classified_emails if e['category'] == 'spam')}")
        
        # Alert on urgent emails
        urgent_emails = [e for e in classified_emails if e['category'] == 'urgent']
        if urgent_emails:
            print(f"\n🚨 URGENT EMAIL ALERTS:")
            for email in urgent_emails:
                print(f"\n   🔴 {email['subject']}")
                print(f"      From: {email['sender']}")
                print(f"      Preview: {email['body_preview'][:100]}...")
                print(f"      Link: {email['gmail_url']}")
        
        # Auto-archive spam
        spam_emails = [e for e in classified_emails if e['category'] == 'spam']
        if spam_emails:
            print(f"\n🗑️  Auto-archiving {len(spam_emails)} spam emails...")
            for email in spam_emails:
                try:
                    service.users().messages().modify(
                        userId='me',
                        id=email['id'],
                        body={'removeLabelIds': ['INBOX']}
                    ).execute()
                except Exception as e:
                    print(f"   Failed to archive {email['id']}: {e}")
        
    except Exception as e:
        print(f"❌ Error checking inbox: {e}")

def generate_daily_summary():
    """Generate daily email summary"""
    data = load_email_data()
    
    # Get today's emails
    today = datetime.now().date()
    today_emails = [
        e for e in data['emails']
        if datetime.fromisoformat(e['classified_at']).date() == today
    ]
    
    if not today_emails:
        print("No emails processed today")
        return
    
    print(f"\n📊 DAILY EMAIL SUMMARY - {today}\n")
    
    by_category = {
        'urgent': [e for e in today_emails if e['category'] == 'urgent'],
        'action_required': [e for e in today_emails if e['category'] == 'action_required'],
        'fyi': [e for e in today_emails if e['category'] == 'fyi'],
        'spam': [e for e in today_emails if e['category'] == 'spam'],
    }
    
    print(f"Total: {len(today_emails)} emails")
    print(f"   🔴 Urgent: {len(by_category['urgent'])}")
    print(f"   🟡 Action Required: {len(by_category['action_required'])}")
    print(f"   🔵 FYI: {len(by_category['fyi'])}")
    print(f"   ⚫ Spam: {len(by_category['spam'])}")
    
    # Show urgent emails
    if by_category['urgent']:
        print(f"\n🔴 URGENT EMAILS:")
        for email in by_category['urgent']:
            print(f"   • {email['subject']}")
            print(f"     From: {email['sender']}")
    
    # Show action required
    if by_category['action_required']:
        print(f"\n🟡 ACTION REQUIRED:")
        for email in by_category['action_required'][:5]:
            print(f"   • {email['subject']}")
            print(f"     From: {email['sender']}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Email Triage System')
    parser.add_argument('--check', action='store_true', help='Check inbox now')
    parser.add_argument('--summary', action='store_true', help='Show daily summary')
    parser.add_argument('--setup', action='store_true', help='Setup Gmail authentication')
    
    args = parser.parse_args()
    
    if args.setup:
        print("🔐 Setting up Gmail authentication...")
        service = get_gmail_service()
        if service:
            print("✅ Authentication successful!")
    elif args.summary:
        generate_daily_summary()
    else:
        check_inbox()

if __name__ == '__main__':
    main()
