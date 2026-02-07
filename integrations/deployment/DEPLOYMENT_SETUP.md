# Deployment Automation Setup

Complete setup in **5 minutes**. Ship fixes automatically, day or night.

---

## Step 1: Connect Railway (2 minutes)

1. **Sign up for Railway:** https://railway.app
2. **Connect GitHub repository:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your FitTrack repository
3. **Note your Railway token:**
   - Click your profile → Account Settings → Tokens
   - Generate new token
   - Copy it - you'll need it next

---

## Step 2: Configure GitHub Secrets (2 minutes)

1. **Go to your GitHub repository**
2. **Settings → Secrets and variables → Actions**
3. **Add these secrets:**

```
RAILWAY_TOKEN=your_railway_token_here
PRODUCTION_URL=https://your-production-url.railway.app
STAGING_URL=https://your-staging-url.railway.app
TELEGRAM_BOT_TOKEN=your_bot_token (optional)
TELEGRAM_CHAT_ID=your_chat_id (optional)
```

---

## Step 3: Enable GitHub Actions (30 seconds)

1. **Go to your repository → Actions tab**
2. **Enable workflows if prompted**
3. **Verify workflows appear:**
   - Deploy to Production
   - Deploy to Staging

Done! GitHub Actions is now monitoring your repository.

---

## Step 4: Test Deployment (1 minute)

Make a test commit to `main` branch:

```bash
echo "# Test deployment" >> README.md
git add README.md
git commit -m "Test: Deploy automation"
git push origin main
```

**Watch it happen:**
1. Go to GitHub → Actions tab
2. See workflow running
3. Get Telegram notification when done (if configured)

---

## How It Works

### Automatic Deployments

**Production (main branch):**
- Every push to `main` triggers production deploy
- Runs tests first
- Deploys to Railway
- Health check
- Telegram notification

**Staging (develop/staging branches):**
- Every push to `develop` or `staging` triggers staging deploy
- Also runs on pull requests to `main`
- Same process as production, but separate environment

### Manual Deployments

Use the manual scripts when:
- GitHub Actions is down
- You want more control
- Testing locally before push

**Deploy script:**
```bash
bash scripts/deploy.sh main production
```

**Rollback script (emergency):**
```bash
bash scripts/rollback.sh production
```

---

## Railway Configuration

### Create Staging Environment

1. **In Railway dashboard:**
   - Click "New Service"
   - Select same repository
   - Name it "FitTrack Staging"

2. **Set environment variables:**
   - `ENVIRONMENT=staging`
   - Copy all other variables from production
   - Use test API keys where possible

### Environment Variables

**Required in Railway:**
```
# App config
FLASK_ENV=production
SECRET_KEY=your_secret_key

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Database
DATABASE_URL=postgresql://...

# Optional integrations
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
GMAIL_CREDENTIALS=...
```

---

## Workflow Triggers

### Production Deploy (deploy-production.yml)

**Triggers:**
- Push to `main` branch
- Manual trigger from Actions tab

**Steps:**
1. Checkout code
2. Set up Python
3. Install dependencies
4. Run tests
5. Deploy to Railway
6. Health check
7. Notify success/failure

### Staging Deploy (deploy-staging.yml)

**Triggers:**
- Push to `develop` or `staging` branches
- Pull requests to `main`
- Manual trigger

**Steps:**
Same as production, but deploys to staging environment

---

## Testing Before Production

### Recommended Flow

1. **Develop on feature branch:**
   ```bash
   git checkout -b feature/new-thing
   # Make changes
   git commit -m "Add new feature"
   git push origin feature/new-thing
   ```

2. **Create pull request to main:**
   - Triggers staging deployment
   - Test on staging URL
   - Review changes

3. **Merge to main:**
   - Auto-deploys to production
   - Get notified when live

### Skip Tests (Emergency)

If you need to deploy immediately without tests:

Edit `.github/workflows/deploy-production.yml`:
```yaml
# Comment out test step
# - name: Run tests
#   run: |
#     python tests/test_suite.py
```

Better: Use manual deploy script:
```bash
bash scripts/deploy.sh main production
# Answer 'y' when prompted, even if tests fail
```

---

## Rollback Procedure

### Automatic Rollback

