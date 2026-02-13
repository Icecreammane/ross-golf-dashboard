# Lean Landing Page

Conversion-focused single-page marketing site for Lean meal logging app.

## Features

✅ Hero section with CTA and demo placeholder  
✅ 4-feature showcase (voice, photo, AI calculator, progress)  
✅ 3-tier pricing (Free, Pro, Lifetime)  
✅ Email capture form  
✅ Cyan-green gradient brand theme  
✅ Mobile-responsive  
✅ Fast & lightweight (single HTML file, no dependencies)  

## Quick Start

### Option 1: Vercel (Recommended)

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Deploy**:
   ```bash
   cd ~/clawd/lean-launch/landing
   vercel
   ```

3. **Follow prompts**:
   - Set up and deploy: `Y`
   - Scope: (select your account)
   - Link to existing project: `N`
   - Project name: `lean-landing`
   - Directory: `./`
   - Override settings: `N`

4. **Get your URL**: Vercel will provide a live URL (e.g., `lean-landing-xyz.vercel.app`)

5. **Set custom domain** (optional):
   ```bash
   vercel domains add yourdomain.com
   ```

### Option 2: Netlify

1. **Install Netlify CLI**:
   ```bash
   npm install -g netlify-cli
   ```

2. **Deploy**:
   ```bash
   cd ~/clawd/lean-launch/landing
   netlify deploy
   ```

3. **For production**:
   ```bash
   netlify deploy --prod
   ```

### Option 3: GitHub Pages (Free)

1. **Create a new GitHub repo** named `lean-landing`

2. **Push to GitHub**:
   ```bash
   cd ~/clawd/lean-launch/landing
   git init
   git add .
   git commit -m "Initial landing page"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/lean-landing.git
   git push -u origin main
   ```

3. **Enable GitHub Pages**:
   - Go to repo Settings → Pages
   - Source: Deploy from branch `main`
   - Folder: `/ (root)`
   - Save

4. **Your site will be live at**: `https://YOUR-USERNAME.github.io/lean-landing/`

## Customization

### Update Email Form

**Option A: Keep mailto (current)**
- Emails open user's mail client
- Simple, no server needed
- Edit the `mailto:` address in `index.html`

**Option B: Switch to Tally**
1. Create form at [tally.so](https://tally.so)
2. Get embed code
3. Replace the form section in `index.html` with the commented Tally iframe
4. Update `YOUR-TALLY-FORM-ID` with your actual form ID

### Add Demo Video/GIF

Replace the `.demo-placeholder` section with:
```html
<video autoplay loop muted playsinline class="demo-video">
    <source src="demo.mp4" type="video/mp4">
</video>
```

Or for GIF:
```html
<img src="demo.gif" alt="Lean Demo" class="demo-gif">
```

### Analytics

Add before `</head>`:

**Google Analytics:**
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

**Plausible (privacy-friendly):**
```html
<script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>
```

## Performance

- **Size**: ~16KB (single HTML file)
- **Load time**: <1s on modern connections
- **Mobile-optimized**: Responsive breakpoints at 768px
- **No external dependencies**: Pure HTML/CSS/JS

## Brand Colors

```css
--cyan: #06b6d4
--green: #10b981
--dark: #0f172a
--gray: #64748b
--light-gray: #f1f5f9
```

## Testing

Open `index.html` in a browser:
```bash
open index.html
```

Or run a local server:
```bash
python3 -m http.server 8000
# Visit: http://localhost:8000
```

## Maintenance

- Update pricing: Edit `.pricing-card` sections
- Change features: Edit `.features-grid` cards
- Modify copy: All text is in semantic HTML
- Adjust colors: Update CSS variables in `:root`

## Support

For issues or questions, contact: bigmeatyclawd@gmail.com

---

Built with ❤️ by Jarvis
