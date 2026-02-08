#!/usr/bin/env python3
"""
Plaid Integration for Ross's Personal Finance Dashboard
Handles Plaid authentication, account linking, and transaction retrieval
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
import os
from datetime import datetime, timedelta
import json
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/clawdbot/clawd/plaid-integration/finance.db'
app.config['SECRET_KEY'] = 'plaid-finance-dashboard-secret'
CORS(app)

db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Plaid Configuration
PLAID_CLIENT_ID = '69b8b5dda8ab8881edc312'
PLAID_SECRET = '97d84d06a39cc134643c64268288f'
PLAID_ENV = 'sandbox'  # Use 'production' for real accounts

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key=PLAID_CLIENT_ID,
    api_version='2020-09-14'
)
api_client = plaid.ApiClient(configuration)
api_client.set_default_header("PLAID-CLIENT-ID", PLAID_CLIENT_ID)
api_client.set_default_header("PLAID-SECRET", PLAID_SECRET)

client = plaid_api.PlaidApi(api_client)

# Database Models
class PlaidItem(db.Model):
    """Represents a linked bank account (Plaid Item)"""
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String(255), unique=True, nullable=False)
    access_token = db.Column(db.String(255), nullable=False)
    institution_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Account(db.Model):
    """Represents a bank account"""
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String(255), db.ForeignKey('plaid_item.item_id'))
    account_id = db.Column(db.String(255), unique=True)
    account_name = db.Column(db.String(255))
    account_type = db.Column(db.String(50))  # checking, savings, credit, etc
    subtype = db.Column(db.String(50))
    balance = db.Column(db.Float)
    currency = db.Column(db.String(3), default='USD')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    """Represents a transaction"""
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

# Routes
@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/link-token', methods=['POST'])
def create_link_token():
    """Create a Plaid Link token for account linking"""
    try:
        request_obj = LinkTokenCreateRequest(
            products=[Products('auth'), Products('transactions')],
            client_name="Ross's Finance Dashboard",
            country_codes=[CountryCode('US')],
            language='en',
            user={"client_user_id": "ross-unique-id"}
        )
        
        response = client.link_token_create(request_obj)
        return jsonify({"link_token": response['link_token']})
    except Exception as e:
        logger.error(f"Error creating link token: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/api/exchange-token', methods=['POST'])
def exchange_public_token():
    """Exchange public token from Plaid Link for access token"""
    try:
        data = request.get_json()
        public_token = data.get('public_token')
        
        # Exchange public token for access token
        request_obj = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(request_obj)
        
        access_token = response['access_token']
        item_id = response['item_id']
        
        # Get institution info
        from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
        inst_request = InstitutionsGetByIdRequest(
            institution_id=response.get('institution_id', 'unknown'),
            country_codes=[CountryCode('US')]
        )
        
        try:
            inst_response = client.institutions_get_by_id(inst_request)
            institution_name = inst_response['institutions'][0]['name']
        except:
            institution_name = 'Unknown Bank'
        
        # Store in database
        plaid_item = PlaidItem(
            item_id=item_id,
            access_token=access_token,
            institution_name=institution_name
        )
        db.session.add(plaid_item)
        db.session.commit()
        
        # Fetch and store accounts
        fetch_and_store_accounts(access_token, item_id)
        
        return jsonify({
            "success": True,
            "institution": institution_name,
            "item_id": item_id
        })
    except Exception as e:
        logger.error(f"Error exchanging token: {str(e)}")
        return jsonify({"error": str(e)}), 400

def fetch_and_store_accounts(access_token, item_id):
    """Fetch accounts from Plaid and store in database"""
    try:
        request_obj = AccountsGetRequest(access_token=access_token)
        response = client.accounts_get(request_obj)
        
        for account in response['accounts']:
            existing = Account.query.filter_by(account_id=account['account_id']).first()
            if not existing:
                acc = Account(
                    item_id=item_id,
                    account_id=account['account_id'],
                    account_name=account['name'],
                    account_type=account['type'],
                    subtype=account.get('subtype', ''),
                    balance=account['balances']['current'],
                    currency=account['balances']['iso_currency_code']
                )
                db.session.add(acc)
        
        db.session.commit()
        
        # Fetch transactions for this account
        fetch_and_store_transactions(access_token)
    except Exception as e:
        logger.error(f"Error fetching accounts: {str(e)}")

def fetch_and_store_transactions(access_token):
    """Fetch transactions from Plaid and store in database"""
    try:
        # Get last 30 days of transactions
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        request_obj = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date
        )
        
        response = client.transactions_get(request_obj)
        
        for transaction in response['transactions']:
            existing = Transaction.query.filter_by(
                transaction_id=transaction['transaction_id']
            ).first()
            
            if not existing:
                txn = Transaction(
                    account_id=transaction['account_id'],
                    transaction_id=transaction['transaction_id'],
                    date=datetime.strptime(transaction['date'], '%Y-%m-%d').date(),
                    amount=transaction['amount'],
                    merchant_name=transaction.get('merchant_name', transaction.get('name', 'Unknown')),
                    category=','.join(transaction.get('personal_finance_category', {}).get('detailed', [])) if transaction.get('personal_finance_category') else 'Uncategorized',
                    description=transaction.get('name', ''),
                    pending=transaction.get('pending', False)
                )
                db.session.add(txn)
        
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
            'institution': PlaidItem.query.filter_by(item_id=acc.item_id).first().institution_name
        } for acc in accounts])
    except Exception as e:
        logger.error(f"Error getting accounts: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get transactions with optional filtering"""
    try:
        account_id = request.args.get('account_id')
        days = request.args.get('days', 30, type=int)
        
        query = Transaction.query
        
        if account_id:
            query = query.filter_by(account_id=account_id)
        
        # Filter by date
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
        return jsonify({"error": str(e)}), 400

@app.route('/api/spending-summary', methods=['GET'])
def spending_summary():
    """Get spending summary by category"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.now().date() - timedelta(days=days)
        
        transactions = Transaction.query.filter(
            Transaction.date >= start_date,
            Transaction.amount > 0
        ).all()
        
        # Group by category
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
        return jsonify({"error": str(e)}), 400

@app.route('/api/net-worth', methods=['GET'])
def net_worth():
    """Calculate total net worth from linked accounts"""
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
        return jsonify({"error": str(e)}), 400

@app.route('/api/refresh-accounts', methods=['POST'])
def refresh_accounts():
    """Manually refresh account data from Plaid"""
    try:
        items = PlaidItem.query.all()
        for item in items:
            fetch_and_store_accounts(item.access_token, item.item_id)
        
        return jsonify({"success": True, "message": "Accounts refreshed"})
    except Exception as e:
        logger.error(f"Error refreshing accounts: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=3100)
