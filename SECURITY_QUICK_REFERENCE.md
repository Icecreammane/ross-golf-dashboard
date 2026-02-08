# 🔒 Security Quick Reference

**For: Ross**  
**Last Updated:** February 8, 2026

---

## 🚀 Quick Commands

### Daily Security Checks
```bash
# View today's audit log
cat ~/clawd/security-logs/audit-$(date +%Y-%m-%d).md

# Check backup status
ls -lht ~/clawd/backups/encrypted-data-backups/ | head -5

# Verify file permissions
stat -f "%Sp %N" ~/clawd/.env
# Should show: -rw------- (600)
```

### Run Manual Backup
```bash
bash ~/clawd/scripts/encrypted_backup.sh
```

### Check LaunchD Services
```bash
# List Jarvis services
launchctl list | grep -E "(jarvis|clawdbot)"

# Load backup service
launchctl load ~/clawd/launchd/com.jarvis.encrypted-backup.plist

# Unload service
launchctl unload ~/clawd/launchd/com.jarvis.encrypted-backup.plist
```

### Log Security Event
```bash
# Daemon execution
python3 ~/clawd/scripts/security_audit_logger.py DAEMON_EXECUTION daemon_name success 0 45.2

# File access
python3 ~/clawd/scripts/security_audit_logger.py SENSITIVE_FILE_ACCESS .env read

# Security scan
python3 ~/clawd/scripts/security_audit_logger.py SECURITY_SCAN credential_scan 0 0
```

---

## 📁 Important File Locations

**Credentials:**
- Main config: `~/.env` (600)
- Fitness Tracker: `~/clawd/fitness-tracker/.env` (600)
- Revenue Dashboard: `~/clawd/revenue_dashboard/.env` (600)
- Gmail/Telegram: `~/clawd/.credentials/*.json` (600)

**Backups:**
- Encrypted backups: `~/clawd/backups/encrypted-data-backups/`
- iCloud backups: `~/Library/Mobile Documents/com~apple~CloudDocs/Jarvis-Backups/`

**Logs:**
- Security audit: `~/clawd/security-logs/audit-YYYY-MM-DD.md`
- Backup logs: `~/clawd/security-logs/backup.log`
- Daemon logs: `~/clawd/logs/`

**Scripts:**
- Audit logger: `~/clawd/scripts/security_audit_logger.py`
- Backup script: `~/clawd/scripts/encrypted_backup.sh`

---

## 🔑 Credential Management

### View Current Credentials
```bash
# Main .env (NEVER cat this in public!)
cat ~/.env  # Shows API keys

# Templates (safe to view)
cat ~/clawd/.env.example  # No real secrets
```

### Update API Key
```bash
# Edit .env securely
nano ~/clawd/.env  # or vim, code, etc.

# Verify permissions after edit
chmod 600 ~/clawd/.env
```

### Credential Locations (for 1Password)
1. **Gemini API:** `.env` → `GEMINI_API_KEY`
2. **Grok API:** `.env` → `GROK_API_KEY`
3. **Gmail:** `.credentials/gmail_credentials.json`
4. **Telegram Bot:** `.credentials/telegram_credentials.json`
5. **Stripe:** `fitness-tracker/.env` → `STRIPE_SECRET_KEY`
6. **Twitter:** `.env` → `TWITTER_*` (not yet configured)

---

## 💾 Backup & Restore

### Restore from Backup
```bash
# List available backups
ls -lh ~/clawd/backups/encrypted-data-backups/

# Mount encrypted backup
hdiutil attach ~/clawd/backups/encrypted-data-backups/data-backup-YYYY-MM-DD_HH-MM-SS.dmg
# Password: JarvisBackup2026! (or from Keychain)

# Backup mounts to /Volumes/data-backup-YYYY-MM-DD_HH-MM-SS/
# Copy files back to ~/clawd/data/

# Unmount when done
hdiutil detach /Volumes/data-backup-*
```

### Change Backup Password
```bash
# Store new password in Keychain
security add-generic-password -s "jarvis-backup-encryption" -a "clawdbot" -w

# Then edit scripts/encrypted_backup.sh to use Keychain
```

---

## 🚨 Emergency Procedures

### Kill Switch (Revoke All Access)
```bash
# In Telegram, send:
/lockdown

# Or manually:
mv ~/.credentials ~/.credentials.locked
mv ~/clawd/.env ~/clawd/.env.locked
```

### Credential Breach Response
1. **Immediately revoke** compromised key at provider
2. **Generate new** API key
3. **Update** `.env` file with new key
4. **Log incident**: 
   ```bash
   python3 ~/clawd/scripts/security_audit_logger.py SECURITY_SCAN credential_breach 1 1
   ```
5. **Review** audit logs for unauthorized access

### Backup Failure
```bash
# Check error logs
cat ~/clawd/logs/encrypted-backup-stderr.log

# Run manual backup
bash ~/clawd/scripts/encrypted_backup.sh

# If still failing, check:
- Disk space: df -h
- Permissions: ls -la ~/clawd/backups/
```

---

## 📊 Security Monitoring

### Weekly Checklist
- [ ] Review audit logs
- [ ] Verify backups running
- [ ] Check file permissions
- [ ] Scan for exposed secrets

### Monthly Tasks
- [ ] Test backup restore
- [ ] Rotate test API keys
- [ ] Review access logs
- [ ] Update documentation

### Quarterly (Every 90 Days)
- [ ] **Rotate ALL production API keys**
- [ ] Update 1Password vault
- [ ] Security audit report
- [ ] Update backup password

---

## 🛠️ Troubleshooting

### "Permission denied" on .env
```bash
# Fix: Set owner-only read/write
chmod 600 ~/clawd/.env
```

### Backup fails with "hdiutil: create failed"
```bash
# Check disk space
df -h ~/clawd/backups/

# Clean old backups manually
rm ~/clawd/backups/encrypted-data-backups/data-backup-2026-01-*.dmg
```

### LaunchD service not running
```bash
# Reload service
launchctl unload ~/clawd/launchd/com.jarvis.encrypted-backup.plist
launchctl load ~/clawd/launchd/com.jarvis.encrypted-backup.plist

# Check for errors
launchctl print gui/$(id -u)/com.jarvis.encrypted-backup
```

### Audit log missing
```bash
# Create security-logs directory
mkdir -p ~/clawd/security-logs

# Test logger
python3 ~/clawd/scripts/security_audit_logger.py DAEMON_EXECUTION test success 0 1
```

---

## 📖 Documentation

**Full Documentation:**
- `SECURITY_HARDENING.md` - Complete security implementation
- `SECURITY_TEST_REPORT.md` - All test results
- `SECURITY.md` - Kill switch & general security
- `SECURITY_CHECKLIST.md` - Quick security review

**This Guide:**
Quick reference for common security tasks. Keep handy!

---

**Need Help?**  
Check the full documentation in `SECURITY_HARDENING.md` or ask Jarvis in Telegram.
