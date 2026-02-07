# Audit System Documentation

## Overview

All autonomous actions are logged to `logs/autonomous-actions.log` in JSONL format (one JSON object per line).

This allows for:
- Transparency (Ross can see everything Jarvis does)
- Learning (patterns in autonomous behavior)
- Debugging (when things go wrong)
- Trust-building (accountability)

---

## Log Format

**JSONL (JSON Lines)** - One JSON object per line

### Required Fields

```json
{
  "timestamp": "2026-02-07T14:30:00Z",
  "zone": "green",
  "action": "Fixed bug in food logging",
  "reason": "User reported error in Discord",
  "result": "Deployed fix, user confirmed working",
  "files_changed": ["app.py", "db_utils.py"]
}
```

**Field Descriptions:**

- **timestamp** - ISO 8601 format (UTC timezone)
- **zone** - One of: `green`, `yellow`, `red`, `emergency`
- **action** - What was done (verb phrase, specific)
- **reason** - Why it was done (context, trigger)
- **result** - Outcome (what happened, success/failure)
- **files_changed** - Array of file paths (if code/docs modified)

### Optional Fields

```json
{
  "timestamp": "2026-02-07T14:30:00Z",
  "zone": "yellow",
  "action": "Deployed hotfix to production",
  "reason": "Checkout was broken, revenue at risk",
  "result": "Fix deployed, tested, users can checkout now",
  "files_changed": ["checkout.js"],
  "notification_sent": true,
  "user_affected": "john@example.com",
  "revenue_impact": "$50 prevented loss",
  "links": ["https://github.com/repo/commit/abc123"]
}
```

**Optional Field Descriptions:**

- **notification_sent** - Did Jarvis notify Ross? (yellow/emergency actions)
- **user_affected** - User email/ID if relevant
- **revenue_impact** - Financial impact (if applicable)
- **links** - URLs to commits, PRs, threads, etc.

---

## Zone Definitions

### Green Zone
**No approval needed, just log it.**

Examples:
- Writing code
- Updating documentation
- Research
- Backups
- Memory updates

### Yellow Zone
**Do it, then notify Ross immediately.**

Examples:
- Deploying bug fixes
- Replying to support emails
- Restarting crashed services

### Red Zone
**Ask first, log the request and outcome.**

Examples:
- Spending money
- Posting publicly
- Deleting data
- Major product changes

### Emergency
**Critical incidents requiring immediate attention.**

Examples:
- Site down >15 mins
- Security breach
- Legal threats

---

## Reading the Log

### Command-Line Tools

**View last 10 actions:**
```bash
tail -10 logs/autonomous-actions.log | jq
```

**Filter by zone:**
```bash
cat logs/autonomous-actions.log | jq 'select(.zone == "yellow")'
```

**Count actions by zone:**
```bash
cat logs/autonomous-actions.log | jq -r .zone | sort | uniq -c
```

**Actions today:**
```bash
cat logs/autonomous-actions.log | jq -r 'select(.timestamp | startswith("2026-02-07"))'
```

**Search for specific action:**
```bash
cat logs/autonomous-actions.log | jq 'select(.action | contains("deploy"))'
```

---

## Weekly Summary

**Auto-generated every Sunday at 8:00 PM**

### Summary Format

```markdown
# Weekly Autonomous Actions Summary
**Week of:** Feb 2-8, 2026

## Overview
- **Total actions:** 47
- **Green zone:** 40 (85%)
- **Yellow zone:** 6 (13%)
- **Red zone:** 1 (2%)
- **Emergency:** 0 (0%)

## Most Common Actions
1. Updated memory files (12 times)
2. Fixed bugs (8 times)
3. Research (7 times)
4. Backup data (5 times)
5. Deployed hotfixes (3 times)

## Yellow Zone Actions (Review)
1. **Deployed hotfix to checkout** (Feb 5, 11:30 PM)
   - Reason: Checkout broken, revenue at risk
   - Result: Fixed, users can pay again
   
2. **Replied to 5 support emails** (Feb 7, 2:00 PM)
   - Reason: Common questions about pricing
   - Result: All answered, users satisfied

## Red Zone Actions
1. **Requested approval for feature change** (Feb 6, 10:00 AM)
   - Request: Add barcode scanner to FitTrack
   - Outcome: Approved, prioritized for next sprint

## System Health
- **Uptime:** 99.8%
- **Errors:** 3 (all fixed)
- **Performance:** Avg response time 120ms (good)

## Next Week Priorities
- Finish FitTrack launch prep
- Build dating prep materials
- Monitor post-launch metrics
```

---

## Viewing Summaries

**List all summaries:**
```bash
ls -lh logs/summaries/
```

