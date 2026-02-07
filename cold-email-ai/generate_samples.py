#!/usr/bin/env python3
"""
Generate sample cold emails for testing
"""

import json
import requests
import time
from datetime import datetime

# Test companies
test_companies = [
    {
        "name": "Stripe",
        "url": "stripe.com",
        "context": "AI-powered fraud detection for payment processors"
    },
    {
        "name": "Shopify",
        "url": "shopify.com",
        "context": "Email marketing automation for e-commerce stores"
    },
    {
        "name": "Notion",
        "url": "notion.so",
        "context": "AI writing assistant integration for productivity tools"
    },
    {
        "name": "Figma",
        "url": "figma.com",
        "context": "AI-powered design feedback and collaboration tools"
    },
    {
        "name": "Linear",
        "url": "linear.app",
        "context": "Sprint analytics and velocity tracking for project management"
    }
]

def generate_email(company):
    """Generate email for a company"""
    try:
        response = requests.post(
            'http://localhost:3001/api/generate',
            json={
                'url': company['url'],
                'context': company['context']
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"HTTP {response.status_code}: {response.text}"}
    
    except Exception as e:
        return {'error': str(e)}

def main():
    print("🚀 Generating sample cold emails...\n")
    
    results = []
    
    for i, company in enumerate(test_companies, 1):
        print(f"[{i}/5] Generating email for {company['name']}...")
        
        result = generate_email(company)
        
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
            results.append({
                'company': company,
                'error': result['error']
            })
        else:
            print(f"   ✅ Success!")
            results.append({
                'company': company,
                'email': result['email'],
                'company_info': result.get('company_info', {})
            })
        
        # Save individual result
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"examples/{i}_{company['name'].lower()}_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write(f"# Cold Email Sample - {company['name']}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Target:** {company['url']}\n\n")
            f.write(f"**Context:** {company['context']}\n\n")
            f.write("---\n\n")
            
            if 'error' in result:
                f.write(f"**Error:** {result['error']}\n")
            else:
                f.write("## Generated Email\n\n")
                f.write(f"```\n{result['email']}\n```\n\n")
                f.write("## Company Info Extracted\n\n")
                f.write(f"- **Domain:** {result.get('company_info', {}).get('domain', 'N/A')}\n")
                f.write(f"- **Title:** {result.get('company_info', {}).get('title', 'N/A')}\n")
        
        print(f"   📄 Saved to {filename}\n")
        
        # Rate limiting - be nice to OpenAI API
        if i < len(test_companies):
            time.sleep(2)
    
    # Save summary
    with open('examples/SUMMARY.md', 'w') as f:
        f.write("# Cold Email Generation Test Results\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Tests:** {len(test_companies)}\n")
        f.write(f"**Successful:** {sum(1 for r in results if 'email' in r)}\n")
        f.write(f"**Failed:** {sum(1 for r in results if 'error' in r)}\n\n")
        
        f.write("## Results\n\n")
        for i, result in enumerate(results, 1):
            company = result['company']
            status = "✅ Success" if 'email' in result else f"❌ Failed: {result.get('error', 'Unknown error')}"
            f.write(f"{i}. **{company['name']}** ({company['url']}) - {status}\n")
        
        f.write("\n## Quality Assessment\n\n")
        f.write("Review individual files for full emails and quality evaluation.\n")
    
    print("=" * 60)
    print(f"✅ Generated {len(results)} sample emails")
    print(f"📁 Saved to examples/ directory")
    print("=" * 60)

if __name__ == '__main__':
    main()
