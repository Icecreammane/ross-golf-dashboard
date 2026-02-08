"""
Revenue Dashboard - Flask Application
Displays real-time revenue metrics, MRR progress, and business insights
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import stripe
from threading import Lock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/revenue_dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
MRR_GOAL = 500  # $500/month goal

# Initialize Stripe
if STRIPE_API_KEY:
    stripe.api_key = STRIPE_API_KEY
else:
    logger.warning("No Stripe API key found. Set STRIPE_API_KEY environment variable.")

# Data storage
data_lock = Lock()
DATA_FILE = 'data/revenue_data.json'

def load_data():
    """Load revenue data from JSON file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading data: {e}")
    
    # Default structure
    return {
        'stripe_sales': [],
        'coaching_inquiries': [],
        'last_updated': None,
        'mrr': 0,
        'daily_revenue': 0,
        'total_revenue': 0
    }

def save_data(data):
    """Save revenue data to JSON file"""
    try:
        with data_lock:
            os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Data saved successfully")
    except Exception as e:
        logger.error(f"Error saving data: {e}")

def fetch_stripe_data():
    """Fetch subscription and payment data from Stripe"""
    try:
        if not STRIPE_API_KEY:
            logger.warning("Stripe API key not configured")
            return {'subscriptions': [], 'payments': [], 'mrr': 0}
        
        # Fetch active subscriptions
        subscriptions = stripe.Subscription.list(
            status='active',
            limit=100
        )
        
        # Calculate MRR
        mrr = 0
        subscription_list = []
        for sub in subscriptions.auto_paging_iter():
            # Convert to monthly amount
            amount = sub['items']['data'][0]['price']['unit_amount'] / 100
            interval = sub['items']['data'][0]['price']['recurring']['interval']
            
            if interval == 'month':
                monthly_amount = amount
            elif interval == 'year':
                monthly_amount = amount / 12
            else:
                monthly_amount = 0
            
            mrr += monthly_amount
            subscription_list.append({
                'id': sub['id'],
                'amount': amount,
                'interval': interval,
                'monthly_amount': monthly_amount,
                'status': sub['status'],
                'customer': sub['customer']
            })
        
        # Fetch recent payments (last 30 days)
        thirty_days_ago = int((datetime.now() - timedelta(days=30)).timestamp())
        charges = stripe.Charge.list(
            created={'gte': thirty_days_ago},
            limit=100
        )
        
        payment_list = []
        total_revenue = 0
        for charge in charges.auto_paging_iter():
            if charge['paid']:
                amount = charge['amount'] / 100
                total_revenue += amount
                payment_list.append({
                    'id': charge['id'],
                    'amount': amount,
                    'created': charge['created'],
                    'description': charge.get('description', 'Payment'),
                    'customer': charge.get('customer', 'Unknown')
                })
        
        logger.info(f"Fetched Stripe data: MRR=${mrr:.2f}, {len(subscription_list)} subscriptions, {len(payment_list)} payments")
        
        return {
            'subscriptions': subscription_list,
            'payments': payment_list,
            'mrr': mrr,
            'total_revenue': total_revenue
        }
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe API error: {e}")
        return {'subscriptions': [], 'payments': [], 'mrr': 0, 'total_revenue': 0}
    except Exception as e:
        logger.error(f"Error fetching Stripe data: {e}")
        return {'subscriptions': [], 'payments': [], 'mrr': 0, 'total_revenue': 0}

