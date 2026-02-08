# Stripe Subscription Integration - Quick Start

Drop-in Stripe subscription code for your fitness tracker. Go from code to subscriptions in **30 minutes**.

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install stripe flask
```

### 2. Set Up Stripe
1. Go to https://dashboard.stripe.com
2. Create account (or log in)
3. Get API keys: **Developers → API keys**
4. Create product: **Products → Add product**
   - Name: "Fitness Tracker Premium"
   - Price: $10.00 USD
   - Billing: Recurring monthly
   - Copy the **Price ID** (starts with `price_`)

### 3. Configure Environment
```bash
cp .env.example .env
nano .env  # Fill in your Stripe keys
```

### 4. Integrate with Your Flask App
```python
# In your main Flask app file (e.g., app.py)
from stripe_integration.backend import subscriptions
from stripe_integration.webhooks import webhooks

app.register_blueprint(subscriptions, url_prefix='/api')
app.register_blueprint(webhooks, url_prefix='/webhooks')
```

### 5. Add Frontend
Copy `frontend.js` into your `static/js/` folder and include in your HTML:
```html
<script src="/static/js/frontend.js"></script>
```

### 6. Test It
```bash
bash test-subscription.sh
```

**Done!** You now have subscriptions.

---

## 📋 Detailed Setup

### Setting Up Webhooks

Webhooks let Stripe notify your app about subscription events (payment succeeded, subscription canceled, etc.)

#### Development (Testing locally)
1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Forward webhooks to local server:
   ```bash
   stripe listen --forward-to localhost:3000/webhooks/stripe-webhook
   ```
3. Copy the webhook signing secret (starts with `whsec_`) to `.env`

#### Production
1. In Stripe Dashboard: **Developers → Webhooks → Add endpoint**
2. URL: `https://yourdomain.com/webhooks/stripe-webhook`
3. Select events to listen for:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `checkout.session.completed`
4. Copy the signing secret to your production `.env`

---

## 🔌 Integration Points

### Database Integration
The code has TODO comments where you need to connect to your database:

```python
# Example: Save customer ID to database
# TODO: Uncomment and customize
# db.execute("UPDATE users SET stripe_customer_id = ? WHERE id = ?", 
#            customer.id, session['user_id'])
```

Update these sections with your database logic.

### Authentication
The code uses `@login_required` decorator and `session['user_id']`:

```python
# Customize to match your auth system
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function
```

---

## 🎨 Frontend Integration

### Basic HTML Structure
```html
<!-- Subscribe Page -->
<div id="subscription-page">
    <h1>Subscribe to Premium</h1>
    <p>$10/month - Unlock all features</p>
    
    <input type="hidden" id="user-email" value="{{ current_user.email }}">
    <input type="hidden" id="user-name" value="{{ current_user.name }}">
    
    <button id="subscribe-btn">Subscribe Now</button>
</div>

<!-- Account/Settings Page -->
<div id="subscription-status">
    <!-- Status loads here automatically -->
</div>

<button id="cancel-subscription-btn">Cancel Subscription</button>
<button id="manage-billing-btn">Manage Billing</button>

<!-- Include the script -->
<script src="/static/js/frontend.js"></script>
```

### Success/Cancel Pages
Create these routes in your Flask app:

```python
@app.route('/subscription/success')
def subscription_success():
    return render_template('subscription_success.html')

@app.route('/subscription/cancel')
def subscription_cancel():
    return render_template('subscription_cancel.html')
```

---

## 🧪 Testing

### Test Stripe Checkout
```bash
bash test-subscription.sh
```

This will:
1. Check environment variables
2. Test API connection
3. Try creating a test customer
4. Generate a test checkout link

### Test Credit Cards
Use these test cards in development mode:
- **Success:** `4242 4242 4242 4242`
- **Declined:** `4000 0000 0000 0002`
- **Requires authentication:** `4000 0025 0000 3155`

Any future expiry date, any CVC, any ZIP code.

