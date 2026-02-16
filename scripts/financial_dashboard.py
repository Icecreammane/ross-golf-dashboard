#!/usr/bin/env python3
"""
Financial Dashboard with Plaid Integration
Real-time balance tracking, spending categorization, and budget alerts
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import plaid
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from flask import Flask, render_template_string, jsonify, request

# Configuration
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID', 'sandbox')
PLAID_SECRET = os.getenv('PLAID_SECRET', 'sandbox')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
DATA_DIR = Path(__file__).parent.parent / 'data'
FINANCIAL_DATA_PATH = DATA_DIR / 'financial_data.json'

# Initialize Plaid client
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox if PLAID_ENV == 'sandbox' else plaid.Environment.Production,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# Flask app
app = Flask(__name__)
app.secret_key = 'financial-dashboard-secret'

# Category mappings for spending
CATEGORY_MAPPINGS = {
    'Food and Drink': ['food', 'restaurant', 'grocery', 'coffee', 'bar'],
    'Transportation': ['gas', 'uber', 'lyft', 'parking', 'transit'],
    'Shopping': ['amazon', 'target', 'walmart', 'retail'],
    'Entertainment': ['movie', 'spotify', 'netflix', 'gaming'],
    'Bills': ['electric', 'water', 'internet', 'phone', 'insurance'],
    'Healthcare': ['pharmacy', 'doctor', 'hospital', 'medical'],
}

def load_financial_data():
    """Load financial data from JSON"""
    if FINANCIAL_DATA_PATH.exists():
        with open(FINANCIAL_DATA_PATH, 'r') as f:
            return json.load(f)
    return {
        'access_token': None,
        'accounts': [],
        'transactions': [],
        'last_sync': None,
        'budgets': {
            'Food and Drink': 500,
            'Transportation': 200,
            'Shopping': 300,
            'Entertainment': 100,
        }
    }

def save_financial_data(data):
    """Save financial data to JSON"""
    DATA_DIR.mkdir(exist_ok=True)
    with open(FINANCIAL_DATA_PATH, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def categorize_transaction(transaction):
    """Categorize a transaction based on name and category"""
    name = transaction.get('name', '').lower()
    categories = transaction.get('category', [])
    
    # Try to match based on transaction name
    for category, keywords in CATEGORY_MAPPINGS.items():
        if any(keyword in name for keyword in keywords):
            return category
    
    # Try to match based on Plaid categories
    if categories:
        main_category = categories[0] if categories else 'Other'
        if 'food' in main_category.lower():
            return 'Food and Drink'
        elif 'travel' in main_category.lower() or 'transport' in main_category.lower():
            return 'Transportation'
        elif 'shops' in main_category.lower():
            return 'Shopping'
        elif 'recreation' in main_category.lower():
            return 'Entertainment'
    
    return 'Other'

def sync_accounts():
    """Sync account balances from Plaid"""
    data = load_financial_data()
    
    if not data.get('access_token'):
        return {'error': 'No access token'}
    
    try:
        # Get accounts
        accounts_request = AccountsGetRequest(access_token=data['access_token'])
        accounts_response = client.accounts_get(accounts_request)
        
        accounts = []
        for account in accounts_response['accounts']:
            accounts.append({
                'id': account['account_id'],
                'name': account['name'],
                'type': account['type'],
                'subtype': account['subtype'],
                'balance': account['balances']['current'],
                'available': account['balances'].get('available'),
            })
        
        data['accounts'] = accounts
        data['last_sync'] = datetime.now().isoformat()
        save_financial_data(data)
        
        return {'accounts': accounts}
    except Exception as e:
        return {'error': str(e)}

def sync_transactions(days=30):
    """Sync transactions from Plaid"""
    data = load_financial_data()
    
    if not data.get('access_token'):
        return {'error': 'No access token'}
    
    try:
        # Get transactions
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        transactions_request = TransactionsGetRequest(
            access_token=data['access_token'],
            start_date=start_date,
            end_date=end_date,
        )
        transactions_response = client.transactions_get(transactions_request)
        
        transactions = []
        for txn in transactions_response['transactions']:
            transaction = {
                'id': txn['transaction_id'],
                'date': str(txn['date']),
                'name': txn['name'],
                'amount': txn['amount'],
                'category': txn.get('category', []),
                'account_id': txn['account_id'],
            }
            transaction['custom_category'] = categorize_transaction(transaction)
            transactions.append(transaction)
        
        data['transactions'] = transactions
        data['last_sync'] = datetime.now().isoformat()
        save_financial_data(data)
        
        return {'transactions': transactions}
    except Exception as e:
        return {'error': str(e)}

def calculate_spending_summary():
    """Calculate spending by category for current week"""
    data = load_financial_data()
    transactions = data.get('transactions', [])
    
    # Get this week's transactions
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    spending_by_category = {}
    
    for txn in transactions:
        txn_date = datetime.fromisoformat(txn['date']).date()
        if txn_date >= week_start and txn['amount'] > 0:  # Positive = spending
            category = txn.get('custom_category', 'Other')
            spending_by_category[category] = spending_by_category.get(category, 0) + txn['amount']
    
    return spending_by_category

def check_budget_status():
    """Check if spending is on track with budgets"""
    data = load_financial_data()
    budgets = data.get('budgets', {})
    spending = calculate_spending_summary()
    
    status = {}
    for category, budget in budgets.items():
        spent = spending.get(category, 0)
        status[category] = {
            'budget': budget,
            'spent': spent,
            'remaining': budget - spent,
            'percentage': (spent / budget * 100) if budget > 0 else 0,
            'status': 'on_track' if spent < budget * 0.8 else 'warning' if spent < budget else 'over_budget'
        }
    
    return status

# API Routes
@app.route('/')
def dashboard():
    """Main dashboard view"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/create_link_token', methods=['POST'])
