# Emergency Protocols: When Things Go Wrong
**Last Updated:** 2026-02-07  
**Keep this handy on launch day**

---

## SCENARIO 1: SITE IS DOWN 🚨

### Symptoms
- Homepage won't load
- Users report 502/503 errors
- Uptime monitor alerts

### Immediate Actions (Do in order)
1. **Verify it's actually down**
   ```bash
   curl -I https://fittrack.app
   # Should return 200 OK. If not, it's down.
   ```

2. **Check server status**
   ```bash
   ssh yourserver
   systemctl status your-app-name
   # Is the service running?
   ```

3. **Restart application**
   ```bash
   sudo systemctl restart your-app-name
   # Wait 30 seconds, check again
   curl -I https://fittrack.app
   ```

4. **If still down, check logs**
   ```bash
   tail -f /var/log/your-app/error.log
   # Look for recent errors
   ```

5. **Post status update**
   - Twitter: "FitTrack is temporarily down. Fixing it now. Back shortly."
   - Reddit: Edit launch post with update
   - (Keeps users informed, reduces panic)

6. **Fix the issue**
   - Common causes: database connection, memory overflow, disk full
   - Check: `df -h` (disk space), `free -m` (memory), database connectivity

7. **Verify it's back**
   ```bash
   curl https://fittrack.app
   # Test signup flow manually
   ```

8. **Post recovery update**
   - "Back online! Sorry for the brief downtime. Thanks for your patience."

---

## SCENARIO 2: SIGNUPS ARE BROKEN 🐛

### Symptoms
- Users report "can't sign up"
- Error messages on signup form
- No new signups showing in dashboard

### Immediate Actions
1. **Test the signup flow yourself**
   - Open incognito window
   - Try to sign up with test email
   - Note exact error message

2. **Check error logs**
   ```bash
   tail -f /var/log/your-app/error.log | grep signup
   ```

