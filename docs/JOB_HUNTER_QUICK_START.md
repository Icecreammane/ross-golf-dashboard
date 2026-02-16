# Job Hunter - Quick Start Guide

**Your daily job search URLs, delivered at 2am every day.**

---

## What You Get Every Morning

Every day at 2am, the Job Hunter runs and generates:
- **50 pre-built job search URLs** (LinkedIn + Indeed)
- **Prioritized for Tampa/Miami** pet food/CPG jobs
- **Filtered to last 24 hours only** (fresh postings)
- **Mars excluded** (no conflicts of interest)

---

## Daily Workflow (5-10 minutes)

### Step 1: Check Your Daily Report
```bash
# View today's report
cat ~/clawd/reports/job_hunt_$(date +%Y-%m-%d).md
```

Or open in your editor:
```bash
open ~/clawd/reports/job_hunt_$(date +%Y-%m-%d).md
```

### Step 2: Click High-Priority URLs
The report shows **Tampa/Miami** searches first. Start there:

1. Click first LinkedIn URL (Tampa Product Dev Scientist)
2. Scan results (should show jobs from last 24h)
3. Bookmark any interesting ones
4. Repeat for next 9 high-priority searches

**Time: ~5-10 minutes for top 10 searches**

### Step 3: (Optional) Check Medium-Priority
If no Tampa/Miami matches, check:
- Orlando/Jacksonville searches
- Remote positions
- Other Florida locations

---

## Example Daily Report

```markdown
## 🔗 Search URLs

### Tampa Priority

- **Product Development Scientist** in Tampa, Florida
  https://www.linkedin.com/jobs/search?keywords=Product+Development+Scientist&location=Tampa%2C+Florida&sortBy=DD&f_TPR=r86400

- **Food Scientist** in Miami, Florida
  https://www.linkedin.com/jobs/search?keywords=Food+Scientist&location=Miami%2C+Florida&sortBy=DD&f_TPR=r86400
```

**Just click and browse!**

---

## What The Scoring Means

Jobs are scored 1-10 based on fit:

| Score | Meaning |
|-------|---------|
| 10 | Tampa/Miami + Pet Food (PERFECT MATCH) |
| 9 | Other Florida + Pet Food |
| 8 | Remote + Pet Food OR Tampa/Miami + CPG |
| 7 | Other Florida + CPG |
| 6 | Remote + CPG |
| 5 | Other combinations |

**Auto-excluded:** Mars, Mars Petcare (conflict of interest)

---

## Files You Care About

### Daily Report (Human-Readable)
```
~/clawd/reports/job_hunt_YYYY-MM-DD.md
```
→ Open this every morning. It has all your URLs.

### Daily Search URLs (JSON)
```
~/clawd/data/job_searches_YYYY-MM-DD.json
```
→ Machine-readable version if you want to script something.

### Job History (Deduplication)
```
~/clawd/data/jobs_history.json
```
→ Tracks URLs you've seen (prevents duplicates)

### Logs (Troubleshooting)
```
~/clawd/logs/job-hunter.log
```
→ Check if something seems wrong

---

## Manual Run (Testing)

Run the job hunter manually:
```bash
python3 ~/clawd/scripts/job_hunter.py
```

This generates fresh URLs for today.

---

## Customizing Your Search

Edit `~/clawd/scripts/job_hunter.py` and change `PREFERENCES`:

```python
PREFERENCES = {
    "titles": [
        "Product Development Scientist",  # Add/remove titles
        "R&D Scientist",
        "Food Scientist"
    ],
    "locations_florida": [
        ("Tampa, FL", "Tampa, Florida"),  # Add/remove cities
        ("Miami, FL", "Miami, Florida")
    ],
    "exclude_companies": [
        "mars",        # Add companies to exclude
        "mars petcare"
    ],
    "bonus_companies": [
        "purina",      # Add preferred companies
        "nestle"
    ]
}
```

Then run manually to test:
```bash
python3 ~/clawd/scripts/job_hunter.py --test
```

---

## Troubleshooting

### "No report generated today"
Check the cron job ran:
```bash
tail -50 ~/clawd/logs/job-hunter.log
```

Should show run at 2am. If not:
```bash
crontab -l  # Verify cron job exists
```

### "URLs don't work"
Sites may have changed. Check logs:
```bash
tail -100 ~/clawd/logs/job-hunter.log
```

### "Not seeing Tampa jobs"
LinkedIn/Indeed may not have postings that day. Try:
- Manual LinkedIn search
- Check if broadening to "Florida" shows more

### "Want to change search times"
Edit crontab:
```bash
crontab -e
```

Change `0 2 * * *` to desired time (24-hour format):
- `0 8 * * *` = 8am daily
- `0 */6 * * *` = Every 6 hours
- `0 9 * * 1-5` = 9am weekdays only

---

## Current Limitations

**Automated scraping is blocked:** LinkedIn and Indeed prevent bots from extracting job details. The system generates **search URLs** instead, which you manually review.

**Why this still saves time:**
- No more typing "Product Development Scientist Tampa" 50 times/day
- Pre-filtered to last 24 hours
- Prioritized by your preferences
- All searches in one place

**Want full automation?** See upgrade options in `BUILD_JOB_HUNTER_PHASE2.md`:
- ScraperAPI service ($50/month)
- Playwright browser automation (free but complex)

---

## Tips for Efficient Job Hunting

1. **Check daily:** Fresh postings appear early morning
2. **Start with Tampa/Miami:** Highest priority
3. **Bookmark as you go:** Don't try to remember interesting jobs
4. **Use LinkedIn/Indeed save feature:** Keeps your job hunt organized on their site
5. **Set up job alerts:** Supplement this system with native alerts
6. **Apply same day:** Early applications get noticed

---

## Need Help?

1. **Check logs:** `tail -100 ~/clawd/logs/job-hunter.log`
2. **Read full docs:** `~/clawd/docs/JOB_HUNTER.md`
3. **Ask Jarvis:** "Debug job hunter"

---

## Next Steps (Phase 3 Options)

If you want to upgrade the system:

### Option 1: Browser Automation (Free)
- Use Playwright to render JavaScript
- Handle authentication
- More reliable scraping
- **Setup time:** 2-3 hours

### Option 2: ScraperAPI ($50/month)
- Handles all anti-bot measures
- 95% success rate
- Fully automated
- **Setup time:** 30 minutes

### Option 3: Keep Current System
- Works today
- No additional cost
- Manual URL review (5-10 min/day)
- **Setup time:** 0 minutes (you're done!)

---

**Built for Ross by Jarvis**  
*Your next job is one click away* 🚀
