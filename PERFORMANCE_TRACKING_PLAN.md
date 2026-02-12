# Performance Tracking Plan

**Inspired by:** Larry tracking RevenueCat metrics to understand conversion  
**Goal:** Connect marketing → product → revenue in trackable loop

---

## What Larry Tracks

**RevenueCat Integration:**
- Daily MRR ($588/month)
- Subscriber count (108 paying)
- Churn rate
- Conversion from TikTok → Download → Trial → Paid

**Why it matters:** Larry knows which TikTok posts convert, not just which get views.

---

## What We Should Track

### Phase 1: Product Launches (This Weekend)

**For each product launched:**
```json
{
  "product": "Golf Coaching Site",
  "launched": "2026-02-15",
  "pricing": "$29/month",
  "metrics": {
    "visitors": 0,
    "signups": 0,
    "paying": 0,
    "mrr": 0,
    "churn": 0
  },
  "traffic_sources": {
    "twitter": 0,
    "reddit": 0,
    "word_of_mouth": 0
  }
}
```

**Tracked in:** `metrics/product-performance.json`

### Phase 2: Stripe Integration (Next Week)

**Connect Stripe API:**
- Customer count
- MRR calculation
- Churn tracking
- Failed payments

**Arnold accesses via Stripe API** to answer:
- "How many customers do we have?"
- "What's our MRR?"
- "Any failed payments today?"

### Phase 3: Traffic Attribution (March)

**When LD posts social content:**
- Track UTM parameters
- Which posts drive signups?
- Which platforms convert best?
- ROI per channel

**LD learns:** "Twitter threads convert 3x better than single tweets" → do more threads

### Phase 4: Cohort Analysis (April+)

**Track user lifecycle:**
- Day 0: Sign up
- Day 1: First use
- Day 7: Still active?
- Day 30: Converted to paid?

**Arnold optimizes:** Onboarding flow based on where users drop off

---

## Implementation

### This Weekend:
Create `metrics/product-performance.json`:
```json
{
  "products": [
    {
      "name": "Golf Coaching Site",
      "url": "golfcoaching.rossw.com",
      "launched": "2026-02-15",
      "status": "live",
      "pricing": {
        "model": "subscription",
        "amount": 29,
        "currency": "USD",
        "interval": "month"
      },
      "metrics": {
        "total_customers": 0,
        "active_subscribers": 0,
        "mrr": 0,
        "lifetime_revenue": 0
      },
      "last_updated": "2026-02-15T12:00:00Z"
    }
  ]
}
```

### Next Week:
**Stripe API Integration:**
```python
# scripts/track_revenue.py
import stripe
import json
from datetime import datetime

def get_mrr():
    """Calculate MRR from Stripe subscriptions"""
    subscriptions = stripe.Subscription.list(status='active')
    mrr = sum(sub.plan.amount / 100 for sub in subscriptions.data)
    return mrr

def update_metrics():
    """Update product performance metrics"""
    with open('metrics/product-performance.json') as f:
        data = json.load(f)
    
    # Update each product
    for product in data['products']:
        # Get Stripe data for this product
        mrr = get_mrr_for_product(product['name'])
        customers = get_customer_count(product['name'])
        
        # Update metrics
        product['metrics']['mrr'] = mrr
        product['metrics']['active_subscribers'] = customers
        product['last_updated'] = datetime.utcnow().isoformat()
    
    # Write back
    with open('metrics/product-performance.json', 'w') as f:
        json.dump(data, f, indent=2)
```

Run daily at 10pm (same time as cost tracker).

### March (When LD Joins):
**Content Performance Tracking:**
```json
{
  "posts": [
    {
      "date": "2026-03-01",
      "platform": "twitter",
      "hook": "Built 3 products this weekend...",
      "metrics": {
        "views": 15000,
        "likes": 234,
        "retweets": 45,
        "clicks": 123,
        "signups": 5,
        "conversions": 1
      },
      "roi": {
        "cost": 0,
        "revenue": 29,
        "roi_percent": "infinite"
      }
    }
  ]
}
```

**LD learns:** Which hooks drive actual revenue, not just engagement.

---

## Dashboard (Future)

**Simple HTML dashboard:**
```
http://localhost:8080/metrics

Products:
- Golf Coaching: $58 MRR (2 customers)
- Notion Templates: $47 one-time
- Fitness Tracker: $15 MRR (3 customers)

Total MRR: $73
Monthly Revenue: $120

Top Traffic Sources:
1. Twitter (45%)
2. Reddit (30%)
3. Word of mouth (25%)

Best Converting Content:
1. "Villain era dating" thread → 2 signups
2. "Built 3 products" tweet → 1 signup
```

---

## Key Insight from Article

> "Larry has access to my RevenueCat analytics. This gives him access to all my reports for customer subscriptions and churn, important metrics for him to track and suggest improvements. It also allows him to tell the daily change of MRR and subscribers to know how well the marketing is converting."

**Translation for us:**

Arnold should know:
- Which products make money
- Which marketing drives conversions
- Where users drop off
- What to optimize next

Not just "build features" — build features that increase revenue.

---

**Status:** Design phase  
**Implementation:** Start this weekend (metrics file)  
**Full integration:** March 2026 (Stripe API + Content tracking)
