# Product Landing Page Template - Quick Start

Modern, conversion-focused landing page template. **Works for any product.** Customize and launch in 45 minutes.

## 🚀 Quick Start (10 minutes to live page)

### 1. Copy Files to Your Project
```bash
# Copy all files to your web directory
cp index.html /your-project/
cp style.css /your-project/
cp variables.css /your-project/
cp script.js /your-project/
```

### 2. Customize Content (30 minutes)
Open `index.html` and replace placeholder text:

**Priority edits (must do):**
- [ ] Page title (line 6)
- [ ] Brand name in nav (line 19)
- [ ] Hero headline (line 31)
- [ ] Hero subtitle (line 34)
- [ ] Product screenshot/demo (line 47 - replace placeholder)
- [ ] Problem/Solution sections (lines 58-116)
- [ ] Features (lines 125-176)
- [ ] Pricing (lines 232-292)

**Optional edits:**
- [ ] Testimonials (add real customer quotes)
- [ ] Stats (replace with your actual numbers)
- [ ] FAQ (customize to your product)
- [ ] Footer links

### 3. Customize Design (5 minutes)
Open `variables.css` and change:

```css
/* Brand Colors */
--color-primary: #5469d4;  /* Your brand color */
```

**Or use a preset theme:**
Uncomment one of the theme presets at the bottom of `variables.css`:
- Blue (default) - Professional, trustworthy
- Green - Natural, growth, finance
- Purple - Creative, modern
- Orange - Energy, excitement
- Red - Bold, urgent
- Teal - Tech, innovation

### 4. Connect Backend (10 minutes)
The signup form sends to `/api/signup`. Create this endpoint:

```python
# Flask example
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    
    # Save email to database
    # Send welcome email
    
    return jsonify({'success': True}), 200
```

### 5. Deploy
```bash
# Static site - just upload files
# Or use with any web framework (Flask, Express, etc.)
```

**Done!** You have a landing page.

---

## 📋 Detailed Customization

### Changing Colors

**Quick method:** Use theme presets in `variables.css`

**Custom method:** Edit these variables:
```css
:root {
    --color-primary: #YOUR_COLOR;       /* Main brand color */
    --color-primary-dark: #DARKER_SHADE; /* For hover states */
    --color-primary-light: #LIGHTER_SHADE; /* For backgrounds */
}
```

**Tool:** Use https://colorhunt.co to find color schemes

### Changing Fonts

Add Google Fonts:
```html
<!-- In <head> of index.html -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

Update variable:
```css
:root {
    --font-sans: 'Inter', sans-serif;
}
```

### Adding Images

**Hero/product screenshots:**
```html
<!-- Replace placeholder div with: -->
<img src="/images/product-screenshot.png" alt="Product Demo">
```

**Optimize images:**
- Hero: 1200x675px (16:9)
- Features: 400x400px (square)
- Testimonial avatars: 100x100px (circular)
- Format: WebP (smaller files) or PNG

**Lazy loading:**
```html
<img class="lazy" data-src="/images/large-image.jpg" alt="Description">
```

### Customizing Sections

**To remove a section:**
Delete the entire `<section>` block from HTML

**To reorder sections:**
Cut and paste entire `<section>` blocks

**To add a new section:**
Copy an existing section and modify

### Responsive Design

The template is mobile-responsive by default. Test on:
- Desktop (1920px+)
- Laptop (1440px)
- Tablet (768px)
- Mobile (375px)

**Breakpoints:**
- < 1024px: 2-column layouts become 1-column
- < 768px: All grids become single column
- < 480px: Mobile menu (TODO: implement hamburger)

---

## 🎨 Design Tips

### Hero Section
- **Headline:** 6-10 words max. Promise a specific outcome.
- **Subtitle:** Expand on headline. Answer "What is this?"
- **CTA:** Action verb + benefit ("Start Free Trial", not just "Sign Up")
- **Visual:** Show the product, not abstract concepts

### Problem/Solution
- **Problem:** Make it painful. They should nod along.
- **Solution:** Show the transformation, not features
- **Be specific:** "Save 10 hours/week" beats "Save time"

### Features
- **3-6 features max:** Focus on what matters most
- **Benefits > Features:** "Track progress effortlessly" > "Built-in analytics"
- **Icons:** Use emojis (easy) or icon library like Heroicons

### Social Proof
- **Real testimonials:** Screenshot customer emails/tweets
- **Specifics:** "Saved $10K" beats "Saved money"
- **Photos:** Real people, not stock photos
- **Stats:** Update with real numbers (even if small)

### Pricing
- **3 tiers max:** Free, Pro, Enterprise
- **Highlight one:** Make Pro tier stand out (most profitable)
- **Annual discount:** Show monthly price, offer annual savings
- **Remove friction:** "No credit card" on free trial

### FAQ
- **Address objections:** Security, privacy, cancellation, refunds
- **Be honest:** Build trust, not hype
- **6-8 questions:** Cover the most common concerns

### Call-to-Action
- **Clear:** One primary CTA (don't give too many options)
- **Repeated:** Hero, pricing, final CTA section
- **Action-oriented:** "Start building" > "Learn more"
- **Low-risk:** "Free trial", "No credit card"

---

## 📊 Analytics Integration

### Google Analytics (GA4)
```html
<!-- Add before </head> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Plausible Analytics (Privacy-friendly)
```html
<script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>
```

### Facebook Pixel
```html
<script>
  !function(f,b,e,v,n,t,s){/* FB pixel code */}
  fbq('init', 'YOUR_PIXEL_ID');
  fbq('track', 'PageView');
</script>
```

