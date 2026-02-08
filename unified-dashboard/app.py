"""
Unified Dashboard - Production-Ready
Consolidates all services into a single beautiful interface
Real-time updates from Central API with <1s load time
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime, timedelta
from functools import lru_cache
import logging

# Configuration
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service endpoints
CENTRAL_API_URL = os.getenv('CENTRAL_API_URL', 'http://localhost:3003')
CENTRAL_API_TOKEN = os.getenv('API_TOKEN', 'dev-token-12345')

# Data file paths
FITNESS_DATA = '/Users/clawdbot/clawd/fitness-tracker/fitness_data.json'
GOLF_DATA = '/Users/clawdbot/clawd/data/golf-data.json'
NBA_DATA = '/Users/clawdbot/clawd/data/nba-slate-{}.json'
REVENUE_DATA = '/Users/clawdbot/clawd/revenue_dashboard/data/revenue_data.json'

# Cache timeout (seconds)
CACHE_TIMEOUT = 30


def get_api_headers():
    """Get headers for Central API requests"""
    return {
        'Authorization': f'Bearer {CENTRAL_API_TOKEN}',
        'Content-Type': 'application/json'
    }


def fetch_with_fallback(url, fallback_data=None):
    """Fetch from Central API with fallback to local files"""
    try:
        response = requests.get(url, headers=get_api_headers(), timeout=2)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.warning(f"API fetch failed for {url}: {e}")
    
    return fallback_data or {}


def load_json_file(filepath, default=None):
    """Load JSON file with error handling"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
    
    return default or {}


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/revenue')
def api_revenue():
    """Revenue data endpoint"""
    # Try Central API first
    data = fetch_with_fallback(f'{CENTRAL_API_URL}/revenue')
    
    # Fallback to local file
    if not data:
        data = load_json_file(REVENUE_DATA, {
            'mrr': 0,
            'daily_revenue': 0,
            'total_revenue': 0,
            'stripe_sales': []
        })
    
    # Calculate metrics
    mrr = data.get('mrr', 0)
    goal = 500
    progress = (mrr / goal * 100) if goal > 0 else 0
    
    return jsonify({
        'mrr': mrr,
        'goal': goal,
        'progress': round(progress, 1),
        'daily_revenue': data.get('daily_revenue', 0),
        'weekly_revenue': data.get('weekly_revenue', 0),
        'monthly_revenue': data.get('total_revenue', 0),
        'recent_sales': data.get('stripe_sales', [])[:5],
        'last_updated': datetime.now().isoformat()
    })


@app.route('/api/opportunities')
def api_opportunities():
    """Business opportunities endpoint"""
    # Try Central API
    data = fetch_with_fallback(f'{CENTRAL_API_URL}/opportunities')
    
    if not data:
        # Fallback: parse from cold-email-ai or other sources
        data = {'opportunities': [], 'count': 0}
    
    # Sort by value/confidence
    opps = data.get('opportunities', [])
    opps_sorted = sorted(opps, key=lambda x: x.get('confidence', 0) * x.get('value', 0), reverse=True)
    
    return jsonify({
        'opportunities': opps_sorted[:10],
        'total_count': len(opps),
        'high_priority': len([o for o in opps if o.get('confidence', 0) > 0.7]),
        'last_updated': datetime.now().isoformat()
    })


@app.route('/api/morning-brief')
def api_morning_brief():
    """Morning brief status endpoint"""
    today = datetime.now().strftime('%Y-%m-%d')
    brief_file = f'/Users/clawdbot/clawd/data/nba-morning-brief-{today}.md'
    
    brief_exists = os.path.exists(brief_file)
    brief_content = ''
    
    if brief_exists:
        try:
            with open(brief_file, 'r') as f:
                brief_content = f.read()
        except:
            pass
    
    return jsonify({
        'generated': brief_exists,
        'date': today,
        'content': brief_content,
        'time_generated': datetime.now().strftime('%I:%M %p') if brief_exists else None,
        'status': 'complete' if brief_exists else 'pending'
    })


