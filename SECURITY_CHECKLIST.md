# Security Audit Checklist

## Weekly Security Audit (Every Sunday 9am)

Run this command:
```bash
python3 ~/clawd/scripts/security_audit.py
```

This automated audit checks:
- ✅ Git history for exposed credentials
- ✅ File permissions on sensitive files  
- ✅ Hardcoded secrets in code
- ✅ API security logs
- ✅ GitHub sync status
- ✅ .gitignore coverage

**Report Location:** `~/clawd/security-logs/audit-YYYY-MM-DD.md`

---

## Manual Security Checklist (Monthly)

### 1. Credential Review
- [ ] Rotate any compromised API keys
- [ ] Review who has access to what
- [ ] Check for unused API keys (revoke them)
- [ ] Verify 2FA enabled on all accounts

### 2. GitHub Security
- [ ] Review commit history for accidental secrets
- [ ] Check `.gitignore` coverage
- [ ] Verify private repo settings
- [ ] Review collaborator access

### 3. API & Service Audit  
- [ ] Google API usage & quotas
- [ ] Telegram bot token status
- [ ] Spotify API connection
- [ ] Gmail app passwords
- [ ] Any new integrations added?

### 4. System Security
- [ ] macOS security updates installed?
- [ ] Clawdbot updated to latest version
- [ ] Python dependencies updated
- [ ] Node.js dependencies audited

### 5. Backup Verification
- [ ] Last backup date: `ls -lt ~/clawd/backups/ | head`
- [ ] Test restore from backup
- [ ] Verify backup includes credentials

---

## Incident Response

If security issue detected:

1. **Immediate Actions:**
   - Run `/lockdown` to revoke all API access
   - Change affected passwords
   - Revoke compromised API keys
   - Log incident to `security-logs/incidents.md`

2. **Investigation:**
   - When was credential exposed?
   - What had access?
   - Was it used maliciously?

3. **Remediation:**
   - Purge from Git history if needed
   - Rotate all related credentials
   - Update security procedures
   - Document lessons learned

---

## Security Contacts

**Owner:** Ross Caster  
**Emergency Contact:** Telegram @rosscaster  
**Kill Switch:** `/lockdown` command to Jarvis

---

## Last Audit

**Date:** 2026-02-07  
**Status:** ✅ PASSED (3 warnings addressed)  
**Issues Found:** 0 critical, 3 warnings  
**Next Audit:** 2026-02-14

---

## Audit History

| Date | Status | Critical | Warnings | Notes |
|------|--------|----------|----------|-------|
| 2026-02-07 | ✅ PASSED | 0 | 3 | Initial audit, GitHub history purged |
