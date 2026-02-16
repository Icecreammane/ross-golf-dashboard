#!/usr/bin/env python3
"""Scrape job listings from Indeed and LinkedIn"""
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_indeed_jobs(query, location, days=7):
    """Scrape Indeed for jobs"""
    jobs = []
    
    # Indeed job search URL
    base_url = "https://www.indeed.com/jobs"
    params = {
        'q': query,
        'l': location,
        'fromage': days  # Posted in last N days
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find job cards
        job_cards = soup.find_all('div', class_='job_seen_beacon')
        
        for card in job_cards[:10]:  # First 10 results
            try:
                title_elem = card.find('h2', class_='jobTitle')
                company_elem = card.find('span', class_='companyName')
                location_elem = card.find('div', class_='companyLocation')
                
                if title_elem and company_elem:
                    # Extract job ID from link
                    link = title_elem.find('a')
                    job_id = link.get('data-jk', '') if link else ''
                    
                    job = {
                        'title': title_elem.get_text(strip=True),
                        'company': company_elem.get_text(strip=True),
                        'location': location_elem.get_text(strip=True) if location_elem else location,
                        'url': f"https://www.indeed.com/viewjob?jk={job_id}" if job_id else '',
                        'source': 'Indeed'
                    }
                    jobs.append(job)
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error scraping Indeed: {e}")
    
    return jobs

def scrape_linkedin_jobs(query, location):
    """Scrape LinkedIn for jobs (limited without auth)"""
    jobs = []
    
    # LinkedIn job search URL
    base_url = "https://www.linkedin.com/jobs/search"
    params = {
        'keywords': query,
        'location': location,
        'f_TPR': 'r86400',  # Last 24 hours
        'position': 1,
        'pageNum': 0
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # LinkedIn structure varies, try to find job cards
        job_cards = soup.find_all('div', class_='base-card')
        
        for card in job_cards[:10]:
            try:
                title_elem = card.find('h3', class_='base-search-card__title')
                company_elem = card.find('h4', class_='base-search-card__subtitle')
                location_elem = card.find('span', class_='job-search-card__location')
                link_elem = card.find('a', class_='base-card__full-link')
                
                if title_elem and company_elem and link_elem:
                    job = {
                        'title': title_elem.get_text(strip=True),
                        'company': company_elem.get_text(strip=True),
                        'location': location_elem.get_text(strip=True) if location_elem else location,
                        'url': link_elem.get('href', ''),
                        'source': 'LinkedIn'
                    }
                    jobs.append(job)
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error scraping LinkedIn: {e}")
    
    return jobs

if __name__ == "__main__":
    print("🔍 Searching for Food Science jobs in Tampa, FL...\n")
    
    # Search queries
    queries = [
        "food scientist",
        "product development scientist",
        "R&D scientist food",
        "senior food scientist"
    ]
    
    all_jobs = []
    
    for query in queries:
        print(f"Searching: {query}")
        indeed_jobs = scrape_indeed_jobs(query, "Tampa, FL", days=7)
        all_jobs.extend(indeed_jobs)
    
    # Deduplicate by URL
    unique_jobs = []
    seen_urls = set()
    
    for job in all_jobs:
        if job['url'] and job['url'] not in seen_urls:
            seen_urls.add(job['url'])
            unique_jobs.append(job)
    
    # Save to JSON
    output = {
        'search_date': datetime.now().isoformat(),
        'location': 'Tampa, FL',
        'total_jobs': len(unique_jobs),
        'jobs': unique_jobs
    }
    
    output_file = '/Users/clawdbot/clawd/data/tampa_jobs.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Found {len(unique_jobs)} unique jobs")
    print(f"📁 Saved to: {output_file}\n")
    
    # Print top 5
    print("Top 5 Results:")
    for i, job in enumerate(unique_jobs[:5], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   URL: {job['url']}")
