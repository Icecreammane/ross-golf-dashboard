# Spending Tracker Integration Examples

## Evening Check-In Integration

```python
#!/usr/bin/env python3
"""
Evening check-in with spending summary
"""

import subprocess
import os
from datetime import datetime

def get_spending_summary():
    """Get evening spending summary"""
    try:
        result = subprocess.run(
            ['python3', 'scripts/spending_alerts.py', 'evening'],
            capture_output=True,
            text=True,
            cwd=os.path.expanduser('~/clawd'),
            timeout=10
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return None
    except Exception as e:
        print(f"Error getting spending summary: {e}")
        return None

def evening_checkin():
    """Generate evening check-in message"""
    message = f"🌙 **Evening Check-in** - {datetime.now().strftime('%A, %B %d')}\n\n"
    
    # Add your existing evening check-in content
    # - Calendar review
    # - Task completion
    # - Tomorrow's preview
    # etc.
    
    # Add spending summary
    spending = get_spending_summary()
    if spending:
        message += f"\n\n{spending}"
    
    return message

if __name__ == "__main__":
    print(evening_checkin())
```

---

## Morning Brief Integration

```python
def morning_brief():
    """Generate morning brief with yesterday's spending"""
    message = f"☀️ **Morning Brief** - {datetime.now().strftime('%A, %B %d')}\n\n"
    
    # Add your existing morning content
    # - Weather
    # - Calendar
    # - Tasks
    
    # Add yesterday's spending
    try:
        result = subprocess.run(
            ['python3', 'scripts/spending_alerts.py', 'morning'],
            capture_output=True,
            text=True,
            cwd=os.path.expanduser('~/clawd'),
            timeout=5
        )
        
        if result.returncode == 0:
            message += f"\n{result.stdout}\n"
    except:
        pass
    
    return message
```

---

## Voice Command Integration

```python
# Add to voice command handler

def handle_spending_query(query):
    """Handle spending-related voice commands"""
    
    if "today" in query or "spent today" in query:
        result = subprocess.run(
            ['python3', 'scripts/spending_alerts.py', 'daily'],
            capture_output=True,
            text=True,
            cwd=os.path.expanduser('~/clawd')
        )
        return result.stdout
    
    elif "dashboard" in query or "show spending" in query:
        subprocess.run(['open', 'dashboard/spending.html'])
        return "Opening spending dashboard"
    
    elif "insights" in query or "advice" in query:
        result = subprocess.run(
            ['python3', 'scripts/spending_alerts.py', 'insights'],
            capture_output=True,
            text=True,
            cwd=os.path.expanduser('~/clawd')
        )
        return result.stdout
```

---

## Telegram Bot Integration

```python
# In your Telegram bot

@bot.command('spending')
async def spending_command(update, context):
    """Show spending summary"""
    
    # Daily summary
    result = subprocess.run(
        ['python3', 'scripts/spending_alerts.py', 'daily'],
        capture_output=True,
        text=True,
        cwd=os.path.expanduser('~/clawd')
    )
    
    await update.message.reply_text(
        result.stdout,
        parse_mode='Markdown'
    )

@bot.command('dashboard')
async def dashboard_command(update, context):
    """Open spending dashboard"""
    subprocess.run(['open', 'dashboard/spending.html'])
    await update.message.reply_text("📊 Dashboard opened!")

@bot.command('insights')
async def insights_command(update, context):
    """Show financial insights"""
    result = subprocess.run(
        ['python3', 'scripts/spending_alerts.py', 'insights'],
        capture_output=True,
        text=True,
        cwd=os.path.expanduser('~/clawd')
    )
    
    await update.message.reply_text(
        result.stdout,
        parse_mode='Markdown'
    )
```

---

## API Integration (for other tools)

```python
import requests

API_BASE = 'http://localhost:5002/api'

def get_today_spending():
    """Fetch today's spending from API"""
    response = requests.get(f'{API_BASE}/today')
    return response.json()

def get_category_breakdown():
    """Fetch category breakdown"""
    response = requests.get(f'{API_BASE}/categories')
    return response.json()

def check_budget_status():
    """Check if over budget this week"""
    week_data = requests.get(f'{API_BASE}/week').json()
    
    if week_data['change_percent'] > 20:
        return f"⚠️ Spending up {week_data['change_percent']:.0f}% this week!"
    else:
        return "✅ On track this week"

# Example usage
today = get_today_spending()
print(f"Spent ${today['total_spent']:.2f} today")

categories = get_category_breakdown()
for cat in categories['categories']:
    print(f"{cat['category']}: ${cat['total']:.2f} ({cat['percentage']}%)")
```

---

## Dashboard Embedding (in other apps)

```html
<!-- Embed spending dashboard in another page -->
<iframe 
    src="http://localhost:5002/dashboard/spending.html" 
    width="100%" 
    height="800px" 
    frameborder="0">
</iframe>
```

---

## Webhook for Real-Time Alerts

```python
# scripts/spending_webhook.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SLACK_WEBHOOK = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
TELEGRAM_BOT_TOKEN = "YOUR_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

@app.route('/webhook/transaction', methods=['POST'])
def transaction_webhook():
    """Receive real-time transaction alerts"""
    data = request.json
    
    if data['amount'] > 100:
        # Large transaction alert
        message = f"💳 Large transaction: ${data['amount']:.2f} at {data['merchant']}"
        
        # Send to Slack
        requests.post(SLACK_WEBHOOK, json={'text': message})
        
        # Send to Telegram
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message
            }
        )
    
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=5003)
```

---

## Weekly Email Report

```python
#!/usr/bin/env python3
"""
Weekly spending report via email
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess

def generate_weekly_report():
    """Generate weekly spending report"""
    
    # Get weekly data
    result = subprocess.run(
        ['python3', 'scripts/spending_alerts.py', 'weekly'],
        capture_output=True,
        text=True,
        cwd=os.path.expanduser('~/clawd')
    )
    
    alerts = result.stdout
    
    # Get insights
    result = subprocess.run(
        ['python3', 'scripts/spending_alerts.py', 'insights'],
        capture_output=True,
        text=True,
        cwd=os.path.expanduser('~/clawd')
    )
    
    insights = result.stdout
    
    return f"""
    📊 Weekly Spending Report
    
    {alerts}
    
    💡 Insights:
    {insights}
    
    View dashboard: http://localhost:5002
    """

def send_email_report(to_email, subject, body):
    """Send email report"""
    # Configure your email settings
    from_email = "your@email.com"
    password = "your-app-password"
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

if __name__ == "__main__":
    report = generate_weekly_report()
    send_email_report("ross@email.com", "Weekly Spending Report", report)
```

---

## Cron Schedule Examples

```bash
# Daily sync at 2am
0 2 * * * cd ~/clawd && python3 scripts/sync_transactions.py >> logs/spending_sync.log 2>&1

# Evening summary at 8pm
0 20 * * * cd ~/clawd && python3 scripts/spending_alerts.py evening >> logs/spending_alerts.log 2>&1

# Weekly report every Friday at 5pm
0 17 * * 5 cd ~/clawd && python3 scripts/weekly_spending_report.py

# Monthly budget review first day of month at 9am
0 9 1 * * cd ~/clawd && python3 scripts/monthly_budget_review.py
```

---

These examples show how to integrate the spending tracker into your existing automation workflows. Customize as needed!
