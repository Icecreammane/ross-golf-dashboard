#!/bin/bash

# Email Automation Test Script
# Tests email sending and sequence setup

echo "🧪 Testing Email Automation System..."
echo ""

# Check Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install Python 3."
    exit 1
fi
echo "✓ Python 3 found"

# Check required files exist
REQUIRED_FILES=("smtp-config.py" "welcome-sequence.py" "scheduler.py" "email-templates.json")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing file: $file"
        exit 1
    fi
done
echo "✓ All required files present"
echo ""

# Test SMTP connection
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Testing SMTP Connection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 smtp-config.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ SMTP connection failed"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check credentials in ~/.credentials/gmail-smtp.json"
    echo "2. Verify app-specific password is correct"
    echo "3. Ensure 2FA is enabled on Gmail account"
    exit 1
fi
echo ""

# Test email sending
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Sending Test Email"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

read -p "Enter test email address (or press Enter to skip): " TEST_EMAIL

if [ -n "$TEST_EMAIL" ]; then
    python3 << EOF
from smtp_config import EmailSender, wrap_html_email

sender = EmailSender()

html_body = wrap_html_email("""
<h2>Test Email</h2>
<p>This is a test email from your email automation system.</p>
<p>If you're reading this, SMTP is configured correctly! ✓</p>
<p><a href='https://yourproduct.com' class='button'>Visit Website</a></p>
""", "Email System Test")

success = sender.send_email(
    "$TEST_EMAIL",
    "Email Automation System - Test",
    html_body
)

if success:
    print("\n✓ Test email sent!")
    print("Check your inbox:", "$TEST_EMAIL")
else:
    print("\n❌ Failed to send test email")
    exit(1)
EOF

    if [ $? -eq 0 ]; then
        echo ""
        read -p "Did you receive the test email? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "⚠️  Email not received. Check spam folder."
        else
            echo "✓ Email delivery confirmed!"
        fi
    fi
else
    echo "⚠️  Skipped test email"
fi
echo ""

# Test database and sequence
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Testing Welcome Sequence"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create test database
TEST_EMAIL="test+$(date +%s)@example.com"
echo "Adding test subscriber: $TEST_EMAIL"
echo ""

python3 welcome-sequence.py add "$TEST_EMAIL" "Test User"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Test subscriber added"
    
    # View stats
    echo ""
    echo "Viewing sequence stats:"
    python3 welcome-sequence.py stats
    
    echo ""
    echo "Listing subscribers:"
    python3 welcome-sequence.py list
else
    echo "❌ Failed to add test subscriber"
    exit 1
fi
echo ""

# Test scheduler
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. Testing Scheduler"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Running scheduler once (processing due emails)..."
python3 scheduler.py once

if [ $? -eq 0 ]; then
    echo "✓ Scheduler test passed"
else
    echo "❌ Scheduler test failed"
    exit 1
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✓ SMTP connection working"
if [ -n "$TEST_EMAIL" ]; then
    echo "✓ Test email sent"
fi
echo "✓ Database initialized"
echo "✓ Welcome sequence ready"
echo "✓ Scheduler functional"
echo ""
echo "🚀 NEXT STEPS:"
echo ""
echo "1. Customize email templates:"
echo "   Edit email-templates.json"
echo ""
echo "2. Add real subscribers:"
echo "   python welcome-sequence.py add user@example.com \"First Name\""
echo ""
echo "3. Start the scheduler:"
echo "   python scheduler.py"
echo ""
echo "4. Monitor activity:"
echo "   python welcome-sequence.py stats"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Cleanup option
echo ""
read -p "Delete test database? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f email_sequences.db
    echo "✓ Test database deleted"
fi
