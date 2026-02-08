"""
Welcome Email Sequence
7-email onboarding automation
"""

import json
import sqlite3
from datetime import datetime, timedelta
from smtp_config import EmailSender, wrap_html_email


class WelcomeSequence:
    """Manages welcome email sequence for new users"""
    
    def __init__(self, db_path='email_sequences.db'):
        self.db_path = db_path
        self.sender = EmailSender()
        self.templates = self._load_templates()
        self._init_database()
    
    def _load_templates(self):
        """Load email templates from JSON file"""
        with open('email-templates.json', 'r') as f:
            data = json.load(f)
        return data['welcome_sequence']['emails']
    
    def _init_database(self):
        """Initialize SQLite database for tracking sequences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Subscribers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                first_name TEXT,
                signed_up_at TEXT NOT NULL,
                sequence_status TEXT DEFAULT 'active',
                last_email_sent TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Email log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subscriber_id INTEGER,
                email_id TEXT NOT NULL,
                subject TEXT,
                sent_at TEXT NOT NULL,
                opened_at TEXT,
                clicked_at TEXT,
                status TEXT DEFAULT 'sent',
                FOREIGN KEY (subscriber_id) REFERENCES subscribers (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_subscriber(self, email, first_name=None, metadata=None):
        """
        Add new subscriber to welcome sequence
        
        Args:
            email: Subscriber email address
            first_name: Subscriber first name
            metadata: Additional data (dict)
        
        Returns:
            int: Subscriber ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO subscribers (email, first_name, signed_up_at, sequence_status)
                VALUES (?, ?, ?, 'active')
            ''', (email, first_name or email.split('@')[0], datetime.now().isoformat()))
            
            subscriber_id = cursor.lastrowid
            conn.commit()
            
            # Send first email immediately (Day 0)
            self.send_email(subscriber_id, 'welcome_day0')
            
            print(f"✓ Added subscriber: {email} (ID: {subscriber_id})")
            return subscriber_id
            
        except sqlite3.IntegrityError:
            print(f"⚠ Subscriber already exists: {email}")
            cursor.execute('SELECT id FROM subscribers WHERE email = ?', (email,))
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def send_email(self, subscriber_id, email_id):
        """Send specific email to subscriber"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get subscriber info
        cursor.execute('SELECT email, first_name FROM subscribers WHERE id = ?', (subscriber_id,))
        subscriber = cursor.fetchone()
        
        if not subscriber:
            print(f"✗ Subscriber {subscriber_id} not found")
            conn.close()
            return False
        
        email, first_name = subscriber
        
        # Get email template
        template = next((t for t in self.templates if t['id'] == email_id), None)
        if not template:
            print(f"✗ Template {email_id} not found")
            conn.close()
            return False
        
        # Replace variables
        variables = {
            'first_name': first_name,
            'sender_name': 'Ross',  # Customize
            'dashboard_url': 'https://yourproduct.com/dashboard',
            'tutorial_url': 'https://yourproduct.com/tutorial',
            'blog_url': 'https://yourproduct.com/blog',
            'pricing_url': 'https://yourproduct.com/pricing',
            'feedback_url': 'https://yourproduct.com/feedback',
            'delete_account_url': 'https://yourproduct.com/delete-account',
            'unsubscribe_url': f'https://yourproduct.com/unsubscribe?email={email}',
        }
        
        subject = template['subject']
        content = template['content']
        
        for key, value in variables.items():
            subject = subject.replace('{{' + key + '}}', str(value))
            content = content.replace('{{' + key + '}}', str(value))
        
        # Wrap in HTML template
        html_body = wrap_html_email(content, template.get('title'))
        
        # Send email
        success = self.sender.send_email(email, subject, html_body)
        
        # Log email
        if success:
            cursor.execute('''
                INSERT INTO email_log (subscriber_id, email_id, subject, sent_at, status)
                VALUES (?, ?, ?, ?, 'sent')
            ''', (subscriber_id, email_id, subject, datetime.now().isoformat()))
            
            cursor.execute('''
                UPDATE subscribers 
                SET last_email_sent = ? 
                WHERE id = ?
            ''', (email_id, subscriber_id))
            
            conn.commit()
        
        conn.close()
        return success
    
    def get_due_emails(self):
        """Get all emails that should be sent now"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get active subscribers
        cursor.execute('''
            SELECT id, email, signed_up_at, last_email_sent
            FROM subscribers
            WHERE sequence_status = 'active'
        ''')
        
        subscribers = cursor.fetchall()
        due_emails = []
        
        for sub_id, email, signed_up_at, last_email_sent in subscribers:
            signup_date = datetime.fromisoformat(signed_up_at)
            days_since_signup = (datetime.now() - signup_date).days
            
            # Check which emails are due
            for template in self.templates:
                email_id = template['id']
                delay_days = template['delay_days']
                
                # Skip if already sent
                cursor.execute('''
                    SELECT id FROM email_log 
                    WHERE subscriber_id = ? AND email_id = ?
                ''', (sub_id, email_id))
                
                if cursor.fetchone():
                    continue  # Already sent
                
                # Check if due
                if days_since_signup >= delay_days:
                    due_emails.append({
                        'subscriber_id': sub_id,
                        'email': email,
                        'email_id': email_id,
                        'days_overdue': days_since_signup - delay_days
                    })
        
        conn.close()
        return due_emails
    
    def process_due_emails(self):
        """Process all emails that are due to be sent"""
        due_emails = self.get_due_emails()
        
        if not due_emails:
            print("No emails due")
            return {'sent': 0, 'failed': 0}
        
        print(f"Processing {len(due_emails)} due emails...")
        
        results = {'sent': 0, 'failed': 0}
        
        for item in due_emails:
            success = self.send_email(item['subscriber_id'], item['email_id'])
            if success:
                results['sent'] += 1
            else:
                results['failed'] += 1
        
        return results
    
    def unsubscribe(self, email):
        """Unsubscribe user from sequence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE subscribers 
            SET sequence_status = 'unsubscribed' 
            WHERE email = ?
        ''', (email,))
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected:
            print(f"✓ Unsubscribed: {email}")
        else:
            print(f"⚠ Email not found: {email}")
        
        return affected > 0
    
    def get_stats(self):
        """Get sequence statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total subscribers
        cursor.execute('SELECT COUNT(*) FROM subscribers')
        total = cursor.fetchone()[0]
        
        # Active subscribers
        cursor.execute("SELECT COUNT(*) FROM subscribers WHERE sequence_status = 'active'")
        active = cursor.fetchone()[0]
        
        # Unsubscribed
        cursor.execute("SELECT COUNT(*) FROM subscribers WHERE sequence_status = 'unsubscribed'")
        unsubscribed = cursor.fetchone()[0]
        
        # Total emails sent
        cursor.execute('SELECT COUNT(*) FROM email_log')
        emails_sent = cursor.fetchone()[0]
        
        # Emails by type
        cursor.execute('''
            SELECT email_id, COUNT(*) as count
            FROM email_log
            GROUP BY email_id
            ORDER BY count DESC
        ''')
        by_type = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_subscribers': total,
            'active_subscribers': active,
            'unsubscribed': unsubscribed,
            'emails_sent': emails_sent,
            'emails_by_type': dict(by_type)
        }
    
    def list_subscribers(self, status='active', limit=50):
        """List subscribers"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, email, first_name, signed_up_at, sequence_status, last_email_sent
            FROM subscribers
            WHERE sequence_status = ?
            ORDER BY signed_up_at DESC
            LIMIT ?
        ''', (status, limit))
        
        subscribers = cursor.fetchall()
        conn.close()
        
        return subscribers


# CLI Interface
if __name__ == '__main__':
    import sys
    
    sequence = WelcomeSequence()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python welcome-sequence.py add <email> [first_name]")
        print("  python welcome-sequence.py process")
        print("  python welcome-sequence.py stats")
        print("  python welcome-sequence.py list [status]")
        print("  python welcome-sequence.py unsubscribe <email>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'add':
        if len(sys.argv) < 3:
            print("Error: Email required")
            sys.exit(1)
        
        email = sys.argv[2]
        first_name = sys.argv[3] if len(sys.argv) > 3 else None
        sequence.add_subscriber(email, first_name)
    
    elif command == 'process':
        results = sequence.process_due_emails()
        print(f"\n✓ Sent: {results['sent']}")
        print(f"✗ Failed: {results['failed']}")
    
    elif command == 'stats':
        stats = sequence.get_stats()
        print("\n📊 Sequence Statistics")
        print("=" * 50)
        print(f"Total subscribers: {stats['total_subscribers']}")
        print(f"Active: {stats['active_subscribers']}")
        print(f"Unsubscribed: {stats['unsubscribed']}")
        print(f"Emails sent: {stats['emails_sent']}")
        print("\nEmails by type:")
        for email_id, count in stats['emails_by_type'].items():
            print(f"  {email_id}: {count}")
    
    elif command == 'list':
        status = sys.argv[2] if len(sys.argv) > 2 else 'active'
        subscribers = sequence.list_subscribers(status)
        
        print(f"\n📋 {status.title()} Subscribers")
        print("=" * 50)
        for sub in subscribers:
            print(f"{sub[0]:3d}. {sub[1]:30s} {sub[2]:15s} {sub[3][:10]} → {sub[5] or 'none'}")
    
    elif command == 'unsubscribe':
        if len(sys.argv) < 3:
            print("Error: Email required")
            sys.exit(1)
        
        email = sys.argv[2]
        sequence.unsubscribe(email)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
