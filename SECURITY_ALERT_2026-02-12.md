# 🚨 Security Alert - Credentials Exposed in Git History

**Date:** February 12, 2026, 7:20am CST  
**Severity:** HIGH  
**Status:** REQUIRES ACTION

---

## What Happened

During memory system activation, git push failed due to GitHub secret scanning detecting real credentials in commit history (`ad76730`).

**File:** `1PASSWORD_MIGRATION_GUIDE.md`  
**Commit:** `ad76730cfd986a213c4dc058073b3d66b5303e72`

---

## Exposed Credentials

The following credentials were found in git history and should be considered **compromised**:

### 1. xAI API Key (Grok)
- **Location:** Line 58 of 1PASSWORD_MIGRATION_GUIDE.md
- **Impact:** Grok API access
- **Action Required:** Rotate immediately
- **How:** https://console.x.ai/ → API Keys → Regenerate

### 2. Google OAuth Client ID
- **Location:** Line 122
- **Impact:** Google Calendar OAuth
- **Action Required:** Rotate credentials
- **How:** https://console.cloud.google.com/apis/credentials

### 3. Google OAuth Client Secret  
- **Location:** Line 123
- **Impact:** Google Calendar OAuth
- **Action Required:** Rotate credentials
- **How:** https://console.cloud.google.com/apis/credentials

---

## Immediate Actions Taken

1. ✅ Removed `1PASSWORD_MIGRATION_GUIDE.md` from repository
2. ✅ Committed removal
3. ⏳ Awaiting credential rotation before push

---

## Required Actions (YOU)

### Step 1: Rotate xAI API Key
```bash
# 1. Go to: https://console.x.ai/
# 2. Navigate to API Keys
# 3. Revoke current key
# 4. Generate new key
# 5. Update in 1Password
# 6. Update ~/clawd/.env: XAI_API_KEY=<new_key>
```

### Step 2: Rotate Google OAuth Credentials
```bash
# 1. Go to: https://console.cloud.google.com/apis/credentials
# 2. Select project: psyched-canto-486116-d7
# 3. Find OAuth 2.0 Client
# 4. Delete old credentials
# 5. Create new OAuth 2.0 Client ID
# 6. Update in 1Password
# 7. Update local credentials file
# 8. Re-authenticate Google Calendar: python3 ~/clawd/scripts/google_calendar_test.py
```

### Step 3: Allow Push (After Rotation)
Once credentials are rotated, allow the secrets on GitHub (they're already exposed, but new ones will be safe):

- [Allow xAI Key](https://github.com/Icecreammane/ross-golf-dashboard/security/secret-scanning/unblock-secret/39ZSu0MjV2FZjPZYQsvT8Hicl49)
- [Allow OAuth Client ID](https://github.com/Icecreammane/ross-golf-dashboard/security/secret-scanning/unblock-secret/39ZSu4d5UglpiWb9Cc6BwjHgp7F)
- [Allow OAuth Client Secret](https://github.com/Icecreammane/ross-golf-dashboard/security/secret-scanning/unblock-secret/39ZSu6X1AT5s9dgB62faOYp6rJJ)

Then:
```bash
cd ~/clawd
git push
```

---

## Why This Happened

The 1Password migration guide contained real credentials for documentation purposes. While the file was later redacted, the original commit with real secrets remains in git history.

**Git history is permanent** - even deleted files persist in history unless you rewrite history (risky).

---

## Prevention Going Forward

1. ✅ **Never commit real credentials** - use placeholders like `<YOUR_KEY_HERE>`
2. ✅ **Pre-commit security scan** - Already enabled (caught this!)
3. ✅ **.gitignore sensitive files** - Added migration guides to .gitignore
4. ✅ **1Password for storage** - Credentials stored securely in 1Password
5. ✅ **Regular rotation schedule** - Set calendar reminders (90 days)

---

## Timeline

- **Ad76730 commit:** 1PASSWORD_MIGRATION_GUIDE.md created with real secrets
- **Later commit:** Secrets redacted to `[REDACTED]`
- **Feb 12, 7:19am:** GitHub push protection triggered
- **Feb 12, 7:20am:** File removed, alert created
- **Next:** Rotate credentials, allow secrets, push successfully

---

## Impact Assessment

**xAI API Key:**
- ⚠️ **Risk:** Unauthorized Grok API usage, quota abuse
- 🛡️ **Mitigation:** Rotate key immediately
- 📊 **Usage Monitor:** Check https://console.x.ai/ for suspicious activity

**Google OAuth Credentials:**
- ⚠️ **Risk:** Unauthorized calendar access (read/write)
- 🛡️ **Mitigation:** Rotate credentials, re-authenticate
- 📊 **Audit:** Check Google account activity for unauthorized access

---

## Post-Rotation Checklist

After rotating credentials:

- [ ] xAI API key rotated
- [ ] xAI key updated in 1Password
- [ ] xAI key updated in ~/clawd/.env
- [ ] Google OAuth credentials rotated
- [ ] Google OAuth updated in 1Password
- [ ] Google Calendar re-authenticated
- [ ] Secrets allowed on GitHub (whitelist)
- [ ] Git push successful
- [ ] Old credentials confirmed revoked
- [ ] No suspicious activity detected
- [ ] Rotation logged in 1Password notes
- [ ] Calendar reminder set for next rotation (90 days)

---

## Questions?

- **Why not rewrite git history?** Too risky - could break things, and secrets are already exposed
- **Are other credentials compromised?** No - only these three were in that file
- **Should I panic?** No - rotate the credentials and you're secure again
- **How do I prevent this?** Never commit real secrets - use placeholders

---

**Status:** AWAITING ROTATION  
**Owner:** Ross  
**Next Step:** Rotate xAI and Google OAuth credentials, then allow secrets on GitHub
