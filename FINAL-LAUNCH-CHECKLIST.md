# ✅ FINAL LAUNCH CHECKLIST - Golf Coaching
## Complete this top to bottom, then you're ready to post.

---

## 🔧 Part 1: Landing Page Setup (30 minutes)

### Step 1: Set Up Formspree Form
- [ ] Go to https://formspree.io/ and create account
- [ ] Create new form: "Golf Coaching Signups"
- [ ] Copy your form endpoint (https://formspree.io/f/YOUR_ID)
- [ ] Open `~/clawd/golf-coaching-landing.html`
- [ ] Find line 193 and replace `YOUR_FORM_ID` with your actual ID
- [ ] Save file

**Guide:** See `FORMSPREE-SETUP.md` for detailed instructions

### Step 2: Add Your Contact Info
- [ ] Open `~/clawd/golf-coaching-landing.html`
- [ ] Find line ~250 (search for "ross@yourdomain.com")
- [ ] Replace with your real email
- [ ] Replace "Your phone number here" with your real number
- [ ] Save file

### Step 3: Deploy Landing Page
Choose ONE deployment method:

**Option A: Netlify Drop (Easiest, 5 minutes)**
- [ ] Go to https://app.netlify.com/drop
- [ ] Drag `golf-coaching-landing.html` onto the page
- [ ] **Important:** Rename file to `index.html` when uploading
- [ ] Copy your site URL (e.g., `random-name.netlify.app`)
- [ ] (Optional) Change subdomain in Site Settings

**Option B: GitHub Pages**
- [ ] Create GitHub repo: `golf-coaching`
- [ ] Upload `golf-coaching-landing.html` as `index.html`
- [ ] Go to Settings > Pages
- [ ] Enable Pages from main branch
- [ ] Copy your site URL

**Your landing page URL:**
```
Write it here: ________________________________
```

### Step 4: Test Landing Page
- [ ] Visit your deployed URL on desktop browser
- [ ] Visit URL on your phone (mobile view)
- [ ] Fill out form with YOUR email as test
- [ ] Submit form
- [ ] Check you received notification email
- [ ] Verify form redirects properly after submit
- [ ] Click all buttons (smooth scroll works?)
- [ ] Page loads in under 3 seconds
- [ ] No broken images or weird styling

**If anything is broken:** See `TROUBLESHOOTING-GUIDE.md`

---

## 📝 Part 2: Reddit Post Preparation (10 minutes)

### Step 5: Choose Your Post Title
Open `REDDIT-POST-FINAL.md` and pick one title:

- [ ] **Option 1:** Value-first approach (RECOMMENDED)
- [ ] **Option 2:** Question hook
- [ ] **Option 3:** Humble approach

**Write your chosen title here:**
```
_________________________________________________________________
```

### Step 6: Update Post Body with Your URL
- [ ] Open `REDDIT-POST-FINAL.md`
- [ ] Copy the "Post Body (Copy-Paste Ready)" section
- [ ] Replace `[YOUR_URL_HERE]` with your actual landing page URL
- [ ] Save this updated version somewhere easy to copy

**Or use the launch script (it does this automatically):**
```bash
bash ~/clawd/launch-golf-coaching.sh
```

### Step 7: Review Response Templates
- [ ] Open `REDDIT-POST-FINAL.md`
- [ ] Read through all 12 response templates
- [ ] Bookmark this file for easy access during launch
- [ ] Feel confident you can handle common questions

### Step 8: Plan Your Launch Timing

**Recommended time:** Wednesday, 7-9pm ET

**Your planned launch time:**
```
Day: ____________  Time: ____________  (Your timezone: __________)
```

- [ ] Clear 2 hours in your calendar after posting
- [ ] Set phone notifications for Reddit
- [ ] Turn off distractions (you need to focus on comments)

---

## 📧 Part 3: Post-Launch Setup (10 minutes)

### Step 9: Prepare Email Templates
- [ ] Open `EMAIL-TEMPLATES.md`
- [ ] Copy "Email 1: Welcome Email" to your email drafts
- [ ] Replace `[your_email]` and `[your_phone]` with real info
- [ ] Replace `[Name]` placeholders (you'll personalize per person)
- [ ] Have this ready to send immediately after first signup

### Step 10: Set Up Tracking
- [ ] Create or open today's memory file: `memory/YYYY-MM-DD.md`
- [ ] Add tracking section:

```markdown
## 🚀 Golf Coaching Launch Tracking

**Launch time:** _________
**Reddit post URL:** _________

### Metrics:
- Upvotes (1 hour): ___
- Comments (1 hour): ___
- Form submissions (1 hour): ___
- Upvotes (24 hours): ___
- Form submissions (24 hours): ___
- Paying customers (1 week): ___

### Notes:
- Best-performing comment: 
- Common questions: 
- Things to improve: 
```

### Step 11: Test Launch Script (Optional but Recommended)
```bash
cd ~/clawd
bash launch-golf-coaching.sh
```

This script will:
- ✅ Verify landing page is accessible
- ✅ Copy post to clipboard
- ✅ Show title options
- ✅ Open Reddit
- ✅ Set 2-hour reminder
- ✅ Log launch to memory

---

## 🚀 Part 4: LAUNCH DAY (5 minutes + 2 hours of engagement)

### Step 12: Final Pre-Launch Check
**Right before posting:**

- [ ] Landing page is live and loads properly
- [ ] Form is working (did you test it?)
- [ ] You have 2+ hours free to engage
- [ ] Response templates are open
- [ ] Phone notifications are on
- [ ] You're ready!

### Step 13: Post to r/golf

**Manual method:**
1. [ ] Go to https://reddit.com/r/golf
2. [ ] Click "Create Post"
3. [ ] Paste your chosen title
4. [ ] Paste your post body (with your URL inserted)
5. [ ] Select "Discussion" flair (NOT "Promotion")
6. [ ] Hit "Post"

**Script method:**
```bash
bash ~/clawd/launch-golf-coaching.sh
# Follow the prompts, it'll open Reddit and copy everything
```

**Your post URL:**
```
Paste here: ________________________________________
```

### Step 14: Engage Like Crazy (First 2 Hours Critical!)

**Minutes 0-15:**
- [ ] Check post every 2-3 minutes
- [ ] Respond to EVERY comment immediately
- [ ] Thank people for feedback
- [ ] Be conversational, not salesy

**Minutes 15-60:**
- [ ] Check every 5-10 minutes
- [ ] Respond to new comments within 5 min
- [ ] Upvote everyone who comments
- [ ] Answer questions thoroughly using your templates

**Minutes 60-120:**
- [ ] Check every 10-15 minutes
- [ ] Continue responding to all comments
- [ ] Update landing page if common questions emerge
- [ ] Screenshot positive comments for testimonials

**After 2 hours:**
- [ ] Check every 30-60 minutes for rest of day
- [ ] Respond to late comments (still important!)
- [ ] Check form submissions
- [ ] Send welcome emails to anyone who signed up

---

## 📬 Part 5: First Signup Response (Act Fast!)

### Step 15: When You Get First Signup

**Within 1 hour:**
- [ ] Check Formspree dashboard for submission
- [ ] Copy their info to tracking spreadsheet
- [ ] Send "Email 1: Welcome Email" (see EMAIL-TEMPLATES.md)
- [ ] Personalize it with their name
- [ ] Provide clear instructions for sending swing video

**Within 24 hours of receiving their swing video:**
- [ ] Watch video 3-5 times
- [ ] Identify main issue
- [ ] Record or write detailed analysis
- [ ] Provide 2-3 custom drills
- [ ] Send "Email 2: After First Analysis"

**Within 3 days:**
- [ ] Send "Email 3: Follow-Up" check-in
- [ ] Ask how drills are going
- [ ] Offer to answer questions

---

## 🎯 Part 6: Success Tracking (Ongoing)

### Immediate Success Metrics (First 24 Hours)
- [ ] **5+ upvotes** = Post is being seen
- [ ] **10+ comments** = Engagement is happening
- [ ] **3+ form submissions** = Interest is real
- [ ] **1+ positive comments** = People see value

### Week 1 Success Metrics
- [ ] **50+ upvotes** = Strong post
- [ ] **10+ form submissions** = Good conversion
- [ ] **5+ paying customers** = Validated idea
- [ ] **0 refunds** = Delivering value

### Week 2-4 Success Metrics
- [ ] **3+ testimonials** = Social proof
- [ ] **10 paying customers** = Hit your goal!
- [ ] **Update landing page** with real testimonials
- [ ] **Close to new signups** (you're at capacity!)

---

## 🆘 Emergency Contacts

**If landing page breaks:**
- See: `TROUBLESHOOTING-GUIDE.md`

**If form breaks:**
- See: `FORMSPREE-SETUP.md`
- Backup: Create Google Form and add link to landing page

**If Reddit post flops:**
- Don't panic – wait 2-3 days and try different title/approach
- See: `TROUBLESHOOTING-GUIDE.md` > "Reddit post getting downvoted"

**If overwhelmed:**
- Take a breath
- You don't need to be perfect
- One customer at a time
- You got this!

---

## 📂 Quick Reference - All Your Files

All files are in `~/clawd/`:

1. **golf-coaching-landing.html** - The landing page (edit this)
2. **REDDIT-POST-FINAL.md** - Post drafts + 12 response templates
3. **EMAIL-TEMPLATES.md** - 7 email templates for customer journey
4. **FORMSPREE-SETUP.md** - Detailed form setup guide
5. **TROUBLESHOOTING-GUIDE.md** - Fixes for common issues
6. **FINAL-LAUNCH-CHECKLIST.md** - This file (your roadmap)
7. **launch-golf-coaching.sh** - Automated launch script

---

## ✨ You're Ready to Launch!

### Pre-flight final check:
- ✅ Landing page is live
- ✅ Form is tested and working
- ✅ Contact info is added
- ✅ Reddit post is prepared
- ✅ Response templates are ready
- ✅ Email templates are ready
- ✅ 2+ hours are cleared for engagement
- ✅ You're confident (or at least ready!)

---

## 🎯 The Moment of Truth

**When you're ready:**

1. Take a deep breath
2. Run `bash ~/clawd/launch-golf-coaching.sh` OR post manually
3. Hit "Post" on Reddit
4. Engage authentically for 2 hours
5. Celebrate your first signup! 🎉

**Remember:**
- You don't need 100 customers to succeed
- You just need 10 happy customers
- One at a time
- Over-deliver
- Ask for feedback
- Iterate

**You've got everything you need. Now go get your first customer!** 🏌️

---

## After Launch

- [ ] Update this checklist with what worked / what didn't
- [ ] Add notes for next time
- [ ] Celebrate small wins
- [ ] Document lessons learned in `memory/YYYY-MM-DD.md`

**Good luck! You've got this.** 🚀
