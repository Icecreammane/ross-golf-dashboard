# FitTrack Launch Day Checklist

## Friday, February 13, 2026 - 7:00 PM Launch

---

## Pre-Launch (Week Before)

### Monday, Feb 10
- [ ] Finalize Reddit post (pick headline, proofread body)
- [ ] Write Product Hunt first comment
- [ ] Create Twitter thread (schedule but don't post)
- [ ] Test signup flow end-to-end (new user → trial → paid)
- [ ] Set up email sequences (test each one)
- [ ] Take screenshots for Product Hunt gallery
- [ ] Write landing page copy (if not done yet)

### Tuesday, Feb 11
- [ ] Test Stripe integration (test mode → live mode transition plan)
- [ ] Set up analytics tracking (Plausible/Fathom/GA)
- [ ] Create "response templates" doc (print or keep open in tab)
- [ ] Test FitTrack on mobile (iPhone + Android if possible)
- [ ] Check all links on landing page
- [ ] Run Lighthouse audit (aim for 90+ performance)

### Wednesday, Feb 12
- [ ] Final bug sweep (test every feature)
- [ ] Verify email sequences are active
- [ ] Check Stripe webhook endpoints working
- [ ] Test password reset flow
- [ ] Test export data feature
- [ ] Prepare social media assets (images for Twitter/PH)

### Thursday, Feb 13 (Launch Day Morning)
- [ ] Get good sleep night before (seriously - you'll be up late)
- [ ] Eat well during the day (you might skip dinner)
- [ ] Clear your evening schedule (7pm-10pm blocked)
- [ ] Charge phone and laptop fully
- [ ] Have coffee/energy drink ready
- [ ] Set up second monitor if you have one (Reddit + analytics)

---

## Launch Day Timeline

### 6:00 PM - Final Prep (T-1 hour)

- [ ] Open tabs:
  - Reddit.com/r/fitness (logged in)
  - FitTrack production site
  - Stripe dashboard
  - Analytics dashboard
  - Response templates doc
  - Twitter (ready to tweet)
  
- [ ] Final production check:
  - [ ] Homepage loads correctly
  - [ ] Signup form works
  - [ ] Login works
  - [ ] Food search works
  - [ ] Dashboard displays correctly
  
- [ ] Verify Stripe is in **live mode** (not test mode)
  - [ ] Check API keys
  - [ ] Test a $1 charge (refund after)
  - [ ] Confirm webhooks are working

- [ ] Check analytics:
  - [ ] Tracking script is active
  - [ ] Test event fires correctly
  - [ ] Conversion tracking set up

- [ ] Have these ready to copy/paste:
  - [ ] Reddit post (full text)
  - [ ] Response templates
  - [ ] Landing page link

---

### 6:30 PM - Mental Prep (T-30 min)

- [ ] Read Reddit post one last time
  - [ ] Spellcheck
  - [ ] Links work
  - [ ] Formatting looks good
  
- [ ] Take 5 deep breaths (seriously - you might be nervous)

- [ ] Put phone on Do Not Disturb (except Reddit notifications)

- [ ] Grab water/coffee

- [ ] Go to bathroom (you'll be glued to screen for 2 hours)

---

### 7:00 PM - LAUNCH 🚀

- [ ] **Post to r/fitness**
  - [ ] Click "Create Post"
  - [ ] Choose "Text" post type
  - [ ] Paste headline
  - [ ] Paste body
  - [ ] Add flair if required
  - [ ] **DOUBLE CHECK EVERYTHING**
  - [ ] Hit "Post"

- [ ] Immediately after posting:
  - [ ] Pin to your Reddit profile
  - [ ] Upvote your own post (automatic but verify)
  - [ ] Open post in new tab (keep refreshing)
  - [ ] Start timer: 2 hours

- [ ] **Share to Twitter** (within 5 minutes)
  - [ ] Post thread
  - [ ] Link to Reddit post
  - [ ] Pin tweet to profile

- [ ] **Monitor analytics dashboard**
  - [ ] Refresh every 30 seconds
  - [ ] Watch for signups in real-time
  - [ ] Track traffic sources

---

### 7:00 PM - 9:00 PM - Active Monitoring (2 Hours)

**Your #1 job: Reply to EVERY comment within 5 minutes**

- [ ] Keep Reddit tab open and refreshing
- [ ] Use response templates (but customize each reply)
- [ ] Be genuine, not salesy
- [ ] Upvote every comment (even critics)
- [ ] Thank people for trying it
- [ ] Answer questions thoroughly
- [ ] Don't argue with trolls (stay positive)

**What to track:**
- [ ] Comment count (engagement)
- [ ] Upvote count (visibility)
- [ ] Signup count (conversions)
- [ ] Revenue (if anyone converts immediately)

**Red flags to watch for:**
- Post gets removed by mods (have backup plan)
- Site goes down (have Netlify/Vercel status page open)
- Stripe errors (monitor webhook logs)
- Negative comment ratio >50% (adjust tone)

**Green flags:**
- Comments asking genuine questions
- "Just signed up!" messages
- Other users defending your product
- Post hits r/fitness front page

---

### 9:00 PM - Wind Down

- [ ] Make final pass through comments
- [ ] Reply to any you missed
- [ ] Thank everyone for engaging
- [ ] Check analytics one last time
- [ ] Screenshot stats for records:
  - [ ] Reddit upvotes
  - [ ] Comment count
  - [ ] Signups
  - [ ] Revenue
  
- [ ] **Go to bed** (seriously - you'll be tempted to keep refreshing)

---

### Saturday Morning, Feb 14 - Follow-up

- [ ] Check Reddit overnight comments
- [ ] Reply to any new questions
- [ ] Check analytics:
  - [ ] Total signups
  - [ ] Conversion rate (visitors → signups)
  - [ ] Revenue (if any)
  
- [ ] **Post to Product Hunt** (if planned)
  - [ ] Launch at 12:01 AM PT (9:01 PM CT)
  - [ ] Post first comment immediately
  - [ ] Share to Twitter
  - [ ] Monitor all day Saturday

- [ ] Tweet launch results:
  - "24 hours post-launch: [X] signups, [Y] upvotes on Reddit. Blown away by the response. 🙏"

---

## Backup Plans

### If post gets removed by r/fitness mods:

**Option 1:** Repost on "Self-Promotion Saturday" (if it's Saturday)  
**Option 2:** Post to r/Fitness30Plus (more lenient rules)  
**Option 3:** Post to r/leangains, r/bodybuilding, r/gainit  
**Option 4:** Focus on Product Hunt + Twitter instead

### If site goes down:

- [ ] Check hosting status (Netlify/Vercel)
- [ ] Restart server if needed
- [ ] Post holding message: "High traffic, back in 5 mins!"
- [ ] Use Cloudflare or similar CDN to handle load

### If Stripe breaks:

- [ ] Switch to "waitlist mode" temporarily
- [ ] Collect emails instead of taking payments
- [ ] Fix issue, email waitlist when ready

### If overwhelmed by comments:

- [ ] Take a 10-minute break
- [ ] Batch reply to similar questions
- [ ] Prioritize: answer questions > respond to praise > ignore trolls

---

## Success Metrics

**Minimum Viable Launch:**
- 50+ upvotes on Reddit
- 10+ signups
- 5+ engaged comments

**Good Launch:**
- 200+ upvotes
- 50+ signups
- 20+ engaged comments
- Post hits r/fitness front page

**Great Launch:**
- 500+ upvotes
- 100+ signups
- $100+ MRR from day 1 conversions
- Mentioned in comments on other posts

**Remember:** Even if it's "just" a minimum viable launch, you still got your product in front of thousands of people. That's a win.

---

## Post-Launch Notes

### Sunday, Feb 15 - Retrospective

- [ ] Write down what worked
- [ ] Write down what didn't
- [ ] Read all feedback (even harsh stuff)
- [ ] Prioritize feature requests
- [ ] Plan iteration based on learnings
- [ ] Send update email to signups (if >10 people)

### Week After Launch

- [ ] Reply to late comments
- [ ] Monitor trial → paid conversion rate
- [ ] Fix any reported bugs
- [ ] Add top requested feature (if quick win)
- [ ] Plan next launch (ProductHunt, Hacker News, etc.)

---

## Final Reminders

✅ **You've prepared for this.** You know the product, you know the audience, you're ready.

✅ **Not everyone will like it.** That's fine. You're building for people who *do* like simple macro tracking.

✅ **Engagement matters more than upvotes.** 10 comments from interested users > 100 silent upvotes.

✅ **This is just the beginning.** Launch day is one day. Building the product is a marathon.

✅ **Have fun.** You built something. That's awesome. Enjoy the moment.

---

**Now go crush it. 🚀**