def calculate_metrics(data):
    """Calculate dashboard metrics"""
    try:
        # Get today's revenue
        today = datetime.now().date()
        daily_revenue = 0
        
        for payment in data.get('stripe_sales', []):
            payment_date = datetime.fromtimestamp(payment.get('created', 0)).date()
            if payment_date == today:
                daily_revenue += payment.get('amount', 0)
        
        # Calculate days to goal
        mrr = data.get('mrr', 0)
        days_to_goal = None
        projected_run_rate = 0
        
        if mrr > 0 and mrr < MRR_GOAL:
            # Calculate daily growth rate from recent payments
            recent_payments = sorted(
                data.get('stripe_sales', []),
                key=lambda x: x.get('created', 0),
                reverse=True
            )[:30]  # Last 30 payments
            
            if len(recent_payments) > 1:
                # Simple linear projection
                oldest = datetime.fromtimestamp(recent_payments[-1].get('created', 0))
                newest = datetime.fromtimestamp(recent_payments[0].get('created', 0))
                days_span = (newest - oldest).days or 1
                
                growth = sum(p.get('amount', 0) for p in recent_payments) / days_span
                projected_run_rate = mrr + (growth * 30)
                
                if growth > 0:
                    remaining = MRR_GOAL - mrr
                    days_to_goal = int(remaining / growth)
        
        return {
            'mrr': mrr,
            'daily_revenue': daily_revenue,
            'total_revenue': data.get('total_revenue', 0),
            'days_to_goal': days_to_goal,
            'projected_run_rate': projected_run_rate,
            'progress_percent': min(100, (mrr / MRR_GOAL) * 100),
            'coaching_inquiries_count': len(data.get('coaching_inquiries', [])),
            'subscription_count': len(data.get('subscriptions', []))
        }
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        return {
            'mrr': 0,
            'daily_revenue': 0,
            'total_revenue': 0,
            'days_to_goal': None,
            'projected_run_rate': 0,
            'progress_percent': 0,
            'coaching_inquiries_count': 0,
            'subscription_count': 0
        }

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/metrics')
def get_metrics():
    """API endpoint to fetch current metrics"""
    try:
        data = load_data()
        metrics = calculate_metrics(data)
        metrics['last_updated'] = data.get('last_updated')
        
        logger.info("Metrics requested")
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error in /api/metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Manually refresh data from Stripe"""
    try:
        logger.info("Manual refresh triggered")
        
        # Fetch fresh Stripe data
        stripe_data = fetch_stripe_data()
        
        # Load existing data
        data = load_data()
        
        # Update with fresh Stripe data
        data['stripe_sales'] = stripe_data['payments']
        data['subscriptions'] = stripe_data['subscriptions']
        data['mrr'] = stripe_data['mrr']
        data['total_revenue'] = stripe_data['total_revenue']
        data['last_updated'] = datetime.now().isoformat()
        
        # Save updated data
        save_data(data)
        
        # Calculate and return metrics
        metrics = calculate_metrics(data)
        metrics['last_updated'] = data['last_updated']
        
        logger.info("Data refreshed successfully")
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error in /api/refresh: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Stripe webhook endpoint for real-time updates"""
    try:
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')
        
        if not STRIPE_WEBHOOK_SECRET:
            logger.warning("Webhook secret not configured")
            return jsonify({'status': 'webhook secret not configured'}), 200
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return jsonify({'error': 'Invalid payload'}), 400
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return jsonify({'error': 'Invalid signature'}), 400
        
        # Handle relevant events
        if event['type'] in ['charge.succeeded', 'customer.subscription.created', 
                             'customer.subscription.updated', 'customer.subscription.deleted']:
            logger.info(f"Webhook received: {event['type']}")
            
            # Refresh data on relevant events
            stripe_data = fetch_stripe_data()
            data = load_data()
            
            data['stripe_sales'] = stripe_data['payments']
            data['subscriptions'] = stripe_data['subscriptions']
            data['mrr'] = stripe_data['mrr']
            data['total_revenue'] = stripe_data['total_revenue']
            data['last_updated'] = datetime.now().isoformat()
            
            save_data(data)
            
            logger.info(f"Data updated from webhook: {event['type']}")
        
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/coaching/inquiry', methods=['POST'])
def add_coaching_inquiry():
    """Add a golf coaching inquiry"""
    try:
        inquiry_data = request.get_json()
        
        data = load_data()
        
        inquiry = {
            'id': len(data.get('coaching_inquiries', [])) + 1,
            'source': inquiry_data.get('source', 'unknown'),
            'contact': inquiry_data.get('contact', ''),
            'message': inquiry_data.get('message', ''),
            'created': datetime.now().isoformat(),
            'status': 'new'
        }
        
        if 'coaching_inquiries' not in data:
            data['coaching_inquiries'] = []
        
        data['coaching_inquiries'].append(inquiry)
        data['last_updated'] = datetime.now().isoformat()
        
        save_data(data)
        
        logger.info(f"New coaching inquiry added from {inquiry['source']}")
        return jsonify({'status': 'success', 'inquiry': inquiry})
    
    except Exception as e:
        logger.error(f"Error adding coaching inquiry: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'stripe_configured': bool(STRIPE_API_KEY)
    })

if __name__ == '__main__':
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Initial data fetch
    logger.info("Starting revenue dashboard...")
    try:
        stripe_data = fetch_stripe_data()
        data = load_data()
        data['stripe_sales'] = stripe_data['payments']
        data['subscriptions'] = stripe_data['subscriptions']
        data['mrr'] = stripe_data['mrr']
        data['total_revenue'] = stripe_data['total_revenue']
        data['last_updated'] = datetime.now().isoformat()
        save_data(data)
        logger.info("Initial data loaded")
    except Exception as e:
        logger.error(f"Error loading initial data: {e}")
    
    app.run(host='0.0.0.0', port=3002, debug=False)
