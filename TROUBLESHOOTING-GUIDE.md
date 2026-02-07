# 🆘 Golf Coaching Launch - Troubleshooting Guide

## 🔴 Critical Issues (Fix Immediately)

### Issue: Form not receiving submissions

**Symptoms:**
- People say they signed up but you didn't get email
- Form shows success but nothing arrives

**Diagnosis:**
1. Check Formspree dashboard - are submissions there?
2. Check spam folder
3. Test form yourself with your email

**Fix:**
```bash
# Option 1: Check Formspree account
1. Go to https://formspree.io/forms
2. Find your form "Golf Coaching Signups"
3. Check if submissions are there
4. Update your notification email if wrong

# Option 2: If Formspree is down, quick pivot to Google Forms
1. Create Google Form: https://forms.google.com
2. Add fields: Email, Name, Handicap
3. Get shareable link
4. Edit landing page:
   - Replace entire form with iframe to Google Form
   - OR add "Form not working? Sign up here: [Google Form link]"
```

**Prevention:**
- Test form before launch with 2-3 emails
- Check Formspree dashboard after first Reddit comment

---

### Issue: Landing page not loading

**Symptoms:**
- URL returns 404
- Page loads but looks broken
- CSS not loading

**Diagnosis:**
```bash
# Test page loading
curl -I https://your-site.netlify.app

# If 404: page not deployed
# If 200: page is live
# If timeout: DNS issue
```

**Fix:**

**Netlify:**
```bash
# 1. Check site status
# Go to: https://app.netlify.com/sites/[your-site]/deploys

# 2. If deploy failed:
# - Check error logs in deploy log
# - Common issue: file renamed/moved

# 3. If site deleted:
# - Re-upload golf-coaching-landing.html
# - Rename to index.html
```

**GitHub Pages:**
```bash
# 1. Check repo settings
# Go to: Settings > Pages
# Make sure source is set to main branch

# 2. Check file name
# Must be index.html or in docs/ folder

# 3. Wait 2-3 minutes for deploy
```

**Emergency backup:**
```bash
# If can't fix in 5 minutes, use raw GitHub URL:
1. Upload HTML to GitHub
2. Use: https://htmlpreview.github.io/?[raw-github-url]
3. Post that URL to Reddit temporarily
```

---

### Issue: Mobile view looks broken

**Symptoms:**
- Text cut off on phone
- Buttons don't work
- Page too wide

**Quick fix:**
```bash
# Test mobile view:
# 1. Open page on phone
# 2. Or: Desktop Chrome > F12 > Toggle device toolbar

# Common issues:
# - Form too wide → add max-width: 100%
# - Text tiny → check viewport meta tag
# - Buttons not clickable → check z-index

# Emergency fix if broken:
# Add this to <head>:
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

---

## 🟡 Common Issues (Address Soon)

### Issue: Reddit post getting downvoted

**Symptoms:**
- Post at 0 or negative upvotes
- Comments are critical/negative

**Diagnosis:**
- Check if post violates r/golf rules
- Is tone too salesy?
- Wrong time of day?

**Fix:**

**If violating rules:**
```
1. Delete post immediately
2. Message mods: "Sorry, didn't realize. Can I repost with [fix]?"
3. Wait for approval
4. Repost with corrections
```

**If just bad reception:**
```
1. Don't delete - keep engaging
2. Respond to criticism authentically
3. Offer free analysis to top skeptic
4. Learn from comments, try again in 2-3 days

Pivots to try:
- Different title (more humble)
- Different subreddit (r/golftips, r/golf_swing)
- Different approach (ask for feedback, not selling)
```

---

### Issue: Lots of engagement, zero signups

**Symptoms:**
- 50+ upvotes, 20+ comments
- People interested
- Zero form submissions

**Diagnosis:**
- Landing page broken?
- Price too high?
- Not enough trust?

**Fix:**

**Check the funnel:**
```bash
# 1. Click your own Reddit link
# Does it work? Load fast? Form visible?

# 2. Submit test form
# Does it work?

# 3. Check mobile view
# Most Reddit traffic is mobile!
```

**If page works:**
```
Trust issue - try:
1. Offer first 3 people free analysis in comments
2. Add your photo to landing page
3. Record 30-second intro video
4. Share your handicap/background more

Price issue - test:
1. Drop to $19/month
2. First month free
3. Single $29 one-time analysis
```

---

### Issue: Getting signups but no one converts to paid

**Symptoms:**
- People fill out form
- You email them
- No response

**Diagnosis:**
- Email going to spam?
- Message not clear?
- Too much friction?

**Fix:**

**Check email delivery:**
```bash
# 1. Check spam folder (duh)
# 2. Send from real email (not noreply@)
# 3. Keep it conversational, not automated

# Better: Text them directly
# "Hey! Got your signup, ready for your first video?"
```

**Reduce friction:**
```
Make it stupid easy:
1. "Reply to this email with your swing video"
2. "Text me at [number], I'll text you instructions"
3. "No video yet? No problem, I'll wait"