If health check fails, deployment stops. Railway keeps previous version running.

### Manual Rollback

**Option 1: Use rollback script (recommended)**
```bash
bash scripts/rollback.sh production
```

This will:
1. Revert to previous commit
2. Deploy old version
3. Health check
4. Send alerts

**Option 2: Railway dashboard**
1. Go to Railway project
2. Click "Deployments"
3. Find previous successful deploy
4. Click "Redeploy"

**Option 3: Git revert**
```bash
git revert HEAD
git push origin main
# Triggers new deployment with reverted changes
```

---

## Monitoring Deployments

### View Logs

**GitHub Actions:**
- Repository → Actions tab
- Click on workflow run
- View logs for each step

**Railway:**
- Project → Deployments
- Click deployment
- View build logs and runtime logs

**Local logs:**
```bash
cat deployments/deploy.log      # Manual deployments
cat deployments/rollback.log    # Rollbacks
```

### Health Checks

Add health endpoint to your Flask app:

```python
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": os.getenv('GIT_SHA', 'unknown')
    })
```

Workflow automatically checks this endpoint after deploy.

---

## Telegram Notifications

### Setup

1. Create bot with @BotFather
2. Get bot token
3. Get your chat ID from @userinfobot
4. Add to GitHub secrets

### Notification Types

**Successful deploy:**
```
🚀 Production Deploy Successful

✅ Commit: abc1234
👤 By: yourusername
🌐 Live now!
```

**Failed deploy:**
```
🚨 Production Deploy FAILED

❌ Commit: abc1234
👤 By: yourusername

⚠️ Check logs immediately!
```

**Manual deploy:**
```
🚀 Manual Deploy Complete

🌐 Environment: production
📝 Commit: abc1234
✅ Status: 200

🎉 Live now!
```

**Rollback:**
```
🔄 ROLLBACK EXECUTED

🌐 Environment: production
⏪ Reverted to: def5678
✅ Status: 200

⚠️ Investigate the issue!
```

---

## Advanced Configuration

### Deploy on Schedule

Add to workflow:
```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily
```

### Deploy Specific Services

If you have multiple Railway services:
```bash
railway up --service api
railway up --service worker
railway up --service frontend
```

### Custom Health Checks

Add more checks to workflow:
```yaml
- name: Health check
  run: |
    # Check database
    curl -f $HEALTH_URL/db-check
    
    # Check Stripe integration
    curl -f $HEALTH_URL/stripe-check
    
    # Check critical endpoints
    curl -f $HEALTH_URL/api/revenue/mrr
```

---

## Troubleshooting

### "Railway token invalid"
- Regenerate token in Railway dashboard
- Update GitHub secret
- Re-run workflow

### "Tests failed" but code is fine
- Check test environment
- Make sure test database is configured
- Review test logs in Actions tab

### "Health check failed" but app is up
- Verify health endpoint exists
- Check if URL is correct in secrets
- Increase wait time before health check

### Deployment stuck
- Check Railway status page
- View Railway logs for errors
- Try manual deployment

---

## Security Best Practices

🔒 **Never commit secrets**
```bash
echo ".env" >> .gitignore
echo "token.pickle" >> .gitignore
echo "credentials.json" >> .gitignore
```

🔒 **Use different secrets for staging**
- Test Stripe keys in staging
- Separate databases
- Limited API keys

🔒 **Rotate secrets regularly**
- Change Railway token monthly
- Rotate API keys quarterly
- Update webhooks after rotation

🔒 **Limit deploy permissions**
- Only maintainers can push to `main`
- Require PR reviews
- Enable branch protection

---

## Next Steps

✅ **Done!** Deployment automation is live.

**What you can do now:**
1. Push to `main` → Auto-deploys to production
2. Create PR → Auto-deploys to staging
3. Merge PR → Auto-deploys to production
4. Run `scripts/deploy.sh` → Manual deploy
5. Run `scripts/rollback.sh` → Emergency rollback

**Ship at 2 AM without waking up** ✅  
**Automatic testing before deploy** ✅  
**One-click rollback** ✅  
**Instant notifications** ✅  

**Time to activation:** 5 minutes ⚡  
**Deployments per week:** Unlimited 🚀  
**Time saved:** Every deployment is automated 💪
