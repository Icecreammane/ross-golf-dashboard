# 🔐 1Password Migration Guide

**Purpose:** Move all API keys and secrets from `.env` files to 1Password for enhanced security.

**Status:** Ready to execute  
**Estimated Time:** 15-20 minutes

---

## Overview

Currently, API keys are stored in `.env` files with secure permissions (600). This migration will:
1. Store master copies in 1Password vault
2. Keep `.env` files as local cache (regenerated from 1Password)
3. Enable easy credential rotation
4. Provide secure sharing if needed

---

## Prerequisites

- [ ] 1Password account active
- [ ] 1Password CLI installed (optional but recommended)
- [ ] Access to all current `.env` files

---

## Step 1: Create 1Password Vault

### In 1Password App:
1. Open 1Password
2. Create new vault: **"Jarvis Infrastructure"**
3. Set vault icon: 🤖 or 🔧
4. Make vault "Private" (only you have access)

---

## Step 2: Add Credentials to 1Password

### For Each Credential:

#### A. Google Gemini API
1. Click "+" → New Item → "API Credential"
2. **Title:** "Jarvis - Google Gemini API"
3. **Fields:**
   - **API Key:** `AIzaSyD-z8D8Utcuccc0Rig_4w5f_tqumNu_wEM` (from `.env`)
   - **Type:** "API Key"
   - **Endpoint:** `https://generativelanguage.googleapis.com/`
4. **Tags:** `jarvis`, `ai`, `gemini`
5. **Notes:** "Used for Jarvis AI operations, content generation"
6. **Created:** February 8, 2026
7. Click "Save"

#### B. Grok API (xAI)
1. New Item → "API Credential"
2. **Title:** "Jarvis - Grok API (xAI)"
3. **Fields:**
   - **API Key:** `xai-UVWupUxiVqLmjfiV3PUibUTyZV5JyyZh3A2XQZ6krFa1GRYBrZN6bwSQHnnoQVZeiuzKnWxCKtxSbX4M`
   - **Type:** "API Key"
   - **Endpoint:** `https://api.x.ai/`
4. **Tags:** `jarvis`, `ai`, `grok`
5. **Notes:** "Grok API for AI operations"
6. Click "Save"

#### C. Gmail (Jarvis Account)
1. New Item → "Login"
2. **Title:** "Jarvis Gmail Account"
3. **Fields:**
   - **Email:** `bigmeatyclawd@gmail.com`
   - **Password:** `JarvisAssistant3080!`
   - **App Password (SMTP):** `blqs rljt paym kzzp`
4. **Tags:** `jarvis`, `email`, `gmail`
5. **Notes:** "Jarvis operational email. App password for SMTP/IMAP access."
6. **Created:** February 2, 2026
7. Click "Save"

#### D. Telegram Bot
1. New Item → "API Credential"
2. **Title:** "Jarvis Telegram Bot"
3. **Fields:**
   - **Bot Token:** `7869330755:AAEj9m1oMCLcXzHy09TlqxlCZ3E6zlZXaM4`
   - **Bot Username:** `@RossJarvisBot`
   - **Ross Chat ID:** `8412148376`
4. **Tags:** `jarvis`, `telegram`, `bot`
5. **Notes:** "Jarvis Telegram bot for monitoring and commands"
6. **Created:** February 7, 2026
7. Click "Save"

#### E. Stripe (Fitness Tracker)
1. New Item → "API Credential"
2. **Title:** "Jarvis - Stripe Test Keys (Fitness Tracker)"
3. **Fields:**
   - **Secret Key:** `sk_test_...` (from `fitness-tracker/.env`)
   - **Publishable Key:** `pk_test_...`
   - **Webhook Secret:** `whsec_...`
   - **Environment:** "Test"
4. **Tags:** `jarvis`, `stripe`, `fitness-tracker`, `test`
5. **Notes:** "Test keys for Fitness Tracker development. DO NOT use in production."
6. Click "Save"

#### F. Flask Secret Keys
1. New Item → "Secure Note"
2. **Title:** "Jarvis - Flask Secret Keys"
3. **Content:**
   ```
   Fitness Tracker:
   SECRET_KEY=6ea51e0773912047a9b36408bd7cdbdc6cd0980f1127f84b5109f72ae608214e
   
   Revenue Dashboard:
   FLASK_SECRET_KEY=<value from revenue_dashboard/.env>
   
   Generated: python -c "import secrets; print(secrets.token_hex(32))"
   Rotate: Every 90 days
   ```
4. **Tags:** `jarvis`, `flask`, `secrets`
5. Click "Save"

#### G. Google Calendar OAuth
1. New Item → "API Credential"
2. **Title:** "Jarvis - Google Calendar OAuth"
3. **Fields:**
   - **Client ID:** `722126192387-f4strl6hqfp65ge9ot7efta0r73f1k70.apps.googleusercontent.com`
   - **Client Secret:** `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`
   - **Project ID:** `psyched-canto-486116-d7`
4. **Tags:** `jarvis`, `google`, `oauth`, `calendar`
5. **Notes:** "OAuth credentials for Google Calendar integration"
6. Click "Save"

