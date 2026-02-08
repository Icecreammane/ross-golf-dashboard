"""
Stripe Subscription Integration - Backend Routes
Drop-in Flask routes for subscription management
"""

import os
import stripe
from flask import Blueprint, request, jsonify, session
from functools import wraps

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Create Blueprint
subscriptions = Blueprint('subscriptions', __name__)

# Price ID for $10/month subscription (set this in Stripe Dashboard)
SUBSCRIPTION_PRICE_ID = os.getenv('STRIPE_PRICE_ID')

# Decorator for auth (customize to your auth system)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


@subscriptions.route('/create-customer', methods=['POST'])
@login_required
def create_customer():
    """Create a Stripe customer for the logged-in user"""
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name', '')
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
        
        # Create Stripe customer
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={
                'user_id': session['user_id']
            }
        )
        
        # TODO: Save customer.id to your database
        # db.execute("UPDATE users SET stripe_customer_id = ? WHERE id = ?", 
        #            customer.id, session['user_id'])
        
        return jsonify({
            'customer_id': customer.id,
            'email': customer.email
        }), 201
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create a Stripe Checkout session for subscription"""
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        
        if not customer_id:
            return jsonify({'error': 'Customer ID required'}), 400
        
        # Create Checkout Session
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': SUBSCRIPTION_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'subscription/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'subscription/cancel',
            metadata={
                'user_id': session['user_id']
            }
        )
        
        return jsonify({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions.route('/subscription-status', methods=['GET'])
@login_required
def subscription_status():
    """Get current subscription status for user"""
    try:
        customer_id = request.args.get('customer_id')
        
        if not customer_id:
            return jsonify({'error': 'Customer ID required'}), 400
        
        # Get all subscriptions for customer
        subscriptions_list = stripe.Subscription.list(
            customer=customer_id,
            status='all',
            limit=10
        )
        
        active_sub = None
        for sub in subscriptions_list.data:
            if sub.status in ['active', 'trialing']:
                active_sub = sub
                break
        
        if not active_sub:
            return jsonify({
                'status': 'inactive',
                'subscription': None
            }), 200
        
        return jsonify({
            'status': 'active',
            'subscription': {
                'id': active_sub.id,
                'status': active_sub.status,
                'current_period_end': active_sub.current_period_end,
                'cancel_at_period_end': active_sub.cancel_at_period_end,
                'plan_amount': active_sub.items.data[0].price.unit_amount / 100,
                'currency': active_sub.items.data[0].price.currency
            }
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions.route('/cancel-subscription', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancel subscription at end of period"""
    try:
        data = request.get_json()
        subscription_id = data.get('subscription_id')
        immediate = data.get('immediate', False)
        
        if not subscription_id:
            return jsonify({'error': 'Subscription ID required'}), 400
        
        if immediate:
            # Cancel immediately
            subscription = stripe.Subscription.delete(subscription_id)
        else:
            # Cancel at period end
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
        
        return jsonify({
            'status': 'canceled',
            'subscription_id': subscription.id,
            'canceled_at': subscription.canceled_at if immediate else None,
            'cancel_at_period_end': subscription.cancel_at_period_end
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions.route('/reactivate-subscription', methods=['POST'])
@login_required
def reactivate_subscription():
    """Reactivate a canceled subscription"""
    try:
        data = request.get_json()
        subscription_id = data.get('subscription_id')
        
        if not subscription_id:
            return jsonify({'error': 'Subscription ID required'}), 400
        
        # Remove cancel_at_period_end flag
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=False
        )
        
        return jsonify({
            'status': 'active',
            'subscription_id': subscription.id,
            'cancel_at_period_end': subscription.cancel_at_period_end
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions.route('/update-subscription', methods=['POST'])
@login_required
def update_subscription():
    """Update subscription (upgrade/downgrade)"""
    try:
        data = request.get_json()
        subscription_id = data.get('subscription_id')
        new_price_id = data.get('new_price_id')
        
        if not subscription_id or not new_price_id:
            return jsonify({'error': 'Subscription ID and new price ID required'}), 400
        
        # Get subscription
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Update subscription
        updated_subscription = stripe.Subscription.modify(
            subscription_id,
            items=[{
                'id': subscription.items.data[0].id,
                'price': new_price_id,
            }],
            proration_behavior='create_prorations'
        )
        
        return jsonify({
            'status': 'updated',
            'subscription_id': updated_subscription.id,
            'new_price': updated_subscription.items.data[0].price.id
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@subscriptions.route('/billing-portal', methods=['POST'])
@login_required
def billing_portal():
    """Create a billing portal session for customer to manage subscription"""
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        
        if not customer_id:
            return jsonify({'error': 'Customer ID required'}), 400
        
        # Create portal session
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=request.host_url + 'account'
        )
        
        return jsonify({
            'url': session.url
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
