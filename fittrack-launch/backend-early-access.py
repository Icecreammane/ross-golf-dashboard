"""
Backend API Endpoint for Early-Access Email Capture

Purpose: Handle email signups from the early-access form
Location: Add to main Flask app (app_saas.py or similar)
Frontend: Works with email-capture-form.html

Features:
- Captures and stores email + timestamp
- Validates email format
- Prevents duplicate signups
- Returns JSON responses
- Stores in simple text file (can upgrade to database later)

Integration:
  Copy these routes into your main Flask app
  
Test:
  curl -X POST http://localhost:5000/api/early-access \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com"}'
"""

from flask import jsonify, request
import os
import re
from datetime import datetime


# Add these routes to your Flask app

@app.route('/api/early-access', methods=['POST'])
def early_access_signup():
    """
    Capture early-access email signup
    
    Request body:
      { "email": "user@example.com" }
    
    Response (success):
      { "success": true, "message": "You're on the list!" }
    
    Response (error):
      { "success": false, "error": "Invalid email" }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        email = data.get('email', '').strip().lower()
        
        # Validate email format
        if not email:
            return jsonify({
                "success": False,
                "error": "Email is required"
            }), 400
        
        # Basic email validation (RFC 5322 simplified)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({
                "success": False,
                "error": "Invalid email format"
            }), 400
        
        # Ensure data directory exists
        data_dir = os.path.join(os.getcwd(), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        email_file = os.path.join(data_dir, 'early-access-emails.txt')
        
        # Check if email already exists (prevent duplicates)
        if os.path.exists(email_file):
            with open(email_file, 'r') as f:
                existing_emails = [line.split(',')[0].strip() for line in f.readlines()]
                if email in existing_emails:
                    return jsonify({
                        "success": True,
                        "message": "You're already on the list! See you at launch."
                    }), 200
        
        # Save email with timestamp
        timestamp = datetime.now().isoformat()
        with open(email_file, 'a') as f:
            f.write(f"{email},{timestamp}\n")
        
        # Log signup (optional)
        print(f"[Early Access Signup] {email} at {timestamp}")
        
        # Optional: Send to email marketing service
        # Example: Mailchimp, ConvertKit, SendGrid
        # add_to_mailchimp(email)
        
        # Optional: Send confirmation email
        # send_confirmation_email(email)
        
        return jsonify({
            "success": True,
            "message": "You're on the list! Launch day is Feb 13 at 7pm."
        }), 200
        
    except Exception as e:
        # Log error (production: use proper logging)
        print(f"[Error] Early access signup failed: {str(e)}")
        
        return jsonify({
            "success": False,
            "error": "Server error. Please try again."
        }), 500


@app.route('/api/early-access/count', methods=['GET'])
def early_access_count():
    """
    Get count of early-access signups
    
    Use this to check progress:
      curl http://localhost:5000/api/early-access/count
    
    Returns:
      { "count": 42 }
    """
    try:
        email_file = os.path.join(os.getcwd(), 'data', 'early-access-emails.txt')
        
        if os.path.exists(email_file):
            with open(email_file, 'r') as f:
                count = len(f.readlines())
            return jsonify({"count": count}), 200
        
        return jsonify({"count": 0}), 200
        
    except Exception as e:
        print(f"[Error] Failed to get count: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/early-access/export', methods=['GET'])
def early_access_export():
    """
    Export all early-access emails (for launch day)
    
    ⚠️ SECURITY: Add authentication before using this in production!
    
    Example with simple token:
      @app.route('/api/early-access/export/<token>')
      def early_access_export(token):
          if token != os.environ.get('ADMIN_TOKEN'):
              return "Unauthorized", 401
          # ... rest of code
    
    Returns:
      {
        "count": 42,
        "emails": [
          {"email": "user1@example.com", "timestamp": "2026-02-10T10:30:00"},
          {"email": "user2@example.com", "timestamp": "2026-02-11T14:22:00"}
        ]
      }
    """
    try:
        email_file = os.path.join(os.getcwd(), 'data', 'early-access-emails.txt')
        
        if not os.path.exists(email_file):
            return jsonify({
                "count": 0,
                "emails": []
            }), 200
        
        emails = []
        with open(email_file, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    emails.append({
                        "email": parts[0],
                        "timestamp": parts[1]
                    })
        
        return jsonify({
            "count": len(emails),
            "emails": emails
        }), 200
        
    except Exception as e:
        print(f"[Error] Failed to export: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Optional: Mailchimp Integration
def add_to_mailchimp(email):
    """
    Add email to Mailchimp list
    
    Requires:
      pip install mailchimp-marketing
    
    Setup:
      1. Get Mailchimp API key: mailchimp.com/developer/
      2. Get List ID from Mailchimp dashboard
      3. Set environment variables:
         MAILCHIMP_API_KEY=your-key
         MAILCHIMP_LIST_ID=your-list-id
    """
    try:
        import mailchimp_marketing as MailchimpMarketing
        
        api_key = os.environ.get('MAILCHIMP_API_KEY')
        list_id = os.environ.get('MAILCHIMP_LIST_ID')
        
        if not api_key or not list_id:
            print("Mailchimp not configured, skipping...")
            return
        
        # Extract datacenter from API key (e.g., us1)
        datacenter = api_key.split('-')[1]
        
        client = MailchimpMarketing.Client()
        client.set_config({
            "api_key": api_key,
            "server": datacenter
        })
        
        # Add subscriber
        response = client.lists.add_list_member(list_id, {
            "email_address": email,
            "status": "subscribed",
            "tags": ["early-access", "fittrack-launch"]
        })
        
        print(f"[Mailchimp] Added {email} to list")
        
    except Exception as e:
        print(f"[Mailchimp Error] {str(e)}")


# Optional: Send Confirmation Email
def send_confirmation_email(email):
    """
    Send confirmation email to new signup
    
    Options:
    - SendGrid
    - Mailgun
    - AWS SES
    - SMTP (Gmail, etc.)
    
    Example with SendGrid:
      pip install sendgrid
    """
    # Implement if needed
    pass


# Usage in your Flask app:
"""
# In app_saas.py:

from flask import Flask, jsonify, request

app = Flask(__name__)

# ... other routes ...

# Copy the routes above here
@app.route('/api/early-access', methods=['POST'])
def early_access_signup():
    # ... (code from above)

@app.route('/api/early-access/count', methods=['GET'])
def early_access_count():
    # ... (code from above)

# ... rest of your app ...

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""


# Testing:
"""
# Test signup
curl -X POST http://localhost:5000/api/early-access \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'

# Expected response:
# {"success":true,"message":"You're on the list! Launch day is Feb 13 at 7pm."}

# Test duplicate
curl -X POST http://localhost:5000/api/early-access \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'

# Expected response:
# {"success":true,"message":"You're already on the list! See you at launch."}

# Test invalid email
curl -X POST http://localhost:5000/api/early-access \
  -H "Content-Type: application/json" \
  -d '{"email":"notanemail"}'

# Expected response:
# {"success":false,"error":"Invalid email format"}

# Check count
curl http://localhost:5000/api/early-access/count

# Expected response:
# {"count":1}

# Export emails (for launch day)
curl http://localhost:5000/api/early-access/export

# Expected response:
# {"count":1,"emails":[{"email":"test@example.com","timestamp":"2026-02-10T10:30:00"}]}
"""
