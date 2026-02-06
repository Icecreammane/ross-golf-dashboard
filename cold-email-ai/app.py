#!/usr/bin/env python3
"""
Cold Email AI Platform
Flask app that generates personalized cold emails from company URLs
"""

from flask import Flask, render_template, request, jsonify
import os
import requests
from bs4 import BeautifulSoup
import json
import re

app = Flask(__name__)

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

def fetch_company_info(url):
    """Fetch and extract basic company info from URL"""
    try:
        # Clean URL
        if not url.startswith('http'):
            url = 'https://' + url
        
        # Fetch page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract key information
        title = soup.find('title')
        title = title.get_text() if title else ''
        
        # Get meta description
        description = soup.find('meta', attrs={'name': 'description'})
        if not description:
            description = soup.find('meta', attrs={'property': 'og:description'})
        description = description.get('content', '') if description else ''
        
        # Get headings for context
        headings = []
        for h in soup.find_all(['h1', 'h2'], limit=5):
            text = h.get_text().strip()
            if text and len(text) > 3:
                headings.append(text)
        
        # Get some body text
        paragraphs = []
        for p in soup.find_all('p', limit=10):
            text = p.get_text().strip()
            if len(text) > 50:
                paragraphs.append(text)
        
        return {
            'success': True,
            'url': url,
            'title': title,
            'description': description,
            'headings': headings[:3],
            'content_sample': ' '.join(paragraphs[:3])[:500]
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def generate_email_with_openai(company_info):
    """Generate personalized cold email using OpenAI API"""
    if not OPENAI_API_KEY:
        # Return mock email if no API key
        return generate_mock_email(company_info)
    
    try:
        prompt = f"""You are an expert cold email writer. Based on the following company information, write a personalized, compelling cold email.

Company URL: {company_info['url']}
Company Title: {company_info['title']}
Description: {company_info['description']}
Key Topics: {', '.join(company_info['headings'])}

Write a cold email that:
1. Shows you've researched the company
2. Identifies a specific pain point or opportunity
3. Offers clear value proposition
4. Has a soft call-to-action
5. Is under 150 words
6. Feels personal, not generic

Format:
Subject: [subject line]

[email body]

Return ONLY the subject and email body, no other commentary."""

        # Call OpenAI API
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-4',
            'messages': [
                {'role': 'system', 'content': 'You are an expert cold email copywriter.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 400
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        email_text = result['choices'][0]['message']['content']
        
        # Parse subject and body
        lines = email_text.split('\n')
        subject = ''
        body = []
        
        for line in lines:
            if line.startswith('Subject:'):
                subject = line.replace('Subject:', '').strip()
            elif line.strip() and not line.startswith('[') and not line.startswith('Subject'):
                body.append(line)
        
        return {
            'success': True,
            'subject': subject or 'Quick question about ' + company_info['title'].split('-')[0].strip(),
            'body': '\n'.join(body).strip()
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def generate_mock_email(company_info):
    """Generate mock email when OpenAI API is not available"""
    company_name = company_info['title'].split('-')[0].split('|')[0].strip()
    
    subject = f"Loved what I saw on {company_name}"
    
    body = f"""Hi there,

I was just browsing {company_name}'s website and noticed you're focused on {company_info['headings'][0] if company_info['headings'] else 'innovation'}.

I work with companies like yours to help them streamline their outreach and close more deals using AI-powered personalization.

Would love to show you a quick 10-minute demo of how we've helped similar companies increase response rates by 3x.

Worth a quick call?

Best,
[Your Name]

---
⚠️ DEMO MODE: This is a mock email. Add your OpenAI API key to generate AI-powered emails.
Set environment variable: export OPENAI_API_KEY=your_key_here"""
    
    return {
        'success': True,
        'subject': subject,
        'body': body,
        'is_mock': True
    }

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/app')
def app_page():
    """Main app interface"""
    return render_template('app.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    """API endpoint to generate cold email"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'Please provide a company URL'
            }), 400
        
        # Fetch company info
        company_info = fetch_company_info(url)
        
        if not company_info['success']:
            return jsonify({
                'success': False,
                'error': f"Couldn't fetch company info: {company_info['error']}"
            }), 400
        
        # Generate email
        email_result = generate_email_with_openai(company_info)
        
        if not email_result['success']:
            return jsonify({
                'success': False,
                'error': f"Couldn't generate email: {email_result['error']}"
            }), 500
        
        return jsonify({
            'success': True,
            'company': {
                'name': company_info['title'].split('-')[0].strip(),
                'url': company_info['url']
            },
            'email': {
                'subject': email_result['subject'],
                'body': email_result['body']
            },
            'is_mock': email_result.get('is_mock', False)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'openai_configured': bool(OPENAI_API_KEY)
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3001))
    print(f"\n🚀 Cold Email AI Platform")
    print(f"🌐 Running on http://localhost:{port}")
    print(f"🤖 OpenAI API: {'Configured ✅' if OPENAI_API_KEY else 'Not configured (using mock mode) ⚠️'}")
    print(f"\nPress CTRL+C to quit\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)
