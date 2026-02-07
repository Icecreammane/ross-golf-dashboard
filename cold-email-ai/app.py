#!/usr/bin/env python3
"""
Cold Email AI Platform - MVP
Generates personalized cold emails from company URLs
"""

import os
import re
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import openai
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

# OpenAI API key from environment
openai.api_key = os.getenv('OPENAI_API_KEY')

def extract_domain(url):
    """Extract clean domain from URL"""
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    return domain.replace('www.', '')

def scrape_company_info(url):
    """Scrape basic company information from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text() if title else ''
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''
        
        # Extract first few paragraphs of text
        paragraphs = soup.find_all('p')
        text_content = ' '.join([p.get_text() for p in paragraphs[:5]])
        
        # Clean up text
        text_content = re.sub(r'\s+', ' ', text_content).strip()[:1000]
        
        return {
            'domain': extract_domain(url),
            'title': title_text,
            'description': description,
            'content': text_content
        }
    except Exception as e:
        return {
            'domain': extract_domain(url),
            'title': '',
            'description': '',
            'content': '',
            'error': str(e)
        }

def generate_cold_email(company_info, user_context=''):
    """Generate personalized cold email using OpenAI"""
    
    prompt = f"""You are an expert cold email writer. Generate a personalized, compelling cold email based on the company information below.

Company Domain: {company_info['domain']}
Company Title: {company_info['title']}
Description: {company_info['description']}
Website Content: {company_info['content']}

Additional Context: {user_context or 'Offering AI/automation consulting services'}

Write a cold email that:
- Is personalized to this specific company
- Highlights a relevant pain point or opportunity
- Keeps it under 150 words
- Has a clear, low-friction CTA
- Sounds human and conversational (not salesy)
- Includes a compelling subject line

Format:
Subject: [subject line]

[email body]

Generate ONLY the email. Be specific to this company."""

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert cold email copywriter who writes highly personalized, effective outreach emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        email_content = response.choices[0].message.content
        return email_content
    
    except Exception as e:
        return f"Error generating email: {str(e)}"

@app.route('/')
def index():
    """Main app page"""
    return render_template('index.html')

@app.route('/landing')
def landing():
    """Landing page"""
    return render_template('landing.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    """API endpoint to generate cold email"""
    data = request.json
    url = data.get('url', '').strip()
    context = data.get('context', '')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Scrape company info
    company_info = scrape_company_info(url)
    
    # Generate email
    email = generate_cold_email(company_info, context)
    
    return jsonify({
        'email': email,
        'company_info': company_info
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Cold Email AI is running'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
