"""
Stripe Alert System
Sends Telegram notifications for important revenue events
"""

import os
import requests
from datetime import datetime
from typing import Dict, Optional
from stripe_integration import StripeIntegration
from dotenv import load_dotenv

load_dotenv()

class StripeAlerts:
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.stripe = StripeIntegration()
        
    def is_configured(self) -> bool:
        """Check if alerts are properly configured"""
        return bool(self.telegram_token and self.telegram_chat_id)
    
    def send_telegram(self, message: str, parse_mode: str = "HTML"):
        """Send Telegram notification"""
        if not self.is_configured():
            print(f"Alert (would send): {message}")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Failed to send Telegram alert: {e}")
            return False
    
    def alert_new_customer(self, customer_data: Dict):
        """Alert when new customer subscribes"""
        customer_id = customer_data.get('id', 'Unknown')
        email = customer_data.get('email', 'No email')
        
        # Get current MRR
        mrr_data = self.stripe.get_mrr()
        current_mrr = mrr_data.get('mrr', 0)
        
        message = f"""💰 <b>New Customer!</b>

👤 Customer: {email}
🆔 ID: {customer_id}
💵 Current MRR: ${current_mrr:.2f}

🎉 Keep it rolling!"""
        
        self.send_telegram(message)
    
    def alert_new_subscription(self, subscription_data: Dict):
        """Alert when new subscription created"""
        sub_id = subscription_data.get('id', 'Unknown')
        customer_id = subscription_data.get('customer', 'Unknown')
        status = subscription_data.get('status', 'unknown')
        
        # Calculate subscription value
        amount = 0
        if 'items' in subscription_data:
            for item in subscription_data['items'].get('data', []):
                amount += item['price']['unit_amount'] / 100
        
        # Get updated MRR
        mrr_data = self.stripe.get_mrr()
        current_mrr = mrr_data.get('mrr', 0)
        
        message = f"""💰 <b>New Subscription!</b>

💵 Amount: ${amount:.2f}/mo
👤 Customer: {customer_id}
📊 Status: {status}
💰 Total MRR: ${current_mrr:.2f}

🚀 Revenue growing!"""
        
        self.send_telegram(message)
    
    def alert_failed_payment(self, charge_data: Dict):
        """Alert when payment fails"""
        customer_id = charge_data.get('customer', 'Unknown')
        amount = charge_data.get('amount', 0) / 100
        failure_message = charge_data.get('failure_message', 'Unknown error')
        
        message = f"""⚠️ <b>Payment Failed</b>

👤 Customer: {customer_id}
💵 Amount: ${amount:.2f}
❌ Reason: {failure_message}

⚡ Follow up needed!"""
        
        self.send_telegram(message)
    
    def alert_cancellation(self, subscription_data: Dict):
        """Alert when subscription cancelled"""
        customer_id = subscription_data.get('customer', 'Unknown')
        sub_id = subscription_data.get('id', 'Unknown')
        
        # Calculate lost MRR
        amount = 0
        if 'items' in subscription_data:
            for item in subscription_data['items'].get('data', []):
                amount += item['price']['unit_amount'] / 100
        
        # Get updated MRR
        mrr_data = self.stripe.get_mrr()
        current_mrr = mrr_data.get('mrr', 0)
        
        message = f"""❌ <b>Subscription Cancelled</b>

👤 Customer: {customer_id}
💸 Lost MRR: ${amount:.2f}/mo
💰 Current MRR: ${current_mrr:.2f}

📉 Check cancellation reason"""
        
        self.send_telegram(message)
    
    def alert_milestone(self, milestone: int, current_mrr: float):
        """Alert when MRR milestone reached"""
        message = f"""🎉 <b>MILESTONE REACHED!</b>

💰 ${milestone} MRR Achieved!
📊 Current: ${current_mrr:.2f}

🚀 Next target: ${milestone * 2}!"""
        
        self.send_telegram(message)
    
    def check_milestones(self):
        """Check if any MRR milestones have been reached"""
        mrr_data = self.stripe.get_mrr()
        current_mrr = mrr_data.get('mrr', 0)
        
        # Define milestones
        milestones = [50, 100, 250, 500, 1000, 2000, 3000, 5000, 10000]
        
        # Load last checked milestone
        milestone_file = "integrations/stripe/last_milestone.txt"
        try:
            with open(milestone_file, 'r') as f:
                last_milestone = float(f.read().strip())
        except:
            last_milestone = 0
        
        # Check if crossed new milestone
        for milestone in milestones:
            if last_milestone < milestone <= current_mrr:
                self.alert_milestone(milestone, current_mrr)
                last_milestone = milestone
        
        # Save last milestone
        os.makedirs(os.path.dirname(milestone_file), exist_ok=True)
        with open(milestone_file, 'w') as f:
            f.write(str(last_milestone))
    
    def daily_summary(self):
        """Send daily revenue summary"""
        mrr_data = self.stripe.get_mrr()
        customer_data = self.stripe.get_customer_count()
        growth_data = self.stripe.get_growth_data(days=7)
        
        mrr = mrr_data.get('mrr', 0)
        arr = mrr_data.get('arr', 0)
        customers = customer_data.get('active_customers', 0)
        growth = growth_data.get('growth_percentage', 0)
        
        # Progress to $3K goal
        goal = 3000
        progress_pct = (mrr / goal) * 100
        
        message = f"""📊 <b>Daily Revenue Report</b>

💰 MRR: ${mrr:.2f}
📈 ARR: ${arr:.2f}
👥 Active Customers: {customers}
📊 7-Day Growth: {growth:+.1f}%

🎯 Goal Progress: {progress_pct:.1f}% to $3K
💵 ${goal - mrr:.2f} to go!

{'🚀 Keep pushing!' if growth > 0 else '💪 Time to hustle!'}"""
        
        self.send_telegram(message)


if __name__ == "__main__":
    alerts = StripeAlerts()
    
    if not alerts.is_configured():
        print("⚠️  Alerts not configured. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env")
    else:
        print("✅ Alerts configured!")
        print("\nSending test daily summary...")
        alerts.daily_summary()
        
        print("\nChecking milestones...")
        alerts.check_milestones()
