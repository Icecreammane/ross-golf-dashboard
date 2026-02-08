"""
Email Parser for Golf Coaching Inquiries
Monitors email for coaching-related keywords and logs inquiries
"""

import imaplib
import email
import os
import logging
import json
from datetime import datetime
from email.header import decode_header

logger = logging.getLogger(__name__)

class EmailParser:
    def __init__(self):
        self.username = os.getenv('EMAIL_USERNAME', '')
        self.password = os.getenv('EMAIL_PASSWORD', '')
        self.imap_server = 'imap.gmail.com'
        
        # Keywords to identify coaching inquiries
        self.coaching_keywords = [
            'golf coaching',
            'golf lessons',
            'golf instruction',
            'swing help',
            'golf tips',
            'coaching inquiry',
            'book a lesson',
            'golf training'
        ]
    
    def connect(self):
        """Connect to email server"""
        try:
            if not self.username or not self.password:
                logger.warning("Email credentials not configured")
                return None
            
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.username, self.password)
            logger.info("Email connection successful")
            return mail
        except Exception as e:
            logger.error(f"Email connection failed: {e}")
            return None
    
    def parse_emails(self, days=7):
        """Parse recent emails for coaching inquiries"""
        mail = self.connect()
        if not mail:
            return []
        
        inquiries = []
        
        try:
            # Select inbox
            mail.select('inbox')
            
            # Search for recent emails
            from datetime import timedelta
            date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
            status, messages = mail.search(None, f'(SINCE {date})')
            
            if status != 'OK':
                logger.error("Failed to search emails")
                return inquiries
            
            email_ids = messages[0].split()
            
            for email_id in email_ids[-50:]:  # Last 50 emails
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                
                if status != 'OK':
                    continue
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Decode subject
                        subject = self.decode_subject(msg['Subject'])
                        
                        # Get sender
                        sender = msg['From']
                        
                        # Get date
                        date_str = msg['Date']
                        
                        # Get body
                        body = self.get_email_body(msg)
                        
                        # Check for coaching keywords
                        text_to_check = f"{subject} {body}".lower()
                        
                        if any(keyword in text_to_check for keyword in self.coaching_keywords):
                            inquiry = {
                                'source': 'email',
                                'contact': sender,
                                'subject': subject,
                                'message': body[:500],  # First 500 chars
                                'date': date_str,
                                'created': datetime.now().isoformat()
                            }
                            inquiries.append(inquiry)
                            logger.info(f"Found coaching inquiry from {sender}")
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            logger.error(f"Error parsing emails: {e}")
        
        return inquiries
    
    def decode_subject(self, subject):
        """Decode email subject"""
        if not subject:
            return ""
        
        decoded = decode_header(subject)
        subject_text = ""
        
        for content, encoding in decoded:
            if isinstance(content, bytes):
                if encoding:
                    subject_text += content.decode(encoding)
                else:
                    subject_text += content.decode('utf-8', errors='ignore')
            else:
                subject_text += content
        
        return subject_text
    
    def get_email_body(self, msg):
        """Extract email body"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                pass
        
        return body.strip()

def check_for_inquiries():
    """Standalone function to check for new inquiries"""
    parser = EmailParser()
    inquiries = parser.parse_emails(days=1)  # Check last 24 hours
    
    if inquiries:
        logger.info(f"Found {len(inquiries)} new coaching inquiries")
        
        # Save to file
        inquiry_file = 'data/coaching_inquiries.json'
        os.makedirs('data', exist_ok=True)
        
        existing = []
        if os.path.exists(inquiry_file):
            with open(inquiry_file, 'r') as f:
                existing = json.load(f)
        
        # Append new inquiries
        existing.extend(inquiries)
        
        with open(inquiry_file, 'w') as f:
            json.dump(existing, f, indent=2)
        
        logger.info(f"Saved inquiries to {inquiry_file}")
    
    return inquiries

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    inquiries = check_for_inquiries()
    print(f"Found {len(inquiries)} coaching inquiries")
