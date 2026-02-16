# Job Hunter - Phase 2 Documentation

**Real LinkedIn & Indeed Job Scraping for Ross**

## Overview

The Job Hunter automatically searches LinkedIn and Indeed for relevant job postings in the pet food and CPG industries, focusing on Florida locations (especially Tampa and Miami). It runs daily at 2am, finds new postings from the last 24 hours, scores them 1-10 based on fit, and generates a daily report.

## Features

✅ **Real job scraping** from LinkedIn and Indeed  
✅ **Smart scoring algorithm** (1-10 scale based on location + industry)  
✅ **Deduplication** (tracks seen jobs for 7 days)  
✅ **Mars exclusion** (conflict of interest filter)  
✅ **Daily reports** (human-readable markdown)  
✅ **Error handling** (continues if one source fails)  
✅ **Rate limiting** (random delays to avoid detection)

## Architecture

### Core Files

```
scripts/
├── job_hunter.py          # Main orchestrator
├── linkedin_scraper.py    # LinkedIn scraping module
└── indeed_scraper.py      # Indeed scraping module

data/
├── jobs_YYYY-MM-DD.json   # Daily job results
└── jobs_history.json      # Deduplication tracking

reports/
└── job_hunt_YYYY-MM-DD.md # Daily human-readable report

logs/
└── job-hunter.log         # Execution logs
```

## Scoring Algorithm

Jobs are scored 1-10 based on **location + industry**:

| Location | Industry | Score |
|----------|----------|-------|
| Tampa/Miami | Pet Food | 10 |
| Other Florida | Pet Food | 9 |
| Remote | Pet Food | 8 |
| Tampa/Miami | CPG | 8 |
| Other Florida | CPG | 7 |
| Remote | CPG | 6 |

**Adjustments:**
- +1 for senior/lead/principal roles
- -1 for manager/director roles (Ross prefers IC)
- -2 for technician/associate roles
- +1 for bonus companies (Purina, P&G, Unilever, etc.)
- **Auto-exclude:** Mars, Mars Petcare (conflict of interest)

## Search Parameters

### Locations
- Tampa, FL (priority)
- Miami, FL (priority)
- Orlando, FL
- Jacksonville, FL
- Remote

### Job Titles
- Product Development Scientist
- R&D Scientist
- Food Scientist
- Senior Scientist
- Formulation Scientist

### Industries
- Pet food / pet nutrition (highest priority)
- CPG / consumer packaged goods

## Usage

### Manual Run

```bash
# Full production run
python3 ~/clawd/scripts/job_hunter.py

# Test mode (same as production for now)
python3 ~/clawd/scripts/job_hunter.py --test
```

### Automated Schedule

Runs via cron at 2am daily:
```bash
0 2 * * * cd ~/clawd && python3 scripts/job_hunter.py >> logs/job-hunter.log 2>&1
```

### Individual Scraper Testing

Test LinkedIn scraper:
```bash
python3 ~/clawd/scripts/linkedin_scraper.py
```

Test Indeed scraper:
```bash
python3 ~/clawd/scripts/indeed_scraper.py
```

## Output Files

### Daily Jobs JSON (`data/jobs_YYYY-MM-DD.json`)

```json
{
  "date": "2026-02-16",
  "total_jobs": 12,
  "high_priority": 5,
  "jobs": [
    {
      "title": "Senior Product Development Scientist",
      "company": "Nestlé Purina PetCare",
      "location": "Tampa, FL",
      "url": "https://www.linkedin.com/jobs/view/12345",
      "source": "linkedin",
      "score": 10,
      "description": "Lead R&D for premium pet food...",
      "found_date": "2026-02-16T02:00:00",
      "status": "new"
    }
  ]
}
```

### Daily Report (`reports/job_hunt_YYYY-MM-DD.md`)

Human-readable markdown with:
- Summary statistics
- High priority matches (8+) with full details
- Medium priority matches (6-7) as list
- Source attribution

### Job History (`data/jobs_history.json`)

Tracks seen URLs to prevent duplicates:
```json
{
  "https://www.linkedin.com/jobs/view/12345": {
    "first_seen": "2026-02-16T02:00:00",
    "title": "Product Development Scientist",
    "company": "Purina"
  }
}
```

Jobs older than 7 days are automatically removed.

## Web Scraping Details

### Technology Stack
- **requests** - HTTP requests with custom headers
- **BeautifulSoup4** - HTML parsing
- **No Selenium** - Lightweight, fast scraping

### Anti-Detection Measures
- User-agent rotation (4 different agents)
- Random delays between requests (2-5 seconds)
- Proper HTTP headers (Accept, Referer, etc.)
- Session management
- Exponential backoff on errors

### Rate Limiting
- 2-5 second delay between searches
- Random jitter added to delays
- Batch size limited to 25 jobs per search

### Error Handling
- Continue if one source fails (LinkedIn or Indeed)
- Log all errors to `logs/job-hunter.log`
- Graceful degradation (partial results better than none)
- Timeout protection (15 seconds per request)

## LinkedIn Scraping

### URL Pattern
```
https://www.linkedin.com/jobs/search?keywords={query}&location={location}&f_TPR=r86400&sortBy=DD
```

