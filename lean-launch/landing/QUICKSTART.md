# 🚀 5-Minute Quick Start

## Deploy to Vercel (Fastest)

```bash
# 1. Login
vercel login

# 2. Navigate to directory
cd ~/clawd/lean-launch/landing

# 3. Deploy
vercel --prod

# Done! You'll get a live URL
```

## Deploy to Netlify

```bash
# 1. Login
netlify login

# 2. Deploy
cd ~/clawd/lean-launch/landing
netlify deploy --prod --dir=.

# Done!
```

## Deploy to GitHub Pages (Free)

```bash
# 1. Create repo at https://github.com/new (name it "lean-landing")

# 2. Push code
cd ~/clawd/lean-launch/landing
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/lean-landing.git
git push -u origin main

# 3. Enable Pages
# Go to: Settings → Pages → Source: "main" branch
# Your site: https://YOUR-USERNAME.github.io/lean-landing/
```

## Preview Locally

```bash
cd ~/clawd/lean-launch/landing
python3 -m http.server 8080
# Visit: http://localhost:8080
```

## Customize

**Email address**: Edit `index.html`, search for `mailto:bigmeatyclawd@gmail.com`

**Add demo video**: Replace `.demo-placeholder` div with:
```html
<video autoplay loop muted playsinline style="width: 100%; max-width: 800px; border-radius: 20px;">
    <source src="demo.mp4" type="video/mp4">
</video>
```

**Change pricing**: Edit `.pricing-card` sections in `index.html`

**Use Tally form**: Uncomment Tally iframe in `index.html`, add your form ID

**Add analytics**: Paste Google Analytics or Plausible code before `</head>`

## Need Help?

- Full docs: `DEPLOYMENT_GUIDE.md`
- Customization: `README.md`
- Build details: `BUILD_COMPLETE.md`

That's it! 🎉
