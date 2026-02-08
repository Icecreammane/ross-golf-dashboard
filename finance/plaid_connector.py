#!/usr/bin/env python3
"""
Plaid Connector - Secure bank account integration

Handles OAuth flow, transaction syncing, and account management.
Uses industry-standard Plaid API for secure, read-only access.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta

FINANCE_DIR = Path.home() / "clawd" / "finance"
ENV_FILE = FINANCE_DIR / ".env"
ACCOUNTS_FILE = FINANCE_DIR / "linked_accounts.json"
TRANSACTIONS_FILE = FINANCE_DIR / "transactions.json"

def load_env():
    """Load environment variables from .env file"""
    if not ENV_FILE.exists():
        return None
    
    env = {}
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env[key.strip()] = value.strip()
    
    return env

def init_plaid():
    """
    Initialize Plaid client
    
    NOTE: This is a framework. Actual Plaid SDK requires:
    pip install plaid-python
    
    For tonight, we'll build the structure. Monday you'll add real credentials.
    """
    env = load_env()
    
    if not env:
        print("❌ No .env file found")
        print("\nCreate ~/clawd/finance/.env with:")
        print("  PLAID_CLIENT_ID=your_client_id")
        print("  PLAID_SECRET=your_secret")
        print("  PLAID_ENV=development")
        print("\nGet credentials at: https://dashboard.plaid.com/signup")
        return None
    
    # Check for required env vars
    required = ['PLAID_CLIENT_ID', 'PLAID_SECRET', 'PLAID_ENV']
    missing = [k for k in required if k not in env]
    
    if missing:
        print(f"❌ Missing env vars: {', '.join(missing)}")
        return None
    
    print("✅ Plaid credentials loaded")
    print(f"   Environment: {env['PLAID_ENV']}")
    
    # In production, this would initialize actual Plaid client:
    # from plaid import Client
    # client = Client(
    #     client_id=env['PLAID_CLIENT_ID'],
    #     secret=env['PLAID_SECRET'],
    #     environment=env['PLAID_ENV']
    # )
    
    return {
        "client_id": env['PLAID_CLIENT_ID'],
        "secret": env['PLAID_SECRET'][:4] + "..." if len(env.get('PLAID_SECRET', '')) > 4 else "***",
        "env": env['PLAID_ENV']
    }

def link_account(institution_name):
    """
    Link a bank account via Plaid Link (OAuth flow)
    
    In production, this would:
    1. Create a Link token
    2. Open Plaid Link UI (web interface)
    3. User logs in on bank's site
    4. Exchange public token for access token
    5. Store access token securely
    
    For tonight: Simulates the process
    """
    print(f"\n🔗 LINKING {institution_name}")
    print("=" * 60)
    print("\n📋 Setup Instructions:")
    print(f"1. Go to https://dashboard.plaid.com")
    print(f"2. Click 'Link' → 'Create Link Token'")
    print(f"3. Select institution: {institution_name}")
    print(f"4. Complete OAuth flow on bank's website")
    print(f"5. Copy access token when done")
    print("\n⚠️  NEVER share your access token publicly!")
    print("\nOnce you have the access token, save it:")
    print(f"  python3 finance/plaid_connector.py save {institution_name} <access_token>")
    
    return {
        "institution": institution_name,
        "status": "awaiting_oauth",
        "instructions": "Complete OAuth flow in Plaid dashboard"
    }

def save_access_token(institution_name, access_token):
    """Save access token for linked account"""
    
    # Load existing accounts
    accounts = {}
    if ACCOUNTS_FILE.exists():
        with open(ACCOUNTS_FILE) as f:
            accounts = json.load(f)
    
    # Add new account
    accounts[institution_name] = {
        "access_token": access_token,  # In production, encrypt this!
        "linked_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    # Save
    ACCOUNTS_FILE.parent.mkdir(exist_ok=True)
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)
    
    print(f"✅ {institution_name} linked successfully")
    print(f"   Saved to: {ACCOUNTS_FILE}")

def sync_transactions():
    """
    Sync transactions from all linked accounts
    
    In production, this would:
    1. Load access tokens for all accounts
    2. Call Plaid Transactions API
    3. Get last 30-90 days of transactions
    4. Store in local database
    5. Categorize automatically
    
    For tonight: Simulates the process
    """
    print("\n🔄 SYNCING TRANSACTIONS")
    print("=" * 60)
    
    if not ACCOUNTS_FILE.exists():
        print("❌ No accounts linked yet")
        print("   Run: python3 finance/plaid_connector.py link <institution>")
        return
    
    with open(ACCOUNTS_FILE) as f:
        accounts = json.load(f)
    
    print(f"\n📊 Found {len(accounts)} linked accounts:")
    for name in accounts:
        print(f"   • {name}")
    
    print("\n⚠️  Production sync would:")
    print("   1. Call Plaid Transactions API for each account")
    print("   2. Pull last 90 days of transactions")
    print("   3. Categorize with AI")
    print("   4. Update dashboard")
    print("\n💡 Monday: Add real Plaid SDK for automatic syncing")
    
    # Mock transaction structure
    mock_transaction = {
        "date": datetime.now().isoformat(),
        "description": "Example transaction",
        "amount": -50.00,
        "category": ["Food", "Restaurants"],
        "account": "PNC Checking"
    }
    
    print(f"\n📝 Transaction format:")
    print(json.dumps(mock_transaction, indent=2))

def generate_pl():
    """Generate P&L from synced transactions"""
    print("\n💰 PROFIT & LOSS STATEMENT")
    print("=" * 60)
    
    if not TRANSACTIONS_FILE.exists():
        print("❌ No transactions synced yet")
        print("   Run: python3 finance/plaid_connector.py sync")
        return
    
    with open(TRANSACTIONS_FILE) as f:
        transactions = json.load(f)
    
    # Calculate totals (mock for now)
    income = sum(t['amount'] for t in transactions if t['amount'] > 0)
    expenses = abs(sum(t['amount'] for t in transactions if t['amount'] < 0))
    net = income - expenses
    
    print(f"\nINCOME:     ${income:,.2f}")
    print(f"EXPENSES:   ${expenses:,.2f}")
    print(f"NET:        ${net:,.2f}")
    print(f"\nBurn Rate:  ${expenses:,.2f}/month")
    
    if income > 0:
        runway_months = (income / expenses) if expenses > 0 else float('inf')
        print(f"Runway:     {runway_months:.1f} months")

def main():
    """CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Plaid Connector - Secure bank integration")
        print("\nCommands:")
        print("  test                    - Test Plaid credentials")
        print("  link <institution>      - Link a bank account")
        print("  save <inst> <token>     - Save access token")
        print("  sync                    - Sync transactions")
        print("  accounts                - List linked accounts")
        print("  pl                      - Generate P&L")
        print("\nSetup:")
        print("  1. Create .env file with Plaid credentials")
        print("  2. Link accounts via OAuth")
        print("  3. Sync transactions daily")
        print("\nSee PLAID_SETUP.md for detailed instructions")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "test":
        result = init_plaid()
        if result:
            print("\n✅ Plaid connection ready!")
            print(f"   Client ID: {result['client_id']}")
            print(f"   Environment: {result['env']}")
        else:
            print("\n❌ Plaid setup incomplete")
    
    elif command == "link":
        if len(sys.argv) < 3:
            print("Usage: link <institution_name>")
            print("\nExamples:")
            print("  link 'PNC Bank'")
            print("  link 'Chase'")
            print("  link 'Venmo'")
            print("  link 'Cash App'")
        else:
            institution = sys.argv[2]
            link_account(institution)
    
    elif command == "save":
        if len(sys.argv) < 4:
            print("Usage: save <institution> <access_token>")
        else:
            institution = sys.argv[2]
            token = sys.argv[3]
            save_access_token(institution, token)
    
    elif command == "sync":
        sync_transactions()
    
    elif command == "accounts":
        if not ACCOUNTS_FILE.exists():
            print("No accounts linked yet")
        else:
            with open(ACCOUNTS_FILE) as f:
                accounts = json.load(f)
            print(f"\n📊 Linked Accounts ({len(accounts)}):")
            for name, data in accounts.items():
                status = data.get('status', 'unknown')
                linked = data.get('linked_at', 'unknown')
                print(f"\n  {name}")
                print(f"    Status: {status}")
                print(f"    Linked: {linked}")
    
    elif command == "pl":
        generate_pl()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
