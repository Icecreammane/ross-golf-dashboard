#!/usr/bin/env python3
"""
Email Daemon for Jarvis
Monitors bigmeatyclawd@gmail.com for important emails
Runs every 30 minutes via launchd
"""

import imaplib
import email
from email.header import decode_header
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import traceback
from dotenv import load_dotenv
import re

# Paths
WORKSPACE = Path("/Users/clawdbot/clawd")
DATA_FILE = WORKSPACE / "data" / "email-summary.json"
LOG_FILE = WORKSPACE / "logs" / "email-daemon.log"
STATE_FILE = WORKSPACE / "data" / "email-daemon-state.json"

# Ensure directories exist
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Load environment variables
load_dotenv(WORKSPACE / ".env")

# Email configuration
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
EMAIL_ADDRESS = os.getenv("JARVIS_EMAIL", "bigmeatyclawd@gmail.com")
EMAIL_PASSWORD = os.getenv("JARVIS_EMAIL_PASSWORD")

# Importance filters
IMPORTANT_SENDERS = [
    # Boss/work related
    "ross",
    "manager",
    "ceo",
    "founder",
    # Investors
    "investor",
    "venture",
    "capital",
    "funding",
    # Business
    "stripe",
    "paypal",
    "bank",
    "invoice",
]

IMPORTANT_KEYWORDS = [
    "urgent",
    "deadline",
    "action needed",
    "action required",
    "asap",
    "important",
    "payment",
    "invoice",
    "overdue",
    "expired",
    "expiring",
    "verify",
    "confirm",
    "security alert",
    "suspended",
    "required",
    "immediately",
]

IMPORTANT_DOMAINS = [
    # Add specific domains that are always important
    "@stripe.com",
    "@github.com",
    "@openai.com",
    "@anthropic.com",
]


def log(message, level="INFO"):
    """Log message to file and stdout"""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] [{level}] {message}"
    
    print(log_entry)
    
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"Failed to write to log file: {e}")