- `f_TPR=r86400` - Last 24 hours filter
- `sortBy=DD` - Date descending

### Parsing Strategy
Tries multiple selectors (LinkedIn changes HTML frequently):
1. `<li>` with class containing "job"
2. `<div>` with class "job-search-card"
3. `<div>` with class "base-card"

Extracts:
- Title from `<h3>` or `.job-card-list__title`
- Company from `<h4>` or `.company`
- Location from `.location`
- URL from `<a href>`
- Description snippet from `<p>`

### Limitations
- No authentication (public job listings only)
- Structure changes may break parsing (multiple fallbacks mitigate this)
- Rate limiting possible (delays help avoid)

## Indeed Scraping

### URL Pattern
```
https://www.indeed.com/jobs?q={query}&l={location}&fromage=1&sort=date
```

- `fromage=1` - Last 24 hours (1 day ago)
- `sort=date` - Most recent first

### Parsing Strategy
Tries multiple selectors:
1. `<div>` with class "job_seen_beacon"
2. `<div>` with "jobsearch" and "card" in class
3. `<td>` with class "resultContent"
4. `<div>` with `data-jk` attribute (job key)

Extracts:
- Job key from `data-jk` attribute
- Title from `.jobTitle` or `.jcs-JobTitle`
- Company from `.companyName`
- Location from `.companyLocation`
- URL built as `https://www.indeed.com/viewjob?jk={job_key}`
- Description from `.snippet`

### Limitations
- No official API
- HTML structure changes frequently (multiple fallbacks help)
- Some jobs may be sponsored/duplicated

## Deduplication

Jobs are deduplicated by URL across:
1. **Within session:** Same job from multiple searches
2. **Across days:** Jobs seen in last 7 days

History stored in `data/jobs_history.json`:
- Key: Job URL
- Value: First seen date, title, company

Old entries (>7 days) automatically pruned.

## Filtering

### Auto-Exclude Companies
- Mars
- Mars Petcare

These are filtered out during scoring (score = 0) due to conflict of interest.

### Location Filtering
Jobs automatically prioritized by location relevance:
- Tampa/Miami > Other Florida > Remote

### Industry Detection
Scans description and company name for:
- Pet food keywords: "pet food", "pet nutrition", "petcare"
- CPG keywords: "cpg", "consumer packaged goods"

## Testing

### Quick Test
```bash
python3 ~/clawd/scripts/job_hunter.py --test
```

### Verify Output
```bash
# Check latest results
cat ~/clawd/data/jobs_$(date +%Y-%m-%d).json | jq '.total_jobs, .high_priority'

# View report
cat ~/clawd/reports/job_hunt_$(date +%Y-%m-%d).md

# Check logs
tail -50 ~/clawd/logs/job-hunter.log
```

### Validation Checklist
- ✅ Real URLs load in browser
- ✅ Mars postings excluded
- ✅ Scores accurate (Tampa pet food = 10)
- ✅ Deduplication works (run twice, no duplicates second time)
- ✅ Both sources working (LinkedIn + Indeed)

## Troubleshooting

### No Jobs Found
1. Check internet connection
2. Verify URLs load manually
3. Check if site structure changed (update selectors)
4. Review error logs: `tail -100 logs/job-hunter.log`

### Rate Limited
- Errors like "429 Too Many Requests"
- **Solution:** Increase delays in scraper files
- Edit `delay_between_searches` parameter

### Parsing Errors
- "Error parsing job card" in logs
- **Cause:** LinkedIn/Indeed changed HTML structure
- **Solution:** Update selectors in scraper files

### Missing Jobs
- Job exists on site but not in results
- **Possible causes:**
  - Not posted in last 24 hours
  - Already in history (deduplicated)
  - Company excluded (Mars)
  - Parsing failed (check logs)

### Duplicate Jobs
- Same job appearing multiple times
- Check `data/jobs_history.json` is being updated
- Verify URL extraction is consistent

## Maintenance

### Regular Checks
- **Weekly:** Review scoring accuracy, adjust if needed
- **Monthly:** Check scraper success rate in logs
- **As needed:** Update selectors if sites change structure

### Updating Preferences

Edit `PREFERENCES` dict in `job_hunter.py`:
```python
PREFERENCES = {
    "titles": [...],           # Add/remove job titles
    "locations_florida": [...], # Add/remove cities
    "exclude_companies": [...], # Add companies to exclude
    "bonus_companies": [...],   # Add preferred companies
    "bonus_keywords": [...]     # Add industry keywords
}
```

### Updating Scoring

Edit `score_job()` function in `job_hunter.py` to adjust priority rules.

## Future Enhancements

**Potential v3 features:**
- Email notifications for high-priority matches
- Glassdoor integration for salary data
- Resume auto-generation for matches
- Company research automation
- Application tracking integration
- Indeed/LinkedIn API access (if available)
- Browser automation for more reliable scraping

## Dependencies

```bash
pip3 install requests beautifulsoup4
```

Already installed on Ross's system.

## Support

Questions or issues? Check:
1. Logs: `logs/job-hunter.log`
2. This documentation
3. Scraper code comments
4. Ask Jarvis: "Debug job hunter"

---

**Built for Ross by Jarvis**  
*Finding your next job while you sleep* 🌙💼
