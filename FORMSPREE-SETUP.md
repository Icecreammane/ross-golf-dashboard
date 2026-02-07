# 📧 Formspree Setup Guide (5 Minutes)

Formspree is the easiest way to handle form submissions without backend code. Here's exactly how to set it up.

---

## Step 1: Create Formspree Account

1. Go to: **https://formspree.io/**
2. Click "Get Started" or "Sign Up"
3. Sign up with your email (the one where you want to receive submissions)
4. Verify your email

**Free tier includes:**
- ✅ 50 submissions/month (plenty to start)
- ✅ Email notifications
- ✅ Spam filtering
- ✅ File uploads

---

## Step 2: Create New Form

1. After logging in, click **"+ New Form"**
2. **Form name:** `Golf Coaching Signups`
3. **Notification email:** Your email (where signups will be sent)
4. Click **"Create Form"**

---

## Step 3: Get Your Form Endpoint

After creating the form, you'll see a screen with your form endpoint.

**It looks like:**
```
https://formspree.io/f/YOUR_FORM_ID
```

**Copy this entire URL!** You'll need it in the next step.

Example: `https://formspree.io/f/xvoepzka`

---

## Step 4: Update Your Landing Page

1. Open `golf-coaching-landing.html` in a text editor
2. Find line 193 (or search for `YOUR_FORM_ID`)
3. Replace the placeholder with your actual endpoint

**Before:**
```html
<form action="https://formspree.io/f/YOUR_FORM_ID" method="POST" class="space-y-4">
```

**After:**
```html
<form action="https://formspree.io/f/xvoepzka" method="POST" class="space-y-4">
```
(Use YOUR actual form ID, not `xvoepzka`)

4. Save the file

---

## Step 5: Test the Form

**Before deploying to production, test locally:**

1. Open `golf-coaching-landing.html` in your browser
2. Scroll to the signup form
3. Fill it out with YOUR email
4. Click "Reserve Your Spot"
5. You should be redirected to Formspree's thank-you page
6. Check your email – you should receive a notification

**If test works:** You're good to go! 🎉

**If test fails:**
- Check that form endpoint URL is exactly correct
- Make sure you verified your email with Formspree
- Check spam folder for notification email

---

## Step 6: Customize Formspree Settings (Optional)

Go to your form dashboard: https://formspree.io/forms

**Settings to configure:**

### 6.1 Custom Thank You Page
- Instead of Formspree's page, redirect to your own
- **Redirect URL:** `https://your-site.com/thank-you.html`
- Or leave default (works fine!)

### 6.2 Email Subject
- Change notification subject
- Example: `🏌️ New Golf Coaching Signup!`

### 6.3 Auto-Reply (Recommended!)
- Send instant confirmation to users
- **Enable:** Auto-reply
- **Subject:** `Thanks for signing up! Let's get started 🏌️`
- **Message:**
```
Hi {{name}}!

Thanks for signing up for golf swing coaching! You're one of the first 10 members, which means you've locked in lifetime 50% off.

I'll send you a welcome email within the next few hours with instructions on how to send your first swing video.

Looking forward to helping you improve!

– Ross
```

### 6.4 Spam Filtering
- Already enabled by default
- Uses Google reCAPTCHA invisibly
- No action needed!

---

## Step 7: Deploy and Monitor

Once your landing page is live:

1. **Monitor submissions:**
   - Go to: https://formspree.io/forms
   - Click on your form
   - See all submissions in real-time

2. **Email notifications:**
   - You'll get an email every time someone submits
   - Check spam folder if not receiving

3. **Export data:**
   - Click "Export" to download CSV of all submissions
   - Good for tracking in spreadsheet

---

## Common Issues & Fixes

### Issue: Not receiving email notifications

**Fix:**
1. Check spam folder
2. Go to Formspree dashboard > Settings
3. Verify notification email is correct
4. Add formspree.io to email whitelist

### Issue: Form submission fails

**Fix:**
1. Check form endpoint URL is correct
2. Make sure `method="POST"` is in form tag
3. Check field names match (email, name, handicap)
4. Test in different browser

### Issue: Hit 50 submission limit

**Fix (Good problem!):**
1. Upgrade to paid plan ($10/mo for 1000 submissions)
2. Or switch to Google Forms temporarily

### Issue: Getting spam submissions

**Fix:**
1. Enable reCAPTCHA in settings (should be on by default)
2. Use Formspree's spam filtering
3. Add honeypot field (advanced)

---

## Alternative: Google Forms (If Formspree Doesn't Work)

If Formspree is down or you prefer Google:

1. Go to: https://forms.google.com
2. Create new form with fields:
   - Email (required)
   - First Name (required)
   - Current Handicap (optional)
3. Click "Send" and copy link
4. Replace entire form section in landing page with iframe:

```html
<iframe src="YOUR_GOOGLE_FORM_LINK" width="100%" height="800" frameborder="0">
</iframe>
```

**Pros:** Unlimited submissions, integrates with Google Sheets
**Cons:** Less customizable, looks less professional

---

## Testing Checklist

Before launching, test:

- [ ] Form submits successfully
- [ ] You receive email notification
- [ ] Email goes to correct address
- [ ] Form works on mobile (phone screen)
- [ ] Success message displays after submit
- [ ] Test with multiple browsers (Chrome, Safari, Firefox)
- [ ] Auto-reply email works (if enabled)

---

## After First Real Submission

When you get your first real signup:

1. **Respond fast** (within 1-2 hours if possible)
2. **Copy submission data** to a spreadsheet for tracking
3. **Send welcome email** (see EMAIL-TEMPLATES.md)
4. **Ask how they heard about you** (Reddit, friend, etc.)

---

## Formspree Dashboard Overview

**Forms Tab:**
- See all your forms
- Click into specific form for submissions

**Submissions Tab:**
- All form fills
- Filter by date
- Export to CSV

**Settings:**
- Notification email
- Auto-reply
- Redirect URL
- Spam filtering

**Billing:**
- Current plan (Free: 50/mo)
- Upgrade options

---

## Pro Tips

1. **Set up auto-reply** – Makes you look professional and responsive
2. **Check submissions daily** – Don't miss signups!
3. **Export to spreadsheet weekly** – Track conversion metrics
4. **Upgrade when you hit 40 submissions** – Don't wait until you hit the limit
5. **Add UTM parameters** – Track where signups come from (Reddit, Twitter, etc.)

---

## You're Ready!

Form setup is done. Now just:
1. ✅ Test with your email
2. ✅ Deploy landing page
3. ✅ Post to Reddit

Questions? Check Formspree docs: https://help.formspree.io/

🏌️ Let's get some signups!
