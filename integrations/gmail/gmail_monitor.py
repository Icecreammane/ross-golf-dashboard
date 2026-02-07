"""
Gmail Support Monitor
24/7 email monitoring with priority classification
"""

import os
import json
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import re

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.compose']

class GmailMonitor:
    def __init__(self, token_file='token.pickle', credentials_file='credentials.json'):
        self.token_file = token_file
        self.credentials_file = credentials_file
        self.service = None
        self.support_queue_file = 'support-tickets.json'
        
    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise Exception(f"Credentials file not found: {self.credentials_file}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        return True
    
    def get_unread_emails(self, max_results=50) -> List[Dict]:
        """Fetch unread emails"""
        if not self.service:
            self.authenticate()
        
        try:
            # Search for unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            emails = []
            for msg in messages:
                email_data = self.get_email_details(msg['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            print(f'Error fetching emails: {error}')
            return []
    
    def get_email_details(self, msg_id: str) -> Optional[Dict]:
        """Get full email details"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            
            # Extract key headers
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Extract body
            body = self.extract_body(message['payload'])
            
            return {
                'id': msg_id,
                'subject': subject,
                'from': from_email,
                'date': date,
                'body': body,
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', [])
            }
            
        except HttpError as error:
            print(f'Error getting email details: {error}')
            return None
    
    def extract_body(self, payload) -> str:
        """Extract email body from payload"""
        if 'body' in payload and 'data' in payload['body']:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif 'parts' in part:
                    return self.extract_body(part)
        
        return ""
    
    def classify_priority(self, email: Dict) -> str:
        """Classify email priority (P0/P1/P2/P3)"""
        subject = email['subject'].lower()
        body = email['body'].lower()
        combined = subject + " " + body
        
        # P0: Critical issues (payment failures, app down, data loss)
        p0_keywords = ['payment failed', 'charge failed', 'app down', 'not working', 
                       'crash', 'lost data', 'cant access', "can't access"]
        if any(keyword in combined for keyword in p0_keywords):
            return 'P0'
        
        # P1: High priority (bugs, cancellation requests)
        p1_keywords = ['bug', 'error', 'cancel', 'refund', 'issue', 'problem']
        if any(keyword in combined for keyword in p1_keywords):
            return 'P1'
        
        # P2: Medium (feature requests, questions)
        p2_keywords = ['feature', 'suggest', 'how do i', 'how to', 'question']
        if any(keyword in combined for keyword in p2_keywords):
            return 'P2'
        
        # P3: Low priority (feedback, general inquiries)
        return 'P3'
    
    def detect_fittrack_related(self, email: Dict) -> bool:
        """Check if email is FitTrack-related"""
        combined = (email['subject'] + " " + email['body']).lower()
        
        keywords = ['fittrack', 'macro', 'nutrition', 'calorie', 'fitness', 
                   'tracking', 'diet', 'workout']
        
        return any(keyword in combined for keyword in keywords)
    
    def load_support_queue(self) -> List[Dict]:
        """Load existing support ticket queue"""
        if os.path.exists(self.support_queue_file):
            with open(self.support_queue_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_support_queue(self, queue: List[Dict]):
        """Save support ticket queue"""
        with open(self.support_queue_file, 'w') as f:
            json.dump(queue, f, indent=2)
    
    def add_to_queue(self, email: Dict, priority: str):
        """Add email to support queue"""
        queue = self.load_support_queue()
        
        # Check if already in queue
        if any(ticket['email_id'] == email['id'] for ticket in queue):
            return
        
        ticket = {
            'email_id': email['id'],
            'subject': email['subject'],
            'from': email['from'],
            'priority': priority,
            'received_at': datetime.now().isoformat(),
            'status': 'new',
            'category': self.categorize_email(email)
        }
        
        queue.append(ticket)
        self.save_support_queue(queue)
        
        print(f"📥 Added to queue: {priority} - {email['subject']}")
    
    def categorize_email(self, email: Dict) -> str:
        """Categorize email for template matching"""
        combined = (email['subject'] + " " + email['body']).lower()
        
        categories = {
            'bug_report': ['bug', 'error', 'crash', 'not working', 'broken'],
            'feature_request': ['feature', 'add', 'suggest', 'would be nice', 'idea'],
            'payment_issue': ['payment', 'charge', 'billing', 'refund', 'subscription'],
            'how_to': ['how do i', 'how to', 'how can i', 'tutorial', 'guide'],
            'cancellation': ['cancel', 'unsubscribe', 'stop'],
            'positive_feedback': ['love', 'great', 'awesome', 'thank you', 'amazing']
        }
        
        for category, keywords in categories.items():
            if any(keyword in combined for keyword in keywords):
                return category
        
        return 'general_inquiry'
    
    def scan_inbox(self):
        """Scan inbox for new FitTrack-related emails"""
        print("🔍 Scanning inbox for new emails...")
        
        emails = self.get_unread_emails()
        
        if not emails:
            print("✅ No new emails")
            return []
        
        print(f"📧 Found {len(emails)} unread emails")
        
        new_tickets = []
        for email in emails:
            # Check if FitTrack-related
            if self.detect_fittrack_related(email):
                priority = self.classify_priority(email)
                self.add_to_queue(email, priority)
                new_tickets.append({
                    'email': email,
                    'priority': priority
                })
                
                print(f"  → {priority}: {email['subject'][:50]}")
        
        if not new_tickets:
            print("✅ No FitTrack-related emails")
        else:
            print(f"✅ Processed {len(new_tickets)} FitTrack emails")
        
        return new_tickets
    
    def get_high_priority_tickets(self) -> List[Dict]:
        """Get P0 and P1 tickets"""
        queue = self.load_support_queue()
        return [t for t in queue if t['priority'] in ['P0', 'P1'] and t['status'] == 'new']


if __name__ == "__main__":
    monitor = GmailMonitor()
    
    try:
        print("🔐 Authenticating with Gmail...")
        monitor.authenticate()
        print("✅ Authenticated!")
        
        print("\n" + "="*50)
        new_tickets = monitor.scan_inbox()
        print("="*50)
        
        # Show high priority tickets
        high_priority = monitor.get_high_priority_tickets()
        if high_priority:
            print(f"\n🚨 {len(high_priority)} HIGH PRIORITY tickets need attention:")
            for ticket in high_priority:
                print(f"  {ticket['priority']}: {ticket['subject']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
