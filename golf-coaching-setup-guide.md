# Golf Coaching Landing Page - Setup Guide

## ✅ What's Done

1. **Landing page created:** `golf-coaching-landing.html`
2. **Reddit post drafted:** `golf-coaching-reddit-post.md`
3. **Design:** Mobile-responsive, golf-themed, fast-loading
4. **Form:** Ready for email capture (needs Formspree setup)

---

## 🚀 Quick Launch (5 minutes)

### Step 1: Set Up Form Capture (Formspree - Free)

1. Go to **https://formspree.io/**
2. Sign up (free account)
3. Create a new form
4. Copy your form endpoint (looks like: `https://formspree.io/f/xyzabc123`)
5. Open `golf-coaching-landing.html`
6. Find this line (around line 193):
   ```html
   <form action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
   ```
7. Replace `YOUR_FORM_ID` with your actual form ID
8. **Alternative:** Use Google Forms or Typeform if you prefer

### Step 2: Add Your Contact Info

In the "About & Footer" section (near bottom), replace:
- `ross@yourdomain.com` with your real email
- `Your phone number here` with your real number (or remove if you don't want to share)

### Step 3: Deploy (Choose One)

#### Option A: Netlify (Easiest - Drag & Drop)
1. Go to **https://app.netlify.com/drop**
2. Drag `golf-coaching-landing.html` onto the page
3. Rename it to `index.html` when uploading
4. Get instant URL: `random-name.netlify.app`
5. Optional: Change subdomain in settings

#### Option B: GitHub Pages (Free, Permanent)
```bash
# In your terminal:
cd ~/clawd
mkdir golf-coaching-site
cp golf-coaching-landing.html golf-coaching-site/index.html
cd golf-coaching-site
git init
git add index.html
git commit -m "Initial landing page"

# Create a new GitHub repo called 'golf-coaching'
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/golf-coaching.git
git branch -M main
git push -u origin main

# Enable GitHub Pages:
# Go to repo Settings → Pages → Source: main branch → Save
# Your site will be at: YOUR_USERNAME.github.io/golf-coaching
```

#### Option C: Vercel (Also Easy)
1. Go to **https://vercel.com**
2. Sign up/login
3. Import project or drag file
4. Deploy instantly

---

## 📱 Test Before Posting

1. **Desktop test:** Open the page, fill out form, submit
2. **Mobile test:** Open on phone, check all sections load properly
3. **Form test:** Submit a test entry, verify you receive it
4. **Speed test:** Page should load instantly (it's lightweight)
5. **Links test:** Click CTA buttons, make sure they scroll correctly

---

## 📝 Post to r/golf

1. **Read the draft:** `golf-coaching-reddit-post.md`
2. **Choose title:** I recommend Title Option 2 (less salesy, asks for feedback)
3. **Best time:** Evening (6-9pm ET when r/golf is active)
4. **Engage fast:** Respond to every comment in first hour
5. **Be authentic:** You're testing an idea, asking for feedback

---

## 🎯 After First Sign-Up

When someone fills the form:
1. **Email them within 1 hour** (fast response builds trust)
2. **Ask for swing video** via email or text
3. **Deliver analysis within 24 hours** (or faster for first few)
4. **Over-deliver** on first 5 customers to get testimonials

---

## 🔧 Quick Edits You Might Want

### Change Pricing
Search for `$14.50` and `$29` in the HTML to update pricing

### Change "First 10" to Different Number
Search for `10` and `first 10` to update limits

### Add Your Photo
Add this in the "About" section:
```html
<img src="your-photo-url.jpg" alt="Ross" class="w-32 h-32 rounded-full mx-auto mb-4">
```

### Change Colors
The golf-green color is defined at the top. Change these values:
```javascript
'golf-green': '#1a4d2e',    // Dark green
'golf-light': '#4f772d',    // Medium green  
'golf-accent': '#90cc92',   // Light green accent
```

---

## 💡 Next Steps After Launch

1. **Collect testimonials** from first customers
2. **Update social proof section** with real numbers
3. **Add before/after** swing comparison examples
4. **Create FAQ section** based on common questions
5. **A/B test** different headlines/pricing

---

## 🆘 Troubleshooting

**Form not working?**
- Check Formspree setup
- Make sure you replaced YOUR_FORM_ID
- Test in incognito mode

**Page looks weird on mobile?**
- Clear cache and reload
- Tailwind CDN might be slow - wait a few seconds

**Not getting signups?**
- Price too high? Test $19/month
- Not enough trust signals? Add your photo
- CTA unclear? Make buttons more prominent

---

## 📊 Track Your Results

Create a simple spreadsheet:
- Date posted to Reddit
- Upvotes / comments
- Landing page visits (use Google Analytics or Simple Analytics)
- Form submissions
- Conversion rate
- Paying customers

This helps you iterate and improve.

---

**You're ready to launch! 🚀**

Questions? Issues? Let me know and I'll help you fix them in real-time.