def load_state():
    """Load last processed email state"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            log(f"Failed to load state: {e}", "WARN")
    return {"last_uid": 0, "last_check": None}


def save_state(state):
    """Save last processed email state"""
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        log(f"Failed to save state: {e}", "ERROR")


def decode_header_value(header):
    """Decode email header to string"""
    if header is None:
        return ""
    
    decoded_parts = decode_header(header)
    result = []
    
    for content, encoding in decoded_parts:
        if isinstance(content, bytes):
            try:
                result.append(content.decode(encoding or 'utf-8', errors='replace'))
            except:
                result.append(content.decode('latin-1', errors='replace'))
        else:
            result.append(str(content))
    
    return ''.join(result)


def is_important(sender, subject, from_addr):
    """Determine if email is important based on filters"""
    sender_lower = sender.lower()
    subject_lower = subject.lower()
    from_addr_lower = from_addr.lower()
    
    # Check domains
    for domain in IMPORTANT_DOMAINS:
        if domain.lower() in from_addr_lower:
            return True, f"important domain: {domain}"
    
    # Check sender patterns
    for pattern in IMPORTANT_SENDERS:
        if pattern.lower() in sender_lower or pattern.lower() in from_addr_lower:
            return True, f"important sender: {pattern}"
    
    # Check subject keywords
    for keyword in IMPORTANT_KEYWORDS:
        if keyword.lower() in subject_lower:
            return True, f"keyword: {keyword}"
    
    return False, None


def extract_body(msg):
    """Extract email body text"""
    body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            
            # Get text/plain parts
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode('utf-8', errors='replace')
                except Exception as e:
                    log(f"Failed to decode body part: {e}", "WARN")
    else:
        # Not multipart
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='replace')
        except Exception as e:
            log(f"Failed to decode body: {e}", "WARN")
    
    # Clean up body - take first 500 chars for summary
    body = body.strip()
    if len(body) > 500:
        body = body[:500] + "..."
    
    return body


def summarize_email(sender, subject, body, reason):
    """Create email summary"""
    # Extract key points from body
    lines = [line.strip() for line in body.split('\n') if line.strip()]
    key_points = lines[:3]  # First 3 lines as key points
    
    return {
        "sender": sender,
        "subject": subject,
        "key_points": key_points,
        "preview": body[:200] + "..." if len(body) > 200 else body,
        "importance_reason": reason,
        "timestamp": datetime.now().isoformat()
    }


def fetch_and_process_emails():
    """Main email fetching and processing logic"""
    if not EMAIL_PASSWORD:
        log("JARVIS_EMAIL_PASSWORD not set in .env file", "ERROR")
        return False
    
    log(f"Connecting to {IMAP_SERVER} as {EMAIL_ADDRESS}")
    
    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        log("Successfully connected to IMAP server")
        
        # Select inbox
        mail.select("INBOX")
        
        # Load state
        state = load_state()
        last_uid = state.get("last_uid", 0)
        
        # Search for unread emails
        status, message_ids = mail.search(None, "UNSEEN")
        
        if status != "OK":
            log("Failed to search emails", "ERROR")
            return False
        
        email_ids = message_ids[0].split()
        log(f"Found {len(email_ids)} unread emails")
        
        if not email_ids:
            log("No new emails to process")
            state["last_check"] = datetime.now().isoformat()
            save_state(state)
            mail.logout()
            return True
        
        # Load existing summaries
        summaries = []
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, "r") as f:
                    summaries = json.load(f)
            except Exception as e:
                log(f"Failed to load existing summaries: {e}", "WARN")
        
        # Process each email
        important_count = 0
        for email_id in email_ids:
            try:
                # Fetch email
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                
                if status != "OK":
                    log(f"Failed to fetch email {email_id}", "WARN")
                    continue
                
                # Parse email
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Extract headers
                subject = decode_header_value(msg.get("Subject", ""))
                from_header = decode_header_value(msg.get("From", ""))
                
                # Parse sender name and email
                sender_match = re.match(r'"?([^"<]+)"?\s*<?([^>]*)>?', from_header)
                if sender_match:
                    sender_name = sender_match.group(1).strip()
                    sender_email = sender_match.group(2).strip() or from_header
                else:
                    sender_name = from_header
                    sender_email = from_header
                
                date = msg.get("Date", "")
                
                log(f"Processing: {subject} from {sender_name}")
                
                # Check if important
                important, reason = is_important(sender_name, subject, sender_email)
                
                if important:
                    log(f"✓ IMPORTANT EMAIL detected: {reason}", "INFO")
                    
                    # Extract body
                    body = extract_body(msg)
                    
                    # Create summary
                    summary = summarize_email(sender_name, subject, body, reason)
                    summary["date"] = date
                    summary["from_email"] = sender_email
                    
                    summaries.append(summary)
                    important_count += 1
                else:
                    log(f"  Regular email, skipping")
                
            except Exception as e:
                log(f"Error processing email {email_id}: {e}", "ERROR")
                log(traceback.format_exc(), "ERROR")
        
        # Save summaries
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(summaries, f, indent=2)
            log(f"Saved {len(summaries)} total summaries ({important_count} new)")
        except Exception as e:
            log(f"Failed to save summaries: {e}", "ERROR")
        
        # Update state
        if email_ids:
            state["last_uid"] = int(email_ids[-1])
        state["last_check"] = datetime.now().isoformat()
        save_state(state)
        
        # Logout
        mail.logout()
        log(f"Completed: processed {len(email_ids)} emails, {important_count} important")
        
        return True
        
    except imaplib.IMAP4.error as e:
        log(f"IMAP error: {e}", "ERROR")
        return False
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
        log(traceback.format_exc(), "ERROR")
        return False


def main():
    """Main entry point"""
    log("=" * 80)
    log("Email Daemon starting")
    log("=" * 80)
    
    try:
        success = fetch_and_process_emails()
        
        if success:
            log("Email daemon completed successfully")
            sys.exit(0)
        else:
            log("Email daemon completed with errors", "ERROR")
            sys.exit(1)
    except Exception as e:
        log(f"Fatal error: {e}", "ERROR")
        log(traceback.format_exc(), "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
