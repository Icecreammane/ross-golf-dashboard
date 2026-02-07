#!/usr/bin/env python3
"""
Telegram Signup Alerts for FitTrack
Sends real-time notification when someone signs up
"""

import os
import requests
from datetime import datetime

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID_HERE')

def send_telegram_message(message):
    """Send message via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        return False

def notify_new_signup(email, source=None, timestamp=None):
    """Send notification for new trial signup"""
    if timestamp is None:
        timestamp = datetime.now().strftime('%Y-%m-%d %I:%M %p')
    
    source_text = f"Source: {source}" if source else ""
    
    message = f"""🎉 *New FitTrack Signup!*

Email: `{email}`
{source_text}
Time: {timestamp}

Trial Day 1 of 7
"""
    return send_telegram_message(message)

def notify_first_conversion():
    """Special alert for first paid customer"""
    message = """💰 *FIRST PAID CUSTOMER!!!* 🎊🎊🎊

Someone just converted from trial to paid!

Check dashboard for details.

*This is HUGE!* 🚀
"""
    return send_telegram_message(message)

def notify_milestone(count, metric="signups"):
    """Send milestone notifications"""
    milestones = {
        10: "🎯 10 signups! Double digits! 💪",
        25: "🔥 25 signups! Quarter century! 🔥",
        50: "🚀 50 SIGNUPS! Launch goal achieved! 🚀",
        100: "💯 100 SIGNUPS! TRIPLE DIGITS! 💯",
    }
    
    if count in milestones:
        message = f"*Milestone Reached!*\n\n{milestones[count]}"
        return send_telegram_message(message)
    return False

def notify_error(error_type, error_message, page=None):
    """Send error alert"""
    page_text = f"Page: `{page}`" if page else ""
    
    message = f"""🚨 *ERROR ALERT*

Type: {error_type}
{page_text}
Message: `{error_message}`

Check logs immediately!
"""
    return send_telegram_message(message)

def notify_site_down():
    """Alert if site goes down"""
    message = """⚠️ *SITE DOWN ALERT* ⚠️

FitTrack is not responding.

Check server status NOW!
"""
    return send_telegram_message(message)

# Example usage / integration with Flask
"""
# In your Flask app (FitTrack backend):

from telegram_signup_alerts import notify_new_signup, notify_milestone

@app.route('/api/signup', methods=['POST'])
def signup():
    # ... your signup logic ...
    user = create_user(email, password)
    
    # Send Telegram notification
    notify_new_signup(
        email=user.email,
        source=request.args.get('utm_source', 'direct'),
        timestamp=datetime.now().strftime('%Y-%m-%d %I:%M %p')
    )
    
    # Check for milestones
    total_signups = User.query.count()
    notify_milestone(total_signups, "signups")
    
    return jsonify({'success': True})

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    # ... your payment logic ...
    
    # Check if this is first customer
    if Payment.query.count() == 1:
        notify_first_conversion()
    
    return jsonify({'success': True})
"""

if __name__ == "__main__":
    # Test the notification
    print("Testing Telegram notifications...")
    
    if TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Please set TELEGRAM_BOT_TOKEN environment variable")
        print("Get token from @BotFather on Telegram")
        exit(1)
    
    if TELEGRAM_CHAT_ID == 'YOUR_CHAT_ID_HERE':
        print("❌ Please set TELEGRAM_CHAT_ID environment variable")
        print("Get your chat ID from @userinfobot on Telegram")
        exit(1)
    
    # Send test notification
    test_message = "✅ FitTrack Telegram alerts are working!\n\nLaunch automation is ready. 🚀"
    success = send_telegram_message(test_message)
    
    if success:
        print("✅ Test notification sent successfully!")
        print("Check your Telegram for the message.")
    else:
        print("❌ Failed to send test notification.")
        print("Check your bot token and chat ID.")