#### H. Twitter API (Placeholder)
1. New Item → "API Credential"
2. **Title:** "Jarvis - Twitter API (X)"
3. **Fields:**
   - **API Key:** `<not configured yet>`
   - **API Secret:** `<not configured yet>`
   - **Access Token:** `<not configured yet>`
   - **Access Secret:** `<not configured yet>`
   - **Bearer Token:** `<not configured yet>`
4. **Tags:** `jarvis`, `twitter`, `social`
5. **Notes:** "Configure when Twitter integration is set up. Get from: https://developer.twitter.com/en/portal/dashboard"
6. Click "Save"

---

## Step 3: Verify 1Password Storage

### Checklist:
- [ ] 8 items created in "Jarvis Infrastructure" vault
- [ ] All items properly tagged
- [ ] All sensitive fields marked as "concealed"
- [ ] Creation dates documented
- [ ] Notes added for context

---

## Step 4: Update Local .env Files (Optional)

You can **either**:

### Option A: Keep current .env files as-is
- Already secured with 600 permissions
- 1Password is backup/reference
- Simple, no code changes needed

### Option B: Reference 1Password in code
- Install 1Password CLI: `brew install --cask 1password-cli`
- Replace hardcoded values with 1Password references
- More secure, but requires op CLI setup

**Recommendation:** Start with Option A (current approach is secure enough)

---

## Step 5: Set Credential Rotation Schedule

### Add to Calendar:
1. **Quarterly Rotation (every 90 days):**
   - Gemini API key
   - Grok API key
   - Flask secret keys
   - Stripe test keys (or move to production)

2. **Annual Rotation (yearly):**
   - Gmail app password
   - Google OAuth credentials
   - Telegram bot token (if needed)

3. **On Breach (immediate):**
   - Any compromised credential
   - Follow incident response in `SECURITY_HARDENING.md`

---

## Step 6: Test Access

After migration:

```bash
# Verify you can still access credentials from .env
cat ~/clawd/.env  # Should still work

# Test daemons still function
python3 ~/clawd/scripts/email_daemon.py --test

# Verify 1Password access
open "onepassword://vault/Jarvis Infrastructure"
```

---

## Step 7: Document & Cleanup

### Update Documentation:
- [x] `SECURITY_HARDENING.md` - Reference 1Password
- [x] `TOOLS.md` - Add 1Password section
- [x] `SECURITY_QUICK_REFERENCE.md` - 1Password commands

### Secure Backup:
- [ ] Export 1Password emergency kit (paper backup)
- [ ] Store in physical safe location
- [ ] Test 1Password recovery process

---

## Emergency Recovery

### If 1Password is Unavailable:

1. **Credentials still in local `.env` files:**
   ```bash
   cat ~/clawd/.env
   cat ~/clawd/fitness-tracker/.env
   cat ~/clawd/.credentials/*.json
   ```

2. **Encrypted backups contain copies:**
   ```bash
   hdiutil attach ~/clawd/backups/encrypted-data-backups/data-backup-latest.dmg
   # Password: JarvisBackup2026!
   ```

3. **Regenerate from providers:**
   - Gemini: https://aistudio.google.com/apikey
   - Grok: https://console.x.ai/
   - Stripe: https://dashboard.stripe.com/test/apikeys
   - Gmail: https://myaccount.google.com/apppasswords

---

## 1Password CLI (Advanced)

### Installation:
```bash
brew install --cask 1password-cli
op signin
```

### Retrieve Credentials:
```bash
# Get Gemini API key
op read "op://Jarvis Infrastructure/Jarvis - Google Gemini API/api key"

# Get all credentials for a project
op item get "Jarvis - Stripe Test Keys" --vault "Jarvis Infrastructure"
```

### Auto-populate .env from 1Password:
```bash
# Create script to sync from 1Password to .env
# (Advanced - implement if needed later)
```

---

## Benefits of 1Password

1. ✅ **Centralized Storage:** All credentials in one secure vault
2. ✅ **Easy Rotation:** Update in one place, reference everywhere
3. ✅ **Audit Trail:** 1Password logs all access
4. ✅ **Secure Sharing:** Share specific credentials if needed
5. ✅ **Cross-Device:** Access from phone, laptop, desktop
6. ✅ **Emergency Access:** Emergency kit for recovery
7. ✅ **Version History:** Rollback to previous credentials
8. ✅ **Breach Detection:** 1Password Watchtower alerts

---

## Completion Checklist

- [ ] 1Password vault created
- [ ] All 8 credentials migrated
- [ ] Credentials verified accessible
- [ ] Rotation schedule set
- [ ] Emergency kit exported
- [ ] Documentation updated
- [ ] Team (Ross) has access to vault
- [ ] Test credential retrieval

---

## Next Steps

After 1Password migration:

1. **Enable Watchtower** in 1Password (monitors for breaches)
2. **Set up Emergency Kit** (paper backup in safe)
3. **Review quarterly** rotation calendar
4. **Consider 1Password CLI** for automation (optional)

---

**Migration Status:** Ready to execute  
**Owner:** Ross  
**Support:** Jarvis can guide through process  
**Est. Completion:** 15-20 minutes
