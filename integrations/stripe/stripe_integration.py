"""
Stripe Integration Framework
Complete revenue tracking, subscription management, and webhook handling
"""

import os
import stripe
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class StripeIntegration:
    def __init__(self):
        self.api_key = os.getenv('STRIPE_SECRET_KEY')
        if self.api_key:
            stripe.api_key = self.api_key
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
    def is_configured(self) -> bool:
        """Check if Stripe is properly configured"""
        return bool(self.api_key)
    
    def get_mrr(self) -> Dict:
        """Calculate Monthly Recurring Revenue"""
        if not self.is_configured():
            return {"error": "Stripe not configured", "mrr": 0}
        
        try:
            # Get all active subscriptions
            subscriptions = stripe.Subscription.list(
                status='active',
                limit=100
            )
            
            total_mrr = 0
            subscription_count = 0
            
            for sub in subscriptions.auto_paging_iter():
                # Calculate MRR from subscription items
                for item in sub['items']['data']:
                    amount = item['price']['unit_amount'] / 100  # Convert from cents
                    interval = item['price']['recurring']['interval']
                    
                    # Normalize to monthly
                    if interval == 'month':
                        monthly_amount = amount
                    elif interval == 'year':
                        monthly_amount = amount / 12
                    elif interval == 'week':
                        monthly_amount = amount * 4.33
                    elif interval == 'day':
                        monthly_amount = amount * 30
                    else:
                        monthly_amount = amount
                    
                    total_mrr += monthly_amount
                
                subscription_count += 1
            
            # Calculate ARR
            arr = total_mrr * 12
            
            return {
                "mrr": round(total_mrr, 2),
                "arr": round(arr, 2),
                "active_subscriptions": subscription_count,
                "currency": "usd",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "mrr": 0}
    
    def get_customer_count(self) -> Dict:
        """Get total customer count"""
        if not self.is_configured():
            return {"error": "Stripe not configured", "customers": 0}
        
        try:
            customers = stripe.Customer.list(limit=1)
            total = customers.get('total_count', 0)
            
            # Get customers with active subscriptions
            active_subs = stripe.Subscription.list(status='active', limit=100)
            active_count = len(list(active_subs.auto_paging_iter()))
            
            return {
                "total_customers": total,
                "active_customers": active_count,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "customers": 0}
    
    def get_recent_events(self, hours: int = 24) -> List[Dict]:
        """Get recent subscription events"""
        if not self.is_configured():
            return []
        
        try:
            since = int((datetime.now() - timedelta(hours=hours)).timestamp())
            
            events = stripe.Event.list(
                type='customer.subscription.*',
                created={'gte': since},
                limit=100
            )
            
            processed_events = []
            for event in events.auto_paging_iter():
                processed_events.append({
                    "type": event['type'],
                    "created": datetime.fromtimestamp(event['created']).isoformat(),
                    "customer_id": event['data']['object'].get('customer'),
                    "subscription_id": event['data']['object'].get('id'),
                    "status": event['data']['object'].get('status')
                })
            
            return processed_events
            
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    def get_failed_payments(self, days: int = 7) -> List[Dict]:
        """Get recent failed payments"""
        if not self.is_configured():
            return []
        
        try:
            since = int((datetime.now() - timedelta(days=days)).timestamp())
            
            charges = stripe.Charge.list(
                created={'gte': since},
                limit=100
            )
            
            failed = []
            for charge in charges.auto_paging_iter():
                if not charge['paid']:
                    failed.append({
                        "customer_id": charge.get('customer'),
                        "amount": charge['amount'] / 100,
                        "currency": charge['currency'],
                        "failure_message": charge.get('failure_message'),
                        "created": datetime.fromtimestamp(charge['created']).isoformat()
                    })
            
            return failed
            
        except Exception as e:
            print(f"Error fetching failed payments: {e}")
            return []
    
    def get_growth_data(self, days: int = 30) -> Dict:
        """Calculate revenue growth over time"""
        if not self.is_configured():
            return {"error": "Stripe not configured"}
        
        try:
            # Get charges for the period
            since = int((datetime.now() - timedelta(days=days)).timestamp())
            
            charges = stripe.Charge.list(
                created={'gte': since},
                limit=100
            )
            
            # Group by date
            daily_revenue = {}
            for charge in charges.auto_paging_iter():
                if charge['paid']:
                    date = datetime.fromtimestamp(charge['created']).date().isoformat()
                    amount = charge['amount'] / 100
                    
                    if date not in daily_revenue:
                        daily_revenue[date] = 0
                    daily_revenue[date] += amount
            
            # Calculate growth percentage
            sorted_dates = sorted(daily_revenue.keys())
            if len(sorted_dates) >= 2:
                first_week = sum(daily_revenue.get(d, 0) for d in sorted_dates[:7])
                last_week = sum(daily_revenue.get(d, 0) for d in sorted_dates[-7:])
                
                if first_week > 0:
                    growth_pct = ((last_week - first_week) / first_week) * 100
                else:
                    growth_pct = 0
            else:
                growth_pct = 0
            
            return {
                "daily_revenue": daily_revenue,
                "growth_percentage": round(growth_pct, 2),
                "period_days": days
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def verify_webhook(self, payload: bytes, sig_header: str) -> Optional[Dict]:
        """Verify and parse Stripe webhook"""
        if not self.webhook_secret:
            raise Exception("Webhook secret not configured")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            return event
        except Exception as e:
            print(f"Webhook verification failed: {e}")
            return None
    
    def export_data(self, filepath: str = "revenue_data.json"):
        """Export all revenue data to JSON"""
        data = {
            "exported_at": datetime.now().isoformat(),
            "mrr": self.get_mrr(),
            "customers": self.get_customer_count(),
            "recent_events": self.get_recent_events(hours=168),  # Last week
            "failed_payments": self.get_failed_payments(days=30),
            "growth": self.get_growth_data(days=30)
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath


if __name__ == "__main__":
    # Quick test
    integration = StripeIntegration()
    
    if not integration.is_configured():
        print("⚠️  Stripe not configured. Add STRIPE_SECRET_KEY to .env")
    else:
        print("✅ Stripe configured!")
        
        mrr_data = integration.get_mrr()
        print(f"\n💰 MRR: ${mrr_data.get('mrr', 0)}")
        print(f"📈 ARR: ${mrr_data.get('arr', 0)}")
        
        customer_data = integration.get_customer_count()
        print(f"👥 Active Customers: {customer_data.get('active_customers', 0)}")
