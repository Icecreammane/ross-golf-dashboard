#!/usr/bin/env python3
"""
Plaid Account Connection Setup (Modern SDK v38+)
Fixed for newer Plaid API authentication
"""

import os
import json
import webbrowser
from datetime import datetime
import plaid
from plaid import api_client, models
from plaid.api import plaid_api

CREDENTIALS_FILE = os.path.expanduser("~/.clawdbot/credentials/plaid.json")
TOKENS_FILE = os.path.expanduser("~/.clawdbot/credentials/plaid_tokens.json")

def load_credentials():
    """Load Plaid API credentials"""
    if not os.path.exists(CREDENTIALS_FILE):
        print("❌ Plaid credentials not found!")
        return None
    
    with open(CREDENTIALS_FILE, 'r') as f:
        return json.load(f)

def get_plaid_client(creds):
    """Initialize Plaid API client (Modern SDK)"""
    # Map environment to host
    if creds['environment'] == 'sandbox':
        host = plaid.Environment.Sandbox
    elif creds['environment'] == 'development':
        host = plaid.Environment.Development
    else:
        host = plaid.Environment.Production
    
    # Modern configuration
    configuration = plaid.Configuration(
        host=host,
        api_key={
            'clientId': creds['client_id'],
            'secret': creds['secret']
        }
    )
    
    api_client_instance = api_client.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client_instance)
    
    return client

def create_link_token(client):
    """Generate Plaid Link token"""
    try:
        request = models.LinkTokenCreateRequest(
            products=[models.Products('transactions')],
            client_name="Ross Spending Tracker",
            country_codes=[models.CountryCode('US')],
            language='en',
            user=models.LinkTokenCreateRequestUser(
                client_user_id='ross-spending-tracker'
            )
        )
        
        response = client.link_token_create(request)
        return response['link_token']
    
    except plaid.ApiException as e:
        print(f"❌ Plaid API Error: {e}")
        print(f"Response body: {e.body}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🏦 Plaid Setup (Modern SDK)")
    print("=" * 50)
    
    creds = load_credentials()
    if not creds:
        return
    
    print(f"\nUsing environment: {creds['environment']}")
    print(f"Client ID: {creds['client_id'][:10]}...")
    
    client = get_plaid_client(creds)
    
    print("\n📝 Creating Link token...")
    link_token = create_link_token(client)
    
    if link_token:
        print(f"✅ Link token created!")
        link_url = f"https://cdn.plaid.com/link/v2/stable/link.html?isWebview=false&token={link_token}"
        print(f"\n🌐 Opening Plaid Link...")
        print(f"URL: {link_url}")
        webbrowser.open(link_url)
        print("\n✅ Browser opened! Follow the prompts to connect your accounts.")
    else:
        print("❌ Failed to create link token")

if __name__ == "__main__":
    main()
