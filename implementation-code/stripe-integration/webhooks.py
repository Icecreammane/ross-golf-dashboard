"""
Stripe Webhook Handlers
Process subscription events from Stripe
"""

import os
import stripe
from flask import Blueprint, request, jsonify

webhooks = Blueprint('webhooks', __name__)

# Webhook secret for signature verification
WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')


@webhooks.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle incoming Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    event_type = event['type']
    data = event['data']['object']
    
    # Route to appropriate handler
    handlers = {
        'customer.subscription.created': handle_subscription_created,
        'customer.subscription.updated': handle_subscription_updated,
        'customer.subscription.deleted': handle_subscription_deleted,
        'invoice.payment_succeeded': handle_payment_succeeded,
        'invoice.payment_failed': handle_payment_failed,
        'checkout.session.completed': handle_checkout_completed,
    }
    
    handler = handlers.get(event_type)
    if handler:
        handler(data, event)
    else:
        print(f'Unhandled event type: {event_type}')
    
    return jsonify({'status': 'success'}), 200


def handle_subscription_created(subscription, event):
    """Handle new subscription created"""
    customer_id = subscription['customer']
    subscription_id = subscription['id']
    status = subscription['status']
    
    print(f'New subscription created: {subscription_id}')
    print(f'Customer: {customer_id}, Status: {status}')
    
    # TODO: Update your database
    # db.execute("""
    #     UPDATE users 
    #     SET subscription_id = ?, 
    #         subscription_status = ?,
    #         subscription_start = ?
    #     WHERE stripe_customer_id = ?
    # """, subscription_id, status, subscription['current_period_start'], customer_id)
    
    # TODO: Send welcome email
    # send_welcome_email(customer_id)


def handle_subscription_updated(subscription, event):
    """Handle subscription updated (plan change, cancel, reactivate)"""
    customer_id = subscription['customer']
    subscription_id = subscription['id']
    status = subscription['status']
    cancel_at_period_end = subscription['cancel_at_period_end']
    
    print(f'Subscription updated: {subscription_id}')
    print(f'Status: {status}, Cancel at period end: {cancel_at_period_end}')
    
    # TODO: Update your database
    # db.execute("""
    #     UPDATE users 
    #     SET subscription_status = ?,
    #         cancel_at_period_end = ?
    #     WHERE stripe_customer_id = ?
    # """, status, cancel_at_period_end, customer_id)
    
    # If subscription was canceled
    if cancel_at_period_end:
        print(f'Subscription will cancel at period end')
        # TODO: Send cancellation confirmation email
        # send_cancellation_email(customer_id)


def handle_subscription_deleted(subscription, event):
    """Handle subscription deleted (ended)"""
    customer_id = subscription['customer']
    subscription_id = subscription['id']
    
    print(f'Subscription deleted: {subscription_id}')
    
    # TODO: Update your database
    # db.execute("""
    #     UPDATE users 
    #     SET subscription_status = 'canceled',
    #         subscription_end = ?
    #     WHERE stripe_customer_id = ?
    # """, subscription['ended_at'], customer_id)
    
    # TODO: Send subscription ended email
    # send_subscription_ended_email(customer_id)
    
    # TODO: Revoke premium access
    # revoke_premium_access(customer_id)


def handle_payment_succeeded(invoice, event):
    """Handle successful payment"""
    customer_id = invoice['customer']
    subscription_id = invoice['subscription']
    amount = invoice['amount_paid'] / 100  # Convert cents to dollars
    
    print(f'Payment succeeded: ${amount}')
    print(f'Customer: {customer_id}, Subscription: {subscription_id}')
    
    # TODO: Log payment in database
    # db.execute("""
    #     INSERT INTO payments (customer_id, subscription_id, amount, status, paid_at)
    #     VALUES (?, ?, ?, 'succeeded', ?)
    # """, customer_id, subscription_id, amount, invoice['created'])
    
    # TODO: Send payment receipt email
    # send_payment_receipt(customer_id, amount, invoice['hosted_invoice_url'])
    
    # Ensure premium access is active
    # activate_premium_access(customer_id)


def handle_payment_failed(invoice, event):
    """Handle failed payment"""
    customer_id = invoice['customer']
    subscription_id = invoice['subscription']
    amount = invoice['amount_due'] / 100
    
    print(f'Payment failed: ${amount}')
    print(f'Customer: {customer_id}, Subscription: {subscription_id}')
    
    # TODO: Log failed payment
    # db.execute("""
    #     INSERT INTO payments (customer_id, subscription_id, amount, status, failed_at)
    #     VALUES (?, ?, ?, 'failed', ?)
    # """, customer_id, subscription_id, amount, invoice['created'])
    
    # TODO: Send payment failed email
    # send_payment_failed_email(customer_id, amount)
    
    # Stripe will automatically retry payment
    # After all retries fail, subscription will be canceled


def handle_checkout_completed(session, event):
    """Handle successful checkout session"""
    customer_id = session['customer']
    subscription_id = session['subscription']
    
    print(f'Checkout completed!')
    print(f'Customer: {customer_id}, Subscription: {subscription_id}')
    
    # TODO: Update database with subscription info
    # db.execute("""
    #     UPDATE users 
    #     SET subscription_id = ?,
    #         subscription_status = 'active'
    #     WHERE stripe_customer_id = ?
    # """, subscription_id, customer_id)
    
    # TODO: Send success email
    # send_subscription_started_email(customer_id)
    
    # Activate premium features
    # activate_premium_access(customer_id)


# Helper functions (implement these based on your app)

def send_welcome_email(customer_id):
    """Send welcome email to new subscriber"""
    # TODO: Implement email sending
    pass


def send_cancellation_email(customer_id):
    """Send cancellation confirmation email"""
    # TODO: Implement email sending
    pass


def send_subscription_ended_email(customer_id):
    """Send subscription ended email"""
    # TODO: Implement email sending
    pass


def send_payment_receipt(customer_id, amount, invoice_url):
    """Send payment receipt email"""
    # TODO: Implement email sending
    pass


def send_payment_failed_email(customer_id, amount):
    """Send payment failed notification"""
    # TODO: Implement email sending
    pass


def send_subscription_started_email(customer_id):
    """Send subscription started confirmation"""
    # TODO: Implement email sending
    pass


def activate_premium_access(customer_id):
    """Grant premium access to user"""
    # TODO: Implement access control
    pass


def revoke_premium_access(customer_id):
    """Revoke premium access from user"""
    # TODO: Implement access control
    pass
