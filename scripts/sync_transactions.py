#!/usr/bin/env python3
"""
Transaction Sync System
Pulls transactions from Plaid, deduplicates, categorizes, and stores locally
"""

import os
import json
from datetime import datetime, timedelta
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
import plaid
from plaid.api_client import ApiClient
from plaid.configuration import Configuration

CREDENTIALS_FILE = os.path.expanduser("~/.clawdbot/credentials/plaid.json")
TOKENS_FILE = os.path.expanduser("~/.clawdbot/credentials/plaid_tokens.json")
TRANSACTIONS_FILE = os.path.expanduser("~/clawd/data/transactions.json")
SYNC_STATE_FILE = os.path.expanduser("~/clawd/data/transaction_sync_state.json")

# Category mappings
CATEGORY_MAP = {
    'Dining Out': ['Food and Drink, Restaurants', 'Food and Drink, Fast Food', 'Food and Drink, Coffee'],
    'Groceries': ['Food and Drink, Groceries'],
    'Gas & Transportation': ['Transportation, Gas', 'Transportation, Taxi', 'Transportation, Public Transportation'],
    'Subscriptions': ['Service, Subscription', 'Recreation, Gyms and Fitness Centers'],
    'Shopping': ['Shops, Supermarkets and Groceries', 'Shops'],
    'Entertainment': ['Recreation, Entertainment', 'Recreation, Arts and Entertainment'],
}

def load_credentials():
    """Load Plaid API credentials"""
    with open(CREDENTIALS_FILE, 'r') as f:
        return json.load(f)

def load_tokens():
    """Load access tokens"""
    if not os.path.exists(TOKENS_FILE):
        return {}
    with open(TOKENS_FILE, 'r') as f:
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

def categorize_transaction(plaid_categories):
    """Map Plaid categories to Ross-relevant buckets"""
    if not plaid_categories:
        return 'Other'
    
    category_str = ', '.join(plaid_categories)
    
    for ross_category, patterns in CATEGORY_MAP.items():
        for pattern in patterns:
            if pattern.lower() in category_str.lower():
                return ross_category
    
    return 'Other'

def load_existing_transactions():
    """Load existing transactions from file"""
    if not os.path.exists(TRANSACTIONS_FILE):
        return []
    
    with open(TRANSACTIONS_FILE, 'r') as f:
        return json.load(f)

def load_sync_state():
    """Load last sync state"""
    if not os.path.exists(SYNC_STATE_FILE):
        return {}
    
    with open(SYNC_STATE_FILE, 'r') as f:
        return json.load(f)

def save_sync_state(state):
    """Save sync state"""
    os.makedirs(os.path.dirname(SYNC_STATE_FILE), exist_ok=True)
    with open(SYNC_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def save_transactions(transactions):
    """Save transactions to file"""
    os.makedirs(os.path.dirname(TRANSACTIONS_FILE), exist_ok=True)
    with open(TRANSACTIONS_FILE, 'w') as f:
        json.dump(transactions, f, indent=2)

def fetch_transactions(client, access_token, start_date, end_date):
    """Fetch transactions from Plaid"""
    try:
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions(
                count=500,
                offset=0
            )
        )
        
        response = client.transactions_get(request)
        transactions = response['transactions']
        
        # Handle pagination
        while len(transactions) < response['total_transactions']:
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date,
                options=TransactionsGetRequestOptions(
                    count=500,
                    offset=len(transactions)
                )
            )
            response = client.transactions_get(request)
            transactions.extend(response['transactions'])
        
        return transactions, response.get('accounts', [])
    
    except Exception as e:
        print(f"❌ Error fetching transactions: {e}")
        return [], []

def sync_all_accounts(initial_sync=False):
    """Sync transactions from all connected accounts"""
    print("🔄 Starting transaction sync...")
    
    # Load credentials and tokens
    creds = load_credentials()
    tokens = load_tokens()
    
    if not tokens:
        print("❌ No accounts connected. Run plaid_setup.py first.")
        return
    
    client = get_plaid_client(creds)
    
    # Determine date range
    sync_state = load_sync_state()
    
    if initial_sync or not sync_state:
        # Initial sync: last 30 days
        start_date = (datetime.now() - timedelta(days=30)).date()
        print(f"📅 Initial sync: {start_date} to today")
    else:
        # Incremental sync: since last sync
        last_sync = datetime.fromisoformat(sync_state.get('last_sync', datetime.now().isoformat()))
        start_date = (last_sync - timedelta(days=1)).date()  # Overlap by 1 day to catch updates
        print(f"📅 Incremental sync since {start_date}")
    
    end_date = datetime.now().date()
    
    # Load existing transactions
    existing_transactions = load_existing_transactions()
    existing_ids = {t['transaction_id'] for t in existing_transactions}
    
    new_count = 0
    account_names = {}
    
    # Fetch from each account
    for item_id, token_data in tokens.items():
        if not token_data.get('active', True):
            continue
        
        institution = token_data['institution']
        print(f"\n🏦 Fetching from {institution}...")
        
        transactions, accounts = fetch_transactions(
            client,
            token_data['access_token'],
            start_date,
            end_date
        )
        
        # Build account name map
        for account in accounts:
            account_names[account['account_id']] = f"{institution} {account.get('name', account.get('subtype', ''))}"
        
        # Process transactions
        for txn in transactions:
            txn_id = txn['transaction_id']
            
            if txn_id in existing_ids:
                # Update existing transaction (in case amount/status changed)
                for i, existing_txn in enumerate(existing_transactions):
                    if existing_txn['transaction_id'] == txn_id:
                        existing_transactions[i] = {
                            'transaction_id': txn_id,
                            'date': str(txn['date']),
                            'amount': -float(txn['amount']),  # Plaid uses negative for purchases
                            'merchant': txn.get('merchant_name') or txn.get('name', 'Unknown'),
                            'category': categorize_transaction(txn.get('category')),
                            'plaid_category': txn.get('category', []),
                            'account': account_names.get(txn['account_id'], institution),
                            'pending': txn.get('pending', False),
                            'updated_at': datetime.now().isoformat()
                        }
                        break
            else:
                # New transaction
                existing_transactions.append({
                    'transaction_id': txn_id,
                    'date': str(txn['date']),
                    'amount': -float(txn['amount']),
                    'merchant': txn.get('merchant_name') or txn.get('name', 'Unknown'),
                    'category': categorize_transaction(txn.get('category')),
                    'plaid_category': txn.get('category', []),
                    'account': account_names.get(txn['account_id'], institution),
                    'pending': txn.get('pending', False),
                    'synced_at': datetime.now().isoformat()
                })
                existing_ids.add(txn_id)
                new_count += 1
        
        print(f"   ✅ {len(transactions)} transactions fetched")
    
    # Sort by date (newest first)
    existing_transactions.sort(key=lambda x: x['date'], reverse=True)
    
    # Save transactions
    save_transactions(existing_transactions)
    
    # Update sync state
    save_sync_state({
        'last_sync': datetime.now().isoformat(),
        'total_transactions': len(existing_transactions),
        'accounts_synced': len([t for t in tokens.values() if t.get('active', True)])
    })
    
    print(f"\n✅ Sync complete!")
    print(f"   📊 {new_count} new transactions")
    print(f"   📊 {len(existing_transactions)} total transactions")
    print(f"   💾 Saved to {TRANSACTIONS_FILE}")

if __name__ == "__main__":
    import sys
    initial = '--initial' in sys.argv or '-i' in sys.argv
    sync_all_accounts(initial_sync=initial)
