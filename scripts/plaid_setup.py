#!/usr/bin/env python3
"""
Plaid Account Connection Setup
Generates Link token, opens browser for account connection, stores access tokens
"""

import os
import json
import webbrowser
from datetime import datetime
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
import plaid
from plaid.api_client import ApiClient
from plaid.configuration import Configuration

CREDENTIALS_FILE = os.path.expanduser("~/.clawdbot/credentials/plaid.json")
TOKENS_FILE = os.path.expanduser("~/.clawdbot/credentials/plaid_tokens.json")

def load_credentials():
    """Load Plaid API credentials"""
    if not os.path.exists(CREDENTIALS_FILE):
        print("❌ Plaid credentials not found!")
        print(f"Create {CREDENTIALS_FILE} with:")
        print(json.dumps({
            "client_id": "YOUR_CLIENT_ID",
            "secret": "YOUR_SECRET",
            "environment": "sandbox"  # or "development" or "production"
        }, indent=2))
        return None
    
    with open(CREDENTIALS_FILE, 'r') as f:
        return json.load(f)

def get_plaid_client(creds):
    """Initialize Plaid API client"""
    host = plaid.Environment.Sandbox
    if creds['environment'] == 'development':
        host = plaid.Environment.Development
    elif creds['environment'] == 'production':
        host = plaid.Environment.Production
    
    configuration = Configuration(
        host=host,
        api_key={
            'clientId': creds['client_id'],
            'secret': creds['secret'],
        }
    )
    
    api_client = ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)

def create_link_token(client, creds):
    """Generate Plaid Link token for account connection"""
    try:
        request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="Ross Spending Tracker",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id='ross-unique-id'
            )
        )
        response = client.link_token_create(request)
        return response['link_token']
    except Exception as e:
        print(f"❌ Error creating link token: {e}")
        return None

def exchange_public_token(client, public_token):
    """Exchange public token for access token"""
    try:
        request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        response = client.item_public_token_exchange(request)
        return response['access_token'], response['item_id']
    except Exception as e:
        print(f"❌ Error exchanging token: {e}")
        return None, None

def save_access_token(access_token, item_id, institution_name="Unknown"):
    """Save access token securely"""
    tokens = {}
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'r') as f:
            tokens = json.load(f)
    
    tokens[item_id] = {
        'access_token': access_token,
        'institution': institution_name,
        'connected_at': datetime.now().isoformat(),
        'active': True
    }
    
    os.makedirs(os.path.dirname(TOKENS_FILE), exist_ok=True)
    with open(TOKENS_FILE, 'w') as f:
        json.dump(tokens, f, indent=2)
    
    # Secure the file
    os.chmod(TOKENS_FILE, 0o600)
    print(f"✅ Access token saved for {institution_name}")

def interactive_setup():
    """Interactive setup flow"""
    print("🏦 Plaid Account Connection Setup")
    print("=" * 50)
    
    # Load credentials
    creds = load_credentials()
    if not creds:
        return
    
    client = get_plaid_client(creds)
    
    # Create link token
    print("\n📝 Creating Link token...")
    link_token = create_link_token(client, creds)
    if not link_token:
        return
    
    print(f"✅ Link token created: {link_token[:20]}...")
    
    # Generate Link URL
    if creds['environment'] == 'sandbox':
        link_url = f"https://cdn.plaid.com/link/v2/stable/link.html?isWebview=false&token={link_token}"
        print(f"\n🌐 Opening Plaid Link in browser...")
        print(f"Link URL: {link_url}")
        
        # For sandbox, provide instructions
        print("\n📌 SANDBOX MODE INSTRUCTIONS:")
        print("1. Browser will open with Plaid Link")
        print("2. Select any test institution (e.g., 'First Platypus Bank')")
        print("3. Use Plaid's test credentials (user_good / pass_good)")
        print("4. After connecting, you'll receive a public token")
        print("\nCopy the public token and paste it here when ready.")
        
        webbrowser.open(link_url)
        
        # Wait for public token
        public_token = input("\n🔑 Enter public token: ").strip()
        
    else:
        # Production/Development
        link_url = f"https://cdn.plaid.com/link/v2/stable/link.html?isWebview=false&token={link_token}"
        print(f"\n🌐 Opening Plaid Link: {link_url}")
        webbrowser.open(link_url)
        public_token = input("\n🔑 After connecting your account, paste the public token here: ").strip()
    
    if not public_token:
        print("❌ No public token provided")
        return
    
    # Exchange for access token
    print("\n🔄 Exchanging public token for access token...")
    access_token, item_id = exchange_public_token(client, public_token)
    
    if access_token:
        institution_name = input("\n🏦 Enter institution name (e.g., Chase, Venmo): ").strip() or "Unknown"
        save_access_token(access_token, item_id, institution_name)
        print(f"\n✅ Account connected successfully!")
        print(f"Item ID: {item_id}")
        print(f"Institution: {institution_name}")
        print("\n🎉 You can now run sync_transactions.py to pull transaction data")
    else:
        print("❌ Failed to exchange token")

def list_connected_accounts():
    """List all connected accounts"""
    if not os.path.exists(TOKENS_FILE):
        print("No accounts connected yet")
        return
    
    with open(TOKENS_FILE, 'r') as f:
        tokens = json.load(f)
    
    print("\n🏦 Connected Accounts:")
    print("=" * 50)
    for item_id, data in tokens.items():
        status = "✅ Active" if data.get('active', True) else "❌ Inactive"
        print(f"{status} {data['institution']} (Connected: {data['connected_at'][:10]})")
        print(f"   Item ID: {item_id}")
    print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        list_connected_accounts()
    else:
        interactive_setup()