def create_link_token():
    """Create a Plaid Link token"""
    try:
        request_data = LinkTokenCreateRequest(
            products=[Products('transactions'), Products('auth')],
            client_name='Jarvis Financial Dashboard',
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(client_user_id='jarvis-user'),
        )
        response = client.link_token_create(request_data)
        return jsonify({'link_token': response['link_token']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/exchange_public_token', methods=['POST'])
def exchange_public_token():
    """Exchange public token for access token"""
    try:
        public_token = request.json.get('public_token')
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_request)
        
        # Save access token
        data = load_financial_data()
        data['access_token'] = response['access_token']
        save_financial_data(data)
        
        # Initial sync
        sync_accounts()
        sync_transactions()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/accounts')
def get_accounts():
    """Get account balances"""
    data = load_financial_data()
    if not data.get('accounts'):
        sync_accounts()
        data = load_financial_data()
    return jsonify(data.get('accounts', []))

@app.route('/api/transactions')
def get_transactions():
    """Get recent transactions"""
    data = load_financial_data()
    return jsonify(data.get('transactions', []))

@app.route('/api/spending_summary')
def get_spending_summary():
    """Get spending by category"""
    spending = calculate_spending_summary()
    return jsonify(spending)

@app.route('/api/budget_status')
def get_budget_status():
    """Get budget status"""
    status = check_budget_status()
    return jsonify(status)

@app.route('/api/sync', methods=['POST'])
def manual_sync():
    """Manual sync trigger"""
    sync_accounts()
    sync_transactions()
    return jsonify({'success': True})

# Dashboard HTML
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Financial Dashboard - Jarvis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { 
            color: white; 
            margin-bottom: 30px; 
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .card h2 { 
            color: #667eea; 
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        .accounts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        .account {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
        }
        .account-name { font-size: 0.9em; opacity: 0.9; }
        .account-balance { 
            font-size: 2em; 
            font-weight: bold; 
            margin-top: 10px;
        }
        .budget-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        .budget-bar {
            width: 200px;
            height: 10px;
            background: #e0e0e0;
            border-radius: 5px;
            overflow: hidden;
        }
        .budget-fill {
            height: 100%;
            transition: width 0.3s;
        }
        .on-track { background: #4caf50; }
        .warning { background: #ff9800; }
        .over-budget { background: #f44336; }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }
        button:hover { background: #764ba2; transform: translateY(-2px); }
        .transactions {
            max-height: 400px;
            overflow-y: auto;
        }
        .transaction {
            display: flex;
            justify-content: space-between;
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        .transaction-amount { font-weight: bold; }
        .chart-container { height: 300px; margin-top: 20px; }
        .last-sync { 
            color: #666; 
            font-size: 0.9em; 
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💰 Financial Dashboard</h1>
        
        <div class="card">
            <h2>Quick Actions</h2>
            <button id="connect-bank">Connect Bank Account</button>
            <button onclick="syncData()">Sync Now</button>
            <div class="last-sync" id="last-sync"></div>
        </div>
        
        <div class="card">
            <h2>Account Balances</h2>
            <div class="accounts-grid" id="accounts"></div>
        </div>
        
        <div class="card">
            <h2>Budget Status (This Week)</h2>
            <div id="budget-status"></div>
        </div>
        
        <div class="card">
            <h2>Spending by Category</h2>
            <div class="chart-container">
                <canvas id="spending-chart"></canvas>
            </div>
        </div>
        
        <div class="card">
            <h2>Recent Transactions</h2>
            <div class="transactions" id="transactions"></div>
        </div>
    </div>
    
    <script>
        let spendingChart = null;
        
        // Initialize Plaid Link
        document.getElementById('connect-bank').addEventListener('click', async () => {
            const response = await fetch('/api/create_link_token', { method: 'POST' });
            const data = await response.json();
            
            const handler = Plaid.create({
                token: data.link_token,
                onSuccess: async (public_token) => {
                    await fetch('/api/exchange_public_token', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ public_token })
                    });
                    loadDashboard();
                }
            });
            handler.open();
        });
        
        async function syncData() {
            await fetch('/api/sync', { method: 'POST' });
            loadDashboard();
        }
        
        async function loadDashboard() {
            // Load accounts
            const accounts = await fetch('/api/accounts').then(r => r.json());
            const accountsHtml = accounts.map(acc => `
                <div class="account">
                    <div class="account-name">${acc.name} (${acc.type})</div>
                    <div class="account-balance">$${acc.balance.toFixed(2)}</div>
                    ${acc.available ? `<div style="font-size: 0.9em; opacity: 0.8; margin-top: 5px;">Available: $${acc.available.toFixed(2)}</div>` : ''}
                </div>
            `).join('');
            document.getElementById('accounts').innerHTML = accountsHtml || '<p>No accounts connected</p>';
            
            // Load budget status
            const budgetStatus = await fetch('/api/budget_status').then(r => r.json());
            const budgetHtml = Object.entries(budgetStatus).map(([category, status]) => `
                <div class="budget-item">
                    <div>
                        <strong>${category}</strong><br>
                        <span style="font-size: 0.9em; color: #666;">
                            $${status.spent.toFixed(2)} / $${status.budget.toFixed(2)}
                        </span>
                    </div>
                    <div class="budget-bar">
                        <div class="budget-fill ${status.status}" style="width: ${Math.min(status.percentage, 100)}%"></div>
                    </div>
                </div>
            `).join('');
            document.getElementById('budget-status').innerHTML = budgetHtml || '<p>No budget data</p>';
            
            // Load spending chart
            const spending = await fetch('/api/spending_summary').then(r => r.json());
            updateSpendingChart(spending);
            
            // Load transactions
            const transactions = await fetch('/api/transactions').then(r => r.json());
            const transactionsHtml = transactions.slice(0, 20).map(txn => `
                <div class="transaction">
                    <div>
                        <strong>${txn.name}</strong><br>
                        <span style="font-size: 0.9em; color: #666;">${txn.date} • ${txn.custom_category}</span>
                    </div>
                    <div class="transaction-amount" style="color: ${txn.amount > 0 ? '#f44336' : '#4caf50'}">
                        ${txn.amount > 0 ? '-' : '+'}$${Math.abs(txn.amount).toFixed(2)}
                    </div>
                </div>
            `).join('');
            document.getElementById('transactions').innerHTML = transactionsHtml || '<p>No transactions</p>';
        }
        
        function updateSpendingChart(spending) {
            const ctx = document.getElementById('spending-chart').getContext('2d');
            
            if (spendingChart) {
                spendingChart.destroy();
            }
            
            spendingChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(spending),
                    datasets: [{
                        data: Object.values(spending),
                        backgroundColor: [
                            '#667eea', '#764ba2', '#f093fb', '#4facfe',
                            '#43e97b', '#fa709a', '#fee140', '#30cfd0'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right' }
                    }
                }
            });
        }
        
        // Initial load
        loadDashboard();
        
        // Auto-refresh every 5 minutes
        setInterval(loadDashboard, 300000);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 Financial Dashboard starting on http://localhost:8082/finances")
    print("💡 Use PLAID_CLIENT_ID and PLAID_SECRET environment variables for production")
    app.run(host='0.0.0.0', port=8082, debug=False)