**Events automatically tracked:**
- ✓ Page views
- ✓ CTA clicks (location + button text)
- ✓ Scroll depth (25%, 50%, 75%, 100%)
- ✓ Time on page (30s, 1m, 2m, 5m)
- ✓ Exit intent
- ✓ Plan selection
- ✓ Signup attempts

---

## 🔌 Backend Integration

### Email Capture Endpoint

**Flask:**
```python
from flask import request, jsonify

@app.route('/api/signup', methods=['POST'])
def signup():
    email = request.json.get('email')
    
    # Validate email
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return jsonify({'error': 'Invalid email'}), 400
    
    # Save to database
    db.execute("INSERT INTO signups (email, created_at) VALUES (?, ?)", 
               email, datetime.now())
    
    # Send welcome email (integrate with email-automation package!)
    send_welcome_email(email)
    
    return jsonify({'success': True}), 200
```

**Express (Node.js):**
```javascript
app.post('/api/signup', async (req, res) => {
    const { email } = req.body;
    
    // Validate email
    if (!email || !email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
        return res.status(400).json({ error: 'Invalid email' });
    }
    
    // Save to database
    await db.query('INSERT INTO signups (email) VALUES (?)', [email]);
    
    // Send welcome email
    await sendWelcomeEmail(email);
    
    res.json({ success: true });
});
```

### Event Tracking Endpoint

**Flask:**
```python
@app.route('/api/track', methods=['POST'])
def track_event():
    event = request.json.get('event')
    properties = request.json.get('properties', {})
    
    # Log to database or analytics service
    db.execute("""
        INSERT INTO events (event_name, properties, url, timestamp)
        VALUES (?, ?, ?, ?)
    """, event, json.dumps(properties), request.json.get('url'), datetime.now())
    
    return jsonify({'success': True}), 200
```

---

## ✅ Pre-Launch Checklist

### Content
- [ ] All placeholder text replaced
- [ ] Real testimonials added
- [ ] Actual pricing set
- [ ] FAQ answers customized
- [ ] Product screenshots added
- [ ] Footer links updated

### Technical
- [ ] Email signup endpoint working
- [ ] Analytics tracking installed
- [ ] Mobile responsive (test on phone)
- [ ] Forms working (try submitting)
- [ ] Links working (click everything)
- [ ] Images optimized (< 500KB each)

### SEO
- [ ] Page title set (60 chars max)
- [ ] Meta description set (160 chars max)
- [ ] Open Graph image added (1200x630px)
- [ ] Favicon added
- [ ] Alt text on images

### Legal
- [ ] Privacy policy page
- [ ] Terms of service page
- [ ] Cookie consent (if EU traffic)
- [ ] Refund policy (if paid product)

### Performance
- [ ] Test load speed: https://pagespeed.web.dev
- [ ] Compress images
- [ ] Minify CSS/JS (production)
- [ ] Enable browser caching

---

## 🎯 Conversion Optimization

### A/B Test These Elements
1. **Headline** - Biggest impact on conversions
2. **CTA text** - "Start Free Trial" vs "Get Started" vs "Try It Free"
3. **CTA color** - Test 2-3 contrasting colors
4. **Hero image** - Product demo vs benefit-focused image
5. **Pricing display** - Monthly vs annual first

### Quick Wins
- **Add urgency:** "Join 10,000+ users" (social proof)
- **Remove friction:** "No credit card required"
- **Show value fast:** Lead with benefits, not features
- **Trust signals:** Customer logos, security badges
- **Scarcity:** "Limited spots" (if genuine)

### Tools
- **Hotjar:** See where users click/scroll
- **Google Optimize:** A/B testing (free)
- **Optimizely:** Advanced testing
- **Crazy Egg:** Heatmaps

---

## 🔧 Common Issues

### Signup form not working
- Check `/api/signup` endpoint exists
- Verify email validation regex
- Check browser console for errors
- Test with curl: `curl -X POST http://localhost:3000/api/signup -H "Content-Type: application/json" -d '{"email":"test@example.com"}'`

### Styles not loading
- Check CSS file paths are correct
- Clear browser cache (Cmd+Shift+R)
- Verify `variables.css` loads before `style.css`

### Images not showing
- Check file paths (relative vs absolute)
- Verify images exist in `/images/` folder
- Check image file extensions match HTML

### Layout broken on mobile
- Test in Chrome DevTools mobile view
- Check `viewport` meta tag exists
- Verify responsive CSS isn't overridden

---

## 🚀 Next Steps

1. **Connect to Stripe:** Use the `stripe-integration` package for payments
2. **Set up email automation:** Use the `email-automation` package for follow-ups
3. **Add live chat:** Intercom, Drift, or Crisp
4. **Implement SEO:** Add blog, optimize meta tags
5. **Build integrations:** Zapier, API docs
6. **Scale traffic:** Content marketing, ads, SEO

---

## 📚 Resources

**Design Inspiration:**
- https://land-book.com - Landing page gallery
- https://lapa.ninja - Design examples
- https://saaslandingpage.com - SaaS-specific

**Copywriting:**
- https://copyhackers.com - Landing page copy
- https://swiped.co - Swipe file of great copy

**Icons & Images:**
- https://heroicons.com - Free icon set
- https://unsplash.com - Free stock photos
- https://storyset.com - Free illustrations

**Color Schemes:**
- https://colorhunt.co - Curated palettes
- https://coolors.co - Color generator

---

**Time to ship:** ~45 minutes from here to live landing page 🚀
