#!/usr/bin/env python3
"""
Simple email sender using SMTP
Usage: python3 send-email.py <to> <subject> <body>
"""

import smtplib
import sys
import json
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Load credentials from secure storage
CREDENTIALS_PATH = Path.home() / "clawd" / ".credentials" / "gmail_credentials.json"
with open(CREDENTIALS_PATH) as f:
    credentials = json.load(f)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
FROM_EMAIL = credentials["email"]
FROM_NAME = "Jarvis"
PASSWORD = credentials["smtp_app_password"]

def send_email(to_email, subject, body, body_html=None):
    """Send email via Gmail SMTP"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
        
        # Add plain text body
        part1 = MIMEText(body, 'plain')
        msg.attach(part1)
        
        # Add HTML body if provided
        if body_html:
            part2 = MIMEText(body_html, 'html')
            msg.attach(part2)
        
        # Connect and send
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(FROM_EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True, "✅ Email sent successfully"
    
    except Exception as e:
        return False, f"❌ Failed to send: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 send-email.py <to> <subject> <body>")
        sys.exit(1)
    
    to = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    
    success, message = send_email(to, subject, body)
    print(message)
    sys.exit(0 if success else 1)
