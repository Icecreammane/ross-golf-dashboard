# Golf Coaching MVP - $29/mo Product

**Target Launch:** 7 days  
**Revenue Goal:** $290/mo with 10 customers

---

## Product Overview

**What:** Monthly golf coaching subscription  
**Who:** Intermediate golfers looking to improve (handicap 15-25)  
**Value Prop:** Personalized swing analysis + weekly drills for $29/mo

### MVP Scope (Week 1):
- ✅ Landing page with signup
- ✅ Stripe subscription ($29/mo)
- ✅ Basic dashboard for video uploads
- ✅ Email onboarding sequence
- ❌ NO custom video analysis yet (manual in MVP)
- ❌ NO mobile app (web only)

---

## Tech Stack

- **Frontend:** Simple HTML/CSS/JS (no framework)
- **Backend:** Flask Python (reuse FitTrack infrastructure)
- **Payments:** Stripe Checkout + Customer Portal
- **Storage:** S3 for video uploads
- **Email:** SendGrid for onboarding

---

## Landing Page (High-Converting)

### Hero Section:
```
Break 90 in 90 Days
Get personalized golf coaching for $29/month

[Start Free Trial] [See How It Works]

"Finally fixed my slice after 2 years of struggling" - John M.
```

### Key Features:
- 📹 Upload swing videos
- 📊 Get personalized analysis
- 💪 Weekly drill plans
- 📧 Direct coach access
- ✅ Track your progress

### Pricing:
```
$29/month (cancel anytime)
or
$290/year (save $58!)

7-day free trial • No credit card required
```

### Social Proof:
- 3-5 testimonials (get from friends/test users)
- Before/after swing comparisons
- "As seen on Reddit r/golf"

---

## Stripe Integration (30 min setup)

### Step 1: Create Products
```bash
# Go to Stripe Dashboard → Products
# Create product: "Golf Coaching Monthly"
# Price: $29/month
# Copy Price ID
```

### Step 2: Integrate Checkout
```python
# Flask endpoint
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_xxxxx',  # Your price ID
            'quantity': 1,
        }],
        mode='subscription',
        success_url='https://yourdomain.com/success',
        cancel_url='https://yourdomain.com/cancel',
    )
    return redirect(session.url)
```

### Step 3: Webhooks
```python
@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    event = stripe.Event.construct_from(
        request.json, stripe.api_key
    )
    
    if event.type == 'customer.subscription.created':
        # Send welcome email
        send_onboarding_email(event.data.object.customer)
    
    return {'status': 'success'}
```

---

## Onboarding Email Sequence

### Day 0 (Immediate):
**Subject:** Welcome to Your Golf Coaching Journey! 🏌️

```
Hey {name},

Welcome! You're now part of an exclusive group getting personalized golf coaching.

Here's what happens next:

1. Upload your first swing video (any shot, any angle)
2. I'll analyze it within 24 hours
3. You'll get 3 drills to work on this week

UPLOAD YOUR FIRST VIDEO:
[Dashboard Link]

Questions? Just reply to this email.

To better swings,
Ross
```

### Day 2:
**Subject:** Quick tip while you wait...

```
Most golfers struggle with the same 3 things:
1. Over-the-top swing path
2. Early release
3. Poor weight transfer

Which one sounds like you?

Reply and I'll send you a drill specifically for that issue.

- Ross
```

### Day 7 (End of trial):
**Subject:** Your trial ends tomorrow - here's what you've achieved

```
{name},

This week you:
✅ Uploaded 2 swing videos
✅ Got personalized feedback on your slice
✅ Learned 3 new drills

Your trial ends tomorrow. Continue for just $29/month to keep improving!

[Continue My Coaching]

Or cancel anytime - no hard feelings!

- Ross
```

---

## Dashboard MVP (3-4 hours)

### Features:
1. **Upload Video** - Simple drag-drop interface
2. **My Videos** - List of uploaded swings
3. **Feedback** - Text feedback from coach (manual for MVP)
4. **This Week's Drills** - 3 drills with video demos
5. **Progress Tracker** - Simple before/after comparison

### Stack:
```
- Flask backend
- SQLite database
- AWS S3 for videos
- Simple HTML/CSS frontend (reuse FitTrack design system)
```

---

## Marketing Strategy (Week 1)

### Reddit Launch:
- Post to r/golf: "I built a $29/month coaching alternative to $200/hour lessons"
- Be helpful, not salesy
- Offer discount code for Redditors

### Content:
- 5 Instagram Reels: "Common swing mistakes"
- 1 YouTube video: "How I analyze swings"
- Twitter thread: Golf tips

### Early Adopters:
- Message 10 golfer friends
- Offer free coaching in exchange for testimonials
- Get 5 video testimonials

---

## Revenue Projections

### Conservative (Year 1):
- Month 1: 5 customers = $145
- Month 2: 10 customers = $290
- Month 3: 15 customers = $435
- Month 6: 30 customers = $870
- Month 12: 50 customers = $1,450

### Annual Revenue (Year 1): ~$12,000

### Time Investment:
- Setup: 20 hours (week 1)
- Ongoing: 5 hours/week (coaching + content)

**Effective hourly rate after 6 months:** $50/hour

---

## Next Steps (Priority Order)

### Week 1:
1. [ ] Design landing page (4 hours)
2. [ ] Set up Stripe (30 min)
3. [ ] Build basic dashboard (4 hours)
4. [ ] Write onboarding emails (1 hour)
5. [ ] Create 3 drill videos (2 hours)
6. [ ] Launch on Reddit (1 hour)

### Week 2:
1. [ ] Get first 5 customers
2. [ ] Deliver coaching manually
3. [ ] Collect testimonials
4. [ ] Iterate based on feedback

### Week 3:
1. [ ] Add more drill library
2. [ ] Improve video upload UX
3. [ ] Start Instagram content
4. [ ] Aim for 10 customers

---

## Files to Create

```
golf-coaching/
├── landing.html          # Marketing page
├── app.py               # Flask backend
├── dashboard.html       # Member dashboard
├── stripe_webhook.py    # Payment handling
├── onboarding.py        # Email automation
├── drills/              # Drill videos
│   ├── slice-fix.mp4
│   ├── power-drill.mp4
│   └── short-game.mp4
└── static/
    ├── styles.css
    └── scripts.js
```

---

## Key Success Metrics

- **MRR:** Monthly Recurring Revenue
- **Churn Rate:** % customers canceling
- **LTV:** Customer Lifetime Value
- **CAC:** Customer Acquisition Cost

**Target:** $1,000 MRR within 3 months

---

## Risks & Mitigation

**Risk:** Can't scale coaching 1-on-1  
**Solution:** Create drill library, automate common feedback

**Risk:** Low conversion rate  
**Solution:** Free trial, testimonials, money-back guarantee

**Risk:** High churn  
**Solution:** Weekly engagement, progress tracking, community

---

## Competitive Advantage

- **Price:** $29/mo vs $200/hour lessons
- **Convenience:** Upload anytime vs schedule lessons
- **Personalized:** Not cookie-cutter programs
- **Results:** Track improvement over time

---

**Status:** Ready to build  
**Time to Launch:** 7 days  
**First Dollar:** Week 2
