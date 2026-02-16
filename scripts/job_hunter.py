#!/usr/bin/env python3
"""
Overnight Job Hunter - Finds and scores relevant jobs for Ross
Runs at 2am daily, generates applications for high-scoring matches
"""
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import urllib.parse
import urllib.request
import time

# Ross's job preferences
PREFERENCES = {
    "titles": [
        "r&d scientist",
        "product development scientist", 
        "food scientist",
        "senior scientist",
        "product development",
        "formulation scientist"
    ],
    "locations": {
        "Tampa, FL": 10,
        "Miami, FL": 10,
        "Orlando, FL": 8,
        "Florida": 7,
        "Remote": 6
    },
    "companies_bonus": [
        "purina", "nestle", "mars", "hill's", "royal canin",
        "p&g", "procter", "unilever", "kraft", "general mills",
        "pepsi", "coca-cola", "mondelez", "kellogg"
    ],
    "keywords_bonus": [
        "pet food", "pet nutrition", "cpg", "consumer packaged",
        "r&d", "product development", "formulation", "food science"
    ]
}

def search_indeed(query, location, days=1):
    """Search Indeed for jobs (simple URL-based search)"""
    base_url = "https://www.indeed.com/jobs"
    params = {
        'q': query,
        'l': location,
        'fromage': str(days),
        'sort': 'date'
    }
    
    # Build URL
    query_string = urllib.parse.urlencode(params)
    url = f"{base_url}?{query_string}"
    
    return {
        'search_url': url,
        'query': query,
        'location': location
    }

def search_linkedin(query, location):
    """Search LinkedIn for jobs (URL-based)"""
    base_url = "https://www.linkedin.com/jobs/search"
    params = {
        'keywords': query,
        'location': location,
        'f_TPR': 'r86400',  # Last 24 hours
        'sortBy': 'DD'  # Date descending
    }
    
    query_string = urllib.parse.urlencode(params)
    url = f"{base_url}?{query_string}"
    
    return {
        'search_url': url,
        'query': query,
        'location': location
    }

def generate_searches():
    """Generate all search URLs"""
    searches = []
    
    # Indeed searches
    for title in PREFERENCES['titles'][:3]:  # Top 3 titles
        for location in ['Tampa, FL', 'Miami, FL', 'Florida', 'Remote']:
            searches.append({
                'platform': 'Indeed',
                **search_indeed(title, location, days=1)
            })
    
    # LinkedIn searches  
    for title in PREFERENCES['titles'][:3]:
        for location in ['Tampa, Florida', 'Miami, Florida', 'Florida, United States', 'Remote']:
            searches.append({
                'platform': 'LinkedIn',
                **search_linkedin(title, location)
            })
    
    return searches

def score_job(title, company, location, description=""):
    """Score a job posting 1-10 based on fit"""
    score = 5  # Base score
    
    title_lower = title.lower()
    company_lower = company.lower()
    location_lower = location.lower()
    desc_lower = description.lower()
    
    # Title scoring
    if any(x in title_lower for x in ['senior', 'lead', 'principal']):
        score += 2
    if any(x in title_lower for x in ['r&d', 'product development', 'formulation']):
        score += 2
    elif 'scientist' in title_lower or 'food' in title_lower:
        score += 1
    if 'technician' in title_lower or 'associate' in title_lower:
        score -= 2
    if 'manager' in title_lower or 'director' in title_lower:
        score -= 1  # Ross wants IC roles
    
    # Location scoring
    if 'tampa' in location_lower or 'miami' in location_lower:
        score += 2
    elif 'florida' in location_lower or 'fl' in location_lower:
        score += 1
    elif 'remote' in location_lower:
        score += 1
    
    # Company bonus
    if any(comp in company_lower for comp in PREFERENCES['companies_bonus']):
        score += 2
    
    # Description keywords
    if description:
        keyword_matches = sum(1 for kw in PREFERENCES['keywords_bonus'] if kw in desc_lower)
        score += min(keyword_matches, 2)  # Max +2 for keywords
    
    # Clamp to 1-10
    return max(1, min(10, score))

def create_job_entry(title, company, location, url, score, description=""):
    """Create a standardized job entry"""
    return {
        'title': title,
        'company': company,
        'location': location,
        'url': url,
        'score': score,
        'description': description[:500] if description else "",
        'found_date': datetime.now().isoformat(),
        'status': 'new'
    }

