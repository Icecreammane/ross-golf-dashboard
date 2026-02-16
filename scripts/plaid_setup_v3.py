#!/usr/bin/env python3
"""
Plaid Setup - Direct API approach
Bypassing SDK issues with direct HTTP requests
"""

import os
import json
import requests
import webbrowser

CREDENTIALS_FILE = os.path.expanduser("~/.clawdbot/credentials/plaid.json")
PLAID_SANDBOX_URL = "https://sandbox.plaid.com"

def load_credentials():
    with open(CREDENTIALS_FILE, 'r') as f:
        return json.load(f)

def create_link_token_direct(creds):
    """Create link token via direct API call"""
    url = f"{PLAID_SANDBOX_URL}/link/token/create"
    
    payload = {
        "client_id": creds['client_id'],
        "secret": creds['secret'],
        "client_name": "Ross Spending Tracker",
        "country_codes": ["US"],
        "language": "en",
        "user": {
            "client_user_id": "ross-spending-tracker"
        },
        "products": ["transactions"]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"📡 Sending request to: {url}")
    print(f"Client ID: {creds['client_id'][:10]}...")
    
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        return response.json()['link_token']
    else:
        print(f"❌ Error: {response.text}")
        return None

def main():
    print("🏦 Plaid Setup (Direct API)")
    print("=" * 50)
    
    creds = load_credentials()
    print(f"\nClient ID: {creds['client_id']}")
    print(f"Secret: {creds['secret'][:10]}...")
    
    link_token = create_link_token_direct(creds)
    
    if link_token:
        print(f"\n✅ Link token created: {link_token[:30]}...")
        link_url = f"https://cdn.plaid.com/link/v2/stable/link.html?isWebview=false&token={link_token}"
        print(f"Opening: {link_url}")
        webbrowser.open(link_url)
        print("\n✅ Browser opened! Connect your accounts.")
        print("\nFor sandbox, use Plaid's test credentials")
        print("  See: https://plaid.com/docs/sandbox/test-credentials/")
    else:
        print("❌ Failed")

if __name__ == "__main__":
    main()