3. **Common issues:**
   - Database full (can't insert users)
   - Email service down (can't send welcome email)
   - Form validation bug
   - Session/cookie issue

4. **Quick fix if possible**
   - If it's validation: relax validation temporarily
   - If it's email: disable email temporarily (log it instead)
   - If it's database: clear old test data

5. **Communicate**
   - Post on Reddit: "Found a signup bug, fixing now. Back in 30 min."
   - Be honest, users appreciate transparency

6. **Fix, test, deploy**
   - Fix the bug
   - Test locally
   - Test on production
   - Verify with test signup

7. **Offer compensation**
   - Free month for anyone affected by the bug

---

## SCENARIO 3: DATABASE CRASH 💥

### Symptoms
- All pages showing errors
- Can't fetch data
- "Database connection failed"

### Immediate Actions
1. **Check database status**
   ```bash
   # For PostgreSQL
   sudo systemctl status postgresql
   
   # For MySQL
   sudo systemctl status mysql
   ```

2. **Restart database**
   ```bash
   sudo systemctl restart postgresql  # or mysql
   ```

3. **Check disk space**
   ```bash
   df -h
   # Database logs can fill disk, causing crash
   ```

4. **If disk is full:**
   ```bash
   # Clear old logs (CAREFUL!)
   sudo find /var/log -name "*.log" -mtime +7 -delete
   ```

5. **Verify application can connect**
   ```bash
   # Test database connection in your app
   python manage.py db-test  # or equivalent
   ```

6. **If data is corrupted:**
   - Restore from backup (see backup protocol below)
   - This is why backups matter!

---

## SCENARIO 4: GETTING DDOS'ED / TRAFFIC SPIKE 📈

### Symptoms
- Site extremely slow
- Hundreds of requests per second
- Servers maxed out on CPU/memory

### Immediate Actions
1. **Verify it's real traffic, not attack**
   - Check analytics: real users or bots?
   - Check logs: same IP making 1000s of requests?

2. **If it's real users (good problem!):**
   - Scale server temporarily (add more RAM/CPU)
   - Enable caching (if not already)
   - Simplify queries (remove expensive database calls)

3. **If it's an attack (bad problem):**
   - Enable Cloudflare (free DDoS protection)
   - Rate limit by IP (block IPs making >100 requests/min)
   - Temporarily require CAPTCHA on signup

4. **Quick rate limiting (nginx example):**
   ```nginx
   limit_req_zone $binary_remote_addr zone=one:10m rate=30r/m;
   limit_req zone=one burst=5;
   ```

---

## SCENARIO 5: DATA LOSS / ACCIDENTAL DELETION 😱

### Symptoms
- Users report missing data
- Database table accidentally dropped
- Deployment overwrote production data

### Immediate Actions
1. **STOP EVERYTHING**
   - Don't make it worse
   - Take site offline if necessary

2. **Assess damage**
   - What data is lost?
   - How many users affected?
   - When did it happen?

3. **Restore from backup**
   ```bash
   # PostgreSQL example
   psql fittrack_db < backup_2026-02-07.sql
   ```

4. **If no recent backup:**
   - Check database logs for recovery
   - PostgreSQL: write-ahead logs (WAL)
   - MySQL: binary logs

5. **Communicate honestly**
   - "We experienced data loss. Restoring from backup."
   - "If you logged meals today, you may need to re-log."
   - Be transparent, apologize, offer compensation

6. **After recovery:**
   - Set up automated backups (if not already)
   - Test backup restoration process
   - Document what happened (post-mortem)

---

## SCENARIO 6: PAYMENT PROCESSING FAILURE 💳

### Symptoms
- Users can't subscribe
- Stripe webhook failing
- "Payment failed" errors

### Immediate Actions
1. **Check Stripe dashboard**
   - Are payments actually failing?
   - What's the error message?

2. **Common issues:**
   - Webhook URL changed (update in Stripe)
   - API key expired (regenerate)
   - Card declined (user issue, not yours)

3. **Test payment yourself**
   - Use Stripe test card: 4242 4242 4242 4242
   - Verify webhook received

4. **If webhook broken:**
   - Update URL in Stripe dashboard
   - Re-test with test payment

5. **Communicate**
   - Email affected users: "Payment processing temporarily down, fixed now"
   - Offer to manually activate if urgent

---

## SCENARIO 7: NEGATIVE VIRAL ATTENTION 📉

### Symptoms
- Reddit post gets negative traction
- Comments turning hostile
- "This is spam" accusations

### Immediate Actions
1. **Stay calm**
   - Don't defensive-reply emotionally
   - Take 30 minutes before responding

2. **Assess criticism**
   - Is it valid? (e.g., "signup is broken") → Fix it
   - Is it taste-based? (e.g., "I prefer MFP") → Respect opinion
   - Is it trolling? (e.g., "This is garbage") → Ignore

3. **Respond professionally**
   - Acknowledge valid criticism
   - Thank them for feedback
   - Don't argue or justify excessively

4. **Know when to disengage**
   - If it's turning into an argument, stop replying
   - "Thanks for the feedback, I'll consider it."

5. **Learn and iterate**
   - If multiple people say the same thing, it's real feedback
   - Implement changes, announce improvements

---

## BACKUP PROTOCOL 💾

### Daily Backups (Automated)
```bash
#!/bin/bash
# Run daily at 2 AM
DATE=$(date +%Y-%m-%d)
pg_dump fittrack_db > /backups/fittrack_$DATE.sql
# Keep last 7 days
find /backups -name "fittrack_*.sql" -mtime +7 -delete
```

### Manual Backup (Before Risky Changes)
```bash
pg_dump fittrack_db > /backups/pre-launch_$(date +%Y-%m-%d_%H-%M).sql
```

### Test Restoration (Do this BEFORE launch)
```bash
# On test server
dropdb fittrack_test
createdb fittrack_test
psql fittrack_test < backup_2026-02-07.sql
# Verify data looks correct
```

---

## CONTACT LIST (Emergency)

**Hosting Provider:**
- Support: [provider support URL]
- Account: [login details in password manager]

**Domain Registrar:**
- Support: [registrar support]
- Account: [login details]

**Payment Processor (Stripe):**
- Dashboard: https://dashboard.stripe.com
- Support: https://support.stripe.com

**Email Service:**
- Dashboard: [email service dashboard]

**DNS Provider:**
- Dashboard: [DNS dashboard]

---

## POST-INCIDENT CHECKLIST ✅

After every incident:
- [ ] Document what happened
- [ ] Document what fixed it
- [ ] Update this emergency checklist
- [ ] Implement preventive measures
- [ ] Test backup/recovery process
- [ ] Communicate with affected users

---

## KEEP CALM MANTRA 🧘

> "Launch day issues are NORMAL. Every product has them. Users are forgiving if you're honest, fast, and apologetic. Fix it, learn from it, move on."

**Remember:**
- Stripe went down on launch day
- Product Hunt has bugs regularly
- Even Google has outages

You're not alone. You've got this. 💪

---

## QUICK REFERENCE COMMANDS

**Check if site is up:**
```bash
curl -I https://fittrack.app
```

**Check server resources:**
```bash
top  # CPU/memory usage
df -h  # Disk space
```

**Restart app:**
```bash
sudo systemctl restart fittrack
```

**Check logs:**
```bash
tail -f /var/log/fittrack/error.log
```

**Database backup:**
```bash
pg_dump fittrack_db > backup.sql
```

**Database restore:**
```bash
psql fittrack_db < backup.sql
```

---

**Print this. Keep it next to your computer. You'll need it. 🚀**
