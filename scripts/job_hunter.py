#!/usr/bin/env python3
"""
Overnight Job Hunter - Finds and scores relevant jobs for Ross
Phase 2: Real LinkedIn and Indeed integration (hybrid mode)
Generates search URLs + attempts scraping where possible
Runs at 2am daily, finds actual Florida pet food/CPG jobs
"""
import json
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Try to import scrapers (may not work due to anti-bot measures)
SCRAPERS_AVAILABLE = False
try:
    from linkedin_scraper import search_linkedin_multiple
    from indeed_scraper import search_indeed_multiple
    SCRAPERS_AVAILABLE = True
    logger_msg = "✅ Scrapers loaded"
except ImportError as e:
    logger_msg = f"⚠️  Scrapers not available: {e}"

# Configure logging
log_dir = Path.home() / 'clawd' / 'logs'
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'job-hunter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(logger_msg)

# Ross's job preferences
PREFERENCES = {
    "titles": [
        "Product Development Scientist",
        "R&D Scientist", 
        "Food Scientist",
        "Senior Scientist",
        "Formulation Scientist"
    ],
    "locations_florida": [
        ("Tampa, FL", "Tampa, Florida"),
        ("Miami, FL", "Miami, Florida"),
        ("Orlando, FL", "Orlando, Florida"),
        ("Jacksonville, FL", "Jacksonville, Florida")
    ],
    "locations_remote": [("Remote", "Remote")],
    "exclude_companies": [
        "mars",
        "mars petcare"
    ],
    "bonus_companies": [
        "purina", "nestlé", "nestle", "hill's", "royal canin",
        "p&g", "procter", "unilever", "kraft", "general mills",
        "pepsico", "coca-cola", "mondelez", "kellogg"
    ],
    "bonus_keywords": [
        "pet food", "pet nutrition", "petcare", "cpg", 
        "consumer packaged", "food science", "r&d", 
        "product development", "formulation"
    ]
}

def build_indeed_url(query, location, days_ago=1):
    """Build Indeed search URL"""
    from urllib.parse import urlencode
    params = {
        'q': query,
        'l': location,
        'fromage': str(days_ago),
        'sort': 'date'
    }
    return f"https://www.indeed.com/jobs?{urlencode(params)}"

def build_linkedin_url(keywords, location):
    """Build LinkedIn search URL"""
    from urllib.parse import urlencode
    params = {
        'keywords': keywords,
        'location': location,
        'sortBy': 'DD',
        'f_TPR': 'r86400'  # Last 24 hours
    }
    return f"https://www.linkedin.com/jobs/search?{urlencode(params)}"

def generate_search_urls():
    """Generate all search URLs for manual/automated use"""
    searches = []
    
    # LinkedIn searches
    for title in PREFERENCES['titles']:
        for indeed_loc, linkedin_loc in PREFERENCES['locations_florida']:
            searches.append({
                'platform': 'LinkedIn',
                'title': title,
                'location': linkedin_loc,
                'url': build_linkedin_url(title, linkedin_loc),
                'query_type': 'florida'
            })
        
        # Remote searches
        searches.append({
            'platform': 'LinkedIn',
            'title': title,
            'location': 'Remote',
            'url': build_linkedin_url(title, 'Remote'),
            'query_type': 'remote'
        })
    
    # Indeed searches
    for title in PREFERENCES['titles']:
        for indeed_loc, linkedin_loc in PREFERENCES['locations_florida']:
            searches.append({
                'platform': 'Indeed',
                'title': title,
                'location': indeed_loc,
                'url': build_indeed_url(title, indeed_loc, days_ago=1),
                'query_type': 'florida'
            })
        
        # Remote searches
        searches.append({
            'platform': 'Indeed',
            'title': title,
            'location': 'Remote',
            'url': build_indeed_url(title, 'Remote', days_ago=1),
            'query_type': 'remote'
        })
    
    return searches

