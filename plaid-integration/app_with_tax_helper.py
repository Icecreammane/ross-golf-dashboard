#!/usr/bin/env python3
"""
Financial Dashboard with Smart Expense Categorizer + Tax Helper
Extended Plaid integration with automated tax deduction tracking
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
import json
from datetime import datetime, timedelta
import logging
import os
from expense_categorizer import ExpenseCategorizer, TaxHelper

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/clawdbot/clawd/plaid-integration/finance.db'
app.config['SECRET_KEY'] = 'plaid-finance-secret'
CORS(app)

db = SQLAlchemy(app)

# Initialize tax helper
categorizer = ExpenseCategorizer()
tax_helper = TaxHelper()

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
    name = db.Column(db.String(255))
    amount = db.Column(db.Float)
    category = db.Column(db.String(100))
    merchant_name = db.Column(db.String(255))
    location = db.Column(db.String(255))
    is_deductible = db.Column(db.Boolean, default=False)
    deductible_amount = db.Column(db.Float)
    deduction_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Tax Helper Endpoints

@app.route('/api/tax/categorize', methods=['POST'])
def categorize_transaction():
    """Auto-categorize a transaction"""
    data = request.json
    
    category = categorizer.categorize(
        data.get('description', ''),
        data.get('amount', 0),
        data.get('merchant', '')
    )
    
    return jsonify({
        'category': category,
        'description': data.get('description')
    })

@app.route('/api/tax/deductions/check', methods=['POST'])
def check_deduction():
    """Check if a transaction is tax deductible"""
    data = request.json
    
    deduction = categorizer.identify_deductions(
        data.get('description', ''),
        data.get('category', ''),
        data.get('amount', 0),
        data.get('location', '')
    )
    
    if deduction:
        return jsonify({
            'is_deductible': True,
            'deduction': deduction
        })
    else:
        return jsonify({
            'is_deductible': False
        })

@app.route('/api/tax/report/monthly', methods=['GET'])
def monthly_tax_report():
    """Generate monthly tax deduction report"""
    # Get current month transactions from DB
    current_month = datetime.now().strftime('%Y-%m')
    
    transactions = Transaction.query.filter(
        Transaction.date >= datetime.now().replace(day=1)
    ).all()
    
    # Convert to list of dicts
    txn_list = [
        {
            'date': txn.date.isoformat(),
            'description': txn.name,
            'amount': txn.amount,
            'category': txn.category,
            'merchant': txn.merchant_name or '',
            'location': txn.location or ''
        }
        for txn in transactions
    ]
    
    # Generate report
    report = categorizer.generate_monthly_report(txn_list)
    
    return jsonify(report)

@app.route('/api/tax/report/ytd', methods=['GET'])
def ytd_tax_report():
    """Get year-to-date tax deduction summary"""
    year = request.args.get('year', datetime.now().year, type=int)
    summary = tax_helper.get_ytd_summary(year)
    return jsonify(summary)

@app.route('/api/tax/export/csv', methods=['POST'])
def export_tax_csv():
    """Export tax deductions to CSV"""
    data = request.json
    
    # Get transactions for date range
    start_date = datetime.fromisoformat(data.get('start_date', '2026-01-01'))
    end_date = datetime.fromisoformat(data.get('end_date', datetime.now().isoformat()))
    
    transactions = Transaction.query.filter(
        Transaction.date >= start_date,
        Transaction.date <= end_date,
        Transaction.is_deductible == True
    ).all()
    
    # Convert to list of dicts
    txn_list = [
        {
            'date': txn.date.isoformat(),
            'description': txn.name,
            'amount': txn.amount,
            'category': txn.category,
            'merchant': txn.merchant_name or '',
            'location': txn.location or ''
        }
        for txn in transactions
    ]
    
    # Generate report
    report = categorizer.generate_monthly_report(txn_list)
    
    # Export to CSV
    filename = f"tax_deductions_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
    filepath = categorizer.export_to_csv(report, filename)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'filepath': filepath,
        'total_deductions': report['total_deductions']
    })

@app.route('/api/tax/dashboard', methods=['GET'])
def tax_dashboard_data():
    """Get comprehensive tax dashboard data"""
    # Get this month's data
    current_month = datetime.now().strftime('%Y-%m')
    current_year = datetime.now().year
    
    # Monthly deductions
    monthly_deductions = tax_helper.get_monthly_summary(current_month)
    
    # YTD deductions
    ytd_summary = tax_helper.get_ytd_summary(current_year)
    
    # Get top 3 categories this month
    transactions_this_month = Transaction.query.filter(
        Transaction.date >= datetime.now().replace(day=1),
        Transaction.is_deductible == True
    ).all()
    
    txn_list = [
        {
            'date': txn.date.isoformat(),
            'description': txn.name,
            'amount': txn.amount,
            'category': txn.category,
            'merchant': txn.merchant_name or '',
            'location': txn.location or ''
        }
        for txn in transactions_this_month
    ]
    
    monthly_report = categorizer.generate_monthly_report(txn_list)
    
    return jsonify({
        'monthly_deductions': monthly_deductions,
        'ytd_total': ytd_summary['total_deductions'],
        'ytd_by_category': ytd_summary['by_category'],
        'top_3_categories': monthly_report.get('top_3_categories', []),
        'summary': monthly_report.get('summary', '$0 in potential deductions')
    })

# Auto-categorize transactions on sync
def auto_categorize_and_flag_deductions(transactions):
    """
    Auto-categorize transactions and flag deductions when syncing from Plaid
    """
    for txn in transactions:
        # Categorize
        category = categorizer.categorize(
            txn.name,
            txn.amount,
            txn.merchant_name or ''
        )
        
        # Check for deductions
        deduction = categorizer.identify_deductions(
            txn.name,
            category,
            txn.amount,
            txn.location or ''
        )
        
        # Update transaction
        txn.category = category
        if deduction:
            txn.is_deductible = True
            txn.deductible_amount = deduction['deductible_amount']
            txn.deduction_type = deduction['type']
            
            # Track in tax helper
            tax_helper.track_transaction(
                txn.date.isoformat(),
                txn.name,
                txn.amount,
                category,
                txn.merchant_name or '',
                txn.location or ''
            )
    
    db.session.commit()

# Dashboard route
@app.route('/')
def index():
    """Main financial dashboard with tax helper widget"""
    return render_template('dashboard_with_tax.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5002)
