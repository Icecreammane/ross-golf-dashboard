#!/usr/bin/env python3
"""
Indeed Jobs Scraper
Scrapes indeed.com for recent job postings
Uses requests + BeautifulSoup (no Selenium)
"""
import requests
from bs4 import BeautifulSoup
import time
import random
import json
from urllib.parse import urlencode, quote
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# User agent rotation
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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://www.indeed.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

def build_search_url(query, location, days_ago=1, start=0):
    """
    Build Indeed search URL
    
    Args:
        query: Job title or keywords
        location: Location string (e.g., "Tampa, FL")
        days_ago: Filter by days since posted (1 = last 24h)
        start: Pagination offset
    """
    base_url = "https://www.indeed.com/jobs"
    
    params = {
        'q': query,
        'l': location,
        'fromage': str(days_ago),  # Days ago
        'sort': 'date',
        'start': start
    }
    
    url = f"{base_url}?{urlencode(params)}"
    return url

def scrape_indeed_jobs(query, location, max_results=25, delay=2.0):
    """
    Scrape Indeed jobs for given search parameters
    
    Args:
        query: Job title or keywords to search
        location: Location string (e.g., "Tampa, FL")
        max_results: Maximum number of jobs to return
        delay: Delay between requests in seconds
        
    Returns:
        List of job dictionaries
    """
    url = build_search_url(query, location, days_ago=1)
    logger.info(f"Searching Indeed: {query} in {location}")
    logger.info(f"URL: {url}")
    
    jobs = []
    
    try:
        # Add random delay before request
        time.sleep(delay + random.uniform(0, 1))
        
        # Make request with headers
        session = requests.Session()
        response = session.get(url, headers=get_random_headers(), timeout=15)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find job cards - Indeed uses various card structures
        # Try multiple selectors to be resilient to changes
        job_cards = []
        
        # Primary selector - mosaic cards
        job_cards = soup.find_all('div', class_=lambda x: x and 'job_seen_beacon' in x)
        
        if not job_cards:
            # Alternative - job card divs
            job_cards = soup.find_all('div', class_=lambda x: x and 'jobsearch' in x.lower() and 'card' in x.lower())
        
        if not job_cards:
            # Try table-based layout (older format)
            job_cards = soup.find_all('td', class_=lambda x: x and 'resultContent' in x)
        
        if not job_cards:
            # Last resort - any div with job data attributes
            job_cards = soup.find_all('div', attrs={'data-jk': True})
        
        logger.info(f"Found {len(job_cards)} job cards")
        
        for card in job_cards[:max_results]:
            try:
                job = parse_job_card(card)
                if job and is_valid_job(job):
                    jobs.append(job)
            except Exception as e:
                logger.warning(f"Error parsing job card: {e}")
                continue
        
        logger.info(f"Successfully parsed {len(jobs)} jobs from Indeed")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error for Indeed search: {e}")
    except Exception as e:
        logger.error(f"Unexpected error scraping Indeed: {e}")
    
    return jobs

def parse_job_card(card):
    """Parse an Indeed job card into structured data"""
    job = {
        'title': None,
        'company': None,
        'location': None,
        'url': None,
        'description': None,
        'source': 'indeed'
    }
    
    # Extract job key (ID) for URL
    job_key = card.get('data-jk') or card.get('data-job-id')
    if not job_key:
        # Try to find it in a child element
        key_elem = card.find('a', attrs={'data-jk': True})
        if key_elem:
            job_key = key_elem.get('data-jk')
    
    # Extract title
    title_elem = card.find('h2', class_=lambda x: x and 'jobTitle' in x)
    if not title_elem:
        title_elem = card.find('a', class_=lambda x: x and 'jcs-JobTitle' in x)
    if not title_elem:
        title_elem = card.find('span', attrs={'title': True})
    if title_elem:
        job['title'] = title_elem.get_text(strip=True)
    
    # Extract company
    company_elem = card.find('span', class_=lambda x: x and 'companyName' in x)
    if not company_elem:
        company_elem = card.find('span', attrs={'data-testid': 'company-name'})
    if not company_elem:
        company_elem = card.find('div', class_=lambda x: x and 'company' in x.lower())
    if company_elem:
        job['company'] = company_elem.get_text(strip=True)
    
    # Extract location
    location_elem = card.find('div', class_=lambda x: x and 'companyLocation' in x)
    if not location_elem:
        location_elem = card.find('div', attrs={'data-testid': 'text-location'})
    if not location_elem:
        location_elem = card.find('span', class_=lambda x: x and 'location' in x.lower())
    if location_elem:
        job['location'] = location_elem.get_text(strip=True)
    
    # Build URL
    if job_key:
        job['url'] = f"https://www.indeed.com/viewjob?jk={job_key}"
    else:
        # Try to find direct link
        link_elem = card.find('a', href=True)
        if link_elem:
            href = link_elem['href']
            if href.startswith('http'):
                job['url'] = href
            elif href.startswith('/'):
                job['url'] = f"https://www.indeed.com{href}"
    
    # Extract description snippet
    desc_elem = card.find('div', class_=lambda x: x and 'snippet' in x.lower())
    if not desc_elem:
        desc_elem = card.find('div', class_=lambda x: x and 'summary' in x.lower())
    if desc_elem:
        job['description'] = desc_elem.get_text(strip=True)[:500]
    
    return job

def is_valid_job(job):
    """Check if job has minimum required fields"""
    return job.get('title') and job.get('company') and job.get('url')

def search_indeed_multiple(queries, delay_between_searches=3.0):
    """
    Run multiple Indeed searches
    
    Args:
        queries: List of dicts with 'query' and 'location'
        delay_between_searches: Seconds to wait between searches
        
    Returns:
        List of all jobs found (deduplicated by URL)
    """
    all_jobs = []
    seen_urls = set()
    
    for i, search in enumerate(queries):
        logger.info(f"Search {i+1}/{len(queries)}: {search['query']} in {search['location']}")
        
        jobs = scrape_indeed_jobs(
            query=search['query'],
            location=search['location'],
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
        {'query': 'Product Development Scientist', 'location': 'Tampa, FL'},
        {'query': 'Food Scientist', 'location': 'Miami, FL'},
    ]
    
    jobs = search_indeed_multiple(test_queries)
    
    print(f"\n✅ Found {len(jobs)} jobs:")
    for job in jobs[:5]:
        print(f"\n{job['title']} at {job['company']}")
        print(f"Location: {job['location']}")
        print(f"URL: {job['url']}")
    
    # Save to file
    with open('indeed_test_results.json', 'w') as f:
        json.dump(jobs, f, indent=2)
    
    print(f"\n💾 Saved to indeed_test_results.json")
