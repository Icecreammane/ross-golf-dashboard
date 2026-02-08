# Twitter Daemon - Deployment Checklist

Complete this checklist before marking the daemon as production-ready.

---

## Pre-Deployment

### ✅ Dependencies Installed
```bash
pip3 list | grep tweepy
pip3 list | grep python-dotenv
```
- [ ] tweepy installed
- [ ] python-dotenv installed

### ✅ Credentials Configured
```bash
grep "TWITTER_API_KEY=" /Users/clawdbot/clawd/.env
```
- [ ] TWITTER_API_KEY set
- [ ] TWITTER_API_SECRET set
- [ ] TWITTER_ACCESS_TOKEN set
- [ ] TWITTER_ACCESS_SECRET set
- [ ] TWITTER_BEARER_TOKEN set (optional but recommended)
- [ ] Twitter app has correct permissions (Read + Write + DM)

### ✅ Directory Structure
```bash
ls -la ~/clawd/daemons/
ls -la ~/clawd/data/
ls -la ~/clawd/logs/
```
- [ ] daemons/ directory exists
- [ ] data/ directory exists
- [ ] logs/ directory exists
- [ ] Scripts are executable (chmod +x)

---

## Testing Phase

### ✅ Unit Tests
```bash
cd /Users/clawdbot/clawd
python3 daemons/test_twitter_daemon.py
```
- [ ] Environment test passed
- [ ] Scoring logic test passed
- [ ] Authentication test passed
- [ ] File operations test passed
- [ ] Full daemon run test passed

### ✅ Manual Run
```bash
python3 daemons/twitter_daemon.py
```
- [ ] Daemon runs without errors
- [ ] Authentication successful
- [ ] Logs created in logs/twitter-daemon.log
- [ ] State file created in data/twitter-daemon-state.json
- [ ] Opportunities file created (even if empty)

### ✅ Log Verification
```bash
cat logs/twitter-daemon.log
```
- [ ] Log file exists and is readable
- [ ] Log contains timestamp and structured entries
- [ ] No ERROR or FATAL messages (warnings OK)
- [ ] Successful authentication message present

### ✅ Output Verification
```bash
cat data/twitter-opportunities.json
python3 daemons/view_opportunities.py
```
- [ ] JSON file is valid (can be parsed)
- [ ] Viewer script works
- [ ] Opportunities (if any) have all required fields

---

## launchd Installation

### ✅ Configuration File
```bash
cat daemons/com.clawdbot.twitter-daemon.plist
```
- [ ] Plist file exists
- [ ] Paths are absolute (not relative)
- [ ] StartInterval is 900 (15 minutes)
- [ ] RunAtLoad is true

### ✅ Install launchd Service
```bash
cp daemons/com.clawdbot.twitter-daemon.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist
```
- [ ] Plist copied to ~/Library/LaunchAgents/
- [ ] Service loaded successfully
- [ ] No error messages from launchctl

### ✅ Verify Running
```bash
launchctl list | grep twitter-daemon
```
- [ ] Service appears in list
- [ ] Has a PID (not "-")
- [ ] Exit code is 0 or blank

---

## Production Monitoring

### ✅ First 24 Hours
- [ ] Check logs every 4 hours
- [ ] Verify daemon runs on schedule
- [ ] Confirm no repeated errors
- [ ] Monitor system resource usage (minimal expected)

### ✅ Log Rotation
```bash
ls -lh logs/twitter-daemon*.log
```
- [ ] Logs don't grow too large (>100MB = issue)
- [ ] Consider adding log rotation if needed

### ✅ Alert Integration (Optional)
- [ ] Set up notification for high-score opportunities (≥70)
- [ ] Configure email/Telegram alerts for critical errors
- [ ] Document alert thresholds

---

## Documentation Review

### ✅ Documentation Complete
- [ ] README.md - Overview and features
- [ ] QUICK_START.md - 5-minute setup
- [ ] SETUP.md - Detailed configuration
- [ ] CREDENTIALS.md - API credentials guide
- [ ] DEPLOYMENT_CHECKLIST.md - This checklist
- [ ] All docs accurate and tested

### ✅ Code Quality
- [ ] Scripts have error handling
- [ ] Logging is comprehensive
- [ ] No hardcoded credentials
- [ ] Comments explain complex logic
- [ ] File paths use Path() objects

---

## Security Review

### ✅ Credential Security
- [ ] .env file NOT committed to git
- [ ] .env in .gitignore
- [ ] Credentials not in logs
- [ ] Consider 1Password integration

### ✅ Permissions
- [ ] Scripts run as user (not root)
- [ ] Data directory has correct permissions
- [ ] Logs directory writable

### ✅ Error Handling
- [ ] Graceful handling of API failures
- [ ] Rate limiting handled (wait_on_rate_limit=True)
- [ ] Network errors caught
- [ ] Daemon doesn't crash on errors

---

## Final Checks

### ✅ Performance
- [ ] Daemon completes in <60 seconds typically
- [ ] Memory usage reasonable (<100MB)
- [ ] CPU usage negligible between runs
- [ ] No memory leaks over 24 hours

### ✅ Reliability
- [ ] Runs automatically after reboot
- [ ] Survives network outages
- [ ] Handles API changes gracefully
- [ ] State persists correctly

### ✅ Functionality
- [ ] Mentions detected correctly
- [ ] DMs checked (if elevated access)
- [ ] Scoring algorithm works as expected
- [ ] Opportunities stored correctly
- [ ] No duplicate opportunities

---

## Sign-Off

**Deployed by:** _________________  
**Date:** _________________  
**Version:** 1.0  
**Status:** ☐ STAGING   ☐ PRODUCTION

**Notes:**
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________

---

## Rollback Plan

If issues occur:

```bash
# 1. Stop the daemon
launchctl unload ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist

# 2. Check logs
cat logs/twitter-daemon-stderr.log

# 3. Fix issue

# 4. Test manually
python3 daemons/twitter_daemon.py

# 5. Restart
launchctl load ~/Library/LaunchAgents/com.clawdbot.twitter-daemon.plist
```

---

## Support Contacts

- **Primary:** Ross (user)
- **Developer:** Jarvis (AI assistant)
- **Documentation:** ~/clawd/daemons/

---

**Once all boxes are checked, the daemon is PRODUCTION READY! 🚀**
