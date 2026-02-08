"""
Support Response Generator
Auto-draft personalized responses using templates
"""

import json
import os
from typing import Dict, Optional
from gmail_monitor import GmailMonitor
import base64
from email.mime.text import MIMEText

class SupportResponder:
    def __init__(self, templates_file='support_templates.json'):
        self.templates_file = templates_file
        self.templates = self.load_templates()
        self.monitor = GmailMonitor()
        
    def load_templates(self) -> Dict:
        """Load response templates"""
        if os.path.exists(self.templates_file):
            with open(self.templates_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get_template(self, category: str) -> Optional[str]:
        """Get template for category"""
        return self.templates.get(category, self.templates.get('general_inquiry'))
    
    def personalize_response(self, template: str, email_data: Dict) -> str:
        """Personalize template with email data"""
        # Extract name from email
        from_email = email_data.get('from', '')
        name = self.extract_name(from_email)
        
        # Replace placeholders
        response = template.replace('{name}', name)
        response = response.replace('{subject}', email_data.get('subject', ''))
        
        return response
    
    def extract_name(self, from_email: str) -> str:
        """Extract name from email address"""
        # Format: "John Doe <john@example.com>"
        if '<' in from_email:
            name = from_email.split('<')[0].strip()
            if name:
                return name.split()[0]  # First name only
        
        # Fallback: use email username
        email = from_email.split('<')[-1].replace('>', '').strip()
        username = email.split('@')[0]
        return username.capitalize()
    
    def create_draft(self, email_id: str, response_text: str) -> bool:
        """Create draft response in Gmail"""
        if not self.monitor.service:
            self.monitor.authenticate()
        
        try:
            # Get original message
            original = self.monitor.service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()
            
            headers = original['payload']['headers']
            to_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            
            # Create reply subject
            if not subject.startswith('Re:'):
                subject = f'Re: {subject}'
            
            # Create message
            message = MIMEText(response_text)
            message['to'] = to_email
            message['subject'] = subject
            message['In-Reply-To'] = email_id
            message['References'] = email_id
            
            # Encode message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Create draft
            draft = self.monitor.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw, 'threadId': original['threadId']}}
            ).execute()
            
            print(f"✅ Draft created: {draft['id']}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create draft: {e}")
            return False
    
    def process_ticket(self, ticket: Dict) -> bool:
        """Process support ticket and create draft response"""
        email_id = ticket['email_id']
        category = ticket.get('category', 'general_inquiry')
        
        print(f"\n📝 Processing ticket: {ticket['subject']}")
        print(f"   Category: {category}")
        
        # Get email details
        email_data = self.monitor.get_email_details(email_id)
        if not email_data:
            print("❌ Could not fetch email details")
            return False
        
        # Get template
        template = self.get_template(category)
        if not template:
            print(f"⚠️  No template for category: {category}")
            return False
        
        # Personalize response
        response = self.personalize_response(template, email_data)
        
        print(f"📧 Draft response:\n{'-'*50}")
        print(response[:200] + "..." if len(response) > 200 else response)
        print('-'*50)
        
        # Create draft
        return self.create_draft(email_id, response)
    
    def process_queue(self):
        """Process all new tickets in queue"""
        queue = self.monitor.load_support_queue()
        new_tickets = [t for t in queue if t['status'] == 'new']
        
        if not new_tickets:
            print("✅ No new tickets to process")
            return 0
        
        print(f"📋 Processing {len(new_tickets)} tickets...")
        
        drafts_created = 0
        for ticket in new_tickets:
            success = self.process_ticket(ticket)
            
            if success:
                # Update ticket status
                ticket['status'] = 'drafted'
                ticket['drafted_at'] = datetime.now().isoformat()
                drafts_created += 1
        
        # Save updated queue
        self.monitor.save_support_queue(queue)
        
        print(f"\n✅ Processed {len(new_tickets)} tickets")
        return drafts_created


if __name__ == "__main__":
    from datetime import datetime
    
    responder = SupportResponder()
    
    print("🤖 Support Responder Active")
    print("="*50)
    
    # Authenticate
    responder.monitor.authenticate()
    
    # Process queue
    responder.process_queue()
