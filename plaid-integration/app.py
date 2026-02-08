#!/usr/bin/env python3
"""
Plaid Integration for Ross's Personal Finance Dashboard
Using direct REST API calls instead of SDK
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
import json
from datetime import datetime, timedelta
import logging
import os

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/clawdbot/clawd/plaid-integration/finance.db'
app.config['SECRET_KEY'] = 'plaid-finance-secret'
CORS(app)

db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Plaid Configuration
PLAID_CLIENT_ID = '6988b58d0aba88001ee6c312'
PLAID_SECRET = '97d06ab9ba30cc336643cdd428280f'
PLAID_ENV = 'sandbox'
PLAID_URL = 'https://sandbox.plaid.com'

# Database Models
class PlaidItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String(255), unique=True, nullable=False)
    access_token = db.Column(db.String(255), nullable=False)
    institution_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String(255), db.ForeignKey('plaid_item.item_id'))
    account_id = db.Column(db.String(255), unique=True)
    account_name = db.Column(db.String(255))
    account_type = db.Column(db.String(50))
    subtype = db.Column(db.String(50))
    balance = db.Column(db.Float)
    currency = db.Column(db.String(3), default='USD')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(255), db.ForeignKey('account.account_id'))
    transaction_id = db.Column(db.String(255), unique=True)
    date = db.Column(db.Date)
    amount = db.Column(db.Float)
    merchant_name = db.Column(db.String(255))
    category = db.Column(db.String(100))
    description = db.Column(db.String(500))
    pending = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper functions
def plaid_request(endpoint, data):
    """Make a request to Plaid API"""
    try:
        url = f"{PLAID_URL}{endpoint}"
        payload = {
            'client_id': PLAID_CLIENT_ID,
            'secret': PLAID_SECRET,
            **data
        }
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        logger.error(f"Plaid API error: {str(e)}")
        return {"error": str(e)}

# Routes
@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/exchange-token', methods=['POST'])
def exchange_public_token():
    """Exchange public token for access token"""
    try:
        data = request.get_json()
        public_token = data.get('public_token')
        
        response = plaid_request('/item/public_token/exchange', {
            'public_token': public_token
        })
        
        if 'access_token' in response:
            access_token = response['access_token']
            item_id = response['item_id']
            
            # Save to database
            plaid_item = PlaidItem(
                item_id=item_id,
                access_token=access_token,
                institution_name='Connected Bank'
            )
            db.session.add(plaid_item)
            db.session.commit()
            
            # Fetch accounts
            fetch_accounts(access_token, item_id)
            
            return jsonify({
                'success': True,
                'institution': 'Connected Bank',
                'item_id': item_id
            })
        else:
            return jsonify({'error': response.get('error_message', 'Unknown error')}), 400
    except Exception as e:
        logger.error(f"Error exchanging token: {str(e)}")
        return jsonify({'error': str(e)}), 400

def fetch_accounts(access_token, item_id):
    """Fetch accounts from Plaid"""
    try:
        response = plaid_request('/accounts/get', {
            'access_token': access_token
        })
        
        if 'accounts' in response:
            for account in response['accounts']:
                existing = Account.query.filter_by(account_id=account['account_id']).first()
                if not existing:
                    acc = Account(
                        item_id=item_id,
                        account_id=account['account_id'],
                        account_name=account['name'],
                        account_type=account['type'],
                        subtype=account.get('subtype', ''),
                        balance=account.get('balances', {}).get('current', 0),
                        currency=account.get('balances', {}).get('iso_currency_code', 'USD')
                    )
                    db.session.add(acc)
            
            db.session.commit()
            fetch_transactions(access_token)
    except Exception as e:
        logger.error(f"Error fetching accounts: {str(e)}")

def fetch_transactions(access_token):
    """Fetch transactions from Plaid"""
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        response = plaid_request('/transactions/get', {
            'access_token': access_token,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        })
        
        if 'transactions' in response:
            for txn in response['transactions']:
                existing = Transaction.query.filter_by(
                    transaction_id=txn['transaction_id']
                ).first()
                
                if not existing:
                    category = txn.get('personal_finance_category', {}).get('detailed', 'Uncategorized')
                    if isinstance(category, list):
                        category = ', '.join(category) if category else 'Uncategorized'
                    
                    t = Transaction(
                        account_id=txn['account_id'],
                        transaction_id=txn['transaction_id'],
                        date=datetime.strptime(txn['date'], '%Y-%m-%d').date(),
                        amount=txn['amount'],
                        merchant_name=txn.get('merchant_name', txn.get('name', 'Unknown')),
                        category=category,
                        description=txn.get('name', ''),
                        pending=txn.get('pending', False)
                    )
                    db.session.add(t)
            
            db.session.commit()
    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Get all linked accounts"""
    try:
        accounts = Account.query.all()
        return jsonify([{
            'id': acc.account_id,
            'name': acc.account_name,
            'type': acc.account_type,
            'balance': acc.balance,
            'currency': acc.currency,
            'institution': 'Bank'
        } for acc in accounts])
    except Exception as e:
        logger.error(f"Error getting accounts: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get transactions with filtering"""
    try:
        account_id = request.args.get('account_id')
        days = request.args.get('days', 30, type=int)
        
        query = Transaction.query
        
        if account_id:
            query = query.filter_by(account_id=account_id)
        
        start_date = datetime.now().date() - timedelta(days=days)
        query = query.filter(Transaction.date >= start_date)
        
        transactions = query.order_by(Transaction.date.desc()).all()
        
        return jsonify([{
            'id': txn.transaction_id,
            'date': txn.date.isoformat(),
            'amount': txn.amount,
            'merchant': txn.merchant_name,
            'category': txn.category,
            'description': txn.description,
            'pending': txn.pending,
            'account_id': txn.account_id
        } for txn in transactions])
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/add-account', methods=['POST'])
def add_account_manual():
    """Manually add a bank account"""
    try:
        data = request.get_json()
        
        account = Account(
            item_id='manual',
            account_id=f"manual-{datetime.now().timestamp()}",
            account_name=data.get('account_name'),
            account_type=data.get('account_type'),
            subtype='',
            balance=data.get('balance', 0),
            currency='USD'
        )
        db.session.add(account)
        db.session.commit()
        
        return jsonify({'success': True, 'account_id': account.account_id})
    except Exception as e:
        logger.error(f"Error adding account: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/add-transaction', methods=['POST'])
def add_transaction_manual():
    """Manually add a transaction"""
    try:
        data = request.get_json()
        
        transaction = Transaction(
            account_id=data.get('account_id'),
            transaction_id=f"manual-{datetime.now().timestamp()}",
            date=datetime.strptime(data.get('date'), '%Y-%m-%d').date(),
            amount=float(data.get('amount', 0)),
            merchant_name=data.get('merchant_name'),
            category=data.get('category', 'Uncategorized'),
            description=data.get('description', ''),
            pending=False
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({'success': True, 'transaction_id': transaction.transaction_id})
    except Exception as e:
        logger.error(f"Error adding transaction: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/net-worth', methods=['GET'])
def net_worth():
    """Calculate net worth"""
    try:
        accounts = Account.query.all()
        total = sum(acc.balance for acc in accounts if acc.balance)
        
        breakdown = {}
        for acc in accounts:
            acc_type = acc.account_type
            if acc_type not in breakdown:
                breakdown[acc_type] = 0
            breakdown[acc_type] += acc.balance if acc.balance else 0
        
        return jsonify({
            'total': total,
            'breakdown': breakdown,
            'accounts_count': len(accounts)
        })
    except Exception as e:
        logger.error(f"Error calculating net worth: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/spending-summary', methods=['GET'])
def spending_summary():
    """Get spending by category"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.now().date() - timedelta(days=days)
        
        transactions = Transaction.query.filter(
            Transaction.date >= start_date,
            Transaction.amount > 0
        ).all()
        
        summary = {}
        for txn in transactions:
            category = txn.category if txn.category else 'Uncategorized'
            if category not in summary:
                summary[category] = {'total': 0, 'count': 0}
            summary[category]['total'] += txn.amount
            summary[category]['count'] += 1
        
        return jsonify(summary)
    except Exception as e:
        logger.error(f"Error getting spending summary: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/refresh-accounts', methods=['POST'])
def refresh_accounts():
    """Refresh account data"""
    try:
        items = PlaidItem.query.all()
        for item in items:
            fetch_accounts(item.access_token, item.item_id)
        
        return jsonify({'success': True, 'message': 'Accounts refreshed'})
    except Exception as e:
        logger.error(f"Error refreshing: {str(e)}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=3100)