**Read this week's summary:**
```bash
cat logs/summaries/2026-02-02_week.md
```

**Compare to last week:**
```bash
diff logs/summaries/2026-01-26_week.md logs/summaries/2026-02-02_week.md
```

---

## Retention Policy

**Log files:**
- Keep all logs indefinitely (they're small, text-based)
- Archive annually (move to `logs/archive/YYYY/`)

**Weekly summaries:**
- Keep all summaries (they're markdown, highly compressible)
- Never delete (they're the historical record)

**Why keep everything:**
- Learning patterns over time
- Debugging old issues
- Accountability and transparency

---

## Security & Privacy

**What gets logged:**
- Actions taken (code, deploys, research)
- Reasons (context, triggers)
- Results (outcomes)
- File changes (paths, not contents)

**What does NOT get logged:**
- User passwords or API keys
- Private messages (unless relevant to action)
- Sensitive financial details (beyond high-level impact)

**Who can access logs:**
- Ross (full access)
- Jarvis (read/write)
- No one else (logs are private)

---

## Generating Weekly Summaries

**Automated process (runs Sunday 8:00 PM):**

1. Read `logs/autonomous-actions.log`
2. Filter to last 7 days
3. Aggregate by zone
4. Count action types
5. Extract yellow/red zone details
6. Check system health metrics
7. Generate markdown summary
8. Save to `logs/summaries/YYYY-MM-DD_week.md`
9. Send to Ross via Telegram

**Manual generation:**
```bash
python3 scripts/generate_weekly_summary.py
```

---

## Example Real-World Log Entries

### Green Zone: Bug Fix
```json
{
  "timestamp": "2026-02-07T10:15:00Z",
  "zone": "green",
  "action": "Fixed food search autocomplete bug",
  "reason": "User reported search not showing results for common foods",
  "result": "Fixed SQL query, tested, deployed to staging",
  "files_changed": ["app.py", "db_queries.py"]
}
```

### Yellow Zone: Deployment
```json
{
  "timestamp": "2026-02-07T23:45:00Z",
  "zone": "yellow",
  "action": "Deployed hotfix to production",
  "reason": "Stripe webhook failing, payments not processing",
  "result": "Fixed webhook handler, payments working again",
  "files_changed": ["stripe_webhooks.py"],
  "notification_sent": true,
  "revenue_impact": "~$200 in pending payments recovered"
}
```

### Red Zone: Spending Request
```json
{
  "timestamp": "2026-02-08T09:00:00Z",
  "zone": "red",
  "action": "Requested approval to purchase Google Ads credits",
  "reason": "FitTrack launch next week, ads could drive signups",
  "result": "Awaiting Ross's approval",
  "links": ["https://ads.google.com/pricing"]
}
```

### Emergency: Site Down
```json
{
  "timestamp": "2026-02-06T03:30:00Z",
  "zone": "emergency",
  "action": "Site down for 20 minutes, restarted server",
  "reason": "Server crashed due to memory leak",
  "result": "Site back up, monitoring for repeat issues",
  "notification_sent": true,
  "links": ["https://status.fittrack.app"]
}
```

---

## Troubleshooting

### "Log file is missing"
```bash
# Create it
touch logs/autonomous-actions.log
```

### "Log file is corrupted"
```bash
# Validate JSONL
cat logs/autonomous-actions.log | jq empty
# If errors, find bad lines:
cat logs/autonomous-actions.log | jq -c . || echo "Error at line $?"
```

### "Can't read log entries"
```bash
# Install jq (JSON parser)
brew install jq  # macOS
sudo apt install jq  # Linux
```

---

## Adding Custom Fields

**Example: Track deployment time**

```json
{
  "timestamp": "2026-02-07T14:30:00Z",
  "zone": "yellow",
  "action": "Deployed hotfix",
  "reason": "Critical bug",
  "result": "Fixed",
  "files_changed": ["app.py"],
  "deploy_duration_seconds": 45,
  "rollback_plan": "Revert commit abc123"
}
```

**Document new fields here** so future-you knows what they mean.

---

## Best Practices

1. **Log immediately** - Don't wait until end of day
2. **Be specific** - "Fixed bug" is bad, "Fixed food search autocomplete bug" is good
3. **Include context** - Why did you do this? Who requested it?
4. **Log failures too** - "Attempted fix, didn't work, trying alternative approach"
5. **Link to evidence** - Commits, PRs, threads, screenshots
6. **Review weekly** - Check summaries for patterns and learnings

---

## Questions?

If you're unsure whether to log something: **log it.**

Too much logging is better than too little.

Ross can always filter/ignore. But he can't recover missing logs.

**When in doubt, log it out. 📝**
