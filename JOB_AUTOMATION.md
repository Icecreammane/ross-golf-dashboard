# 🎯 Job Search Automation - Florida Edition

**Automated job hunting for Product Development / R&D roles in Florida**

---

## 🚀 Quick Start

### Run a Job Search
```bash
python3 scripts/job_hunter.py scan --location Florida
```

### View Report
```bash
python3 scripts/job_hunter.py report
```

---

## 📋 What It Does

### Multi-Site Scraping
- **Indeed** - Largest job board
- **LinkedIn** - Professional network jobs
- **ZipRecruiter** - Aggregated listings
- **Glassdoor** - Company reviews + jobs

### Smart Filtering
- **Location:** Florida (Miami, Tampa, Orlando, Jacksonville, Fort Myers, Sarasota)
- **Industry:** Food science, pet food, CPG, R&D
- **Salary Range:** $90k - $130k
- **Keywords:** Product development, R&D, formulation, food science

### Match Scoring (1-10)
- **9-10:** 🔥 Perfect fit - Apply immediately
- **7-8:** ⭐ Strong match - Review carefully
- **5-6:** 📋 Possible fit - Consider
- **<5:** ⏭️ Skip

**Scoring factors:**
- Title match (product development, R&D, scientist)
- Company reputation (Mars, Nestlé, P&G, etc.)
- Experience requirements (pet food, formulation, CPG)
- Location preference (beach cities prioritized)
- Salary alignment
- Seniority level

---

## 🎯 Your Profile

The system knows you:
- **Current:** Senior Product Development Scientist, Mars Petcare
- **Experience:** Nutro renovation, IAMS NCH, Portfolio Architecture
- **Skills:** R&D, formulation, product development, food science
- **Target:** Florida, prefer beach access
- **Salary:** $90k-$130k range

---

## 📝 Auto-Generated Materials

### Cover Letter
For each job, the system generates a personalized cover letter:
- References the specific company and role
- Highlights relevant Mars experience
- Emphasizes food science background
- Mentions Florida relocation plans

**Access:** After scan, check `data/job_matches.json` → each job has `cover_letter` field

---

## 📊 Data Storage

**Location:** `data/job_matches.json`

**Structure:**
```json
{
  "jobs": [
    {
      "source": "Indeed",
      "title": "Senior Food Scientist",
      "company": "Nestlé Purina",
      "location": "Tampa, FL",
      "salary": "$95,000 - $120,000",
      "url": "https://...",
      "description": "...",
      "match_score": 9,
      "cover_letter": "Dear Hiring Manager...",
      "posted_date": "2025-02-13T10:30:00",
      "scanned_at": "2025-02-13T14:22:00"
    }
  ],
  "history": [
    {
      "scan_date": "2025-02-13T14:22:00",
      "jobs_found": 5,
      "high_matches": 2,
      "medium_matches": 3
    }
  ]
}
```

---

## 🤖 Daily Automation

**Cron Job** (runs at 8am daily):
```bash
# Add to crontab:
0 8 * * * cd /Users/clawdbot/clawd && python3 scripts/job_hunter.py scan
```

**Telegram Notification:**
Jarvis will send you a morning brief with:
- "5 new Florida jobs found"
- "2 high matches (9+), 3 strong matches (7-8)"
- Links to top jobs
- Quick decision: Apply / Save / Skip

---

## 📱 Application Workflow

### Option 1: Manual Review (Recommended)
1. Get morning notification with jobs
2. Click links to review postings
3. Use pre-generated cover letter
4. Apply directly on company site

### Option 2: Assisted Application
1. Review high-match jobs (8+)
2. Tell Jarvis: "Apply to [company] job"
3. Jarvis opens application, pre-fills known info
4. You review and submit

### Option 3: Full Auto (Future)
- Auto-apply to 9+ matches
- Ross approval required first
- Track application status

---

## 🎯 Current Limitations

**Note:** This is v1 - functional but not perfect.

**Scraping limitations:**
- Some sites block automated scraping (Indeed, LinkedIn)
- Currently returns sample data to demonstrate functionality
- Real implementation needs:
  - Selenium for dynamic sites
  - Rotating proxies
  - Rate limiting
  - Or paid APIs (SimplyHired, Adzuna)

**To make fully production:**
1. Add Selenium with headless Chrome
2. Implement proper rate limiting
3. Use paid APIs where needed (LinkedIn API requires company account)
4. Add CAPTCHA solving (2captcha.com)

---

## 🛠️ Customization

**Change target location:**
```bash
python3 scripts/job_hunter.py scan --location "California"
```

**Modify profile:**
Edit `scripts/job_hunter.py` → `PROFILE` dict

**Adjust scoring:**
Edit `score_job_match()` function to change weights

**Add job sites:**
Add new `scrape_[site]()` function and call it in `scan_jobs()`

---

## 📈 Future Enhancements

- [ ] Real-time scraping (not mock data)
- [ ] Application tracking (which jobs applied to)
- [ ] Auto-fill application forms
- [ ] Interview scheduling integration
- [ ] Salary negotiation guidance
- [ ] Company research summaries
- [ ] Network connection finder (who do you know there?)

---

## 🐛 Troubleshooting

**"No jobs found"**
- Check internet connection
- Verify data directory exists
- Check if sites changed their structure

**"Scraping error"**
- Sites may be blocking requests
- Try adding delays between requests
- Consider using paid APIs

**"Bad match scores"**
- Adjust scoring weights in code
- Update profile with more keywords
- Check if job descriptions are parsing correctly

---

## 💡 Pro Tips

1. **Run daily** - Best jobs go fast
2. **Apply same day** - First 10 applicants have huge advantage
3. **Customize cover letter** - Use generated one as template, add personal touch
4. **Track applications** - Keep spreadsheet of what you applied to
5. **Network** - Check if you know anyone at the company (LinkedIn)
6. **Research company** - 5 minutes of research = better application

---

**Questions?** Tell Jarvis: "Explain job automation" or "How do I apply to jobs?"
