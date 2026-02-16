#!/usr/bin/env python3
"""
Spending Tracker API
Flask backend serving transaction data and analytics
"""

import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TRANSACTIONS_FILE = os.path.expanduser("~/clawd/data/transactions.json")

def load_transactions():
    """Load transactions from file"""
    if not os.path.exists(TRANSACTIONS_FILE):
        return []
    
    with open(TRANSACTIONS_FILE, 'r') as f:
        return json.load(f)

def filter_by_date_range(transactions, start_date, end_date=None):
    """Filter transactions by date range"""
    if end_date is None:
        end_date = datetime.now().date()
    
    return [
        t for t in transactions
        if start_date <= datetime.fromisoformat(t['date']).date() <= end_date
    ]

def calculate_spending_by_category(transactions):
    """Calculate total spending by category"""
    by_category = defaultdict(float)
    
    for txn in transactions:
        if txn['amount'] > 0:  # Only count expenses (positive = spending)
            by_category[txn['category']] += txn['amount']
    
    return dict(by_category)

def get_top_merchants(transactions, limit=10):
    """Get top merchants by spending"""
    by_merchant = defaultdict(float)
    
    for txn in transactions:
        if txn['amount'] > 0:
            by_merchant[txn['merchant']] += txn['amount']
    
    sorted_merchants = sorted(by_merchant.items(), key=lambda x: x[1], reverse=True)
    return [{'merchant': m, 'total': round(t, 2)} for m, t in sorted_merchants[:limit]]

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/today', methods=['GET'])
def today():
    """Today's spending summary"""
    transactions = load_transactions()
    today_date = datetime.now().date()
    
    today_txns = filter_by_date_range(transactions, today_date, today_date)
    
    total_spent = sum(t['amount'] for t in today_txns if t['amount'] > 0)
    by_category = calculate_spending_by_category(today_txns)
    
    return jsonify({
        'date': str(today_date),
        'total_spent': round(total_spent, 2),
        'transaction_count': len(today_txns),
        'by_category': by_category,
        'recent_transactions': today_txns[:10]
    })

@app.route('/api/week', methods=['GET'])
def week():
    """This week's spending summary"""
    transactions = load_transactions()
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())  # Monday
    
    this_week = filter_by_date_range(transactions, week_start, today)
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_start - timedelta(days=1)
    last_week = filter_by_date_range(transactions, last_week_start, last_week_end)
    
    this_week_total = sum(t['amount'] for t in this_week if t['amount'] > 0)
    last_week_total = sum(t['amount'] for t in last_week if t['amount'] > 0)
    
    change_pct = 0
    if last_week_total > 0:
        change_pct = ((this_week_total - last_week_total) / last_week_total) * 100
    
    return jsonify({
        'week_start': str(week_start),
        'week_end': str(today),
        'total_spent': round(this_week_total, 2),
        'last_week_total': round(last_week_total, 2),
        'change_percent': round(change_pct, 1),
        'by_category': calculate_spending_by_category(this_week),
        'transaction_count': len(this_week)
    })

@app.route('/api/month', methods=['GET'])
def month():
    """This month's spending summary"""
    transactions = load_transactions()
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    this_month = filter_by_date_range(transactions, month_start, today)
    
    # Calculate average daily spending
    days_elapsed = (today - month_start).days + 1
    total_spent = sum(t['amount'] for t in this_month if t['amount'] > 0)
    daily_avg = total_spent / days_elapsed if days_elapsed > 0 else 0
    
    # Project end-of-month
    days_in_month = 30  # Approximation
    projected_total = daily_avg * days_in_month
    
    return jsonify({
        'month_start': str(month_start),
        'current_date': str(today),
        'total_spent': round(total_spent, 2),
        'daily_average': round(daily_avg, 2),
        'projected_month_total': round(projected_total, 2),
        'days_elapsed': days_elapsed,
        'by_category': calculate_spending_by_category(this_month),
        'transaction_count': len(this_month)
    })

@app.route('/api/categories', methods=['GET'])
def categories():
    """Category breakdown for last 30 days"""
    transactions = load_transactions()
    today = datetime.now().date()
    start_date = today - timedelta(days=30)
    
    recent = filter_by_date_range(transactions, start_date, today)
    by_category = calculate_spending_by_category(recent)
    
    # Calculate percentages
    total = sum(by_category.values())
    category_data = [
        {
            'category': cat,
            'total': round(amount, 2),
            'percentage': round((amount / total * 100) if total > 0 else 0, 1)
        }
        for cat, amount in sorted(by_category.items(), key=lambda x: x[1], reverse=True)
    ]
    
    return jsonify({
        'period': f'{start_date} to {today}',
        'categories': category_data,
        'total_spent': round(total, 2)
    })

@app.route('/api/trends', methods=['GET'])
def trends():
    """Daily spending trends for last 30 days"""
    transactions = load_transactions()
    today = datetime.now().date()
    start_date = today - timedelta(days=30)
    
    recent = filter_by_date_range(transactions, start_date, today)
    
    # Group by date
    by_date = defaultdict(float)
    for txn in recent:
        if txn['amount'] > 0:
            by_date[txn['date']] += txn['amount']
    
    # Create daily array
    daily_data = []
    current_date = start_date
    while current_date <= today:
        date_str = str(current_date)
        daily_data.append({
            'date': date_str,
            'total': round(by_date.get(date_str, 0), 2)
        })
        current_date += timedelta(days=1)
    
    return jsonify({
        'period': f'{start_date} to {today}',
        'daily_spending': daily_data
    })

@app.route('/api/merchants', methods=['GET'])
def merchants():
    """Top merchants for last 30 days"""
    transactions = load_transactions()
    today = datetime.now().date()
    start_date = today - timedelta(days=30)
    
    recent = filter_by_date_range(transactions, start_date, today)
    top = get_top_merchants(recent, limit=20)
    
    return jsonify({
        'period': f'{start_date} to {today}',
        'top_merchants': top
    })

@app.route('/api/transactions/recent', methods=['GET'])
def recent_transactions():
    """Recent transactions (last 20)"""
    transactions = load_transactions()
    limit = int(request.args.get('limit', 20))
    
    return jsonify({
        'transactions': transactions[:limit],
        'total_count': len(transactions)
    })

@app.route('/api/stats', methods=['GET'])
def stats():
    """Overall statistics"""
    transactions = load_transactions()
    
    if not transactions:
        return jsonify({'message': 'No transactions yet'})
    
    total_spent = sum(t['amount'] for t in transactions if t['amount'] > 0)
    
    # Date range
    dates = [datetime.fromisoformat(t['date']).date() for t in transactions]
    oldest = min(dates)
    newest = max(dates)
    days_tracked = (newest - oldest).days + 1
    
    # Averages
    daily_avg = total_spent / days_tracked if days_tracked > 0 else 0
    
    return jsonify({
        'total_transactions': len(transactions),
        'total_spent': round(total_spent, 2),
        'date_range': f'{oldest} to {newest}',
        'days_tracked': days_tracked,
        'daily_average': round(daily_avg, 2),
        'weekly_average': round(daily_avg * 7, 2),
        'monthly_average': round(daily_avg * 30, 2)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print(f"🚀 Spending Tracker API running on http://localhost:{port}")
    print(f"📊 Serving data from {TRANSACTIONS_FILE}")
    app.run(host='0.0.0.0', port=port, debug=True)