def load_job_history():
    """Load history of previously seen jobs"""
    history_file = Path.home() / 'clawd' / 'data' / 'jobs_history.json'
    
    if not history_file.exists():
        return {}
    
    try:
        with open(history_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading job history: {e}")
        return {}

def save_job_history(history):
    """Save job history"""
    history_file = Path.home() / 'clawd' / 'data' / 'jobs_history.json'
    history_file.parent.mkdir(exist_ok=True)
    
    try:
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving job history: {e}")

def clean_old_history(history, days=7):
    """Remove jobs older than N days from history"""
    cutoff = datetime.now() - timedelta(days=days)
    cutoff_str = cutoff.isoformat()
    
    cleaned = {}
    for url, data in history.items():
        if data.get('first_seen', '') >= cutoff_str:
            cleaned[url] = data
    
    removed = len(history) - len(cleaned)
    if removed > 0:
        logger.info(f"Cleaned {removed} old jobs from history")
    
    return cleaned

def is_excluded_company(company):
    """Check if company should be excluded"""
    company_lower = company.lower()
    return any(excl in company_lower for excl in PREFERENCES['exclude_companies'])

def score_job(title, company, location, description=""):
    """
    Score a job posting 1-10 based on fit
    
    Scoring rules:
    - Tampa/Miami + pet food = 10
    - Other Florida + pet food = 8-9
    - Remote + pet food = 7-8
    - Tampa/Miami + CPG = 8
    - Other Florida + CPG = 6-7
    - Remote + CPG = 5-6
    """
    title = title.lower()
    company = company.lower()
    location = location.lower()
    description = description.lower()
    
    # Check for Mars (auto-exclude)
    if is_excluded_company(company):
        return 0  # Will be filtered out
    
    # Industry detection
    is_pet_food = any(kw in description or kw in company for kw in ['pet food', 'pet nutrition', 'petcare', 'pet care'])
    is_cpg = any(kw in description or kw in company for kw in ['cpg', 'consumer packaged goods', 'consumer goods'])
    
    # Location scoring
    is_tampa_miami = any(city in location for city in ['tampa', 'miami'])
    is_florida = 'florida' in location or ', fl' in location
    is_remote = 'remote' in location
    
    # Apply scoring rules
    if is_tampa_miami and is_pet_food:
        score = 10
    elif is_florida and is_pet_food:
        score = 9
    elif is_remote and is_pet_food:
        score = 8
    elif is_tampa_miami and is_cpg:
        score = 8
    elif is_florida and is_cpg:
        score = 7
    elif is_remote and is_cpg:
        score = 6
    elif is_tampa_miami:
        score = 7
    elif is_florida:
        score = 6
    elif is_remote:
        score = 5
    else:
        score = 5
    
    # Title adjustments
    if any(kw in title for kw in ['senior', 'lead', 'principal']):
        score += 1
    if any(kw in title for kw in ['manager', 'director']) and 'project manager' not in title:
        score -= 1  # Ross wants IC roles
    if 'technician' in title or 'associate' in title:
        score -= 2
    
    # Company bonus
    if any(comp in company for comp in PREFERENCES['bonus_companies']):
        score += 1
    
    # Clamp to 1-10
    return max(1, min(10, score))

def attempt_scraping():
    """
    Attempt to scrape jobs from LinkedIn and Indeed
    Falls back gracefully if blocked
    """
    if not SCRAPERS_AVAILABLE:
        logger.warning("Scrapers not available, skipping automated scraping")
        return []
    
    logger.info("Attempting automated scraping...")
    all_jobs = []
    
    # Prepare queries
    linkedin_queries = []
    indeed_queries = []
    
    for title in PREFERENCES['titles'][:3]:  # Top 3 to reduce requests
        for indeed_loc, linkedin_loc in PREFERENCES['locations_florida'][:2]:  # Tampa, Miami
            linkedin_queries.append({'keywords': title, 'location': linkedin_loc})
            indeed_queries.append({'query': title, 'location': indeed_loc})
    
    # Try LinkedIn
    try:
        logger.info(f"Attempting LinkedIn scraping ({len(linkedin_queries)} queries)...")
        linkedin_jobs = search_linkedin_multiple(linkedin_queries, delay_between_searches=4.0)
        if linkedin_jobs:
            logger.info(f"✅ Found {len(linkedin_jobs)} jobs from LinkedIn")
            all_jobs.extend(linkedin_jobs)
        else:
            logger.warning("⚠️  No jobs from LinkedIn (may be blocked)")
    except Exception as e:
        logger.error(f"LinkedIn scraping failed: {e}")
    
    # Try Indeed
    try:
        logger.info(f"Attempting Indeed scraping ({len(indeed_queries)} queries)...")
        indeed_jobs = search_indeed_multiple(indeed_queries, delay_between_searches=4.0)
        if indeed_jobs:
            logger.info(f"✅ Found {len(indeed_jobs)} jobs from Indeed")
            all_jobs.extend(indeed_jobs)
        else:
            logger.warning("⚠️  No jobs from Indeed (may be blocked)")
    except Exception as e:
        logger.error(f"Indeed scraping failed: {e}")
    
    return all_jobs

def save_searches(searches):
    """Save search URLs for manual review"""
    today = datetime.now().strftime('%Y-%m-%d')
    search_file = Path.home() / 'clawd' / 'data' / f'job_searches_{today}.json'
    search_file.parent.mkdir(exist_ok=True)
    
    with open(search_file, 'w') as f:
        json.dump({
            'date': today,
            'total_searches': len(searches),
            'searches': searches,
            'note': 'These URLs can be manually reviewed if automated scraping is blocked'
        }, f, indent=2)
    
    logger.info(f"Saved {len(searches)} search URLs to {search_file}")
    return search_file

def save_results(jobs, scraped_count=0):
    """Save job results to daily file"""
    today = datetime.now().strftime('%Y-%m-%d')
    jobs_file = Path.home() / 'clawd' / 'data' / f'jobs_{today}.json'
    jobs_file.parent.mkdir(exist_ok=True)
    
    high_priority = [j for j in jobs if j.get('score', 0) >= 8]
    
    data = {
        'date': today,
        'total_jobs': len(jobs),
        'scraped_jobs': scraped_count,
        'high_priority': len(high_priority),
        'jobs': sorted(jobs, key=lambda x: x.get('score', 0), reverse=True),
        'note': 'Automated scraping may be limited due to anti-bot measures. Check search URLs for manual review.'
    }
    
    with open(jobs_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved {len(jobs)} jobs to {jobs_file}")
    return jobs_file

def generate_report(jobs, searches, scraped_count=0):
    """Generate human-readable markdown report"""
    today = datetime.now().strftime('%Y-%m-%d')
    report_file = Path.home() / 'clawd' / 'reports' / f'job_hunt_{today}.md'
    report_file.parent.mkdir(exist_ok=True)
    
    high_priority = [j for j in jobs if j.get('score', 0) >= 8]
    medium_priority = [j for j in jobs if 6 <= j.get('score', 0) < 8]
    
    # Count by source
    linkedin_count = len([j for j in jobs if j.get('source') == 'linkedin'])
    indeed_count = len([j for j in jobs if j.get('source') == 'indeed'])
    
    # Group searches by platform
    linkedin_searches = [s for s in searches if s['platform'] == 'LinkedIn']
    indeed_searches = [s for s in searches if s['platform'] == 'Indeed']
    
    report = f"""# Job Hunt Report - {today}

## Summary
- **Searches Generated:** {len(searches)} (LinkedIn: {len(linkedin_searches)}, Indeed: {len(indeed_searches)})
- **Jobs Found:** {scraped_count} via automated scraping
- **High Priority (8+):** {len(high_priority)} 🎯
- **Medium Priority (6-7):** {len(medium_priority)} 📋

---

"""
    
    if scraped_count == 0:
        report += """## ⚠️ Automated Scraping Blocked

LinkedIn and Indeed actively block automated scraping. The search URLs below can be manually reviewed.

**Alternative approaches:**
1. Manual review of generated search URLs (below)
2. Use RapidAPI or ScraperAPI services
3. Browser automation (Playwright/Selenium) with rotating proxies
4. LinkedIn/Indeed API access (if available)

---

"""
    
    report += """## 🔗 Search URLs

### Tampa Priority

"""
    
    # Show Tampa/Miami searches first (highest priority)
    tampa_miami = [s for s in searches if 'Tampa' in s['location'] or 'Miami' in s['location']]
    for search in tampa_miami[:10]:
        report += f"- **{search['title']}** in {search['location']} ([{search['platform']}]({search['url']}))\n"
    
    if high_priority:
        report += f"""

---

## 🎯 High Priority Matches (Score 8+)

"""
        for job in sorted(high_priority, key=lambda x: x.get('score', 0), reverse=True):
            report += f"""### {job.get('title')} - {job.get('company')}
**Score:** {job.get('score')}/10  
**Location:** {job.get('location')}  
**Source:** {job.get('source', 'manual').title()}  
**URL:** {job.get('url')}

{job.get('description', 'No description available.')[:300]}...

---

"""
    
    if medium_priority:
        report += """## 📋 Medium Priority Matches (Score 6-7)

"""
        for job in sorted(medium_priority, key=lambda x: x.get('score', 0), reverse=True)[:10]:
            report += f"- **{job.get('title')}** at {job.get('company')} ({job.get('location')}) - {job.get('score')}/10 - [{job.get('source', 'manual').title()}]({job.get('url')})\n"
    
    report += f"""

---

## 📚 All Search URLs

### LinkedIn ({len(linkedin_searches)} searches)

"""
    
    for search in linkedin_searches[:20]:
        report += f"- {search['title']} in {search['location']}\n  {search['url']}\n\n"
    
    report += f"""

### Indeed ({len(indeed_searches)} searches)

"""
    
    for search in indeed_searches[:20]:
        report += f"- {search['title']} in {search['location']}\n  {search['url']}\n\n"
    
    report += f"""

---

*Generated by Job Hunter v2.0 (Hybrid Mode)*  
*Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*Note: Automated scraping may be limited. Use search URLs for manual review.*
"""
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"Generated report: {report_file}")
    return report_file

def main(test_mode=False):
    """Main job hunter execution"""
    logger.info("=" * 60)
    logger.info("🔍 OVERNIGHT JOB HUNTER - PHASE 2 (HYBRID MODE)")
    logger.info(f"⏰ Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Load job history
    logger.info("Loading job history...")
    history = load_job_history()
    logger.info(f"Loaded {len(history)} previously seen jobs")
    
    # Clean old history
    history = clean_old_history(history, days=7)
    
    # Generate all search URLs
    logger.info("Generating search URLs...")
    searches = generate_search_urls()
    logger.info(f"Generated {len(searches)} search combinations")
    
    # Save search URLs
    search_file = save_searches(searches)
    
    # Attempt automated scraping
    scraped_jobs = attempt_scraping()
    scraped_count = len(scraped_jobs)
    
    if scraped_count > 0:
        logger.info(f"✅ Scraped {scraped_count} jobs successfully")
        
        # Score and deduplicate
        jobs = []
        now = datetime.now().isoformat()
        
        for job in scraped_jobs:
            url = job.get('url')
            if not url or url in history:
                continue
            
            company = job.get('company', '')
            if is_excluded_company(company):
                logger.info(f"Excluding {company}: {job.get('title')}")
                continue
            
            score = score_job(
                job.get('title', ''),
                company,
                job.get('location', ''),
                job.get('description', '')
            )
            
            if score == 0:
                continue
            
            job['score'] = score
            job['found_date'] = now
            job['status'] = 'new'
            
            history[url] = {
                'first_seen': now,
                'title': job.get('title'),
                'company': company
            }
            
            jobs.append(job)
        
        save_job_history(history)
    else:
        logger.warning("⚠️  No jobs scraped (sites may be blocking bots)")
        logger.info("💡 Search URLs available for manual review")
        jobs = []
    
    # Save results
    jobs_file = save_results(jobs, scraped_count)
    
    # Generate report
    report_file = generate_report(jobs, searches, scraped_count)
    
    # Summary
    high_priority = [j for j in jobs if j.get('score', 0) >= 8]
    
    logger.info("=" * 60)
    logger.info("✅ JOB HUNT COMPLETE")
    logger.info(f"📋 Searches generated: {len(searches)}")
    logger.info(f"🤖 Jobs scraped: {scraped_count}")
    logger.info(f"📊 New jobs found: {len(jobs)}")
    logger.info(f"🎯 High priority: {len(high_priority)}")
    
    if high_priority:
        logger.info("\n🚀 HIGH PRIORITY MATCHES:")
        for job in high_priority[:5]:
            logger.info(f"   • {job.get('title')} at {job.get('company')} ({job.get('location')}) - {job.get('score')}/10")
    
    if scraped_count == 0:
        logger.info("\n💡 TIP: Review search URLs in report for manual checking")
    
    logger.info(f"\n📄 Report: {report_file}")
    logger.info(f"🔗 Searches: {search_file}")
    logger.info("=" * 60)
    
    return {
        'success': True,
        'searches_generated': len(searches),
        'jobs_scraped': scraped_count,
        'total_jobs': len(jobs),
        'high_priority': len(high_priority),
        'report_path': str(report_file),
        'searches_path': str(search_file)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Job Hunter - Find Florida pet food/CPG jobs')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    args = parser.parse_args()
    
    try:
        result = main(test_mode=args.test)
        print(f"\n📈 Final stats:")
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get('success') else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