Don't:
- Require payment before first analysis
- Make them create account anywhere
- Send them to another form
```

---

### Issue: One person signed up and you're freaking out about delivering

**Symptoms:**
- First real customer
- Nervous about analyzing swing
- Worried you'll disappoint

**Fix:**

**You got this! Here's the plan:**

```
1. Breathe. You don't need to be perfect.

2. Watch their swing 3-5 times
   - What stands out immediately?
   - What's the biggest issue?
   - What's one thing that would help most?

3. Record a simple video analysis
   - Screen record using QuickTime (Mac) or OBS (free)
   - Talk through their swing frame by frame
   - Point out 1-2 main issues
   - Keep it under 5 minutes

4. Write a simple email
   - Summary of main issue
   - 2-3 drills that would help
   - Links to videos of the drills (YouTube)
   - "Try these for a week, send me an update"

5. Follow up in 3 days
   - "How's it going?"
   - Offer to clarify anything
   - Adjust drills if needed

Pro tip: Over-deliver on first customer
- Respond fast (within 12 hours)
- Be available for questions
- Check in proactively
- They'll become your best testimonial
```

---

## 🟢 Non-Critical Issues (Nice to Fix)

### Issue: Someone asks a question you don't know the answer to

**Fix:**
- "Great question! Let me think about that and get back to you."
- Research it
- Respond within a few hours
- Be honest if you don't know

**Don't:**
- Make shit up
- Pretend to know something you don't
- Get defensive

---

### Issue: Someone calls you out for not being certified

**Fix:**
```
"You're absolutely right - I'm not a PGA pro or certified instructor. 
This is more like having a knowledgeable friend help you out for cheap, 
not formal coaching. If you need PGA-level instruction, this probably 
isn't for you. But if you want affordable feedback from someone who's 
been through the improvement grind, I'm here!"
```

**Don't:**
- Argue
- Pretend to have credentials
- Get defensive

---

### Issue: Formspree says you hit free tier limit

**Symptoms:**
- More than 50 submissions in one month (congrats!)
- Forms stop working

**Fix:**
```bash
# Option 1: Upgrade Formspree ($10/mo for 1000 forms)
# Worth it if you're getting customers!

# Option 2: Switch to Google Forms
# See "Form not working" section above

# Option 3: Use Netlify Forms (built-in)
# If using Netlify hosting:
# Add netlify attribute to form:
<form netlify name="golf-signups">
```

---

### Issue: You're overwhelmed with customers

**Good problem!**

**Fix:**
```
If you have 10+ active customers:

1. Close signups temporarily
   - Update landing page: "Currently full, join waitlist"
   - Add waitlist form

2. Raise prices for new members
   - $29/month (as planned)
   - First 10 keep their $14.50

3. Batch your work
   - Set specific days for analysis (Mon/Wed/Fri)
   - Block out 2-hour chunks
   - Don't try to do everything in real-time

4. Create templates
   - Common swing issues
   - Standard drill recommendations
   - Weekly check-in templates

5. Consider hiring help
   - If making $300+/month, outsource video editing
   - Fiverr for basic video annotations
   - You still do the analysis
```

---

## 🧰 Emergency Toolkit

### Quick link to test landing page on mobile
```bash
# Get your computer's local IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# Start local server
cd ~/clawd
python3 -m http.server 8000

# Visit on phone: http://[your-ip]:8000/golf-coaching-landing.html
```

### Quick form test
```bash
# Submit test form via command line (Mac/Linux)
curl -X POST https://formspree.io/f/YOUR_FORM_ID \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","handicap":"15"}'
```

### Check if site is down (not just you)
- https://downforeveryoneorjustme.com/your-site-url
- https://isitdownrightnow.com/your-site-url

### Reddit post performance benchmark
- 10+ upvotes in 1 hour = good
- 50+ upvotes in 24 hours = great
- 100+ upvotes = viral

If under 5 upvotes after 1 hour → might be bad timing or wrong sub

---

## 📞 When to Ask for Help

**Ask Ross:**
- Form completely broken and can't fix in 10 minutes
- Post getting negative feedback and unsure how to respond
- First customer asked question you truly don't know
- Page is down and you can't figure out why

**Ask Reddit:**
- Technical issues (r/webdev, r/netlify)
- Formspree issues (their support is quick)
- Golf-specific questions (r/golf, r/golftips)

**Ask ChatGPT/Claude:**
- How to analyze specific swing faults
- HTML/CSS fixes for landing page
- Email copywriting improvements
- "Here's the comment I got, how should I respond?"

---

## 🎯 Success Checklist (You're Doing Great If...)

- [ ] 1+ form submission = people are interested!
- [ ] 1+ paying customer = idea validated!
- [ ] 1+ positive comment = you provided value!
- [ ] 0 refunds = customers are happy!
- [ ] 1+ testimonial = social proof building!

**Don't stress if:**
- Post gets downvoted (Reddit is random)
- Only 2-3 people sign up first week (that's normal)
- Someone criticizes your lack of credentials (be honest, move on)
- You're nervous about first analysis (everyone is, you'll do great)

**You're building something real. One customer at a time.** 🏌️
