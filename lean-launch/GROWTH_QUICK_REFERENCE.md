# Lean Growth Engine - Quick Reference

**5 systems ready to launch →**

---

## 🎁 1. Referral System

**User Flow:**
1. User visits `/settings`
2. Sees their unique referral code (e.g., `XY8Z4K2L`)
3. Clicks "Copy Link" → gets `lean.app?ref=XY8Z4K2L`
4. Shares with friend
5. Friend signs up with code
6. Both get 30 days Pro after friend logs first meal

**Test It:**
```bash
# Visit settings page
http://localhost:3000/settings

# Or use API
curl -X POST http://localhost:3000/api/referral/generate \
  -H "Content-Type: application/json" \
  -d '{"user_id": "ross"}'
```

**Track Performance:**
- View stats in `/settings` under "Refer Friends"
- Check `referral_data.json` for raw data

---

## 📊 2. Viral Share Cards

**User Flow:**
1. User visits `/settings`
2. Clicks "Generate Share Card"
3. App creates Instagram-story-ready image (1080x1920)
4. Preview shows in page
5. Click "Download Image" for local save
6. Share to Instagram/Twitter/anywhere

**What It Shows:**
- "Lost X lbs in Y weeks with @LeanApp"
- Progress bar to goal
- Current weight, goal weight, remaining
- Clean branding

**Test It:**
```bash
# Generate via API
curl -X POST http://localhost:3000/api/share/progress \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "ross",
    "weight_lost": 12,
    "weeks": 8,
    "current_weight": 175,
    "goal_weight": 160
  }'
```

**Output Location:**
- `static/shares/lean_progress_*.png`
- Accessible at `/static/shares/filename.png`

---

## 📈 3. Analytics (PostHog)

**What's Tracked:**
- User signups (with source)
- Meal logging (voice vs photo vs text)
- Goal setting
- Share card generation
- Referral usage
- Subscription purchases
- Milestones & streaks

**Setup:**
1. Create free PostHog account: https://posthog.com
2. Get API key
3. Add to `.env`:
   ```
   POSTHOG_API_KEY=phc_xxxxxxxxxxxx
   ```
4. Install: `pip install posthog`

**View Dashboard:**
- Login to PostHog
- See live events, funnels, retention
- Track conversion rates
- Analyze user behavior

**Test It:**
```bash
# Events tracked automatically when users:
- Sign up
- Log meals
- Set goals
- Generate shares
- Use referral codes
```

---

## 💳 4. Stripe Payments

**Plans:**
- **Free:** $0 - 50 meals/month
- **Pro:** $4.99/mo - Unlimited meals
- **Lifetime:** $49 - One-time payment

**User Flow:**
1. User hits meal limit (50/month on free)
2. Sees "Upgrade to Pro" prompt
3. Clicks → redirects to `/pricing`
4. Chooses plan → Stripe Checkout opens
5. Enters card (test: `4242 4242 4242 4242`)
6. Redirects to `/payment_success`
7. Account upgraded instantly

**Setup:**
1. Create Stripe account: https://stripe.com
2. Get test keys (Dashboard → API keys)
3. Add to `.env`:
   ```
   STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxx
   STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxx
   ```
4. Install: `pip install stripe`

**Webhook Setup:**
1. Stripe Dashboard → Webhooks
2. Add endpoint: `https://yourdomain.com/api/webhook/stripe`
3. Select event: `checkout.session.completed`
4. Add secret to `.env`

**Test Cards:**
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- Use any future expiry, any CVC

---

## 📧 5. Email Capture

**User Flow:**
1. Visitor lands on `/landing_email.html`
2. Enters name & email
3. Submits form
4. Gets welcome email (Day 0)
5. Receives follow-up emails (Day 3, 7)

**Setup Options:**

### Option A: Simple (Local)
- No setup needed
- Emails saved to `email_subscribers.json`
- Access via API: `/api/email/stats`

### Option B: Airtable
1. Create base with "Subscribers" table
2. Get API key: https://airtable.com/account
3. Add to `.env`:
   ```
   AIRTABLE_API_KEY=keyxxxxxxxxxxxx
   AIRTABLE_BASE_ID=appxxxxxxxxxxxx
   ```
4. Emails auto-sync to Airtable

### Option C: Loops.so (Recommended)
1. Create account: https://loops.so
2. Get API key
3. Add to `.env`:
   ```
   LOOPS_API_KEY=xxxxxxxxxxxx
   ```
4. Drip emails sent automatically

**Test It:**
```bash
# Submit via landing page
http://localhost:3000/landing_email.html

# Or use API
curl -X POST http://localhost:3000/api/email/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Ross",
    "source": "landing"
  }'
```

---

## 🚀 Launch Checklist

### Pre-Launch
- [ ] Add production API keys to `.env`
- [ ] Switch Stripe to live mode
- [ ] Configure PostHog project
- [ ] Set up Loops.so or email service
- [ ] Test referral flow end-to-end
- [ ] Generate test share card
- [ ] Process test payment (then refund)
- [ ] Verify webhook delivery

### Launch Day
- [ ] Monitor PostHog dashboard
- [ ] Watch Stripe events
- [ ] Check email deliverability
- [ ] Track first referrals
- [ ] Monitor error logs
- [ ] Respond to user feedback

---

## 📊 Key Metrics

**Track These:**

| Metric | Where to Check | Target |
|--------|---------------|--------|
| Signups | PostHog | 100/week |
| Referral rate | `/api/email/stats` | 20% |
| Share cards generated | PostHog | 50% of users |
| Free → Pro conversion | Stripe | 10% |
| Email capture rate | Landing page | 30% |

---

## 🐛 Troubleshooting

### "Referral rewards not granted"
- New user must log first meal
- Check `referral_data.json`
- Verify referral code matches

### "Share cards won't generate"
- Install: `pip install Pillow`
- Check `static/shares/` exists
- Verify image preview shows

### "Stripe webhook not firing"
- Use ngrok for local testing: `ngrok http 3000`
- Update webhook URL in Stripe
- Check webhook secret matches

### "Analytics not tracking"
- Verify PostHog API key
- Check browser console
- Events take 1-2 min to appear

### "Emails not sending"
- Verify Loops.so API key
- Check Airtable permissions
- Review console logs

---

## 💡 Pro Tips

1. **Test with incognito** - Use private browsing to test referral flow
2. **Use ngrok** - For local Stripe webhook testing
3. **Monitor early** - Watch dashboards closely first week
4. **Iterate fast** - Adjust pricing/copy based on data
5. **Celebrate wins** - Share milestones with users

---

## 📞 Quick Commands

```bash
# Start app
python app_pro.py

# Run tests
python test_growth_systems.py

# Check subscriber stats
curl http://localhost:3000/api/email/stats

# Check user subscription
curl "http://localhost:3000/api/subscription/status?user_id=ross"

# View pricing
curl http://localhost:3000/api/pricing
```

---

## 📚 Full Documentation

**See `GROWTH.md` for:**
- Complete API reference
- Setup instructions
- Environment variables
- Deployment guide
- Troubleshooting
- Growth strategies

---

**Built:** 2026-02-13  
**Status:** Production-ready ✅  
**Location:** `/Users/clawdbot/clawd/fitness-tracker/`

🚀 **Ready to launch!**