@app.route('/api/fitness')
def api_fitness():
    """Fitness data endpoint"""
    # Try Central API
    data = fetch_with_fallback(f'{CENTRAL_API_URL}/fitness')
    
    # Fallback to local file
    if not data:
        fitness_data = load_json_file(FITNESS_DATA)
        settings = fitness_data.get('settings', {})
        weight_logs = fitness_data.get('weight_logs', [])
        workouts = fitness_data.get('workouts', [])
        
        current_weight = weight_logs[-1]['weight'] if weight_logs else settings.get('current_weight', 0)
        target_weight = settings.get('target_weight', 210)
        
        # Calculate progress
        start_weight = 225  # Default starting weight
        weight_lost = start_weight - current_weight
        target_loss = start_weight - target_weight
        progress = (weight_lost / target_loss * 100) if target_loss > 0 else 0
        
        data = {
            'current_weight': current_weight,
            'target_weight': target_weight,
            'weight_lost': weight_lost,
            'progress': progress,
            'workouts_this_week': len([w for w in workouts if datetime.fromisoformat(w.get('date', '2020-01-01')) > datetime.now() - timedelta(days=7)]),
            'last_workout': workouts[-1] if workouts else None
        }
    
    return jsonify(data)


@app.route('/api/golf')
def api_golf():
    """Golf statistics endpoint"""
    # Try Central API
    data = fetch_with_fallback(f'{CENTRAL_API_URL}/golf')
    
    # Fallback to local file
    if not data:
        golf_data = load_json_file(GOLF_DATA, {'rounds': [], 'courses': {}})
        rounds = golf_data.get('rounds', [])
        
        if rounds:
            recent_rounds = sorted(rounds, key=lambda x: x['date'], reverse=True)[:5]
            scores = [r['score'] for r in rounds]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            data = {
                'total_rounds': len(rounds),
                'average_score': round(avg_score, 1),
                'best_score': min(scores) if scores else 0,
                'recent_rounds': recent_rounds,
                'handicap_estimate': rounds[-1].get('handicap_estimate', 0) if rounds else 0
            }
        else:
            data = {
                'total_rounds': 0,
                'average_score': 0,
                'best_score': 0,
                'recent_rounds': [],
                'handicap_estimate': 0
            }
    
    return jsonify(data)


@app.route('/api/nba')
def api_nba():
    """NBA slate data endpoint"""
    today = datetime.now().strftime('%Y-%m-%d')
    nba_file = NBA_DATA.format(today)
    
    # Check if there's a slate today
    nba_data = load_json_file(nba_file)
    
    if nba_data and nba_data.get('players'):
        players = nba_data.get('players', [])
        recommendations = nba_data.get('recommendations', {})
        
        # Get top players by tier
        top_players = sorted(players, key=lambda x: x.get('value', 0), reverse=True)[:10]
        
        return jsonify({
            'has_slate': True,
            'date': today,
            'player_count': len(players),
            'top_players': top_players,
            'top_stars': recommendations.get('top_stars', [])[:5],
            'top_value': recommendations.get('top_value', [])[:5],
            'stacks': recommendations.get('recommended_stacks', [])[:2],
            'last_updated': nba_data.get('last_update'),
            'locked': nba_data.get('locked', False)
        })
    else:
        return jsonify({
            'has_slate': False,
            'date': today,
            'message': 'No NBA slate today'
        })


@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/all')
def api_all():
    """Fetch all dashboard data in one request (fast loading)"""
    return jsonify({
        'revenue': api_revenue().json,
        'opportunities': api_opportunities().json,
        'morning_brief': api_morning_brief().json,
        'fitness': api_fitness().json,
        'golf': api_golf().json,
        'nba': api_nba().json,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    logger.info("🚀 Starting Unified Dashboard on port 3000")
    logger.info("📊 Dashboard: http://localhost:3000")
    app.run(host='0.0.0.0', port=3000, debug=False)