### Manual Testing Flow
1. Click "Subscribe Now" button
2. Redirects to Stripe Checkout
3. Enter test card: `4242 4242 4242 4242`
4. Complete checkout
5. Redirected back to success page
6. Check webhook events in Stripe Dashboard

---

## 🔧 Common Issues & Fixes

### "Invalid API Key"
- Check your `.env` file has correct keys
- Make sure you're using the right mode (test vs live)
- Keys should start with `sk_test_` or `sk_live_`

### Webhooks Not Working
- **Local:** Make sure Stripe CLI is running (`stripe listen`)
- **Production:** Check webhook URL is publicly accessible
- Verify signing secret in `.env` matches Stripe Dashboard

### "Customer not found"
- Make sure customer is created before checkout
- Check customer ID is saved to database
- Try creating customer again

### Checkout Session Expires
- Sessions expire after 24 hours
- Generate new session for each checkout attempt
- Don't save/reuse session IDs

### Payment Succeeded But User Doesn't Have Access
- Check webhook is configured and receiving events
- Look at webhook logs in Stripe Dashboard
- Make sure `handle_payment_succeeded` is updating your database

---

## 📊 Subscription Flow

```
User clicks "Subscribe"
    ↓
Create Stripe Customer (if new)
    ↓
Create Checkout Session
    ↓
Redirect to Stripe Checkout
    ↓
User enters payment info
    ↓
Payment processed
    ↓
Stripe sends webhook: checkout.session.completed
    ↓
Stripe sends webhook: invoice.payment_succeeded
    ↓
Your webhook handler activates premium access
    ↓
User redirected to success page
```

---

## 💰 Pricing Tiers (Future)

To add multiple plans:

1. Create more products in Stripe Dashboard
2. Save their price IDs:
   ```python
   BASIC_PRICE_ID = "price_basic"
   PRO_PRICE_ID = "price_pro"
   PREMIUM_PRICE_ID = "price_premium"
   ```
3. Pass selected price to checkout:
   ```python
   checkout_session = stripe.checkout.Session.create(
       customer=customer_id,
       line_items=[{
           'price': selected_price_id,  # Dynamic
           'quantity': 1,
       }],
       # ...
   )
   ```

---

## 🔐 Security Checklist

- [ ] Never expose secret keys in frontend code
- [ ] Always verify webhook signatures
- [ ] Use HTTPS in production
- [ ] Validate user owns customer/subscription before modifications
- [ ] Rate limit subscription endpoints
- [ ] Log all subscription changes
- [ ] Handle failed payments gracefully

---

## 📈 Production Checklist

Before going live:

- [ ] Switch from test keys to live keys
- [ ] Update webhook URL to production domain
- [ ] Test with real (small amount) card
- [ ] Set up email notifications (payment failed, subscription ending)
- [ ] Monitor webhook delivery in Stripe Dashboard
- [ ] Set up billing portal for customers to manage subscriptions
- [ ] Add terms of service / refund policy
- [ ] Test subscription cancellation flow

---

## 🆘 Support

**Stripe Docs:** https://stripe.com/docs
**Stripe Dashboard:** https://dashboard.stripe.com
**Test Mode Toggle:** Top right in Stripe Dashboard

**Key Stripe Concepts:**
- **Customer:** A user in your app (reusable across subscriptions)
- **Subscription:** Recurring payment plan
- **Price:** Defines amount and interval ($10/month)
- **Product:** Container for prices (your "Premium Plan")
- **Invoice:** Bill sent to customer each period
- **Checkout Session:** Hosted payment page

---

## 🎯 Next Steps

1. **Email Integration:** Connect webhook handlers to email system
2. **Access Control:** Add middleware to check subscription status
3. **Analytics:** Track subscription metrics
4. **Dunning:** Handle failed payment recovery
5. **Upgrades:** Add ability to change plans
6. **Coupons:** Implement discount codes

---

**Time to ship:** ~30 minutes from here to working subscriptions 🚀
