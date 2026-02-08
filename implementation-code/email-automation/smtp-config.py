"""
SMTP Configuration for Gmail
Handles email sending via Gmail SMTP
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json

# Gmail SMTP Configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587  # TLS port
SMTP_EMAIL = os.getenv('SMTP_EMAIL', 'bigmeatyclawd@gmail.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')  # App-specific password

# Load from .credentials if password not in env
if not SMTP_PASSWORD:
    try:
        with open(os.path.expanduser('~/.credentials/gmail-smtp.json'), 'r') as f:
            creds = json.load(f)
            SMTP_PASSWORD = creds.get('password')
    except FileNotFoundError:
        print("Warning: SMTP password not found. Set SMTP_PASSWORD env var.")


class EmailSender:
    """Gmail SMTP email sender"""
    
    def __init__(self, smtp_email=SMTP_EMAIL, smtp_password=SMTP_PASSWORD):
        self.smtp_email = smtp_email
        self.smtp_password = smtp_password
        
        if not self.smtp_password:
            raise ValueError("SMTP password not configured")
    
    def send_email(self, to_email, subject, html_body, text_body=None, attachments=None):
        """
        Send an email via Gmail SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_body: HTML version of email body
            text_body: Plain text version (optional, auto-generated if not provided)
            attachments: List of file paths to attach (optional)
        
        Returns:
            bool: True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text version (fallback)
            if text_body:
                text_part = MIMEText(text_body, 'plain')
                msg.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    self._add_attachment(msg, file_path)
            
            # Connect to Gmail SMTP server
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()  # Enable TLS encryption
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(msg)
            
            print(f"✓ Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send email to {to_email}: {str(e)}")
            return False
    
    def _add_attachment(self, msg, file_path):
        """Add file attachment to email"""
        try:
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                
                filename = os.path.basename(file_path)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                msg.attach(part)
        except Exception as e:
            print(f"Warning: Failed to attach {file_path}: {str(e)}")
    
    def send_bulk(self, recipients, subject, html_body, text_body=None):
        """
        Send same email to multiple recipients
        
        Args:
            recipients: List of email addresses
            subject: Email subject
            html_body: HTML body
            text_body: Plain text body (optional)
        
        Returns:
            dict: {success: int, failed: int, errors: list}
        """
        results = {'success': 0, 'failed': 0, 'errors': []}
        
        for email in recipients:
            try:
                success = self.send_email(email, subject, html_body, text_body)
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({'email': email, 'error': str(e)})
        
        return results
    
    def test_connection(self):
        """Test SMTP connection"""
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(self.smtp_email, self.smtp_password)
            print("✓ SMTP connection successful")
            return True
        except Exception as e:
            print(f"✗ SMTP connection failed: {str(e)}")
            return False


# Helper function for quick sending
def send_email(to_email, subject, html_body, text_body=None):
    """Quick helper to send email"""
    sender = EmailSender()
    return sender.send_email(to_email, subject, html_body, text_body)


# HTML email template wrapper
def wrap_html_email(content, title=None):
    """
    Wrap email content in a responsive HTML template
    
    Args:
        content: HTML content to wrap
        title: Optional title/heading
    
    Returns:
        str: Full HTML email template
    """
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title or 'Email'}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .email-container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .email-header {{
            background: linear-gradient(135deg, #5469d4 0%, #3c52b2 100%);
            color: #ffffff;
            padding: 30px 20px;
            text-align: center;
        }}
        .email-header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .email-body {{
            padding: 30px 20px;
        }}
        .email-body h2 {{
            color: #1a1a1a;
            font-size: 20px;
            margin-top: 0;
        }}
        .email-body p {{
            margin: 15px 0;
            color: #555;
        }}
        .button {{
            display: inline-block;
            padding: 12px 24px;
            background-color: #5469d4;
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin: 20px 0;
        }}
        .button:hover {{
            background-color: #3c52b2;
        }}
        .email-footer {{
            background-color: #f9f9f9;
            padding: 20px;
            text-align: center;
            font-size: 14px;
            color: #888;
            border-top: 1px solid #eee;
        }}
        .email-footer a {{
            color: #5469d4;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        {f'<div class="email-header"><h1>{title}</h1></div>' if title else ''}
        <div class="email-body">
            {content}
        </div>
        <div class="email-footer">
            <p>You're receiving this email because you signed up at YourProduct.com</p>
            <p><a href="{{{{unsubscribe_url}}}}">Unsubscribe</a> | <a href="https://yourproduct.com">Visit Website</a></p>
            <p>© 2024 YourProduct. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
    """


if __name__ == '__main__':
    # Test SMTP connection
    sender = EmailSender()
    sender.test_connection()
