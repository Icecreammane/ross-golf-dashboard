#!/usr/bin/env python3
"""
Spending Alerts & Coaching System
Analyzes spending patterns and generates actionable insights
"""

import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

TRANSACTIONS_FILE = os.path.expanduser("~/clawd/data/transactions.json")
ALERTS_LOG = os.path.expanduser("~/clawd/data/spending_alerts.json")

def load_transactions():
    """Load transactions from file"""
    if not os.path.exists(TRANSACTIONS_FILE):
        return []
    
    with open(TRANSACTIONS_FILE, 'r') as f:
        return json.load(f)

def filter_by_period(transactions, days):
    """Filter transactions by number of days back"""
    cutoff_date = (datetime.now() - timedelta(days=days)).date()
    return [
        t for t in transactions
        if datetime.fromisoformat(t['date']).date() >= cutoff_date
    ]

def calculate_category_spending(transactions):
    """Calculate spending by category"""
    by_category = defaultdict(float)
    
    for txn in transactions:
        if txn['amount'] > 0:
            by_category[txn['category']] += txn['amount']
    
    return dict(by_category)

def calculate_merchant_spending(transactions):
    """Calculate spending by merchant"""
    by_merchant = defaultdict(float)
    
    for txn in transactions:
        if txn['amount'] > 0:
            by_merchant[txn['merchant']] += txn['amount']
    
    return dict(by_merchant)

def generate_daily_summary():
    """Generate daily spending summary"""
    transactions = load_transactions()
    today = datetime.now().date()
    
    today_txns = [
        t for t in transactions
        if datetime.fromisoformat(t['date']).date() == today
    ]
    
    if not today_txns:
        return "📊 **Daily Summary:** No spending today (yet!)"
    
    total = sum(t['amount'] for t in today_txns if t['amount'] > 0)
    by_category = calculate_category_spending(today_txns)
    
    # Find top 3 purchases
    top_purchases = sorted(
        [t for t in today_txns if t['amount'] > 0],
        key=lambda x: x['amount'],
        reverse=True
    )[:3]
    
    summary = f"📊 **Today's Spending:** ${total:.2f}\n\n"
    
    if top_purchases:
        summary += "**Top Purchases:**\n"
        for txn in top_purchases:
            summary += f"• {txn['merchant']}: ${txn['amount']:.2f}\n"
    
    # Category breakdown
    if by_category:
        summary += "\n**By Category:**\n"
        for cat, amount in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            summary += f"• {cat}: ${amount:.2f}\n"
    
    return summary

def generate_weekly_alerts():
    """Generate weekly spending alerts"""
    transactions = load_transactions()
    today = datetime.now().date()
    
    # This week
    week_start = today - timedelta(days=today.weekday())
    this_week = filter_by_period(transactions, (today - week_start).days)
    this_week_spending = calculate_category_spending(this_week)
    this_week_total = sum(this_week_spending.values())
    
    # Last week
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_start - timedelta(days=1)
    last_week = [
        t for t in transactions
        if last_week_start <= datetime.fromisoformat(t['date']).date() <= last_week_end
    ]
    last_week_spending = calculate_category_spending(last_week)
    last_week_total = sum(last_week_spending.values())
    
    alerts = []
    
    # Overall spending alert
    if last_week_total > 0:
        change_pct = ((this_week_total - last_week_total) / last_week_total) * 100
        
        if change_pct > 20:
            alerts.append(f"⚠️ **Overall spending up {change_pct:.0f}% this week:** ${this_week_total:.2f} vs ${last_week_total:.2f} last week")
        elif change_pct < -20:
            alerts.append(f"✅ **Great job! Spending down {abs(change_pct):.0f}% this week:** ${this_week_total:.2f} vs ${last_week_total:.2f}")
    
    # Category-specific alerts
    for category, this_week_amt in this_week_spending.items():
        last_week_amt = last_week_spending.get(category, 0)
        
        if last_week_amt > 0:
            change = ((this_week_amt - last_week_amt) / last_week_amt) * 100
            
            if change > 50 and this_week_amt > 50:  # Significant increase
                alerts.append(f"⚠️ **{category}:** ${this_week_amt:.2f} this week (up {change:.0f}% from ${last_week_amt:.2f})")
    
    return alerts

