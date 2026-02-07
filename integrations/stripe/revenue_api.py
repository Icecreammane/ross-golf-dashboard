"""
Revenue API Backend
Flask API for revenue dashboard
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from stripe_integration import StripeIntegration
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

stripe_integration = StripeIntegration()

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "stripe_configured": stripe_integration.is_configured(),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/revenue/mrr', methods=['GET'])
def get_mrr():
    """Get current MRR and ARR"""
    data = stripe_integration.get_mrr()
    return jsonify(data)

@app.route('/api/revenue/customers', methods=['GET'])
def get_customers():
    """Get customer count"""
    data = stripe_integration.get_customer_count()
    return jsonify(data)

@app.route('/api/revenue/growth', methods=['GET'])
def get_growth():
    """Get revenue growth data"""
    days = request.args.get('days', default=30, type=int)
    data = stripe_integration.get_growth_data(days=days)
    return jsonify(data)

@app.route('/api/revenue/events', methods=['GET'])
def get_events():
    """Get recent subscription events"""
    hours = request.args.get('hours', default=24, type=int)
    events = stripe_integration.get_recent_events(hours=hours)
    return jsonify({"events": events})

@app.route('/api/revenue/failed-payments', methods=['GET'])
def get_failed_payments():
    """Get recent failed payments"""
    days = request.args.get('days', default=7, type=int)
    failed = stripe_integration.get_failed_payments(days=days)
    return jsonify({"failed_payments": failed})

@app.route('/api/revenue/projections', methods=['GET'])
def get_projections():
    """Calculate revenue projections"""
    # Get growth data
    growth_data = stripe_integration.get_growth_data(days=30)
    mrr_data = stripe_integration.get_mrr()
    
    current_mrr = mrr_data.get('mrr', 0)
    growth_pct = growth_data.get('growth_percentage', 0)
    
    # Calculate days to $3K goal
    goal = 3000
    
    if current_mrr >= goal:
        days_to_goal = 0
        projected_date = datetime.now()
    elif growth_pct > 0:
        # Simple linear projection
        weekly_growth = current_mrr * (growth_pct / 100)
        weeks_needed = (goal - current_mrr) / weekly_growth if weekly_growth > 0 else 0
        days_to_goal = int(weeks_needed * 7)
        projected_date = datetime.now() + timedelta(days=days_to_goal)
    else:
        days_to_goal = None
        projected_date = None
    
    return jsonify({
        "current_mrr": current_mrr,
        "goal": goal,
        "remaining": goal - current_mrr,
        "progress_percentage": (current_mrr / goal) * 100,
        "growth_rate": growth_pct,
        "days_to_goal": days_to_goal,
        "projected_date": projected_date.isoformat() if projected_date else None
    })

@app.route('/api/revenue/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get all dashboard data in one call"""
    return jsonify({
        "mrr": stripe_integration.get_mrr(),
        "customers": stripe_integration.get_customer_count(),
        "growth": stripe_integration.get_growth_data(days=30),
        "recent_events": stripe_integration.get_recent_events(hours=168),
        "failed_payments": stripe_integration.get_failed_payments(days=7)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"🚀 Revenue API starting on http://localhost:{port}")
    print(f"📊 Dashboard data: http://localhost:{port}/api/revenue/dashboard")
    app.run(host='0.0.0.0', port=port, debug=True)
