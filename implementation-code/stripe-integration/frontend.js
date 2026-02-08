/**
 * Stripe Checkout Integration - Frontend
 * Copy-paste into your fitness tracker frontend
 */

class StripeSubscription {
    constructor(apiBaseUrl = '/api') {
        this.apiBaseUrl = apiBaseUrl;
        this.customerId = null;
        this.subscriptionId = null;
    }

    /**
     * Initialize Stripe customer for current user
     */
    async createCustomer(email, name) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/create-customer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, name })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to create customer');
            }

            const data = await response.json();
            this.customerId = data.customer_id;
            return data;
        } catch (error) {
            console.error('Error creating customer:', error);
            throw error;
        }
    }

    /**
     * Start subscription checkout flow
     */
    async startCheckout(customerId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/create-checkout-session`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ customer_id: customerId })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to create checkout session');
            }

            const data = await response.json();
            
            // Redirect to Stripe Checkout
            window.location.href = data.checkout_url;
        } catch (error) {
            console.error('Error starting checkout:', error);
            throw error;
        }
    }

    /**
     * Get current subscription status
     */
    async getSubscriptionStatus(customerId) {
        try {
            const response = await fetch(
                `${this.apiBaseUrl}/subscription-status?customer_id=${customerId}`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                }
            );

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to get subscription status');
            }

            const data = await response.json();
            
            if (data.subscription) {
                this.subscriptionId = data.subscription.id;
            }
            
            return data;
        } catch (error) {
            console.error('Error getting subscription status:', error);
            throw error;
        }
    }

    /**
     * Cancel subscription at period end
     */
    async cancelSubscription(subscriptionId, immediate = false) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/cancel-subscription`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    subscription_id: subscriptionId,
                    immediate: immediate
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to cancel subscription');
            }

            return await response.json();
        } catch (error) {
            console.error('Error canceling subscription:', error);
            throw error;
        }
    }

    /**
     * Reactivate a canceled subscription
     */
    async reactivateSubscription(subscriptionId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/reactivate-subscription`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ subscription_id: subscriptionId })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to reactivate subscription');
            }

            return await response.json();
        } catch (error) {
            console.error('Error reactivating subscription:', error);
            throw error;
        }
    }

    /**
     * Open Stripe billing portal
     */
    async openBillingPortal(customerId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/billing-portal`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ customer_id: customerId })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to create billing portal session');
            }

            const data = await response.json();
            window.location.href = data.url;
        } catch (error) {
            console.error('Error opening billing portal:', error);
            throw error;
        }
    }

    /**
     * Format subscription expiry date
     */
    formatExpiryDate(timestamp) {
        const date = new Date(timestamp * 1000);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    }
}

// Example usage in your UI
document.addEventListener('DOMContentLoaded', () => {
    const stripe = new StripeSubscription('/api');

    // Subscribe button click
    const subscribeBtn = document.getElementById('subscribe-btn');
    if (subscribeBtn) {
        subscribeBtn.addEventListener('click', async () => {
            try {
                // Show loading state
                subscribeBtn.disabled = true;
                subscribeBtn.textContent = 'Loading...';

                // Get user data (from your app)
                const userEmail = document.getElementById('user-email').value;
                const userName = document.getElementById('user-name').value;

                // Create customer if needed
                let customerId = localStorage.getItem('stripe_customer_id');
                
                if (!customerId) {
                    const customer = await stripe.createCustomer(userEmail, userName);
                    customerId = customer.customer_id;
                    localStorage.setItem('stripe_customer_id', customerId);
                }

                // Start checkout
                await stripe.startCheckout(customerId);

            } catch (error) {
                alert('Error: ' + error.message);
                subscribeBtn.disabled = false;
                subscribeBtn.textContent = 'Subscribe Now';
            }
        });
    }

    // Cancel subscription button
    const cancelBtn = document.getElementById('cancel-subscription-btn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to cancel your subscription?')) {
                return;
            }

            try {
                cancelBtn.disabled = true;
                cancelBtn.textContent = 'Canceling...';

                const subscriptionId = localStorage.getItem('subscription_id');
                await stripe.cancelSubscription(subscriptionId, false);

                alert('Subscription canceled. You\'ll have access until the end of your billing period.');
                location.reload();

            } catch (error) {
                alert('Error: ' + error.message);
                cancelBtn.disabled = false;
                cancelBtn.textContent = 'Cancel Subscription';
            }
        });
    }

    // Manage billing button
    const manageBillingBtn = document.getElementById('manage-billing-btn');
    if (manageBillingBtn) {
        manageBillingBtn.addEventListener('click', async () => {
            try {
                const customerId = localStorage.getItem('stripe_customer_id');
                await stripe.openBillingPortal(customerId);
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
    }

    // Load subscription status on page load
    const statusContainer = document.getElementById('subscription-status');
    if (statusContainer) {
        loadSubscriptionStatus();
    }

    async function loadSubscriptionStatus() {
        try {
            const customerId = localStorage.getItem('stripe_customer_id');
            if (!customerId) {
                statusContainer.innerHTML = '<p>No active subscription</p>';
                return;
            }

            const status = await stripe.getSubscriptionStatus(customerId);

            if (status.status === 'active' && status.subscription) {
                const sub = status.subscription;
                const expiryDate = stripe.formatExpiryDate(sub.current_period_end);
                
                localStorage.setItem('subscription_id', sub.id);

                statusContainer.innerHTML = `
                    <div class="subscription-active">
                        <h3>✓ Active Subscription</h3>
                        <p>Status: ${sub.status}</p>
                        <p>Amount: $${sub.plan_amount}/${sub.currency}</p>
                        <p>Next billing: ${expiryDate}</p>
                        ${sub.cancel_at_period_end ? 
                            '<p class="warning">Will cancel at period end</p>' : ''}
                    </div>
                `;
            } else {
                statusContainer.innerHTML = '<p>No active subscription</p>';
            }

        } catch (error) {
            console.error('Error loading subscription status:', error);
            statusContainer.innerHTML = '<p>Error loading subscription status</p>';
        }
    }
});

// Handle redirect from Stripe Checkout success
const urlParams = new URLSearchParams(window.location.search);
const sessionId = urlParams.get('session_id');

if (sessionId && window.location.pathname.includes('/subscription/success')) {
    // Show success message
    document.body.innerHTML = `
        <div style="text-align: center; padding: 50px;">
            <h1>🎉 Subscription Activated!</h1>
            <p>Thank you for subscribing. Your premium features are now active.</p>
            <a href="/dashboard" style="display: inline-block; margin-top: 20px; 
                padding: 10px 20px; background: #5469d4; color: white; 
                text-decoration: none; border-radius: 5px;">
                Go to Dashboard
            </a>
        </div>
    `;
}
