# FitTrack Email Sequences

## Email 1: Welcome Email
**Trigger:** Immediately after signup  
**Subject:** Welcome to FitTrack! Here's how to get started

---

**Body:**

Hey [First Name],

Thanks for signing up for FitTrack! 

You've got 7 days to try it out - no credit card required, no pressure.

**Here's how to get started:**

1. **Log your first meal:** Hit the "Add Food" button and search for what you ate today. The database has 500k+ foods, so you'll probably find it.

2. **Set your macro targets:** Go to Settings → Nutrition Goals and enter your daily targets (protein, carbs, fat). Not sure what they should be? Start with what you're currently hitting and adjust from there.

3. **Track your weight (optional):** If you want to see trends alongside your nutrition, tap "Log Weight" on the dashboard.

That's it. FitTrack is intentionally simple - you'll figure it out in about 30 seconds.

**Quick tips:**
- Save your favorite foods for faster logging
- Log as you go (don't wait until end of day)
- Barcode scanner coming soon (for now, search is your friend)

If you hit any issues or have questions, just reply to this email. I read every one.

Happy tracking,  
Ross

P.S. — I built FitTrack because I was tired of complicated trackers. If it resonates with you, I'd love to hear why. And if it doesn't, I'd love to hear that too.

---

## Email 2: Day 3 Check-in
**Trigger:** 3 days after signup  
**Subject:** How's it going? Need any help?

---

**Body:**

Hey [First Name],

You've been using FitTrack for a few days now - how's it going?

I'm checking in because I want to make sure it's actually working for you. 

**A few things people usually ask by now:**

- **"Can I track [specific food]?"** — If it's not in the database, you can add custom foods (Settings → Custom Foods)
- **"Can I adjust servings?"** — Yep, just tap the food and edit the portion size
- **"Can I see past days?"** — Use the date picker at the top of the dashboard

**What I'd love to know:**
- Is there anything confusing?
- Missing a feature you need?
- Finding it useful so far?

Just reply to this email - I read every response and use it to make FitTrack better.

Thanks for trying it out,  
Ross

P.S. — Your trial ends in 4 days. No pressure, but if you're finding it useful, you can upgrade anytime in Settings.

---

## Email 3: Day 6 Trial Reminder
**Trigger:** 6 days after signup (1 day before trial ends)  
**Subject:** Your trial ends tomorrow - keep going?

---

**Body:**

Hey [First Name],

Just a heads up: your 7-day free trial ends tomorrow.

**If you want to keep using FitTrack,** head to Settings → Billing and enter your payment info. It's $10/month, cancel anytime.

**If you're not feeling it,** no worries - your account will go read-only after the trial ends, but you can still export your data.

**Still on the fence?**

Here's what people usually say after a week:

✅ "I didn't realize how much faster this is than MyFitnessPal"  
✅ "Finally, a tracker that doesn't feel like a chore"  
✅ "Worth it just for the clean UI and no ads"

But also, I get it - $10/month is real money. If you're not convinced it's worth it, don't pay for it. I'd rather you use a free alternative than pay for something you don't love.

**Before you go:** If there's a reason you're not upgrading (missing feature, too expensive, etc.), I'd genuinely love to hear it. Reply to this email and let me know.

Thanks for giving FitTrack a shot,  
Ross

---

## Email 4: Payment Success
**Trigger:** After first charge (trial → paid)  
**Subject:** Thanks for supporting FitTrack!

---

**Body:**

Hey [First Name],

You just became a paying FitTrack customer. Thanks for supporting what I'm building - it means a lot.

**What happens now:**

- You'll be charged $10/month automatically (you can cancel anytime in Settings)
- You'll get updates when I ship new features
- If you ever have issues or feedback, just reply to any email - I respond to everyone

**What's coming next:**

I'm building based on what users ask for. Right now, the top requests are:

1. Mobile apps (iOS/Android)
2. Barcode scanner
3. Meal templates / saved combos

If you have other ideas, let me know. I'm one person building this, so I can move fast on good suggestions.

Thanks again for the support,  
Ross

P.S. — If FitTrack is working for you, I'd be grateful if you shared it with a lifting buddy. Word of mouth is how this grows.

---

## Email 5: Re-engagement (7 days no activity)
**Trigger:** User hasn't logged in for 7 days  
**Subject:** We miss you! Come back?

---

**Body:**

Hey [First Name],

I noticed you haven't logged anything in FitTrack for a week.

**If you're busy, life happens** - no judgment. Your account is still active whenever you want to come back.

**If something's not working,** I'd love to fix it. Was the app confusing? Missing a feature you need? Too slow? Let me know - I'm actively improving things based on feedback.

**If you're just not feeling it,** that's cool too. You can cancel anytime in Settings, and I won't be offended.

Either way, I'd appreciate knowing what happened. Reply to this email and let me know - even if it's just "not for me," it helps me understand how to make FitTrack better.

Thanks,  
Ross

P.S. — If you come back and log a meal today, I'll send you a virtual high-five. 🙌

---

## Email 6: (Bonus) Cancellation Follow-up
**Trigger:** User cancels subscription  
**Subject:** Sorry to see you go

---

**Body:**

Hey [First Name],

You just cancelled your FitTrack subscription. 

**You'll still have access until [end of billing period],** and you can export your data anytime from Settings.

**If you changed your mind,** you can reactivate anytime - no hard feelings.

**If you're leaving for good,** I'd love to know why. Was it:

- Too expensive?
- Missing a feature you needed?
- Found a better alternative?
- Just didn't stick with tracking?

Whatever the reason, I'd genuinely appreciate the feedback. Reply to this email and let me know - it'll help me make FitTrack better for the next person.

Thanks for giving it a shot,  
Ross

---

## Technical Setup Notes

**Email service:** Use something like Mailgun, SendGrid, or Postmark (transactional email)

**Automation triggers:**
- Email 1: Trigger on `user.created` event
- Email 2: Schedule 3 days after signup
- Email 3: Schedule 6 days after signup
- Email 4: Trigger on `subscription.created` event
- Email 5: Trigger if `last_activity` > 7 days
- Email 6: Trigger on `subscription.cancelled` event

**From address:** ross@fittrack.app (or similar - looks more legit than Gmail)

**Reply-to:** Same as from (you want people to reply)

**Unsubscribe link:** Required by law - add at bottom of every email

**Personalization:**
- [First Name] = user's first name (or "there" if empty)
- [End of billing period] = date their access ends

**A/B test ideas:**
- Subject lines (try 2-3 variations)
- CTA placement (top vs bottom)
- Length (some people prefer shorter)

**Metrics to track:**
- Open rate (aim for >30%)
- Click rate (aim for >5%)
- Reply rate (aim for >1%)
- Conversion rate (trial → paid)
