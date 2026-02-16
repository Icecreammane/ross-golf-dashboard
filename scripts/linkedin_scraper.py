#!/usr/bin/env python3
"""
LinkedIn Jobs Scraper
Scrapes linkedin.com/jobs/search for recent postings
Uses requests + BeautifulSoup (no Selenium)
"""
import requests
from bs4 import BeautifulSoup
import time
import random
import json
from urllib.parse import urlencode
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# User agent rotation to avoid detection
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
]

def get_random_headers():
    """Generate random headers to avoid bot detection"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

def build_search_url(keywords, location, posted_last_24h=True):
    """Build LinkedIn job search URL"""
    base_url = "https://www.linkedin.com/jobs/search"
    
    params = {
        'keywords': keywords,
        'location': location,
        'sortBy': 'DD'  # Date descending
    }
    
    if posted_last_24h:
        params['f_TPR'] = 'r86400'  # Last 24 hours
    
    url = f"{base_url}?{urlencode(params)}"
    return url

def scrape_linkedin_jobs(keywords, location, max_results=25, delay=2.0):
    """
    Scrape LinkedIn jobs for given search parameters
    
    Args:
        keywords: Job title or keywords to search
        location: Location string (e.g., "Tampa, Florida")
        max_results: Maximum number of jobs to return
        delay: Delay between requests in seconds
        
    Returns:
        List of job dictionaries
    """
    url = build_search_url(keywords, location)
    logger.info(f"Searching LinkedIn: {keywords} in {location}")
    logger.info(f"URL: {url}")
    
    jobs = []
    
    try:
        # Add random delay before request
        time.sleep(delay + random.uniform(0, 1))
        
        # Make request with headers
        response = requests.get(url, headers=get_random_headers(), timeout=15)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find job cards - LinkedIn uses <li> with class containing "job"
        # Structure changes frequently, so we'll try multiple selectors
        job_cards = []
        
        # Try primary selector
        job_cards = soup.find_all('li', class_=lambda x: x and 'job' in x.lower())
        
        if not job_cards:
            # Try alternative selector
            job_cards = soup.find_all('div', class_=lambda x: x and 'job-search-card' in x.lower())
        
        if not job_cards:
            # Try base-card selector
            job_cards = soup.find_all('div', class_=lambda x: x and 'base-card' in x.lower())
        
        logger.info(f"Found {len(job_cards)} job cards")
        
        for card in job_cards[:max_results]:
            try:
                job = parse_job_card(card)
                if job and is_valid_job(job):
                    jobs.append(job)
            except Exception as e:
                logger.warning(f"Error parsing job card: {e}")
                continue
        
        logger.info(f"Successfully parsed {len(jobs)} jobs from LinkedIn")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error for LinkedIn search: {e}")
    except Exception as e:
        logger.error(f"Unexpected error scraping LinkedIn: {e}")
    
    return jobs

def parse_job_card(card):
    """Parse a LinkedIn job card into structured data"""
    job = {
        'title': None,
        'company': None,
        'location': None,
        'url': None,
        'description': None,
        'source': 'linkedin'
    }
    
    # Extract title
    title_elem = card.find('h3') or card.find('a', class_=lambda x: x and 'job-card-list__title' in x.lower())
    if title_elem:
        job['title'] = title_elem.get_text(strip=True)
    
    # Extract company
    company_elem = card.find('h4') or card.find('a', class_=lambda x: x and 'company' in x.lower())
    if not company_elem:
        company_elem = card.find('span', class_=lambda x: x and 'company' in x.lower())
    if company_elem:
        job['company'] = company_elem.get_text(strip=True)
    
    # Extract location
    location_elem = card.find('span', class_=lambda x: x and 'location' in x.lower())
    if location_elem:
        job['location'] = location_elem.get_text(strip=True)
    
    # Extract URL
    link_elem = card.find('a', href=True)
    if link_elem:
        href = link_elem['href']
        # Ensure full URL
        if href.startswith('http'):
            job['url'] = href.split('?')[0]  # Remove tracking params
        else:
            job['url'] = f"https://www.linkedin.com{href.split('?')[0]}"
    
    # Extract description snippet (if available)
    desc_elem = card.find('p') or card.find('div', class_=lambda x: x and 'description' in x.lower())
    if desc_elem:
        job['description'] = desc_elem.get_text(strip=True)[:500]
    
    return job

def is_valid_job(job):
    """Check if job has minimum required fields"""
    return job.get('title') and job.get('company') and job.get('url')

def search_linkedin_multiple(queries, delay_between_searches=3.0):
    """
    Run multiple LinkedIn searches
    
    Args:
        queries: List of dicts with 'keywords' and 'location'
        delay_between_searches: Seconds to wait between searches
        
    Returns:
        List of all jobs found (deduplicated by URL)
    """
    all_jobs = []
    seen_urls = set()
    
    for i, query in enumerate(queries):
        logger.info(f"Search {i+1}/{len(queries)}: {query['keywords']} in {query['location']}")
        
        jobs = scrape_linkedin_jobs(
            keywords=query['keywords'],
            location=query['location'],
            max_results=25,
            delay=delay_between_searches
        )
        
        # Deduplicate
        for job in jobs:
            if job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                all_jobs.append(job)
        
        # Random delay between searches
        if i < len(queries) - 1:
            time.sleep(delay_between_searches + random.uniform(0, 2))
    
    logger.info(f"Total unique jobs found: {len(all_jobs)}")
    return all_jobs

# Example usage
if __name__ == "__main__":
    # Test searches
    test_queries = [
        {'keywords': 'Product Development Scientist', 'location': 'Tampa, Florida'},
        {'keywords': 'Food Scientist', 'location': 'Miami, Florida'},
    ]
    
    jobs = search_linkedin_multiple(test_queries)
    
    print(f"\n✅ Found {len(jobs)} jobs:")
    for job in jobs[:5]:
        print(f"\n{job['title']} at {job['company']}")
        print(f"Location: {job['location']}")
        print(f"URL: {job['url']}")
    
    # Save to file
    with open('linkedin_test_results.json', 'w') as f:
        json.dump(jobs, f, indent=2)
    
    print(f"\n💾 Saved to linkedin_test_results.json")