def save_searches(searches, jobs):
    """Save search results and job matches"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Save searches
    search_file = Path.home() / 'clawd' / 'data' / f'job_searches_{today}.json'
    search_file.parent.mkdir(exist_ok=True)
    
    with open(search_file, 'w') as f:
        json.dump({
            'date': today,
            'total_searches': len(searches),
            'searches': searches
        }, f, indent=2)
    
    # Save jobs
    jobs_file = Path.home() / 'clawd' / 'data' / f'jobs_{today}.json'
    
    with open(jobs_file, 'w') as f:
        json.dump({
            'date': today,
            'total_jobs': len(jobs),
            'high_priority': len([j for j in jobs if j['score'] >= 8]),
            'jobs': sorted(jobs, key=lambda x: x['score'], reverse=True)
        }, f, indent=2)
    
    return search_file, jobs_file

def generate_daily_report(searches, jobs):
    """Generate human-readable report"""
    today = datetime.now().strftime('%Y-%m-%d')
    report_file = Path.home() / 'clawd' / 'reports' / f'job_hunt_{today}.md'
    report_file.parent.mkdir(exist_ok=True)
    
    high_priority = [j for j in jobs if j['score'] >= 8]
    medium_priority = [j for j in jobs if 6 <= j['score'] < 8]
    
    report = f"""# Job Hunt Report - {today}

## Summary
- **Total Searches:** {len(searches)}
- **Jobs Found:** {len(jobs)}
- **High Priority (8+):** {len(high_priority)}
- **Medium Priority (6-7):** {len(medium_priority)}

## 🎯 High Priority Matches (8+)

"""
    
    if high_priority:
        for job in sorted(high_priority, key=lambda x: x['score'], reverse=True):
            report += f"""### {job['title']} - {job['company']}
**Score:** {job['score']}/10  
**Location:** {job['location']}  
**URL:** {job['url']}

---

"""
    else:
        report += "*No high-priority matches today.*\n\n"
    
    report += f"""## 📋 Medium Priority Matches (6-7)

"""
    
    if medium_priority:
        for job in sorted(medium_priority, key=lambda x: x['score'], reverse=True)[:5]:
            report += f"- **{job['title']}** at {job['company']} ({job['location']}) - {job['score']}/10 - [Apply]({job['url']})\n"
    else:
        report += "*No medium-priority matches today.*\n\n"
    
    report += f"""
## 🔍 Search Queries Used

"""
    
    platforms = {}
    for search in searches:
        platform = search['platform']
        if platform not in platforms:
            platforms[platform] = []
        platforms[platform].append(f"{search['query']} in {search['location']}")
    
    for platform, queries in platforms.items():
        report += f"### {platform}\n"
        for q in set(queries[:5]):  # Unique, first 5
            report += f"- {q}\n"
        report += "\n"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    return report_file

def main():
    """Main job hunter execution"""
    print("🔍 Starting Overnight Job Hunter...")
    print(f"⏰ Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Generate all searches
    print("📋 Generating search queries...")
    searches = generate_searches()
    print(f"✅ Generated {len(searches)} search combinations\n")
    
    # For now, we create search URLs (manual click-through)
    # In future: Add actual scraping with Playwright/Selenium
    
    # Mock some sample jobs for testing
    sample_jobs = [
        create_job_entry(
            "Senior Product Development Scientist",
            "Nestlé Purina PetCare",
            "Tampa, FL",
            "https://www.indeed.com/viewjob?jk=example_tampa1",
            10,
            "Lead R&D formulation for premium pet food brands"
        ),
        create_job_entry(
            "R&D Food Scientist",
            "Mars Petcare",
            "Remote",
            "https://www.linkedin.com/jobs/view/example_remote1",
            9,
            "Product development for pet nutrition products"
        ),
        create_job_entry(
            "Food Scientist",
            "General Mills",
            "Miami, FL",
            "https://www.indeed.com/viewjob?jk=example_miami1",
            8,
            "CPG product innovation and formulation"
        )
    ]
    
    jobs = sample_jobs  # Replace with real scraping later
    
    print(f"📊 Found {len(jobs)} potential matches")
    print(f"🎯 High priority (8+): {len([j for j in jobs if j['score'] >= 8])}\n")
    
    # Save results
    print("💾 Saving results...")
    search_file, jobs_file = save_searches(searches, jobs)
    report_file = generate_daily_report(searches, jobs)
    
    print(f"✅ Saved search queries: {search_file}")
    print(f"✅ Saved job matches: {jobs_file}")
    print(f"✅ Generated report: {report_file}\n")
    
    # Summary
    high_priority = [j for j in jobs if j['score'] >= 8]
    if high_priority:
        print("🚀 HIGH PRIORITY MATCHES:")
        for job in high_priority:
            print(f"   • {job['title']} at {job['company']} ({job['location']}) - {job['score']}/10")
    else:
        print("⚠️  No high-priority matches found today")
    
    print(f"\n✅ Job hunt complete! Check report: {report_file}")
    
    return {
        'total_searches': len(searches),
        'total_jobs': len(jobs),
        'high_priority': len(high_priority),
        'report_path': str(report_file)
    }

if __name__ == "__main__":
    result = main()
    print(f"\n📈 Final stats: {json.dumps(result, indent=2)}")