def generate_insights():
    """Generate financial coaching insights"""
    transactions = load_transactions()
    
    # Last 30 days
    last_30 = filter_by_period(transactions, 30)
    by_category = calculate_category_spending(last_30)
    by_merchant = calculate_merchant_spending(last_30)
    
    total_30d = sum(by_category.values())
    
    insights = []
    
    # Dining out insights
    dining = by_category.get('Dining Out', 0)
    groceries = by_category.get('Groceries', 0)
    
    if dining > groceries and dining > 200:
        potential_savings = dining * 0.6  # 60% reduction
        annual_savings = potential_savings * 12
        insights.append(
            f"💡 **Dining optimization opportunity:** You spent ${dining:.2f} on dining out vs ${groceries:.2f} on groceries. "
            f"Cooking at home more could save ~${potential_savings:.2f}/month = ${annual_savings:.2f}/year toward Florida!"
        )
    
    # Subscription analysis
    subscriptions = by_category.get('Subscriptions', 0)
    if subscriptions > 50:
        insights.append(
            f"📱 **Subscription check:** ${subscriptions:.2f}/month on subscriptions. "
            f"Review active subscriptions - cancel unused ones to save money."
        )
    
    # Top merchant spending
    top_merchants = sorted(by_merchant.items(), key=lambda x: x[1], reverse=True)[:3]
    if top_merchants:
        insights.append("\n📊 **Top spending sources (30 days):**")
        for merchant, amount in top_merchants:
            monthly_est = amount
            annual_est = amount * 12
            insights.append(f"• {merchant}: ${monthly_est:.2f}/mo (${annual_est:.2f}/year)")
    
    # Overall averages
    daily_avg = total_30d / 30
    weekly_avg = daily_avg * 7
    monthly_avg = daily_avg * 30
    
    insights.append(
        f"\n💰 **Your spending averages:**\n"
        f"• Daily: ${daily_avg:.2f}\n"
        f"• Weekly: ${weekly_avg:.2f}\n"
        f"• Monthly: ${monthly_avg:.2f}"
    )
    
    return insights

def check_large_transactions():
    """Alert on transactions over $100"""
    transactions = load_transactions()
    today = datetime.now().date()
    
    today_large = [
        t for t in transactions
        if datetime.fromisoformat(t['date']).date() == today
        and t['amount'] > 100
    ]
    
    alerts = []
    for txn in today_large:
        alerts.append(f"💳 **Large transaction:** ${txn['amount']:.2f} at {txn['merchant']}")
    
    return alerts

def generate_evening_summary():
    """Full evening spending summary"""
    summary = "🌙 **Evening Financial Check-in**\n\n"
    
    # Daily summary
    summary += generate_daily_summary() + "\n\n"
    
    # Weekly alerts
    weekly_alerts = generate_weekly_alerts()
    if weekly_alerts:
        summary += "**This Week:**\n"
        for alert in weekly_alerts:
            summary += alert + "\n"
        summary += "\n"
    
    # Large transactions
    large_txns = check_large_transactions()
    if large_txns:
        summary += "\n".join(large_txns) + "\n\n"
    
    # Insights (rotate - show one insight per day)
    insights = generate_insights()
    if insights:
        # Pick insight based on day of week
        insight_idx = datetime.now().weekday() % len(insights)
        summary += insights[insight_idx]
    
    return summary

def generate_morning_brief():
    """Yesterday's spending for morning brief"""
    transactions = load_transactions()
    yesterday = (datetime.now() - timedelta(days=1)).date()
    
    yesterday_txns = [
        t for t in transactions
        if datetime.fromisoformat(t['date']).date() == yesterday
    ]
    
    if not yesterday_txns:
        return "📊 **Yesterday:** No spending"
    
    total = sum(t['amount'] for t in yesterday_txns if t['amount'] > 0)
    
    # Calculate weekly average
    last_7 = filter_by_period(transactions, 7)
    weekly_total = sum(t['amount'] for t in last_7 if t['amount'] > 0)
    daily_avg = weekly_total / 7
    
    status = "on track" if total <= daily_avg else "over budget"
    
    return f"📊 **Yesterday:** ${total:.2f} ({status}, avg: ${daily_avg:.2f}/day)"

def save_alert(alert_type, message):
    """Log alert to file"""
    alerts = []
    if os.path.exists(ALERTS_LOG):
        with open(ALERTS_LOG, 'r') as f:
            alerts = json.load(f)
    
    alerts.append({
        'timestamp': datetime.now().isoformat(),
        'type': alert_type,
        'message': message
    })
    
    # Keep last 100 alerts
    alerts = alerts[-100:]
    
    os.makedirs(os.path.dirname(ALERTS_LOG), exist_ok=True)
    with open(ALERTS_LOG, 'w') as f:
        json.dump(alerts, f, indent=2)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'daily':
            print(generate_daily_summary())
        elif command == 'evening':
            result = generate_evening_summary()
            print(result)
            save_alert('evening_summary', result)
        elif command == 'morning':
            print(generate_morning_brief())
        elif command == 'insights':
            for insight in generate_insights():
                print(insight)
        elif command == 'weekly':
            for alert in generate_weekly_alerts():
                print(alert)
    else:
        # Default: evening summary
        print(generate_evening_summary())
